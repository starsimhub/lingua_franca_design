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

example = os.path.join(root, 'examples', 'memilio', 'secir_ageres')
ref = tools.read_results(example)
names = dict(S='Susceptible', E='Exposed', INS='InfectedNoSymptoms', ISy='InfectedSymptoms', ISev='InfectedSevere', ICr='InfectedCritical', R='Recovered')


def report(name, ours, theirs, start=0):
    """ Compare from the original's day `start` on; `ours` begins on that day, and may run past the original's last """
    theirs = np.array(theirs)[start:]
    ours = ours[:len(theirs)]
    diff = np.abs(ours - theirs)
    print(f'{name:20s} at the end {ours[-1]:8.1f} (original {theirs[-1]:8.1f}); largest difference {diff.max():5.2f} people, on day {diff.argmax() + start}')
    return


if __name__ == '__main__':
    for dt in [1, 0.1]:
        res = sim.new(verbose=0, dt=ss.days(dt)).run().results.secir # A shorter step only to show where the differences come from
        step = int(round(1/dt))
        print(f'\nWith a step of {dt} days:')
        # A stock at index k is the number after k steps, so the number on day d is at index d*step
        for key,name in names.items():
            report(name, res[f'n_{key}'].values[::step], ref[name][1])
        dead = res.cum_death.values[::step] # Deaths up to each day
        report('Dead', dead, ref['Dead'][1])
        for g in range(3):
            report(f'InfectedSymptoms_{g}', res.n_ISy.select(age=str(g)).values[::step], ref[f'InfectedSymptoms_{g}'][1])

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'\none run: {tools.time_run(run):.3f} s (original: see {os.path.relpath(example, here)}/reference/timing.json)')
