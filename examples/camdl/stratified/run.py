"""
Run the original pycamdl model and write its reference results and timing.

    python run.py

Needs pycamdl, from a camdl checkout next to this repository (or set PYCAMDL to its folder).
"""
import os
import sys
import runpy
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
examples = os.path.dirname(os.path.dirname(here))
sys.path.insert(0, examples)
sys.path.insert(0, os.environ.get('PYCAMDL', os.path.join(examples, '..', '..', 'camdl', 'pycamdl')))
import tools

model = runpy.run_path(os.path.join(here, 'original', 'stratified.py'), run_name='original')['m']
cells = [f'I_{age}_{patch}' for age in ['child', 'adult', 'elder'] for patch in ['north', 'south']]
n_runs = 200 # For the chain-binomial backend


def series(res, prefix, stochastic=False):
    """ The infectious in each cell, and the total of each compartment """
    rows = []
    keys = cells + ['S', 'E', 'I', 'R']
    for key in keys:
        vals = res[key]
        if stochastic:
            for t,row in zip(res.t, vals):
                ordered = np.sort(row)
                n = len(ordered)
                rows.append(dict(time=t, series=f'{prefix}_{key}', value=row.mean(), low=ordered[int(0.05*(n - 1))], high=ordered[int(0.95*(n - 1))]))
        else:
            rows += [dict(time=t, series=f'{prefix}_{key}', value=v) for t,v in zip(res.t, vals)]
    return rows


if __name__ == '__main__':
    rows = []
    for label,enable in [('novax', []), ('vax', ['vaccinate'])]:
        rows += series(model.run(backend='ode', enable=enable), f'ode_{label}')
        rows += series(model.run(n=n_runs, seed=1, enable=enable), f'stochastic_{label}', stochastic=True)
    tools.write_results(here, rows)
    seconds = tools.time_run(lambda: model.run(backend='ode'))
    tools.write_timing(here, seconds, 'model.run(backend="ode") in Python, with the model already built')
    print(f'Wrote {len(rows)} rows; one ODE run takes {seconds:.3f} s')
