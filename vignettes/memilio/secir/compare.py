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

ref = tools.read_results(os.path.join(root, 'examples', 'memilio', 'secir'))
names = dict(S='Susceptible', E='Exposed', INS='InfectedNoSymptoms', ISy='InfectedSymptoms', ISev='InfectedSevere', ICr='InfectedCritical', R='Recovered')

if __name__ == '__main__':
    res = sim.new(verbose=0).run().results.secir
    for key,name in names.items():
        ours, theirs = res[f'n_{key}'].values[:-1], np.array(ref[name][1])[1:] # A stock at index k is the number after step k, the original's at day k+1
        print(f'{name:20s} at the end {ours[-1]:9.1f} (original {theirs[-1]:9.1f}); largest difference {np.abs(ours - theirs).max():7.1f} people')
    dead = np.append(0, res.cum_death.values[:-1]) # Deaths up to the start of each day
    print(f'{"Dead":20s} at the end {dead[-1]:9.1f} (original {ref["Dead"][1][-1]:9.1f}); largest difference {np.abs(dead - np.array(ref["Dead"][1])).max():7.1f} people')

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one run: {tools.time_run(run):.3f} s')
