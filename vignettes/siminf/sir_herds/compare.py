"""
Compare the Starsim version with the reference results of the original

    python compare.py
"""
import os
import sys
import numpy as np
import sciris as sc

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
sys.path.insert(0, os.path.join(root, 'examples'))
import tools

n_runs = 20
times = [100, 200, 365, 500, 700, 1000, 1460]


def one(seed):
    """ One run: the series the reference has, by day (Starsim's n[t-1] is the state after t steps, so after the transitions of SimInf's day t; it does not yet have day t's scheduled events, which Starsim applies at the start of the next step, and SimInf at the end of day t) """
    from model import sim
    res = sim.new(rand_seed=seed, verbose=0).run().results.sir
    out = {key:res[f'n_{key}'].values for key in 'SIR'}
    I = res.n_I.strata # By herd
    out['nodes_infected'] = (I > 0).sum(axis=1)
    for node in [1, 2, 3]:
        for key in 'SIR':
            out[f'node{node}_{key}'] = res[f'n_{key}'].select(herd=str(node)).values
    return out


if __name__ == '__main__':
    ref = tools.read_results(os.path.join(root, 'examples', 'siminf', 'sir_herds'))
    T = sc.timer()
    runs = sc.parallelize(one, iterarg=list(range(n_runs)))
    print(f'{n_runs} runs in parallel: {T.toc(output=True):.1f} s')
    for key in ['S', 'I', 'R', 'nodes_infected', 'node1_I']:
        rt, rv = ref[key]
        vals = np.array([run[key] for run in runs])
        print(f'{key}:')
        for t in times:
            i = rt.index(float(t))
            mean, se = vals[:, t-1].mean(), vals[:, t-1].std()/np.sqrt(n_runs)
            print(f'  day {t:4d}: Starsim {mean:9,.0f} ± {se:7,.0f}   SimInf {rv[i]:9,.0f}')
    died = np.mean([run['I'][199] == 0 for run in runs])
    print(f'runs with no infection on day 200: {died:.0%} (SimInf about 7%)')
