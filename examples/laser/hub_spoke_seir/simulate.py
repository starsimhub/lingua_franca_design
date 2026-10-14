"""
Run the original LASER example several times, each with a different seed, and
print the results as JSON. This is run by `run.py`, in the LASER environment.

    python simulate.py <n_runs>

The original is run as it is, with two changes made to its text here: the part
after the model run (the plotting) is cut off, and a seed is added to the
parameters, since without one LASER uses the same fixed seed for every run.
"""
import os
import sys
import json
import time

here = os.path.dirname(os.path.abspath(__file__))
patches = ['Central City', 'Town 1', 'Interim 1a', 'Town 3'] # The hub, the seeded town, the patch next to the hub on that spoke, and a far town
states = ['S', 'E', 'I', 'R']

with open(os.path.join(here, 'original', 'grid_examples_seir.py')) as f:
    source = f.read()
source, plotting = source.split('\nimport matplotlib.pyplot as plt\n')
old = '"gravity_c": 2.5}'
new = '"gravity_c": 2.5, "prng_seed": seed}'
assert source.count(old) == 1
code = compile(source.replace(old, new), 'grid_examples_seir.py', 'exec')


def simulate(seed):
    """ Run the model once, returning each series as a list over time, and the time taken """
    names = dict(seed=seed)
    start = time.perf_counter()
    exec(code, names)
    seconds = time.perf_counter() - start
    nodes, scenario = names['model'].nodes, names['scenario']
    out = dict()
    for key in states + ['newly_infected']:
        vals = getattr(nodes, key)
        if key == 'newly_infected':
            key, vals = 'new_infections', vals[:-1] # The last row is never filled in
        out[key] = vals.sum(axis=1).tolist()
        for patch in patches:
            index = int(scenario.nodeid[scenario.name == patch].iloc[0])
            out[f"{key}_{patch.lower().replace(' ', '_')}"] = vals[:, index].tolist()
    return out, seconds


if __name__ == '__main__':
    n_runs = int(sys.argv[1])
    stdout, sys.stdout = sys.stdout, sys.stderr # Keep anything the model prints out of the JSON
    runs, times = [], []
    for i in range(n_runs):
        out, seconds = simulate(seed=1000*(i + 1)) # Spaced out, since LASER seeds thread j with seed + j
        runs.append(out)
        times.append(seconds)
    seconds = sorted(times[1:])[(n_runs - 1)//2] if n_runs > 1 else times[0] # The first run includes compiling
    json.dump(dict(runs=runs, seconds=seconds, first=times[0]), stdout)
