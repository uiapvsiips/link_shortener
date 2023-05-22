import os

from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

DB_HOST = os.environ.get('DB_HOST', 'localhost')  # Потрібно замінити на відповідні дані для підключення до бази даних
conn_str=f'postgresql://user:password@{DB_HOST}:5432/db'

DB_HOST = os.environ.get('DB_HOST', 'localhost')
engine = create_engine(conn_str)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)