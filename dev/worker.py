from honeybee.radiance.recipe.annual.gridbased import GridBased
from honeybee.futil import bat_to_sh
import json
import re
import os

recipe_path = '/usr/honeybee-worker/recipes/annual.json'
folder = "/usr/honeybee-worker/test2"
name = "radiation"

with open(recipe_path) as json_data:
    payload = json.load(json_data)#['payload']

rec = GridBased.from_json(payload)

# Generate bat file
bat = rec.write(folder, name)
# Convert bat to sh
sh = bat_to_sh(bat)

# Clean up shell script for -dr 3.0
with open(sh, "r") as shell_file:
    lines = shell_file.readlines()
    newlines = list()
    for line in lines:
        if "-dr" in line:
            line = re.sub("-dr (.*?) -", "-dr 3 -", line)
        newlines.append(line)
    shell_file.close()

with open(sh, "w") as new_shell:
    new_shell.writelines(newlines)
    new_shell.close()

print "start to run the subprocess"
if os.name == 'nt':
    success = rec.run(bat)
else:
    success = rec.run(sh)

print "Simulation completed."
print "Running post processing..."

grid = rec.results()[0]
print payload["analysis_grids"][0].keys()
if "da_threshold" in payload["analysis_grids"][0].keys():
    da_threshold = payload["analysis_grids"][0]["da_threshold"]
else:
    da_threshold = None
if "udi_min_max" in payload["analysis_grids"][0].keys():
    udi_min_max = payload["analysis_grids"][0]["udi_min_max"]
else:
    udi_min_max = None
if "occ_schedule" in payload["analysis_grids"][0].keys():
    occ_schedule = payload["analysis_grids"][0]["occ_schedule"]
else:
    occ_schedule = None

DA, CDA, UDI, UDILess, UDIMore = grid.annual_metrics(da_threshold, udi_min_max,
    None, occ_schedule)

key_results = {"daylight_autonomy": DA,
               "continuous_daylight_autonomy": CDA,
               "useful_daylight_autonomy": UDI,
               "useful_daylight_autonomy_less": UDILess,
               "useful_daylight_autonomy_more": UDIMore}

with open (folder + '/key_results.json',"w") as key_results_file:
    key_results_file.write(json.dumps(key_results))


grid.load_values_from_files()

with open ('/usr/honeybee-worker/grid_results.json',"w") as results_file:
    results_file.write(json.dumps(grid.to_json()))
    results_file.close()
