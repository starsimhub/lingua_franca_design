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

ref = tools.read_results(os.path.join(root, 'examples', 'atomica', 'sir'))

if __name__ == '__main__':
    res = sim.new(verbose=0).run().results.sir
    for state in ['sus', 'inf', 'rec', 'dead']:
        ours, theirs = res[f'n_{state}'].values[:-1], np.array(ref[f'adults_{state}'][1])[1:] # A stock at index k is the number after step k, the original's at time k+1
        print(f'{state:5s} at the end {ours[-1]:8.2f} (original {theirs[-1]:8.2f}); largest difference {np.abs(ours - theirs).max():.3g} people')
    smooth = sim.new(verbose=0, integrator='rk4', substeps=None).run().results.sir
    print(f'with the default integrator, inf at the end is {smooth.n_inf[-2]:.1f}: the yearly Euler step is part of the original model')

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one run: {tools.time_run(run):.3f} s')
