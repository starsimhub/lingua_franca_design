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
from model import sim, scenarios

ref = tools.read_results(os.path.join(root, 'examples', 'atomica', 'hiv_dyn'))
comps = ['sus', 'undx', 'dx', 'linked', 'tx', 'lost', 'vs', 'dead_hiv', 'dead_other']
cascade = dict(plhiv='all_people', diagnosed='all_dx', treated='all_tx')


def worst(res, scen):
    """ The largest difference in any compartment of either sex, and in the cascade, as a share of the largest value of each """
    # A stock at index k is the number after step k, and the original's at year k+1: compare from 2017 to 2035
    out = {}
    for comp in comps:
        for sex in ['females', 'males']:
            ours, theirs = res[f'n_{comp}'].select(sex=sex).values[:-1], np.array(ref[f'{scen}_{sex}_{comp}'][1])[1:]
            out[f'{sex}_{comp}'] = np.abs(ours - theirs).max()/theirs.max()
    for ours,theirs in cascade.items():
        for sex in ['females', 'males']:
            vals = np.array(ref[f'{scen}_{sex}_{theirs}'][1])[1:]
            out[f'{sex}_{ours}'] = np.abs(res[ours].select(sex=sex).values[:-1] - vals).max()/vals.max()
    return out


if __name__ == '__main__':
    for scen,pars in dict(baseline={}, **scenarios).items():
        res = sim.new(verbose=0, pars=pars).run().results.hiv
        diffs = worst(res, scen)
        key = max(diffs, key=diffs.get)
        vs = {sex: (res.n_vs.select(sex=sex)[-2], ref[f'{scen}_{sex}_vs'][1][-1]) for sex in ['females', 'males']}
        print(f'{scen:15s} largest difference {diffs[key]:.2g} ({key}); virally suppressed in 2035: ' + ', '.join(f'{k} {a:,.0f} (original {b:,.0f})' for k,(a,b) in vs.items()))

    def run(pars={}):
        ss.Sim(sim.new(pars=pars).inputs, verbose=0).run()
    print(f'one run: {tools.time_run(run):.3f} s without programs, {tools.time_run(lambda: run(scenarios["default_budget"])):.3f} s with them')
