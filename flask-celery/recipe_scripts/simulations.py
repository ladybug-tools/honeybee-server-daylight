from honeybee.radiance.recipe.daylightfactor.gridbased import GridBased
from honeybee.futil import bat_to_sh
import json
import re
import os

recipe_path = '/usr/honeybee-worker/recipe.json'
folder = "/usr/honeybee-worker/rad_files"

def run(rec, name, folder="/usr/honeybee-worker/rad_files"):
    # Generate bat file
    bat = rec.write(folder, name)
    # Convert bat to sh
    sh = bat_to_sh(bat)

    # Clean up shell script for -dr 3.0
    with open(sh, "r") as shell_file:
        lines = shell_file.readlines()
        newlines = list()
        for line in lines:
            # This is a patchy bug fix, will need changing!
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
    results = rec.results()[0]

    return results
