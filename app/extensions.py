from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db = declarative_base()
engine = create_engine('sqlite:///714_street.db?check_same_thread=False')


def create_session():
    db.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    session = db_session()
    return session

