# honeybee-docker-daylight
Honeybee docker image for daylight studies

This image is build based on learnings from the [honeybee-server]() project during the hackathon.

The docker images uses Flask, Redis and Celery Python libraries to provide a non-blocking web server.

# How to use this image

- Install docker.
- Pull the image from docker-hub
- docker-up ....

You need a honeybee recipe as JSON to use this docker image.

- You can upload the file from `localhost:5000`
- Or run it from python command line:
```python

code
```
- or from inside Grasshopper or Dynamo
```python

from honeybee-server import Client
...

```

# 

# dependencies
Dependencies is just for the purpose of giving credits. Thanks to docker you don't have to be worried about the dependencies.

0. Python 2.7
1. Flask to create the micro-service.
2. Redis and Redis-server as message broker.
3. Celery for parallel task execution.
4. Honeybee for creating daylight simulation files and parsing the results.
5. Radiance binaries for calculating daylight simulations.


# TODO
-[ ] Add a Database to dump the results. Currently the results are parsed from the file, added to analysis grid and parsed back in JSON format! Not efficient at all!
-[ ] Add a visual front-end to track the tasks. This will be meaningful once Honeybee API can provide percentage of task done. Currently it is as simple as Pending, Started, Success and Failure.

# Note
Honeybee docker image should be kept as small as possible. Eventually these images should be deployed on a server where hundreds of containers can be managed by [Kubernetes](https://kubernetes.io/) or a similar technology. 