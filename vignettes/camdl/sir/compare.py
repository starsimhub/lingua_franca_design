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


def worst(ours, key):
    """ The largest difference from the reference, as a share of its largest value """
    theirs = np.array(ref[key][1])
    return np.abs(np.asarray(ours) - theirs).max()/theirs.max()


if __name__ == '__main__':
    # The ODE; cases are totaled over the week that ends at each reporting time
    ode = sim.new(verbose=0).run()
    res = ode.results.sir
    rows = [(f'ode_{key}', worst(res[f'n_{key}'], f'ode_{key}')) for key in 'SIR']
    rows.append(('ode_cases', worst(res.cases.values[weeks - 1], 'ode_cases')))

    # The stochastic solver, as the mean of many runs
    msim = sim.new(verbose=0, solver='binomial').run(n_runs=200)
    res = msim.results.sir
    rows.append(('stochastic_I', worst(res.n_I.values.mean(axis=0), 'stochastic_I')))
    rows.append(('stochastic_cases', worst(res.cases.values.mean(axis=0)[weeks - 1], 'stochastic_cases')))

    for key,diff in rows:
        print(f'{key:18s} largest difference {diff:6.2%}')

    # Timing: one ODE run, not counting the import or the build
    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one ODE run: {tools.time_run(run):.3f} s (original: see {os.path.relpath(example, here)}/reference/timing.json)')
