"""Set up and run a radiance analysis from a json file."""
import os

from honeybee.radiance.recipe.solaraccess.gridbased import SolarAccessGridBased
from honeybee.radiance.recipe.pointintime.gridbased import GridBased as PITGridBased
from honeybee.radiance.recipe.daylightcoeff.gridbased \
    import DaylightCoeffGridBased as DCGridBased
from honeybee.radiance.recipe.daylightfactor.gridbased import GridBased as DFGridBased

from honeybee.futil import bat_to_sh


def run_from_json(recipe, folder, name):
    """Create a python recipe from json object and run the analysis."""
    if recipe["type"] == "gridbased":
        if recipe["id"] == "solar_access":
            rec = SolarAccessGridBased.from_json(recipe)
        elif recipe["id"] == "point_in_time":
            rec = PITGridBased.from_json(recipe)
        elif recipe["id"] == "daylight_factor":
            rec = DFGridBased.from_json(recipe)
        elif recipe["id"] == "annual":
            raise NotImplementedError(
                "Annual recipe is not supported use daylightcoeff recipe instead."
            )
        elif recipe["id"] == "daylight_coeff":
            rec = DCGridBased.from_json(recipe)
        else:
            raise NotImplementedError(
                "{} {} recipe is not supported yet.".format(recipe['type'],
                                                            recipe['id'])
            )
    else:
        raise NotImplementedError(
            "{} {} recipe is not supported yet.".format(recipe['type'], recipe['id'])
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
