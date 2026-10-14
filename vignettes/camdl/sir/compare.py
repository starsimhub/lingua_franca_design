"""
Compare the Starsim version with the reference results of the original

    python compare.py
"""
import os
import sys
import time
import numpy as np
import starsim as ss

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
sys.path.insert(0, os.path.join(root, 'examples'))
import tools
from sir import sim

example = os.path.join(root, 'examples', 'camdl', 'sir')
ref = tools.read_results(example)
weeks = np.arange(7, 85, 7)


def worst(ours, key, stock=False):
    """ The largest difference from the reference, as a share of its largest value """
    ours, theirs = np.asarray(ours), np.array(ref[key][1])
    if stock: # A stock at index k is the number after step k, the original's at time k+1
        ours, theirs = ours[:-1], theirs[1:]
    return np.abs(np.asarray(ours) - theirs).max()/theirs.max()


if __name__ == '__main__':
    # The ODE; cases are totaled over the week that ends at each reporting time
    ode = sim.new(verbose=0).run()
    res = ode.results.sir
    rows = [(f'ode_{key}', worst(res[f'n_{key}'], f'ode_{key}', stock=True)) for key in 'SIR']
    rows.append(('ode_cases', worst(res.cases.values[weeks - 1], 'ode_cases')))

    # The stochastic solver, as the mean of many runs
    msim = sim.new(verbose=0, solver='binomial').run(n_runs=200)
    res = msim.results.sir
    rows.append(('stochastic_I', worst(res.n_I.values.mean(axis=0), 'stochastic_I', stock=True)))
    rows.append(('stochastic_cases', worst(res.cases.values.mean(axis=0)[weeks - 1], 'stochastic_cases')))

    for key,diff in rows:
        print(f'{key:18s} largest difference {diff:6.2%}')

    # The likelihood: fit beta, gamma, and k to weekly cases drawn around the original's ODE cases
    rng = np.random.default_rng(1)
    mean = np.array(ref['ode_cases'][1])
    data = dict(t=weeks, cases=rng.negative_binomial(10, 10/(10 + mean)))
    fit = sim.new(verbose=0, pars=dict(k=ss.par(3, bounds=[0.1, 100]))).calibrate(data=data, verbose=False)
    print('fitted to cases drawn with beta=0.4, gamma=0.15, k=10:', ', '.join(f'{key}={val.value if hasattr(val, "value") else val:.3g}' for key,val in fit.pars.items()))

    # Timing: one ODE run, not counting the import or the build
    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one ODE run: {tools.time_run(run):.3f} s (original: see {os.path.relpath(example, here)}/reference/timing.json)')
