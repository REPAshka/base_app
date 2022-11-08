from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models # одна точка - импорт из текущей папки, две точки - импорт из папки уровня выше
from .database import engine
from .routers import post, user, auth, vote
from .config import settings

# проверяет есть ли указанные там таблице в бд, если их нет, то создаёт их
# models.Base.metadata.create_all(bind=engine) # т.к. по итогу использю alembic, то это строка уже не нужна

app = FastAPI()

app.include_router(post.router)

origins = ["*"] # список доменов, пользователи которых могут обращаться к нашему приложению, типо https://www.google.com

app.add_middleware(
    CORSMiddleware,
    allow_orgins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"message": "Hello Worldddd"}



