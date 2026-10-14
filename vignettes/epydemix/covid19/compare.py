"""
Compare the Starsim version with the reference results of the original

    python compare.py

Takes about a minute. The runs with a reopening scenario are run one by one, since many runs of a
sim with a modifier would otherwise be spread over processes.
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
import model
from model import data

example = os.path.join(root, 'examples', 'epydemix', 'covid19')
ref = tools.read_results(example)
table = sc.dataframe.read_csv(os.path.join(example, 'reference', 'results.csv')).set_index('series')
n_runs = data['n_runs']
scenarios = ['persistence', 'moderate', 'high']


def weekly(daily, times):
    """ Sum daily flows (index 0 is the first day) over the weeks ending at each reference time (days to the end of the week's last day) """
    return np.array([daily[..., max(0, int(t) - 7):int(t)].sum(axis=-1) for t in times]).T


def show(label, ours, key):
    """ The peaks and when they come, and the largest difference from the original's mean, as a share of its peak """
    times, theirs = ref[key]
    theirs = np.array(theirs)
    n = min(len(ours), len(theirs))
    diff = np.abs(ours[:n] - theirs[:n]).max()/theirs.max()
    print(f'{label:30s} peak {ours.max():9,.0f} on day {times[ours.argmax()]:3.0f} (original {theirs.max():9,.0f} on day {times[theirs.argmax()]:3.0f}); largest difference {diff:.1%} of the peak')
    return


def runs(scenario, n, pars=None):
    """ A function giving a result of n runs of a scenario, with a row for each run """
    sim = model.sim.new(verbose=0, pars=pars, interventions=model.reopening.get(scenario))
    if scenario == 'persistence': # Nothing but compartments: all the runs in one call to the kernel
        res = sim.run(n_runs=n).results.covid
        return lambda key, **kw: res[key].select(**kw).values if kw else res[key].values
    sims = [sim.new(verbose=0, rand_seed=i + 1).run() for i in range(n)]
    return lambda key, **kw: np.array([s.results.covid[key].select(**kw).values if kw else s.results.covid[key].values for s in sims])


if __name__ == '__main__':
    print(f'At fixed values ({data["fixed"]}), the mean of {n_runs} runs:')
    times = ref['fixed_persistence_deaths'][0]
    for scenario in scenarios:
        get = runs(scenario, n_runs)
        show(f'{scenario}: weekly deaths', weekly(get('deaths'), times).mean(axis=0), f'fixed_{scenario}_deaths')
        if scenario == 'persistence':
            for group in data['groups']:
                show(f'  deaths {group}', weekly(get('deaths', age=group), times).mean(axis=0), f'fixed_{scenario}_deaths_{group}')
            for name,state in dict(E='n_E', I='n_I', R='n_R', D='n_D').items(): # The original's are at the end of each day, ours at the start of the next
                show(f'  {name}', get(state).mean(axis=0)[1:], f'fixed_{scenario}_{name}')
            print(f'  total deaths by 2 August: {get("cum_deaths")[:, -1].mean():,.0f} (original {ref[f"fixed_{scenario}_D4"][1][-1]:,.0f})')

    print('\nCalibration to the weekly deaths up to 31 May:')
    fit = model.sim.new(stop='2020-05-31', verbose=0).calibrate(trials=1000, n_runs=5, rand_seed=1, verbose=False)
    for par,name in dict(R0='R0', Delta='Delta', I0='I0', seasonality_min='smin').items():
        row = table.loc[f'posterior_{par}']
        ours = f'{getattr(fit.pars[name], "value", fit.pars[name]):.4g}' if name in fit.pars else 'not fitted'
        print(f'  {par:16s} Starsim {ours:>10s}; original posterior mean {row.value:.4g} (5% to 95%: {row.low:.4g} to {row.high:.4g})')
    weeks, observed = ref['data_deaths']
    abc = np.array(ref['abc_fit_deaths'][1])
    print(f'  mean absolute error over the mean of the data: Starsim {fit.mismatch:.3f} (mean of 5 runs); original {np.abs(abc - observed[:len(abc)]).sum()/np.sum(observed[:len(abc)]):.3f} (the mean of its accepted runs)')
    print('Projections from the fitted values (Starsim, mean of 100 runs) and from the posterior (original, mean of 100 runs):')
    for scenario in scenarios:
        get = runs(scenario, 100, pars=fit.pars)
        show(f'  {scenario}: weekly deaths', weekly(get('deaths'), times).mean(axis=0), f'abc_{scenario}_deaths')

    def run():
        ss.Sim(model.sim.new(stop='2020-05-31').inputs, verbose=0).run()
    built = model.sim.new(stop='2020-05-31', verbose=0).init()
    print(f'\none run of the calibration period: {tools.time_run(run):.3f} s, or {tools.time_run(lambda: built.restart(rand_seed=2).run()):.4f} s restarted')
