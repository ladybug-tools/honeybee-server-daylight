"""Set up and run a radiance analysis from a json file."""
import os

from honeybee.radiance.recipe.solaraccess.gridbased import SolarAccessGridBased
from honeybee.radiance.recipe.pointintime.gridbased import GridBased
from honeybee.futil import bat_to_sh


def run_from_json(recipe, folder, name):
    """Create a python recipe from json object and run the analysis."""
    if recipe["id"] == 0:
        rec = SolarAccessGridBased.from_json(recipe)
    elif recipe["id"] == 1:
        rec = GridBased.from_json(recipe)
    else:
        raise ValueError(
            "Invalid id input {}. "
            "Currently only the id of [0] SolarAccess and [1] pointintime are supported!"
            .format(recipe['id'])
        )

    # generate bat file
    bat = rec.write(folder, name)
    # Convert bat to sh
    sh = bat_to_sh(bat)

    # start to run the subprocess
    if os.name == 'nt':
        success = rec.run(bat)
    else:
        success = rec.run(sh)

    # run post-processing code
    if success:
        return (True, [r.to_json() for r in rec.results()])
    else:
        return (False, ())
