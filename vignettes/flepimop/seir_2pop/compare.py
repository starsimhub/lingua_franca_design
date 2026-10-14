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
from model import sim, pop

ref = tools.read_results(os.path.join(root, 'examples', 'flepimop', 'seir_2pop'))

if __name__ == '__main__':
    res = sim.new(verbose=0).run().results.seir
    for place in pop:
        for state in 'SEIR':
            ours, theirs = res[f'n_{state}'].select(patch=place).values, np.array(ref[f'{place}_{state}'][1])
            n = min(len(ours), len(theirs))
            print(f'{place} {state}: at the end {ours[n-1]:8.1f} (original {theirs[n-1]:8.1f}); peak on day {ours.argmax()} ({theirs.argmax()}); largest difference {np.abs(ours[:n] - theirs[:n]).max():6.1f} people')

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one run: {tools.time_run(run):.3f} s')
