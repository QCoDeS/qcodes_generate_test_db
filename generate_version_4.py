"""
Generate a version 4 database file for qcodes' test suite to consume.
"""

import os
import numpy as np

# NB: it's important that we do not import anything from qcodes before we
# do the git magic (which we do below), hence the relative import here
import utils as utils


def generate_empty_DB_file():
    """
    Generate an empty DB file with no runs
    """

    import qcodes.dataset.sqlite_base as sqlite_base

    v4fixturepath = os.path.join(utils.fixturepath, 'version4')
    os.makedirs(v4fixturepath, exist_ok=True)
    path = os.path.join(v4fixturepath, 'empty.db')

    if os.path.exists(path):
        os.remove(path)

    sqlite_base.connect(path)


def generate_DB_file_with_runs_but_no_snapshots():
    """
    Generate a .db-file with a handful of runs without snapshots
    """

    # This function will run often on CI and re-generate the .db-files
    # That should ideally be a deterministic action
    # (although this hopefully plays no role)
    np.random.seed(0)

    v4fixturepath = os.path.join(utils.fixturepath, 'version4')
    os.makedirs(v4fixturepath, exist_ok=True)
    path = os.path.join(v4fixturepath, 'with_runs_but_no_snapshots.db')

    if os.path.exists(path):
        os.remove(path)

    from qcodes.dataset.sqlite_base import connect, is_column_in_table
    from qcodes.dataset.measurements import Measurement
    from qcodes.dataset.experiment_container import Experiment
    from qcodes import Parameter, Station

    connect(path)

    exp = Experiment(path_to_db=path,
                     name='experiment_1',
                     sample_name='no_sample_1')
    conn = exp.conn

    assert not is_column_in_table(conn, 'runs', 'snapshot')

    # Now make some parameters to use in measurements
    params = []
    for n in range(4):
        params.append(Parameter(f'p{n}', label=f'Parameter {n}',
                                unit=f'unit {n}', set_cmd=None, get_cmd=None))

    assert Station.default is None

    # Set up an experiment

    meas = Measurement(exp)
    meas.register_parameter(params[0])
    meas.register_parameter(params[1])
    meas.register_parameter(params[2], basis=(params[1],))
    meas.register_parameter(params[3], setpoints=(params[1], params[2]))

    # Make a number of identical runs

    for _ in range(4):

        with meas.run() as datasaver:

            for x in np.random.rand(4):
                for y in np.random.rand(4):
                    z = np.random.rand()
                    datasaver.add_result((params[1], x),
                                         (params[2], y),
                                         (params[3], z))

    assert not is_column_in_table(conn, 'runs', 'snapshot')


def generate_DB_file_with_runs_and_snapshots():
    """
    Generate a .db-file with a handful of runs some of which have snapshots.

    Generated runs:
        #1: run with a snapshot that has some content
        #2: run with a snapshot of an empty station
        #3: run without a snapshot
    """
    v4fixturepath = os.path.join(utils.fixturepath, 'version4')
    os.makedirs(v4fixturepath, exist_ok=True)
    path = os.path.join(v4fixturepath, 'with_runs_and_snapshots.db')

    if os.path.exists(path):
        os.remove(path)

    from qcodes.dataset.sqlite_base import is_column_in_table
    from qcodes.dataset.measurements import Measurement
    from qcodes.dataset.experiment_container import Experiment
    from qcodes import Parameter, Station
    from qcodes.dataset.descriptions import RunDescriber
    from qcodes.dataset.dependencies import InterDependencies

    exp = Experiment(path_to_db=path,
                     name='experiment_1',
                     sample_name='no_sample_1')
    conn = exp.conn

    # Now make some parameters to use in measurements
    params = []
    for n in range(4):
        params.append(Parameter(f'p{n}', label=f'Parameter {n}',
                                unit=f'unit {n}', set_cmd=None, get_cmd=None))

    # We are going to make 3 runs
    run_ids = []

    # Make a run with a snapshot with some content

    full_station = Station(*params[0:1], default=False)
    assert Station.default is None

    meas = Measurement(exp, full_station)
    meas.register_parameter(params[0])
    meas.register_parameter(params[1])
    meas.register_parameter(params[2], basis=(params[1],))
    meas.register_parameter(params[3], setpoints=(params[1], params[2]))

    with meas.run() as datasaver:

        for x in np.random.rand(4):
            for y in np.random.rand(4):
                z = np.random.rand()
                datasaver.add_result((params[1], x),
                                     (params[2], y),
                                     (params[3], z))

    run_ids.append(datasaver.run_id)

    # Make a run with a snapshot of empty station

    empty_station = Station(default=False)
    assert Station.default is None

    meas = Measurement(exp, empty_station)
    meas.register_parameter(params[0])
    meas.register_parameter(params[1])
    meas.register_parameter(params[2])
    meas.register_parameter(params[3], setpoints=(params[1], params[2]))

    with meas.run() as datasaver:

        for x in np.random.rand(4):
            for y in np.random.rand(4):
                z = np.random.rand()
                datasaver.add_result((params[1], x),
                                     (params[2], y),
                                     (params[3], z))

    run_ids.append(datasaver.run_id)

    # Make a run without a snapshot (i.e. station is None)

    assert Station.default is None

    meas = Measurement(exp)
    meas.register_parameter(params[0])
    meas.register_parameter(params[1])
    meas.register_parameter(params[2], basis=(params[1],))
    meas.register_parameter(params[3], setpoints=(params[1], params[2]))

    with meas.run() as datasaver:

        for x in np.random.rand(4):
            for y in np.random.rand(4):
                z = np.random.rand()
                datasaver.add_result((params[1], x),
                                     (params[2], y),
                                     (params[3], z))

    run_ids.append(datasaver.run_id)

    # Check correctness of run_id's

    assert [1, 2, 3] == run_ids, 'Run ids of generated runs are not as ' \
                                 'expected after generating runs #1-3'

    # Ensure snapshot column

    assert is_column_in_table(conn, 'runs', 'snapshot')


if __name__ == '__main__':

    gens = (generate_empty_DB_file,
            generate_DB_file_with_runs_but_no_snapshots,
            generate_DB_file_with_runs_and_snapshots)

    # pylint: disable=E1101
    utils.checkout_to_old_version_and_run_generators(version=4, gens=gens)
