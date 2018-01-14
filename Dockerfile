FROM python:2.7

# create honeybee folder
WORKDIR /usr/local/hb_docker

# install python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy radiance libraries
COPY ./radiance/bin /usr/local/bin
COPY ./radiance/lib /usr/local/lib/ray

# create jobs folder as place holder
COPY ./jobs /jobs

# copy ladybug and honeybee libraries.
COPY ./ladybug ./ladybug
COPY ./honeybee ./honeybee

# copy all the python files for the app
COPY ./*.py ./

EXPOSE 5000
