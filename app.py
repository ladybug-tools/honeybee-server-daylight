import os
import json
import zipfile
from flask import Flask, url_for, jsonify, request, send_file
from flask_celery import make_celery
from flask_util import allowed_file

from honeybee_server import run_from_json

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
app.config['HISTORY'] = []
# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
app.config['CELERY_BACKEND'] = 'redis://redis:6379/0'
# Initialize Celery
celery = make_celery(app)

# create the folder in doesn't exist
app.config['UPLOAD_FOLDER'] = os.path.join(BASEDIR, 'jobs')
if not os.path.isdir(app.config['UPLOAD_FOLDER']):
    os.mkdir(app.config['UPLOAD_FOLDER'])


# TODO: wrap the task into a class and separate run from preparation
# see: https://blog.fossasia.org/ideas-on-using-celery-with-flask-for-background-tasks/
# or https://blog.balthazar-rouberol.com/celery-best-practices
# soft_time_limit=60
@celery.task(bind=True, name='app.simulation')
def simulation(self, recipe):
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
        success, results = run_from_json(recipe, app.config['UPLOAD_FOLDER'],
                                         str(self.request.id))
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


# TODO: use flask upload plugin with more roboust checks for inputs
# see: http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Upload json file."""
    if request.method == 'POST':
        input_file = request.files.get('file', None)

        if not input_file:
            response = jsonify({'success': False,
                                'message': 'No file sent with request'})
            response.status_code = 400
            return response

        if input_file and allowed_file(input_file.filename):
            # load json data and start the simulation in the background
            recipe = json.load(input_file)
            task = simulation.delay(recipe)
            app.config['HISTORY'].append(task.id)
            return jsonify(
                {'success': True,
                 'message': 'Uploaded {}. Check status_url for progress and results'
                    .format(input_file.filename),
                 'task_id': task.id,
                 'status_url': url_for('status', task_id=task.id),
                 'download_url': url_for('download', task_id=task.id),
                 }), 202, \
                {'status': url_for('status', task_id=task.id), 'task_id': task.id}
        else:
            response = jsonify({'success': False,
                                'message': 'No file sent or invalid file type'})
            response.status_code = 400
            return response
    else:
        # GET requests
        return '''
        <!doctype html>
        <title>Upload Recipe JSON</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''


@app.route('/history')
def histroy():
    """Get list of all jobs."""
    return jsonify(app.config['HISTORY'])


@app.route('/download/<string:task_id>')
def download(task_id):
    """Return simulation folder as a zipped file."""
    if task_id not in os.listdir(app.config['UPLOAD_FOLDER']):
        response = jsonify({
            'success': False,
            'message': 'Invalid task Id.'
        })
        response.status_code = 400
        return response
    else:
        folder = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
        zipf = zipfile.ZipFile('%s.zip' % task_id, 'w', zipfile.ZIP_DEFLATED)
        root_length = len(folder) + 1
        for root, dirs, files in os.walk(folder):
            for file in files:
                fn = os.path.join(root, file)
                zipf.write(fn, fn[root_length:])
        zipf.close()
        return send_file('%s.zip' % task_id,
                         mimetype='zip',
                         attachment_filename='%s.zip' % task_id,
                         as_attachment=True)


@app.route('/status/<string:task_id>')
def status(task_id):
    """Get status for the task using task id."""
    task = simulation.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state == 'FAILURE':
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    else:
        # task is started
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
