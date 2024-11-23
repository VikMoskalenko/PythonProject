#from datetime import datetime
import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, REAL, DateTime
from sqlalchemy.testing.schema import mapped_column

from database import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), unique=True)
    password = Column(String(50))
    nino = Column(String(50), unique=True)
    fullname = Column(String(150))
    photo = Column(String(150))
    contacts = Column(String(150))



class Item(Base):
    __tablename__ = 'item'
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    photo = Column(String(150))
    name = Column(String(150))
    description = Column(String(150))
    price_hour = Column(REAL)
    price_week = Column(REAL)
    price_month = Column(REAL)
    owner_id = mapped_column(Integer, ForeignKey('users.user_id'))

    def __init__(self, item_id, photo, name, description, price_hour, price_week,price_month, owner_id):
        self.item_id = item_id
        self.photo = photo
        self.name = name
        self.description = description
        self.price_hour = price_hour
        self.price_week = price_week
        self.price_month = price_month
        self.owner_id = owner_id

class Contract(Base):
    __tablename__ = 'contract'
    contract_id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(150))
    start_date = Column(String(150))
    end_date = Column(String(150))
    leaser = mapped_column(Integer, ForeignKey('leaser.leaser_id'))
    taker = mapped_column(Integer, ForeignKey('users.user_id'))
    item = mapped_column(Integer, ForeignKey('item.item_id'))
    status = Column(String(150))
    #signed_date = Column(String(150))
    signed_date = Column(DateTime, default=datetime.datetime.now)


    def __init__(self, text, start_date, end_date, leaser, taker, item, signed_date):
        self.text = text
        self.start_date = start_date
        self.end_date = end_date
        self.leaser = leaser
        self.taker = taker
        self.item = item
        self.status = 'available'
        self.signed_date = signed_date

class Leaser(Base):
    __tablename__ = 'leaser'
    leaser_id = Column(Integer, primary_key=True, autoincrement=True)
    info = Column(String(150))
    leaser_additional_info = Column(String(150))

    def __init__(self, info, leaser_additional_info):
        self.info = info
        self.leaser_additional_info = leaser_additional_info

class Feedback(Base):
    __tablename__ = 'feedback'
    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    author = mapped_column(Integer, ForeignKey('users.user_id'))
    user = mapped_column(Integer, ForeignKey('users.user_id'))
    feedback_text = Column(String(150))
    grade = Column(String(150))
    contract = mapped_column(Integer, ForeignKey('contract.contract_id'))

    def __init__(self, text, author, user, feedback_text, grade, contract):
        self.text = text
        self.author = author
        self.user = user
        self.feedback_text = feedback_text
        self.grade = grade
        self.contract = contract

class Complain(Base):
    __tablename__ = 'complain'
    complain_id = Column(Integer, primary_key=True, autoincrement=True)
    complain_text = Column(String(150))
    user_id = mapped_column(Integer, ForeignKey('users.user_id'))

    def __init__(self, complain_text, user_id):
        self.complain_text = complain_text
        self.user_id = user_id