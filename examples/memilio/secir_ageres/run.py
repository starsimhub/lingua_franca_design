"""
Run the original MEmilio example and write its reference results and timing.

    python run.py

Needs the memilio environment (see `_envs/memilio`).
"""
import os
import sys
import json
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
import tools

script = os.path.join(here, 'original', 'ode_secir_ageres.py')
n_groups = 3

# The original prints the last value and the solver's time points, and plots the rest, so this runs it
# as it is, keeping what it gets back from `simulate`, and interpolates that to whole days with MEmilio's
# own `interpolate_simulation_result` (as the other MEmilio examples do)
driver = """
import io, sys, json, time, contextlib, importlib.util
import matplotlib
matplotlib.use('Agg')
from memilio.simulation.osecir import InfectionState, interpolate_simulation_result

spec = importlib.util.spec_from_file_location('ode_secir_ageres', sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
kept = dict()
simulate = mod.simulate

def wrapper(*args, **kwargs):
    start = time.perf_counter()
    out = simulate(*args, **kwargs)
    kept['seconds'] = time.perf_counter() - start
    kept['result'] = out
    return out

mod.simulate = wrapper
with contextlib.redirect_stdout(io.StringIO()):
    mod.run_ode_secir_ageres_simulation(show_plot=False)

raw = kept['result']
arr = interpolate_simulation_result(raw).as_ndarray()
names = [name for name,state in sorted(InfectionState.__members__.items(), key=lambda item: int(item[1])) if name != 'Count']
n = len(names)
out = dict(time=arr[0].tolist(), steps=raw.get_num_time_points(), seconds=kept['seconds'], names=names)
out['groups'] = [{name:arr[1 + g*n + i].tolist() for i,name in enumerate(names)} for g in range((arr.shape[0] - 1)//n)]
print('RESULT ' + json.dumps(out))
"""


def simulate():
    """ Run the example, returning the times, the count in each state of each age group at each time, and what the solver did """
    with tempfile.TemporaryDirectory() as tmp: # The example would save its plot where it is run
        out = tools.run(['python', '-c', driver, script], 'memilio', cwd=tmp)
    line = [line for line in out.splitlines() if line.startswith('RESULT ')][-1]
    return json.loads(line[len('RESULT '):])


if __name__ == '__main__':
    out = simulate()
    assert len(out['groups']) == n_groups
    rows = []
    for name in out['names']:
        total = [sum(group[name][i] for group in out['groups']) for i in range(len(out['time']))]
        rows += [dict(time=t, series=name, value=value) for t,value in zip(out['time'], total)]
    for g,group in enumerate(out['groups']): # The groups are identical, so one state is enough to show it
        rows += [dict(time=t, series=f'InfectedSymptoms_{g}', value=value) for t,value in zip(out['time'], group['InfectedSymptoms'])]

    tools.write_results(here, rows)
    seconds = tools.time_run(simulate)
    what = f'python ode_secir_ageres.py, as one command (nearly all of it is starting Python and importing; the call to simulate() itself takes about {out["seconds"]*1000:.2f} ms, for {out["steps"]} adaptive time points)'
    tools.write_timing(here, seconds, what)
    print(f'Wrote {len(rows)} rows; one run takes {seconds:.3f} s, of which the solver takes {out["seconds"]*1000:.2f} ms over {out["steps"]} time points')
