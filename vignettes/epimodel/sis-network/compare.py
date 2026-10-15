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

ref = tools.read_results(os.path.join(root, 'examples', 'epimodel', 'sis-network'))

if __name__ == '__main__':
    res = sim.new(verbose=0).run(n_runs=100).results.sis
    theirs = np.array(ref['i.num'][1]) # Index k is the number after k steps in both (the original's first value is the start)
    ours = res.n_I.values.mean(axis=0)[:len(theirs)]
    print(f'infected, mean of the last 200 steps: {ours[-200:].mean():.1f} (original {theirs[-200:].mean():.1f})')
    print(f'infected at step 50: {ours[50]:.1f} ({theirs[50]:.1f}); at step 100: {ours[100]:.1f} ({theirs[100]:.1f})')
    print(f'new infections per step, last 200 steps: {res.infection.values.mean(axis=0)[:len(theirs)][-200:].mean():.2f} (original {np.mean(ref["si.flow"][1][-200:]):.2f})')
    print(f'original network: {np.mean(ref["edges"][1][-200:]):.0f} edges, mean degree {np.mean(ref["meandeg"][1][-200:]):.2f}, {np.mean(ref["concurrent"][1][-200:]):.0f} people with two or more partners')

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one run: {tools.time_run(run):.3f} s')
