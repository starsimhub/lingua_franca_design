"""
Run the original flepiMoP configuration and write its reference results and timing.

    python run.py

Needs the flepimop environment (see `_envs/flepimop`).
"""
import os
import csv
import sys
import glob
import shutil
import tempfile
import datetime

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
import tools

config = 'config_sample_2pop.yml'
subpops = ['large_province', 'small_province']
start = datetime.date(2020, 2, 1) # start_date in the configuration


def simulate():
    """ Run the configuration, returning the rows of its one output file """
    with tempfile.TemporaryDirectory() as tmp: # flepiMoP reads and writes relative to where it is run
        project = shutil.copytree(os.path.join(here, 'original'), os.path.join(tmp, 'project'))
        cmd = ['flepimop', 'simulate', config, '--write-csv', '--no-write-parquet', '--jobs', '1', '--out-id', 'reference']
        tools.run(cmd, 'flepimop', cwd=project)
        files = glob.glob(os.path.join(project, 'model_output', '*', 'reference', 'seir', '*.seir.csv'))
        assert len(files) == 1
        with open(files[0]) as f:
            return list(csv.DictReader(f))


if __name__ == '__main__':
    out = simulate()
    rows = []
    for subpop in subpops:
        for kind in ['prevalence', 'incidence']:
            for state in ['S', 'E', 'I', 'R']:
                if kind == 'incidence' and state == 'S': # Nothing flows into S, so this is all zeros
                    continue
                series = f'{subpop}_{state}' if kind == 'prevalence' else f'{subpop}_incidence_{state}'
                for row in out:
                    if row['mc_value_type'] == kind and row['mc_name'] == state:
                        day = (datetime.date.fromisoformat(row['date'][:10]) - start).days
                        rows.append(dict(time=day, series=series, value=float(row[subpop])))

    tools.write_results(here, rows)
    seconds = tools.time_run(simulate)
    tools.write_timing(here, seconds, 'flepimop simulate config_sample_2pop.yml, as one command (nearly all of it is starting Python and compiling the integrator with Numba, which is done again on every run)')
    print(f'Wrote {len(rows)} rows; one run takes {seconds:.3f} s')
