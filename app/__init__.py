from flask import Flask
from celery import Celery
from flask_celery import make_celery

app = Flask(__name__)
app.config.from_object('config')

celery = make_celery(app)

from app import views
from app import tasks
