"""
Run the original camdl model and write its reference results and timing.

    python run.py

Needs the camdl environment (see `_envs/camdl`).
"""
import os
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
import tools

model = os.path.join(here, 'original', 'sir.camdl')
pars = dict(beta=0.4, gamma=0.15, rho=0.6, k=10)
n_runs = 200 # For the stochastic backend


def simulate(*args):
    """ Run the model, returning the trajectory and the observations as lists of rows """
    with tempfile.TemporaryDirectory() as tmp:
        traj, obs = os.path.join(tmp, 'traj.tsv'), os.path.join(tmp, 'obs.tsv')
        cmd = ['camdl', 'simulate', model, '--no-progress', '--output-dir', os.path.join(tmp, 'store'), '-o', traj, '--obs', obs, *args]
        for key,val in pars.items():
            cmd += ['--param', f'{key}={val}']
        tools.run(cmd, 'camdl')
        return read(traj), read(obs)


def read(path):
    with open(path) as f:
        lines = [line.rstrip('\n').split('\t') for line in f if not line.startswith('#')]
    return [dict(zip(lines[0], map(float, line))) for line in lines[1:]]


def summarize(rows, key, time='t'):
    """ The mean and the 5% and 95% quantiles over the runs, at each time """
    times = sorted({row[time] for row in rows})
    out = []
    for t in times:
        vals = sorted(row[key] for row in rows if row[time] == t)
        n = len(vals)
        out.append(dict(time=t, value=sum(vals)/n, low=vals[int(0.05*(n - 1))], high=vals[int(0.95*(n - 1))]))
    return out


if __name__ == '__main__':
    rows = []

    # The deterministic run: the compartments, and the weekly cases expected from the infections
    traj, obs = simulate('--backend', 'ode')
    for key in ['S', 'I', 'R']:
        rows += [dict(time=row['t'], series=f'ode_{key}', value=row[key]) for row in traj]
    rows += [dict(time=row['t'], series='ode_infection', value=row['flow_infection']) for row in traj]
    for week in range(1, 13):
        total = sum(row['flow_infection'] for row in traj if 7*(week - 1) < row['t'] <= 7*week)
        rows.append(dict(time=7*week, series='ode_cases', value=pars['rho']*total))

    # The stochastic run (chain-binomial, the default), summarized over many runs
    traj, obs = simulate('--replicates', str(n_runs))
    rows += [dict(series='stochastic_I', **row) for row in summarize(traj, 'I')]
    rows += [dict(series='stochastic_cases', **row) for row in summarize(obs, 'cases', time='time')]

    tools.write_results(here, rows)
    seconds = tools.time_run(lambda: simulate('--backend', 'ode'))
    tools.write_timing(here, seconds, 'camdl simulate --backend ode, as one command (the model is already compiled and cached)')
    print(f'Wrote {len(rows)} rows; one ODE run takes {seconds:.3f} s')
