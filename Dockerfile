FROM python:2.7

# create honeybee folder
WORKDIR /usr/local/hb_docker

# install python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# create jobs folder as place holder
COPY ./jobs /jobs

# this didn't solve the permission issues for celery.
# for now running everything as root.
# RUN chown nobody: /jobs && chmod u+rwX /jobs

# copy ladybug and honeybee libraries.
COPY ./ladybug ./ladybug
COPY ./honeybee ./honeybee

# copy all the python files for the app
COPY ./*.py ./

# copy radiance libraries
#COPY ./radiance/bin /usr/local/bin
#COPY ./radiance/lib /usr/local/lib/ray

# Install Radiance from source
# Avoids issue you had here with missing lib file(?)
RUN cd /tmp \
    && wget https://github.com/NREL/Radiance/releases/download/5.1.0/radiance-5.1.0-Linux.tar.gz \
    && tar -xzvf radiance-5.1.0-Linux.tar.gz \
    && cp -a radiance-5.1.0-Linux/usr/local/radiance/bin/. /usr/local/bin \
    && cp -a radiance-5.1.0-Linux/usr/local/radiance/lib/. /usr/local/lib/ray 
# Where do the "man" folder items go?

EXPOSE 5000
