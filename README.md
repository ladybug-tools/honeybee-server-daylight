# honeybee server docker image for daylight analysis
Honeybee docker for daylight studies. This project is built based on the learnings from the [honeybee-server](https://github.com/ladybug-tools/honeybee-server) during the hackathon.
It uses Flask, Redis and Celery libraries to provide a non-blocking web server for [honeybee](https://github.com/ladybug-tools/honeybee).

## Getting started
- Install [docker](https://docs.docker.com/engine/installation/) 17.12.0-ce or higher.
- Install [docker-compose](https://docs.docker.com/compose/install/) 1.18.0 or higher. For Windows it is bundled with the installation.
- Clone this repository.

**NOTE**: If you have docker and docker-compose already installed you can check the version by using commands below:
```shell
>> docker version
>> docker-compose version
```

Now go to the directory and use `docker-compose build` to build the bundle. In Windows run cmd as an administrator. For impatient users try `docker-compose up --build -d` and go to **Run Simulations** section.

Here is a step by step installation to make sure everything is working correctly.
```shell
>> docker-compose build
```

Once the build is done try `docker images` and you should see `redis`, `python`,  `ladybugtools/ladybug`, `ladybugtools/honeybee`, `ladybugtools/hbserver` and `ladybugtools/hbworker` images.

```shell
>> docker images

REPOSITORY              TAG                 IMAGE ID            CREATED             SIZE
ladybugtools/hbworker   latest              a3f135ceed4e        40 minutes ago      749MB
ladybugtools/honeybee   latest              2fbce9e32968        41 minutes ago      703MB
ladybugtools/hbserver   latest              6d38a96eb3b9        2 hours ago         695MB
ladybugtools/ladybug    latest              6928a59830ae        6 hours ago         681MB
python                  2.7                 9e92c8430ba0        5 weeks ago         681MB
redis                   latest              1e70071f4af4        5 weeks ago         107MB
```
Now let's run it for the first time! I will use `-d` run the create the containers in detached mode but if you want to see what happens in the background feel free to remove `-d-`.

```shell
>> docker-compose up -d
```

## Add more workers
If you go to http://localhost:5555 you will see that by default one worker is created and waiting for jobs but we can scale the workers by using `docker-compose up --scale` command. Try the command below to create 5 containers each running a worker.

```shell
>> docker-compose up -d --scale worker=5
Creating network "honeybeedockerdaylight_default" with the default driver
Creating honeybeedockerdaylight_worker_1  ... done
Creating honeybeedockerdaylight_worker_2  ... done
Creating honeybeedockerdaylight_worker_3  ... done
Creating honeybeedockerdaylight_worker_4  ... done
Creating honeybeedockerdaylight_worker_5  ... done
Creating honeybeedockerdaylight_worker_4  ...
Creating honeybeedockerdaylight_api_1     ... done
Creating honeybeedockerdaylight_api_1     ...
```

You can use `docker ps` to see the list of running containers.

```shell
>> docker ps
CONTAINER ID        IMAGE                   COMMAND                  CREATED             STATUS              PORTS                    NAMES
f2e00044532c        ladybugtools/hbserver   "python app.py"          33 seconds ago      Up 31 seconds       0.0.0.0:5000->5000/tcp   honeybeedockerdaylight_api_1
70873256595f        ladybugtools/hbworker   "/bin/sh -c 'celery …"   36 seconds ago      Up 33 seconds                                honeybeedockerdaylight_worker_1
9156fd3b656f        ladybugtools/hbworker   "/bin/sh -c 'celery …"   36 seconds ago      Up 33 seconds                                honeybeedockerdaylight_worker_3
ff8163050210        ladybugtools/hbworker   "/bin/sh -c 'celery …"   36 seconds ago      Up 32 seconds                                honeybeedockerdaylight_worker_4
d5a7beeb85d9        ladybugtools/hbworker   "flower -A tasks --p…"   36 seconds ago      Up 33 seconds       0.0.0.0:5555->5555/tcp   honeybeedockerdaylight_monitor_1
defc0e0c07a0        ladybugtools/hbworker   "/bin/sh -c 'celery …"   36 seconds ago      Up 34 seconds                                honeybeedockerdaylight_worker_2
2b7ae6cae809        ladybugtools/hbworker   "/bin/sh -c 'celery …"   36 seconds ago      Up 34 seconds                                honeybeedockerdaylight_worker_5
ee06f7d06b44        redis                   "docker-entrypoint.s…"   37 seconds ago      Up 36 seconds       6379/tcp                 honeybeedockerdaylight_redis_1
```

## Run simulations
This image works with honeybee recipes in JSON format. If you don't have any check the `tests` folder for a number of sample files.

Open a browser of your choice and go to `localhost:5000`. Select the file and press upload.

![image](https://user-images.githubusercontent.com/2915573/34425465-302cf38a-ebfa-11e7-9055-27e0c6e8e594.png)

The server should return a JSON object similar to this:
```js
{
  "download_url": "/download/7b9fe04c-53ac-4aaa-b6e6-0412ba24e602",
  "message": "Uploaded test_recipe.json. Check status_url for progress and results",
  "status_url": "/status/7b9fe04c-53ac-4aaa-b6e6-0412ba24e602",
  "success": true,
  "task_id": "7b9fe04c-53ac-4aaa-b6e6-0412ba24e602"
}
```
Now you can use the `status_url` to see the progress and results or use or `download_url` to download the simulation folder.

This is the first lines for http://localhost:5000/status/7b9fe04c-53ac-4aaa-b6e6-0412ba24e602
```js
{
  "current": 100,
  "result": [
    {
      "analysis_points": [
        {
          "direction": [
            0.0,
            0.0,
            1.0
          ],
          "location": [
            0.5,
            0.5,
            0.7620000243186951
          ],
          "values": [
            [
              {
                "1639": [
                  1,
                  null
                ], ...
}
```

Or you can send the request using python. This is also how honeybee calls this service. See `test.py` for an example with multiple jobs to see how celery handles multiple jobs without blocking the server. Here is an example for a single simulation.

```python
import requests
import time
import json

data = {'file': open('./tests/solar_access_recipe.json', 'rb')}
response = requests.post(url='http://127.0.0.1:5000/', files=data)
status_url = response.headers['status']

# check the status
while True:
    progress = requests.get('http://127.0.0.1:5000' + status_url)
    content = json.loads(progress.content)
    if content['state'] == 'PENDING':
        print('task is pending!')
    elif content['state'] == 'STARTED':
        print('task is still running!')
    else:
        print('task is finished!')
        break
    time.sleep(1)

# get results
for grid in content['result']:
     for count, pt in enumerate(grid['analysis_points']):
         print('sensor #{}; location: {}'.format(count, pt['location']))
         for values in pt['values'][0]:
             for hour, value in values.iteritems():
                 print('\thour: {} >> result: {}'.format(hour, value[0]))
```


## Remove containers
```shell
>> docker-compose down
```

## Dependencies
Dependencies is just for the purpose of giving credits. Thanks to docker you don't have to be worried about installing them.

1. [Python 2.7](https://www.python.org/)
2. [Flask 0.12.2](http://flask.pocoo.org/)
3. [Redis 2.10.6](https://redis.io/)
4. [Celery 4.1.1](http://www.celeryproject.org/)
5. [Flower 0.9.2](https://flower.readthedocs.io/en/latest/)
6. [Honeybee](http://www.ladybug.tools/honeybee.html)
7. [Radiance 5.2.0](https://github.com/NREL/Radiance/releases/tag/5.2.0)

## TODO
- [ ] Add a database to dump the results. Currently the results are parsed from the file, added to analysis grid and parsed back in JSON format! We need to change Honeybee in the first place and adapt it to put the results in JSON format and then we can go ahead with this change.

- [ ] Add a visual front-end to track the tasks. This will be meaningful once Honeybee API can provide percentage of task done. Currently it is as simple as Pending, Started, Success and Failure.
