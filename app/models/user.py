from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(db, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    login = Column(String(16), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    status = Column(String, nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)
