"""
Shared helpers for the `run.py` of each example: every example writes the same
two files, whatever framework it is written in.

    reference/results.csv   One row per time, series, and value (with low and high, for a summary of many runs)
    reference/timing.json   The wall-clock time of one run, and the machine it was measured on
"""
import os
import csv
import json
import time
import platform
import subprocess

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def env_path(framework):
    """ The PATH with a framework's environment (`_envs/<framework>/bin`) in front """
    return os.path.join(root, '_envs', framework, 'bin') + os.pathsep + os.environ['PATH']


def run(cmd, framework, cwd=None):
    """ Run a command in a framework's environment, and return what it prints """
    env = dict(os.environ, PATH=env_path(framework))
    out = subprocess.run(cmd, cwd=cwd, env=env, check=True, capture_output=True, text=True)
    return out.stdout


def time_run(func, n=5):
    """ The median time in seconds of n calls of a function, after one warm-up call """
    func()
    times = []
    for i in range(n):
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)
    return sorted(times)[n//2]


def write_results(folder, rows):
    """ Write the results: a list of dicts with keys time, series, value, and optionally low and high """
    path = os.path.join(folder, 'reference', 'results.csv')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['time', 'series', 'value', 'low', 'high'], restval='')
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_timing(folder, seconds, what):
    """ Write the time of one run, with what was timed and where """
    path = os.path.join(folder, 'reference', 'timing.json')
    info = dict(seconds=round(seconds, 4), what=what, machine=platform.processor() or platform.machine(), cpus=os.cpu_count(), system=platform.platform())
    with open(path, 'w') as f:
        json.dump(info, f, indent=2)
        f.write('\n')
    return path


def read_results(folder):
    """ Read the results back as `{series: (times, values)}` """
    out = dict()
    with open(os.path.join(folder, 'reference', 'results.csv')) as f:
        for row in csv.DictReader(f):
            times, values = out.setdefault(row['series'], ([], []))
            times.append(float(row['time']))
            values.append(float(row['value']))
    return out
