import os
from os import environ

from celery import Celery
from flask_sqlalchemy import model
from sqlalchemy import select
from database import init_db, db_session

app = Celery('tasks', broker=f'pyamqp://guest@{environ.get("RABBITMQ_HOST","localhost")}//')

@app.task()
def add(x, y):
    print(x+y)

@app.task()
def send_email(item_id):
    import smtplib
    from email.message import EmailMessage
    init_db()
    item = db_session.execute(select(model.Item).where(model.Item.item_id == item_id)).scalar()
    msg = EmailMessage()
    msg.set_content(f'My email')
    msg['Subject'] = 'Contract info'
    msg['From'] = "service_email@gmail.com"
    msg['To'] = "user1@gmail.com"

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()