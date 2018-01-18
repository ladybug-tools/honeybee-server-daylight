FROM python:2.7

ENV CELERY_BROKER_URL=redis://redis:6379 \
  CELERY_RESULT_BACKEND=redis://redis:6379 \
  C_FORCE_ROOT=true \
  HOST=0.0.0.0 \
  PORT=5000 \
  DEBUG=true

# install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# create jobs folder as place holder
RUN mkdir /usr/local/hb_jobs

# copy source code
WORKDIR /usr/local/hb_server

COPY ./*.py ./

# expose the app port
EXPOSE 5000
