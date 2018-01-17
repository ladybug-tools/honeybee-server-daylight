FROM ladybugtools/honeybee

ENV CELERY_BROKER_URL redis://redis:6379
ENV CELERY_RESULT_BACKEND redis://redis:6379
ENV C_FORCE_ROOT true

# install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# create jobs folder as place holder
RUN mkdir /usr/local/hb_jobs

# copy source code
WORKDIR /usr/local/hb_worker
COPY ./*.py ./

# run the worker
ENTRYPOINT celery -A tasks worker --loglevel=info
