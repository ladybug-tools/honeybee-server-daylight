import os
import json
import zipfile
from flask import Flask
from flask import url_for, jsonify, request, send_file
from flask_util import allowed_file
from worker import celery
import celery.states as states

env = os.environ
app = Flask(__name__)
app.config['HISTORY'] = []
app.config['UPLOAD_FOLDER'] = '/usr/local/hb_jobs'


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
            task = celery.send_task('honeybee.simulation',
                                    args=[recipe, app.config['UPLOAD_FOLDER']])
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
    task = celery.AsyncResult(task_id)
    if task.state == states.PENDING:
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state == states.FAILURE:
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
    app.run(debug=env.get('DEBUG', True),
            port=int(env.get('PORT', 5000)),
            host=env.get('HOST', '0.0.0.0')
            )
