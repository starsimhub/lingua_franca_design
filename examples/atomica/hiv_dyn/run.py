"""
Run the original Atomica model and write its reference results and timing.

    python run.py

Needs the Atomica environment (see `_envs/atomica`).
"""
import os
import sys
import json

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(here)))
import tools

if __name__ == '__main__':
    out = json.loads(tools.run(['python', os.path.join(here, 'simulate.py')], 'atomica').splitlines()[-1])
    rows = out['rows']
    tools.write_results(here, rows)
    seconds = out['seconds']
    tools.write_timing(here, seconds, f"Project.run_sim() in Atomica {out['version']}: one run of 20 yearly steps without programs, with the spreadsheets already loaded (loading them takes about {out['load']:.1f} s); the three budget scenarios (Project.run_scenarios()) take {out['scenarios']:.4f} s together")
    print(f"Wrote {len(rows)} rows; one run takes {seconds:.4f} s, and the three scenarios {out['scenarios']:.4f} s")
