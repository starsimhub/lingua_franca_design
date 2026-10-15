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
from model import sim

ref = tools.read_results(os.path.join(root, 'examples', 'odin', 'stochastic_sir_arrays'))

if __name__ == '__main__':
    res = sim.new(verbose=0).run(n_runs=2000).results.sir
    for state in 'SIR':
        ours, theirs = res[f'n_{state}'].values.mean(axis=0), np.array(ref[state][1]) # A stock at index k is the number at time k, in both
        print(f'{state}: mean at the end {ours[-1]:7.1f} (original {theirs[-1]:7.1f}); largest difference in the mean {np.abs(ours - theirs).max():5.1f} people of 1,001')
    print(f'runs that died out: {(res.n_R.values[:, -1] < 50).mean():.1%}')

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one run: {tools.time_run(run):.3f} s')
