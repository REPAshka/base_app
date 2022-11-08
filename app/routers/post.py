from typing import List, Optional
from fastapi import status, HTTPException, Depends, APIRouter, Response
from sqlalchemy.orm import Session
from .. import models, utils, schemas, oauth2
from ..database import get_db # одна точка - импорт из текущей папки, две точки - импорт из папки уровня выше
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# @router.get("/", response_model=List[schemas.PostResponse])  # List - потому что получаем тут не один пост, а несколько постов в листе. Вариант, чтобы показать все строку без джоинов, без кол-ва лайков
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # def get_posts(): # альтернатива через SQL запрос
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).all() # показать все посты на платформе
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all() # приписка .filter(models.Post.owner_id == current_user.id) позволяется смотреть пользователю только свои посты

    # искать посты по ключевому слову в тайтле "search=..." типо "%LIKE%" в sql, если хотим искать несколько слов, то пишем "word1%word2%word3", "%" - це как пробел
    # ограничить кол-во показанных постов "limit=...", по дефолту = 10, пропустить первые n постов "skip=..."
    # "?" - начало запроса с ограничением в строке сайта, типо "WHERE" в sql, "&" - следующий ограничивающий параметр, типо "AND" в sql
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(offset=skip).all() # показать все посты с заданными ограничениями
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(offset=skip).all()
    # равно SQL "SELECT posts.*, COUNT(votes.post_id) AS votes FROM posts LEFT OUTER JOIN votes ON posts.id = votes.post_id group by posts.id
    return results


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """ Создать пост. Для создания поста нужно быть зареганным на платформе """
    # current_user: int = Depends(oauth2.get_current_user) - требует, чтобы пользователь был зареган на платформе, если он хочет создать пост
    # def create_posts(post: Post): # альтернатива через SQL запрос
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id=current_user.id,
        **post.dict())  # **post.dict - распаковывает все поля (колонки из таблицы в бд) по типу title=post.title, content=post.content, published=post.published
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# @router.get("/{id}", response_model=schemas.PostResponse) # вариант, когда возвращаются данные о посте без джоина, без кол-ва лайков
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # def get_post(id: int): # альтернатива через SQL запрос
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first() # вариант, когда возвращаются данные о посте без джоина, без кол-ва лайков
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Have no rights to perform requested action") # Запрещает пользователю смотреть чужие посты
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """ Удалить пост. Для удаления поста нужно быть зареганным на платформе """
    # current_user: int = Depends(oauth2.get_current_user) - требует, чтобы пользователь был зареган на платформе, если он хочет удалить пост
    # def delete_post(id: int): # альтернатива через SQL запрос
    #     cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    #     deleted_post = cursor.fetchone()
    #     conn.commit()
    deleted_post_query = db.query(models.Post).filter(models.Post.id == id)
    deleted_post = deleted_post_query.first()
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    deleted_post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """ Обновить пост. Для обновиления поста нужно быть зареганным на платформе """
    # current_user: int = Depends(oauth2.get_current_user) - требует, чтобы пользователь был зареган на платформе, если он хочет обновить пост
    # def update_post(id: int, post: Post): # альтернатива через SQL запрос
    #     cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
    #                    (post.title, post.content, post.published, str(id)))
    #     updated_post = cursor.fetchone()
    #     conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
