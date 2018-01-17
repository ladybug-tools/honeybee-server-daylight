import os
from celery import Celery
from honeybee_server import run_from_json


env = os.environ
CELERY_BROKER_URL = env.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = env.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')


celery = Celery('hbserver',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)


# TODO: wrap the task into a class and separate run from preparation
# see: https://blog.fossasia.org/ideas-on-using-celery-with-flask-for-background-tasks/
# or https://blog.balthazar-rouberol.com/celery-best-practices
# soft_time_limit=60
@celery.task(bind=True, name='honeybee.simulation')
def simulation(self, recipe, folder):
    """background simulation.
    recipe: Honeybee recipe data as json.
    """
    total = 100
    # create recipe
    self.update_state(state='STARTED',
                      meta={'current': 5, 'total': total,
                            'status': 'Starting the simulation!'})

    # run the recipe from json input
    try:
        success, results = run_from_json(recipe, folder, str(self.request.id))
        # TODO: Currently the process is blocking and waits for analysis to be over
        # This should change to a non-blocking run similar to butterfly
        # check if the recipe is running
    except Exception as e:
        self.update_state(state='FAILURE',
                          meta={'current': 0, 'total': total,
                                'status': 'Task failed!',
                                'result': str(e)})
        return {'current': 0, 'total': total,
                'status': 'Task failed!',
                'result': str(e)}
    else:
        # update the progress
        if success:
            self.update_state(state='SUCCESS',
                              meta={'current': 100, 'total': total,
                                    'status': 'Task completed!',
                                    'result': results})
            return {'current': 100, 'total': 100,
                    'status': 'Task completed!',
                    'result': results}
        else:
            self.update_state(state='FAILURE',
                              meta={'current': 0, 'total': total,
                                    'status': 'Task failed!',
                                    'result': results})
            return {'current': 0, 'total': total,
                    'status': 'Task failed!',
                    'result': []}
