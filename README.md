# honeybee server docker image
Honeybee docker for daylight studies. This project is built based on the learnings from the [honeybee-server](https://github.com/ladybug-tools/honeybee-server) during the hackathon.
It uses Flask, Redis and Celery libraries to provide a non-blocking web server for honeybee.

## Getting started
- Install [docker](https://docs.docker.com/engine/installation/).
- Install [docker-compose](https://docs.docker.com/compose/install/). For Windows it is bundled with the installation.
- clone this repository.

Now go to the directory and use `docker-compose build` to build the bundle. In Windows run cmd as an administrator. For impatient users try `docker-compose up --build -d` and if there is no errors go to Run Simulations section.

Here is a step by step installation to make sure everything is working correctly.
```shell
>> docker-compose build
```

Once the build is done try `docker images` and you should see `python` and `ladybugtools/hbserver` images.

```shell
>> docker images

REPOSITORY              TAG                 IMAGE ID            CREATED              SIZE
ladybugtools/hbserver   latest              ff7d9fac31a7        About a minute ago   716MB
python                  2.7                 9e92c8430ba0        2 weeks ago          681MB
```
Now let's run it for the first time! I don't use `-d` to be able to see the errors if any. Once you run it once with no issues you run the same command with `-d` to run the docker images in detached mode.
exit
* Also when you run this command for the first time it pulls Redis image.

```shell
>> docker-compose up

Creating network "honeybeedockerdaylight_default" with the default driver
Pulling redis (redis:latest)...
latest: Pulling from library/redis
c4bb02b17bb4: Pull complete
58638acf67c5: Pull complete
f98d108cc38b: Pull complete
83be14fccb07: Pull complete
5d5f41793421: Pull complete
ed89ff0d9eb2: Pull complete
Creating honeybeedockerdaylight_redis_1   ... done
Status: Downloaded newer image for redis:latest
Creating honeybeedockerdaylight_celery_1  ... done
Creating honeybeedockerdaylight_celery_1  ...
Creating honeybeedockerdaylight_hbflask_1 ... done
Attaching to honeybeedockerdaylight_redis_1, honeybeedockerdaylight_celery_1, honeybeedockerdaylight_hbflask_1
celery_1   | /usr/local/lib/python2.7/site-packages/celery/platforms.py:795: RuntimeWarning: You are running the worker with superuser privileges: this is
celery_1   | absolutely not recommended!
celery_1   |
celery_1   | Please specify a different user using the -u option.
celery_1   |
celery_1   | User information: uid=0 euid=0 gid=0 egid=0
celery_1   |
celery_1   |   uid=uid, euid=euid, gid=gid, egid=egid,
redis_1    | 1:C 28 Dec 22:49:51.151 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
redis_1    | 1:C 28 Dec 22:49:51.151 # Redis version=4.0.6, bits=64, commit=00000000, modified=0, pid=1, just started
redis_1    | 1:C 28 Dec 22:49:51.151 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
celery_1   | [2017-12-28 22:49:52,526: INFO/MainProcess] Connected to redis://redis:6379/0
redis_1    | 1:M 28 Dec 22:49:51.152 * Running mode=standalone, port=6379.
celery_1   | [2017-12-28 22:49:52,533: INFO/MainProcess] mingle: searching for neighbors
redis_1    | 1:M 28 Dec 22:49:51.152 # WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
redis_1    | 1:M 28 Dec 22:49:51.152 # Server initialized
redis_1    | 1:M 28 Dec 22:49:51.152 # WARNING you have Transparent Huge Pages (THP) support enabled in your kernel. This will create latency and memory usage issues with Redis. To fix this issue run the command echo never > /sys/kernel/mm/transparent_hugepage/enabled as root, and add it to your /etc/rc.local in order to retain the setting after a reboot. Redis must be restarted after THP is disabled.
redis_1    | 1:M 28 Dec 22:49:51.152 * Ready to accept connections
hbflask_1  |  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
celery_1   | [2017-12-28 22:49:53,550: INFO/MainProcess] mingle: all alone
celery_1   | [2017-12-28 22:49:53,573: INFO/MainProcess] celery@51005efc686f ready.
```

If you see errors your server is ready to run the daylight simulations!

## Run simulations
You need a honeybee recipe as JSON to start testing. If you don't have any check the tests folder for a number of sample files.

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

data = {'file': open('./tests/recipe.json', 'rb')}
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


## Stop server
If you didn't run `docker-compose` command with `-d` press ctrl + c to stop the images. Now run `docker-compose down`.

```shell
>> docker-compose down

Stopping honeybeedockerdaylight_hbflask_1 ... done
Stopping honeybeedockerdaylight_celery_1  ... done
Stopping honeybeedockerdaylight_redis_1   ... done
Removing honeybeedockerdaylight_hbflask_1 ... done
Removing honeybeedockerdaylight_celery_1  ... done
Removing honeybeedockerdaylight_redis_1   ... done
Removing network honeybeedockerdaylight_default
```

## Dependencies
Dependencies is just for the purpose of giving credits. Thanks to docker you don't have to be worried about installing them.

1. [Python 2.7](https://www.python.org/)
2. [Flask](http://flask.pocoo.org/)
3. [Redis](https://redis.io/)
4. [Celery](http://www.celeryproject.org/)
5. [Honeybee](http://www.ladybug.tools/honeybee.html)
6. [Radiance 5.1.0](https://github.com/NREL/Radiance/releases/tag/5.1.0)


## TODO
- [ ] Add a database to dump the results. Currently the results are parsed from the file, added to analysis grid and parsed back in JSON format! We need to change Honeybee in the first place and adapt it to put the results in JSON format and then we can go ahead with this change.

- [ ] Add a visual front-end to track the tasks. This will be meaningful once Honeybee API can provide percentage of task done. Currently it is as simple as Pending, Started, Success and Failure.

## Note
Honeybee docker image should be kept as small as possible. Eventually it should be deployed on a server where hundreds of containers can be managed by [Kubernetes](https://kubernetes.io/) or a similar technology. I wanted to say `docker swarm` but it seems that docker is also working with Kubernetes for container orchastration.
