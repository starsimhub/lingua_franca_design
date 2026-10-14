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

example = os.path.join(root, 'examples', 'emulsion', 'quickstart')
ref = tools.read_results(example)
states = dict(growth='J A', life='NG G', health='M S E I R Q')
n_runs = 200
window = ss.timeseries({'2021-01-01': 0, '2021-03-19': 1, '2021-08-21': 0, '2022-03-18': 1, '2022-08-20': 0}) # The quarantine as EMULSION applies it: see the README


class counts(ss.Analyzer):
    """ The number in each of EMULSION's states among the living at the end of each step, after the step's deaths and births (see the README for why not the results) """
    def init_pre(self, sim):
        super().init_pre(sim)
        self.rows = []

    def step(self):
        sim = self.sim
        alive = sim.people.alive.uids
        row = {state:sim.diseases[mod][state][alive].sum() for mod,names in states.items() for state in names.split()}
        row.update(total_population=len(alive), nb_total_abortions=sim.diseases.life.nb_abortions[alive].sum())
        self.rows.append(row)


def run_many(**kwargs):
    """ Run the sim many times, one at a time; Starsim's step k is the state after k + 1 steps, as is EMULSION's row k + 1 """
    out = {key:[] for key in ref}
    for seed in range(n_runs):
        rows = sim.new(verbose=0, rand_seed=seed, analyzers=counts(), **kwargs).run().analyzers[0].rows
        for key in ref:
            out[key].append([row[key] for row in rows][:len(ref[key][1]) - 1])
    return {key:np.array(val) for key,val in out.items()}


if __name__ == '__main__':
    print(f'{"":20s} {"largest difference":>18s} {"(step)":>6s}   at step 13: ours, theirs   at step 53   at step 105')
    for label,kwargs in [('as written', {}), ('with the quarantine as EMULSION applies it', dict(pars=dict(quarantine=window)))]:
        print(label)
        res = run_many(**kwargs)
        for key,vals in res.items():
            ours, theirs = vals.mean(axis=0), np.array(ref[key][1][1:])
            k = np.abs(ours - theirs).argmax()
            print(f'  {key:18s} {ours[k] - theirs[k]:+18.2f} {k+1:6d}   ' + '   '.join(f'{ours[i-1]:6.1f} {theirs[i-1]:6.1f}' for i in [13, 53, 105]))

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one run: {tools.time_run(run):.3f} s (original: see {os.path.relpath(example, here)}/reference/timing.json)')
