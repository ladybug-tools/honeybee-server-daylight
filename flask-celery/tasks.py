import os
import time
from celery import Celery
import json
import re
from celery.result import AsyncResult
import celery.states as states
from flask import url_for

env=os.environ
CELERY_BROKER_URL=env.get('CELERY_BROKER_URL','redis://localhost:6379'),
CELERY_RESULT_BACKEND=env.get('CELERY_RESULT_BACKEND','redis://localhost:6379')

# Custom deploy scripts
from recipe_scripts import simulations

celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

# Task dispatching funcion. It is used for all recipes to split multiple grids
# and run them on seperate containers
@celery.task(name='dispatch.recipe')
def dispatch_recipe(recipe, simulation_type):
    tasks = list()
    for grid in recipe["analysis_grids"]:

        recipe_json = {
            "surfaces": recipe["surfaces"],
            "rad_parameters": recipe["rad_parameters"],
            "sky_mtx": None,
            "analysis_grids": [grid],
            "type": recipe["type"],
            "id": recipe["id"]
        }

        if "sky_mtx" in recipe:
            recipe_json["sky_mtx"] = recipe["sky_mtx"]
        else:
            recipe_json.pop('sky_mtx')

        task = celery.send_task('run.{}'.format(simulation_type), args=[recipe_json])
        return_string = "<a href={url}>check status of {name} ({id}) </a>" \
                    .format(id=task.id, name=grid['name'],
                        url='http://192.168.99.100:5000/status/'+ str(task.id))
        tasks.append(return_string)
    return '<br>'.join(tasks)

# Geometry to Recipe functions
# These take the raw geometric and weather file info from the json payload
# to create company approved Honeybee Daylight recipes.
# One could add some neat stuff to enforce fabric properties here for example
@celery.task(name='geometry.to_daylight_factor')
def recipe_df(payload):
    from honeybee.radiance.recipe.daylightfactor.gridbased import GridBased
    from honeybee.radiance.analysisgrid import AnalysisGrid
    from honeybee.hbsurface import HBSurface
    from honeybee.radiance.parameters.gridbased import LowQuality

    surfaces = tuple(HBSurface.from_json(srf) for srf in payload["surfaces"])
    grids = tuple(AnalysisGrid.from_json(ag) for ag in payload["analysis_grids"])
    # Low Quality settings to test faster
    params = LowQuality()

    analysisRecipe = GridBased(grids, params)
    analysisRecipe.hb_objects = surfaces

    recipe_payload = {"payload": analysisRecipe.to_json()}

    task = celery.send_task('dispatch.recipe', args=[recipe_payload['payload'],'daylight_factor'])
    return_string = "<a href='{url}'>check status of {id} </a>" \
            .format(id=task.id, url='http://192.168.99.100:5000/status/'+ str(task.id))

    return return_string

@celery.task(name='geometry_wea.to_annual')
def recipe_annual(payload):
    from honeybee.radiance.recipe.annual.gridbased import GridBased
    from honeybee.radiance.analysisgrid import AnalysisGrid
    from honeybee.hbsurface import HBSurface
    from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
    from honeybee.radiance.sky.skymatrix import SkyMatrix

    surfaces = tuple(HBSurface.from_json(srf) for srf in payload["surfaces"])
    grids = tuple(AnalysisGrid.from_json(ag) for ag in payload["analysis_grids"])
    # Low Quality settings to test faster
    params = RfluxmtxParameters(0)
    sky_mtx = SkyMatrix.from_json(payload["sky_mtx"])

    analysisRecipe = GridBased(sky_mtx=sky_mtx, analysis_grids=grids,\
        radiance_parameters = params)
    analysisRecipe.hb_objects = surfaces

    recipe_payload = {"payload": analysisRecipe.to_json()}

    task = celery.send_task('dispatch.recipe', args=[reci[e_payload]["payload"], 'annual'])
    return_string = "<a href='{url}'>check status of {id} </a>" \
            .format(id=task.id, url='http://192.168.99.100:5000/status/'+ str(task.id))

    return return_string

@celery.task(name='geometry_wea.to_radiation')
def recipe_radiation(payload):
    from honeybee.radiance.recipe.radiation.gridbased import GridBased
    from honeybee.radiance.analysisgrid import AnalysisGrid
    from honeybee.radiance.parameters.rfluxmtx import RfluxmtxParameters
    from honeybee.radiance.sky.skymatrix import SkyMatrix

    surfaces = tuple(HBSurface.from_json(srf) for srf in payload["surfaces"])
    grids = tuple(AnalysisGrid.from_json(ag) for ag in payload["analysis_grids"])
    # Low Quality settings to test faster
    params = RfluxmtxParameters(0)
    sky_mtx = SkyMatrix.from_json(payload["sky_mtx"])

    analysisRecipe = GridBased(sky_mtx=sky_mtx, analysis_grids=grids,\
        radiance_parameters = params)
    analysisRecipe.hb_objects = surfaces

    recipe_payload = {"payload": analysisRecipe.to_json()}

    task = celery.send_task('dispatch.recipe', args=[recipe_payload["payload"], "radiation"])
    return_string = "<a href='{url}'>check status of {id} </a>" \
            .format(id=task.id, url='http://192.168.99.100:5000/status/'+ str(task.id))

    return return_string

# Run.Recipe functions
# These functions take a recipe with a single analysis grid, run the recipe and
# perform a quick post processing exercise on the results. This could/should be
# more customisable. Would be interesting to maybe add middleware to capture recipe
# results and run custom post-processing.
@celery.task(name='run.daylight_factor')
def run_df(payload):
    from honeybee.radiance.recipe.daylightfactor.gridbased import GridBased
    from honeybee.hbsurface import HBSurface

    analysisRecipe = GridBased.from_json(payload)
    surfaces = tuple(HBSurface.from_json(srf) for srf in payload["surfaces"])
    analysisRecipe.hb_objects = surfaces
    name = "daylightfactor"

    results = simulations.run(analysisRecipe, name)
    results_list = [point["values"][0][0][6324][0] for point in results.to_json()["analysis_points"]]

    average_df =  float(sum(results_list) / len(results_list))

    return json.dumps({"grid results": results.to_json(), "key_results": {"average daylight factor": average_df}})

@celery.task(name='run.annual')
def run_annual(payload):
    from honeybee.radiance.recipe.annual.gridbased import GridBased
    from honeybee.hbsurface import HBSurface

    analysisRecipe = GridBased.from_json(payload)
    surfaces = tuple(HBSurface.from_json(srf) for srf in payload["surfaces"])
    analysisRecipe.hb_objects = surfaces
    name = 'annual'
    results = simulations.run(analysisRecipe, name)

    # There should be a method to determine which post-processing values should
    # be used when calculating annual results metrics
    da_threshold = None
    udi_min_max = None
    occ_schedule = None

    DA, CDA, UDI, UDILess, UDIMore = results.annual_metrics(da_threshold, udi_min_max,
        None, occ_schedule)

    key_results = {"daylight_autonomy": DA,
                   "continuous_daylight_autonomy": CDA,
                   "useful_daylight_autonomy": UDI,
                   "useful_daylight_autonomy_less": UDILess,
                   "useful_daylight_autonomy_more": UDIMore}

    results.load_values_from_files()

    return json.dumps({"grid results": results.to_json(), "key_results": key_results})

@celery.task(name='run.radiation')
def run_radiation(payload):
    from honeybee.radiance.recipe.radiation.gridbased import GridBased
    from honeybee.hbsurface import HBSurface

    analysisRecipe = GridBased.from_json(payload)
    surfaces = tuple(HBSurface.from_json(srf) for srf in payload["surfaces"])
    analysisRecipe.hb_objects = surfaces
    name = 'radiation'
    results = simulations.run(analysisRecipe, name)

    results.load_values_from_files()

    key_results = {}

    for key in json_grid["analysis_points"][0]["values"][0][0].keys():
        pit_grid = [point["values"][0][0][key][0] for point in json_grid["analysis_points"]]
        average_rad = float(sum(pit_grid)/len(pit_grid))
        key_results[str(key)] = average_rad

    return json.dumps({"grid results": results.to_json(), "key_results": key_results})
