from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import Settings
from typing import Optional, Iterable
from sqlalchemy.engine import Engine as Database

app_settings = Settings()

data_base_full_url = app_settings.get_full_db_url()

engine = create_engine(data_base_full_url)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_sess_new_session():
    local_engine = create_engine(app_settings.get_full_db_url())
    return sessionmaker(autocommit=False, autoflush=False, bind=local_engine)


_db_conn: Optional[Database] = None

def open_db_connections():
    global _db_conn
    _db_conn = get_engine()


def close_db_connections():
    global _db_conn
    if _db_conn:
        _db_conn.dispose()


def get_engine():
    return create_engine(app_settings.get_full_db_url())

# Dependency
def get_db():
    # get_db_sess_sess()
    db = get_db_sess()
    try:
        yield db
    finally:
        db.close()  # type: ignore

# ***


def get_db_conn() -> Database:
    assert _db_conn != None, "The DB connection is None"
    if _db_conn is not None:
        return _db_conn



# This is the part that replaces sessionmaker
def get_db_sess(db_conn=Depends(get_db_conn)) -> Iterable[Session]:
    sess = Session(bind=db_conn)

    try:
        yield sess
    finally:
        sess.close()