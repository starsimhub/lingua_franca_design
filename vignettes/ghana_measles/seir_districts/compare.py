"""
Compare the Starsim version with the reference results of the original

    python compare.py
"""
import os
import sys
import numpy as np
import pandas as pd
import sciris as sc
import starsim as ss

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
sys.path.insert(0, os.path.join(root, 'examples'))
import tools
from model import sim

example = os.path.join(root, 'examples', 'ghana_measles', 'seir_districts')
ref = pd.read_csv(os.path.join(example, 'reference', 'results.csv'))
n_runs = 20


def monthly(res, key):
    """ A daily flow summed by month (a flow at index k is the number during the step ending on day k, so during day k-1) """
    months = [str(t)[:7].replace('.', '-') for t in res.timevec[:-1]]
    return pd.Series(res[key].values[1:], index=months).groupby(level=0, sort=False).sum()


def run(seed):
    res = sim.new(verbose=0, rand_seed=seed).run().results.measles
    by_district = res.onset.by('district')
    after = np.array([str(t)[:4] >= '2020' for t in res.timevec[:-1]]) # By the day each step starts on, as in monthly()
    regions = pd.Series(by_district.values[1:][after].sum(axis=0), index=[col.split(':')[1] for col in by_district.columns]).groupby(level=0).sum()
    end = [str(t)[:10] for t in res.timevec].index('2025.12.01') # The original's last value is at the start of the last month
    return sc.objdict(infections=monthly(res, 'onset'), cases=monthly(res, 'cases'), regions=regions, S=res.n_S.values[end], R=res.n_R.values[end])


if __name__ == '__main__':
    runs = sc.parallelize(run, iterarg=range(n_runs))
    for key in ['infections', 'cases']:
        ours = pd.concat([r[key] for r in runs], axis=1).mean(axis=1)
        theirs = ref[ref.series == f'monthly_{key}'].set_index('time')['value']
        ours, theirs = ours.loc[theirs.index], theirs
        yearly = lambda s: s.groupby(s.index.str[:4]).sum()
        print(f'{key}: total {ours.sum():,.0f} (original {theirs.sum():,.0f}); by year, largest difference {(yearly(ours)/yearly(theirs) - 1).abs().max():.1%}; correlation of monthly means {np.corrcoef(ours, theirs)[0, 1]:.3f}')
    ours = pd.concat([r.regions for r in runs], axis=1).mean(axis=1)
    theirs = ref[ref.series.str.startswith('region_')].set_index('series')['value'].rename(lambda s: s[7:])
    print(f'infections from 2020 by region: largest difference {(ours/theirs.loc[ours.index] - 1).abs().max():.1%}')
    last = ref[ref.series.isin(['national_S', 'national_R'])].groupby('series')['value'].last()
    print(f'susceptible at the end {np.mean([r.S for r in runs]):,.0f} (original {last.national_S:,.0f}); immune {np.mean([r.R for r in runs]):,.0f} ({last.national_R:,.0f})')

    def one():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one run: {tools.time_run(one, n=3):.2f} s (original: see {os.path.relpath(example, here)}/reference/timing.json)')
