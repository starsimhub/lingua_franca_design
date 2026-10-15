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

ref = tools.read_results(os.path.join(root, 'examples', 'laser', 'hub_spoke_seir'))
places = dict(central_city='Central City', town_1='Town 1', interim_1a='Interim 1A', town_3='Town 3')


def report(label, res):
    print(label)
    for key,name in dict(total=None, **places).items():
        # A stock at index k is the number on day k, in both, from day 0 (the start) to day 365 (the stop)
        ours = (res.n_I.values if name is None else res.n_I.select(patch=name).values)
        theirs = np.array(ref['I' if name is None else f'I_{key}'][1])
        done = res.n_R.values[-1] if name is None else res.n_R.select(patch=name).values[-1]
        ref_done = ref['R' if name is None else f'R_{key}'][1][-1]
        print(f'  {key:13s} peak infectious {ours.max():9,.0f} on day {ours.argmax():3d} (original {theirs.max():9,.0f} on day {theirs.argmax():3d}); recovered at the end {done:9,.0f} ({ref_done:9,.0f})')
    return


if __name__ == '__main__':
    abm = sim.new(verbose=0).run()
    report(f'As agents ({abm.pars.n_agents:,} agents, one run):', abm.results.seir)
    ode = ss.Sim({key:val for key,val in sim.inputs.items() if key != 'n_agents'}, verbose=0, solver='ode').run()
    report('As an ODE, with the durations as Erlang stages:', ode.results.seir)

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one agent-based run: {tools.time_run(run, n=3):.2f} s')
