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

script = os.path.join(here, 'original', 'ode_secir_simple.py')

# The original prints only the last value and plots the rest, so this runs it as it is, keeping what
# it passes through `simulate` and `interpolate_simulation_result`
driver = """
import sys, json, time, importlib.util
import matplotlib
matplotlib.use('Agg')
from memilio.simulation.osecir import InfectionState

spec = importlib.util.spec_from_file_location('ode_secir_simple', sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
kept = dict()

def keep(name):
    func = getattr(mod, name)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        out = func(*args, **kwargs)
        kept[name] = out
        kept[name + '_seconds'] = time.perf_counter() - start
        return out
    setattr(mod, name, wrapper)

keep('simulate')
keep('interpolate_simulation_result')
mod.run_ode_secir_simulation(show_plot=False)

arr = kept['interpolate_simulation_result'].as_ndarray()
names = [name for name,state in sorted(InfectionState.__members__.items(), key=lambda item: int(item[1])) if name != 'Count']
assert len(names) == arr.shape[0] - 1
out = dict(time=arr[0].tolist(), steps=kept['simulate'].get_num_time_points(), seconds=kept['simulate_seconds'])
out['states'] = {name:arr[i + 1].tolist() for i,name in enumerate(names)}
print('RESULT ' + json.dumps(out))
"""


def simulate():
    """ Run the example, returning the times, the count in each state at each time, and what the solver did """
    with tempfile.TemporaryDirectory() as tmp: # The example saves its plot where it is run
        out = tools.run(['python', '-c', driver, script], 'memilio', cwd=tmp)
    line = [line for line in out.splitlines() if line.startswith('RESULT ')][-1]
    return json.loads(line[len('RESULT '):])


if __name__ == '__main__':
    out = simulate()
    rows = []
    for name,values in out['states'].items():
        rows += [dict(time=t, series=name, value=value) for t,value in zip(out['time'], values)]

    tools.write_results(here, rows)
    seconds = tools.time_run(simulate)
    what = f'python ode_secir_simple.py, as one command (nearly all of it is starting Python, importing, and drawing the plot; the call to simulate() itself takes about {out["seconds"]*1000:.2f} ms, for {out["steps"]} adaptive time points)'
    tools.write_timing(here, seconds, what)
    print(f'Wrote {len(rows)} rows; one run takes {seconds:.3f} s, of which the solver takes {out["seconds"]*1000:.2f} ms')
