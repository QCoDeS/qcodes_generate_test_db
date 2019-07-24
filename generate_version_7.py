"""
Generate version 7 database file sfor qcodes' test suite to consume.
"""

import os
import numpy as np

# NB: it's important that we do not import anything from qcodes before we
# do the git magic (which we do below)

import utils as utils

VERSION = 7


def generate_empty_DB_file(version=VERSION):
    """
    Generate an empty DB file with no runs
    """

    from qcodes.dataset.sqlite.database import connect

    vNfixturepath = os.path.join(utils.fixturepath, f'version{version}')
    os.makedirs(vNfixturepath, exist_ok=True)
    path = os.path.join(vNfixturepath, 'empty.db')

    if os.path.exists(path):
        os.remove(path)

    connect(path)


def generate_DB_file_with_some_runs(version=VERSION):
    """
    Generate a .db-file with a handful of runs with some interdependent
    parameters
    """

    # This function will run often on CI and re-generate the .db-files
    # That should ideally be a deterministic action
    # (although this hopefully plays no role)
    np.random.seed(0)

    vNfixturepath = os.path.join(utils.fixturepath, f'version{version}')
    os.makedirs(vNfixturepath, exist_ok=True)
    path = os.path.join(vNfixturepath, 'some_runs.db')

    if os.path.exists(path):
        os.remove(path)

    from qcodes.dataset.sqlite.database import connect
    from qcodes.dataset.measurements import Measurement
    from qcodes.dataset.experiment_container import Experiment
    from qcodes import Parameter

    connect(path)
    exp = Experiment(path_to_db=path,
                     name='experiment_1',
                     sample_name='no_sample_1')

    # Now make some parameters to use in measurements
    params = []
    for n in range(5):
        params.append(Parameter(f'p{n}', label=f'Parameter {n}',
                                unit=f'unit {n}', set_cmd=None, get_cmd=None))

    # Set up an experiment

    meas = Measurement(exp)
    meas.register_parameter(params[0])
    meas.register_parameter(params[1])
    meas.register_parameter(params[2], basis=(params[0],))
    meas.register_parameter(params[3], basis=(params[1],))
    meas.register_parameter(params[4], setpoints=(params[2], params[3]))

    # Make a number of identical runs

    for _ in range(10):

        with meas.run() as datasaver:

            for x in np.random.rand(10):
                for y in np.random.rand(10):
                    z = np.random.rand()
                    datasaver.add_result((params[0], 0),
                                         (params[1], 1),
                                         (params[2], x),
                                         (params[3], y),
                                         (params[4], z))


if __name__ == '__main__':

    gens = (generate_empty_DB_file,
            generate_DB_file_with_some_runs)

    # pylint: disable=E1101
    utils.checkout_to_old_version_and_run_generators(version=VERSION,
                                                     gens=gens)
