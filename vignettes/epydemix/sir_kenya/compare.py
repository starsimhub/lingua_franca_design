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
from model import sim, data

ref = tools.read_results(os.path.join(root, 'examples', 'epydemix', 'sir_kenya'))

if __name__ == '__main__':
    msim = sim.new(verbose=0, stop='2020-04-02').run(n_runs=100) # To the end of 1 April, the original's day 123
    res = msim.results.sir
    total = sum(data['Nk'])
    for group in data['groups'] + ['total']:
        if group == 'total':
            ours = res.n_I.values.mean(axis=0)
        else: # A result of many runs cannot be selected by age group yet, so do it run by run
            ours = np.mean([run.results.sir.n_I.select(age=group).values for run in msim.sims], axis=0)
        theirs = np.array(ref[f'Infected_{group}'][1]) # A stock at index k is the number on day k, in both
        n = min(len(ours), len(theirs))
        print(f'Infected, {group:6s} peak {ours.max():12,.0f} (original {theirs.max():12,.0f}) on day {ours.argmax()} ({theirs.argmax()}); largest difference {np.abs(ours[:n] - theirs[:n]).max()/theirs.max():.1%} of the peak')
    final = res.n_R.values.mean(axis=0)[-1] # Day 123, the original's last day
    print(f'Recovered at the end: {final/total:.2%} (original {ref["Recovered_total"][1][-1]/total:.2%})')

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one run: {tools.time_run(run):.3f} s')
