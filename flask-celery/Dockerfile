FROM antoinedao/honeybee

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true


# copy requirements
COPY requirements.txt /flask-celery/requirements.txt
WORKDIR /flask-celery

# install requirements
RUN pip install -r requirements.txt

# Copy the source code
COPY . /flask-celery/

# run the worker
#ENTRYPOINT ['celery']
#CMD ['-A','tasks', 'worker','--loglevel=info']
ENTRYPOINT celery -A tasks worker --loglevel=info
