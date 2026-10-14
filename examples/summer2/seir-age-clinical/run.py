"""
Run the original summer2 model and write its reference results and timing.

    python run.py

Needs the summer2 environment (see `_envs/summer2`).
"""
import os
import sys
import json

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
import tools

if __name__ == '__main__':
    out = json.loads(tools.run(['python', os.path.join(here, 'export.py')], 'summer2'))
    rows, seconds, first = out['rows'], out['seconds'], out['first']
    tools.write_results(here, rows)
    what = f'model.run() on a model that is already built and compiled (the last of the seven, with four derived outputs); importing summer2 and JAX, and building, compiling, and running all seven takes {first:.1f} s'
    tools.write_timing(here, seconds, what)
    print(f'Wrote {len(rows)} rows; one run takes {seconds:.4f} s (the first, with imports and compilation of all seven, {first:.1f} s)')
