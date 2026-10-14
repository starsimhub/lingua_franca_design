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

example = os.path.join(root, 'examples', 'summer2', 'sir-age-location')
ref = tools.read_results(example)

if __name__ == '__main__':
    res = sim.new(verbose=0).run().results.sir
    worst = 0
    for state in 'SIR':
        for age in ['young', 'old']:
            for location in ['urban', 'rural']:
                ours = res[f'n_{state}'].select(age=age, location=location).values[:-1] # A stock at index k is the number after step k ...
                theirs = np.array(ref[f'{state}_{age}_{location}'][1])[1:] # ... and the original's at time k+1
                worst = max(worst, np.abs(ours - theirs).max())
    print(f'largest difference in any compartment: {worst:.3g} people (of 1,000)')

    for solver in ['binomial', 'abm']:
        runs = sim.new(verbose=0, solver=solver, **(dict(n_agents=1000) if solver == 'abm' else {})).run(n_runs=100).results.sir
        ode = res.n_R[-2] # At the stop; the last is one step past it
        print(f'{solver}: recovered at the end {runs.n_R.values.mean(axis=0)[-2]:.0f} (ODE {ode:.0f})')

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one ODE run: {tools.time_run(run):.3f} s')
