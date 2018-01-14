import os

REDIS_URL = 'redis://redis:6379/0'
REDIS_URL = 'redis://localhost:6379'
CELERY_BROKER_URL = REDIS_URL
CELERY_BACKEND = REDIS_URL

BASEDIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASEDIR, 'jobs')
HISTORY = []
