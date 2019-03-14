#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import time


# In[2]:


from generate_benckmark_data import generate_data_for_db


# In[ ]:


import os
from qcodes.dataset.sqlite_base import connect
from qcodes.dataset.experiment_container import Experiment

from typing import Sequence, Optional, List, Tuple
from qcodes.dataset.measurements import Measurement
import numpy as np
import time


# # 1D data

# generate a 100 datasets with 1000 points in each

# In[ ]:


db_path = os.path.join(os.getcwd(), 'benchmark_1d.db')
db_conn = connect(db_path)
exp = Experiment(name='benchmarks',
                 sample_name='no_sample',
                 conn=db_conn)
times = []
for i in range(100):
    start = time.perf_counter()
    meas = Measurement(exp=exp)
    data = generate_data_for_db(dependencies=1, dependents=1, shape=(1000,),
                                paramtype='array',
                                measurement=meas, on_grid=True)
    with meas.run() as datasaver:
        datasaver.add_result(*data)
    stop = time.perf_counter()
    times.append(stop-start)

print(times[:5])
print(times[-5:-1])
print(max(times))
print(min(times))


# # 2D data

# In[ ]:


db_path = os.path.join(os.getcwd(), 'benchmark_2d_on_grid.db')
db_conn = connect(db_path)
exp = Experiment(name='benchmarks',
                 sample_name='no_sample',
                 conn=db_conn)
times = []
for i in range(100):
    start = time.perf_counter()
    meas = Measurement(exp=exp)
    data = generate_data_for_db(dependencies=2, dependents=1, shape=(100,100),
                                paramtype='numeric',
                                measurement=meas, on_grid=True)
    with meas.run() as datasaver:
        datasaver.add_result(*data)
    stop = time.perf_counter()
    times.append(stop-start)

print(times[:5])
print(times[-5:-1])
print(max(times))
print(min(times))


# # 2D data as arrays

# In[ ]:


db_path = os.path.join(os.getcwd(), 'benchmark_2d_on_grid_array.db')
db_conn = connect(db_path)
exp = Experiment(name='benchmarks',
                 sample_name='no_sample',
                 conn=db_conn)
times = []
for i in range(100):
    start = time.perf_counter()
    meas = Measurement(exp=exp)
    data = generate_data_for_db(dependencies=2, dependents=1, shape=(100,100),
                                paramtype='array',
                                measurement=meas, on_grid=True)
    with meas.run() as datasaver:
        datasaver.add_result(*data)
    stop = time.perf_counter()
    times.append(stop-start)

print(times[:5])
print(times[-5:-1])
print(max(times))
print(min(times))


# # 2D data scatter

# In[ ]:


db_path = os.path.join(os.getcwd(), 'benchmark_2d_scatter.db')
db_conn = connect(db_path)
exp = Experiment(name='benchmarks',
                 sample_name='no_sample',
                 conn=db_conn)
times = []
for i in range(100):
    start = time.perf_counter()
    meas = Measurement(exp=exp)
    data = generate_data_for_db(dependencies=2, dependents=1, shape=(10000,),
                                paramtype='array',
                                measurement=meas, on_grid=False)
    with meas.run() as datasaver:
        datasaver.add_result(*data)
    stop = time.perf_counter()
    times.append(stop-start)

print(times[:5])
print(times[-5:-1])
print(max(times))
print(min(times))


# In[ ]:




