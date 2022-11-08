""" Все данные для подключения к бд """

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
# import psycopg2 as pc2
# from psycopg2.extras import RealDictCursor
# import time

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}' \
                          f'@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
# парсим все секретные данные из файла окружения .env (config.py)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Проверка успешного подключения к бд, если подключено, то пишет в консоль, что всё оки-доки
# while True:
#     try:
#         conn = pc2.connect(host=settings.database_hostname, database=settings.database_name, user=settings.database_username, password=settings.database_password,
#                            cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connection was succesfull")
#         break
#     except Exception as error:
#         print(f"Failed to connection. Error: {error}")
#         time.sleep(3)