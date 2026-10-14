"""
Compare the Starsim version with the reference results of the original

    python compare.py
"""
import os
import sys
import numpy as np
import sciris as sc
import starsim as ss

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
sys.path.insert(0, os.path.join(root, 'examples'))
import tools
from model import scenarios

example = os.path.join(root, 'examples', 'epimodel', 'hiv')
ref = {}
for k,(t,v) in tools.read_results(example).items(): # Weeks 1 to 1040, with NaN where the original has no value (week 1, for its flows and its own modules)
    ref[k] = np.full(1040, np.nan)
    ref[k][np.array(t, dtype=int) - 1] = v
n_runs = 20 # The reference has 10 of each scenario
late = slice(520, 1040) # The second half, as in the original's summary


def ours(msim):
    """ The original's measures, for each run: one row a step from the first (the initial state) to week 1040 """
    res = msim.results.hiv
    get = lambda r: np.atleast_2d(r.values)[:, :1040]
    inf, sus = get(res.infected), get(res.n_S)
    care = {k:get(res.infected.select(care=k)) for k in ['undx', 'art', 'supp']}
    out = sc.objdict(num=inf + sus, i=inf, s=sus, si=get(res.infection), dx=inf - care['undx'], art=care['art'] + care['supp'], supp=care['supp'])
    if msim.sims[0].interventions: # The PrEP scenarios
        out.prep = get(res.n_S.select(has_prep=True))
    for name in ['main', 'casual']:
        out[f'{name}_deg'] = np.array([sim.networks[name].results.mean_degree[:1040] for sim in msim.sims])
        out[f'{name}_conc'] = np.array([sim.networks[name].results.concurrency[:1040] for sim in msim.sims])
    return out


def theirs(scen):
    """ The same measures from the means of the reference runs """
    g = lambda k: ref[f'{scen}_{k}']
    out = sc.objdict(num=g('num'), i=g('i.num'), s=g('s.num'), si=np.nan_to_num(g('si.flow')), dx=g('dx.num'), art=g('art.num'), supp=g('supp.num'), prep=np.nan_to_num(g('prep.num')))
    for name,key in [('main', 'main'), ('casual', 'cas')]:
        out[f'{name}_deg'] = 2*g(f'{key}.edges')/out.num
        out[f'{name}_conc'] = g(f'{key}.concurrent')/out.num
    return out


def summary(d):
    """ The original's summary table (computed from the means over runs, so the ratios are of means) """
    m = {k:np.mean(v, axis=0) if np.ndim(v) == 2 else v for k,v in d.items()}
    i = np.where(m['i'][late] > 0, m['i'][late], np.nan)
    return dict(
        cum_infections = m['si'][1:].sum(),
        final_prev     = m['i'][-1]/m['num'][-1],
        prev_5y        = m['i'][260]/m['num'][260],
        prev_10y       = m['i'][520]/m['num'][520],
        inc_100py      = np.mean(52*100*m['si'][late]/m['s'][late]),
        pct_dx         = 100*np.nanmean(m['dx'][late]/i),
        pct_art        = 100*np.nanmean(m['art'][late]/i),
        pct_supp       = 100*np.nanmean(m['supp'][late]/i),
        prep_cov       = 100*np.mean(m['prep'][late]/m['s'][late]) if 'prep' in m else 0,
        main_deg       = m['main_deg'][late].mean(),
        main_conc      = 100*m['main_conc'][late].mean(),
        casual_deg     = m['casual_deg'][late].mean(),
        casual_conc    = 100*m['casual_conc'][late].mean(),
        final_num      = m['num'][-1],
    )


if __name__ == '__main__':
    rows = []
    for scen,sim in scenarios.items():
        msim = ss.parallel(sim.new(verbose=0), n_runs=n_runs, parallel=False)
        d = ours(msim)
        a, b = summary(d), summary(theirs(scen))
        se = np.std(d.i[:, -1])/np.sqrt(n_runs)
        print(f'\n{scen} (Starsim, mean of {n_runs} runs, then the original, mean of 10)')
        for k in a:
            print(f'  {k:15s} {a[k]:9.3f} {b[k]:9.3f}')
        print(f'  infected at the end: {d.i[:, -1].mean():.1f} ± {se:.1f} (standard error), against {theirs(scen).i[-1]:.1f}')

    times = {scen:tools.time_run(lambda: sim.new(verbose=0).run(), n=3) for scen,sim in scenarios.items()}
    print('\none run: ' + ', '.join(f'{k} {v:.2f} s' for k,v in times.items()) + f'; mean {np.mean(list(times.values())):.2f} s (original: see {os.path.relpath(example, here)}/reference/timing.json)')
