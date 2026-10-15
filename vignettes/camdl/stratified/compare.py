"""
Compare the Starsim version with the reference results of the original

    python compare.py
"""
import os
import sys
import numpy as np
import starsim as ss

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
sys.path.insert(0, os.path.join(root, 'examples'))
import tools
from model import sim, vaccinate

example = os.path.join(root, 'examples', 'camdl', 'stratified')
ref = tools.read_results(example)
ages = dict(child='0-4', adult='5-49', elder='50+')


def worst(res, prefix):
    """ The largest difference in the infectious of any cell (the mean, for many runs), as a share of the largest value there """
    out = {}
    for age,label in ages.items():
        for patch in ['north', 'south']:
            ours = res.n_I.select(age=label, patch=patch).values
            ours = ours.mean(axis=0) if ours.ndim == 2 else ours # A stock at index k is the number at time k, in both
            theirs = np.array(ref[f'{prefix}_I_{age}_{patch}'][1])
            out[f'{age}_{patch}'] = np.abs(ours - theirs).max()/theirs.max()
    return out


if __name__ == '__main__':
    for label,interventions in [('novax', None), ('vax', vaccinate)]:
        ode = sim.new(verbose=0, interventions=interventions).run().results.seir
        msim = sim.new(verbose=0, interventions=interventions, solver='binomial').run(n_runs=200)
        for kind,res in [('ode', ode), ('stochastic', msim.results.seir)]:
            diffs = worst(res, f'{kind}_{label}')
            print(f'{kind:10s} {label:5s} largest difference in I by cell: ' + ', '.join(f'{k} {v:.2%}' for k,v in diffs.items()))

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one ODE run: {tools.time_run(run):.3f} s (original: see {os.path.relpath(example, here)}/reference/timing.json)')
