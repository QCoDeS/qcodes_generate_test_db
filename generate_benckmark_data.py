import os
from qcodes.dataset.sqlite_base import connect
from qcodes.dataset.experiment_container import Experiment

from typing import Sequence, Optional, List, Tuple
from qcodes.dataset.measurements import Measurement
import numpy as np
import time


def generate_data_for_db(dependencies: int,
                         dependents: int,
                         shape: Sequence[int],
                         measurement: Measurement,
                         paramtype: str = 'numeric',
                         on_grid: bool = True) -> List[Tuple[str, np.ndarray]]:
    """
    "This registers parameters to the measurement given and generates random
    data matching the parameters and shape requested ready to insert into
    an `add_results` method call.


    Args:
        measurement: a measurement context manager to add the results to
        dependencies: number of dependencies for the dataset generated
        dependents: number of dependent variables for the data generated
        shape: shape of the data generated. This should a Sequence with the
             same length as the number of dependencies.
        paramtype: Store this as array, numeric ect.
        on_grid: Should the data be on a regular grid or sampled randomly

    Returns:
        Parameters and data ready to insert into the measurement.

    """
    if on_grid:
        if len(shape) != dependencies:
            raise RuntimeError("Wrong shape, dependency combination")
    else:
        shape = np.array(shape).ravel()

    dependencies_names = []
    dependents_names = []
    for dep_num in range(dependencies):
        name = f"param_{dep_num}"
        dependencies_names.append(name)
        measurement.register_custom_parameter(name=name,
                                            paramtype=paramtype)

    for dependent_num in range(dependents):
        name = f"meas_param_{dependent_num}"
        dependents_names.append(name)
        measurement.register_custom_parameter(name=name,
                                            paramtype=paramtype,
                                            setpoints=dependencies_names)
    output = []
    if on_grid:
        setpoints = []
        for param_name, size in zip(dependencies_names, shape):
            setpoints.append(np.linspace(0, size, size, endpoint=False))
        outgrids = np.meshgrid(*setpoints, indexing='ij')

        for param_name, grid in zip(dependencies_names, outgrids):
            output.append((param_name, grid))
    else:
        for param_name in dependencies_names:
            output.append((param_name, np.random.rand(*shape)))

    for param_name in dependents_names:
        output.append((param_name, np.random.rand(*shape)))

    return output
