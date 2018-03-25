import os
from flask import Flask
from flask import url_for
from flask import request, jsonify
from flask import render_template
from worker import celery
from celery.result import AsyncResult
import celery.states as states

env=os.environ
app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('index.html')

# Checking on running jobs
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
            'current': task.info,#.get('current', 0),
            'total': task.info,#.get('total', 1),
            'status': task.info,#.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info#['result']

    return jsonify(response)

# API end points to run simulation from full recipes
@app.route('/run/daylight_factor', methods = ["POST"])
def daylight_factor():
    content = request.json
    if "analysis_grids" in content["payload"].keys() \
        and "surfaces" in content["payload"].keys() \
        and content["payload"]["id"] == "daylight_factor":
        task = celery.send_task('dispatch.recipe', args=[content['payload'],'daylight_factor'])
        return_string = "<a href='{url}'>check status of {id} </a>" \
                .format(id=task.id, url='http://192.168.99.100:5000/status/'+ str(task.id))
        return return_string
    else:
        return "That doesn't look right..."

@app.route('/run/annual', methods = ["POST"])
def annual():
    content = request.json
    if "analysis_grids" in content["payload"].keys() \
        and "surfaces" in content["payload"].keys() \
        and content["payload"]["id"] == "annual":
        task = celery.send_task('dispatch.recipe', args=[content["payload"], 'annual'])
        return_string = "<a href='{url}'>check status of {id} </a>" \
                .format(id=task.id, url='http://192.168.99.100:5000/check/'+ str(task.id))
        return return_string
    else:
        return "That doesn't look right..."

@app.route('/run/radiation', methods = ["POST"])
def radiation():
    content = request.json
    if "analysis_grids" in content["payload"].keys() \
        and "surfaces" in content["payload"].keys() \
        and content["payload"]["id"] == "radiation":
        task = celery.send_task('dispatch.recipe', args=[content["payload"], "radiation"])
        return_string = "<a href='{url}'>check status of {id} </a>" \
                .format(id=task.id, url='http://192.168.99.100:5000/check/'+ str(task.id))
        return return_string
    else:
        return "That doesn't look right..."

# API end points to run "enforced" specification simulation
# eg: send geometry + grids only and get daylight factor run on high specs
# eg: send geometry + grids + skymtx and simulate daylight factor + annual + radiation
@app.route('/run/geometry/to_daylight_factor', methods = ["POST"])
def geometry_to_df():
    content = request.json
    if "analysis_grids" in content["payload"].keys() \
        and "surfaces" in content["payload"].keys():
        for analysis_grid in content["payload"]["analysis_grids"]:
            for analysis_point in analysis_grid["analysis_points"]:
                del analysis_point["values"]
        task = celery.send_task('geometry.to_daylight_factor', args=[content["payload"]])
        return "<a href='{url}'>check status of {id} </a>".format(id=task.id,
                    url='http://192.168.99.100:5000/check/'+ str(task.id))
    else:
        return "That does not like it's got the right information..."

@app.route('/run/geometry_wea/to_annual', methods = ["POST"])
def geometry_to_annual():
    content = request.json
    if "analysis_grids" in content["payload"].keys() \
        and "surfaces" in content["payload"].keys() \
        and "sky_mtx" in content["payload"].keys():
        for analysis_grid in content["payload"]["analysis_grids"]:
            for analysis_point in analysis_grid["analysis_points"]:
                del analysis_point["values"]
        task = celery.send_task('geometry_wea.to_annual', args=[content["payload"]])
        return "<a href='{url}'>check status of {id} </a>".format(id=task.id,
                    url='http://192.168.99.100:5000/check/'+ str(task.id))
    else:
        return "That does not like it's got the right information..."

@app.route('/run/geometry_wea/to_radiation', methods = ["POST"])
def geometry_to_radiation():
    content = request.json
    if "analysis_grids" in content["payload"].keys() \
        and "surfaces" in content["payload"].keys() \
        and "sky_mtx" in content["payload"].keys():
        for analysis_grid in content["payload"]["analysis_grids"]:
            for analysis_point in analysis_grid["analysis_points"]:
                del analysis_point["values"]
        task = celery.send_task('geometry_wea.to_radiation', args=[content["payload"]])
        return "<a href='{url}'>check status of {id} </a>".format(id=task.id,
                    url='http://192.168.99.100:5000/check/'+ str(task.id))
    else:
        return "That does not like it's got the right information..."

if __name__ == '__main__':
    app.run(debug=env.get('DEBUG',True),
            port=int(env.get('PORT',5000)),
            host=env.get('HOST','0.0.0.0')
    )
