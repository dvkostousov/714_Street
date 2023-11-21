from sqlalchemy import Column, Integer, String, Float

from app.extensions import db


class Product(db):
    __tablename__ = 'products'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    categories = Column(String(100), nullable=False)
    sizes = Column(String(100))
    colors = Column(String(100))
    sections = Column(String(100))
    price = Column(Float(), nullable=False)
    old_price = Column(Float())
    main_photo = Column(String(), nullable=False)
    photos = Column(String())
