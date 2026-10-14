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
from model import compartment, ibm

ref = tools.read_results(os.path.join(root, 'examples', 'emulsion', 'sir'))

if __name__ == '__main__':
    for key,sim in dict(compartment=compartment, ibm=ibm).items():
        res = sim.new(verbose=0).run(n_runs=200).results.sir
        n_I, n_R = res.n_I.values, res.n_R.values
        theirs_I, theirs_R = np.array(ref[f'{key}_I'][1]), np.array(ref[f'{key}_R'][1])
        died_out = (n_R[:, -1] < 10).mean()
        print(f'{key:12s} mean infectious peaks at {n_I.mean(axis=0).max():.1f} on day {n_I.mean(axis=0).argmax()} (original {theirs_I.max():.1f} on day {theirs_I.argmax()}); '
              f'mean recovered at the end {n_R[:, -1].mean():.1f} ({theirs_R[-1]:.1f}); {died_out:.0%} of runs died out early')

    def run():
        ss.Sim(compartment.inputs, verbose=0).run()
    print(f'one compartmental run: {tools.time_run(run):.3f} s')
