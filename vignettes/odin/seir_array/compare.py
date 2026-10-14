"""
Compare the Starsim version with the reference results of the original

    python compare.py
"""
import os
import sys
import numpy as np
import starsim as ss

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
sys.path.insert(0, os.path.join(root, 'examples'))
import tools
from model import sim

ref = tools.read_results(os.path.join(root, 'examples', 'odin', 'seir_array'))
ages = {'0-1':'0', '1-5':'1-4', '5-15':'5-14', '15-30':'15-29', '30+':'30+'} # The original's names, and Starsim's labels


def variant(old, new):
    """ The sim of model.py with one piece of its text replaced, for the checks below """
    with open(os.path.join(here, 'model.py')) as f:
        src = f.read()
    assert old in src
    out = dict(__name__='variant')
    exec(src.replace(old, new), out)
    return out['sim']


def onset(dur):
    """ The sim of model.py with another dwell time for the latent (the sim holds its own copy of the disease, so that is the one changed) """
    out = sim.new()
    out.inputs['modules'][0].onset.dur = dur
    return ss.Sim(out.inputs)


def worst(sim):
    """ The largest difference in each state over the year, as a share of its largest value: in total, and in the age group where it is largest """
    res = sim.new(verbose=0).run().results.seir
    out = {}
    for state in 'SEIR': # A stock at index k is the number after step k, the original's on day k+1, so both start on day 1
        theirs = np.array(ref[state][1])[1:]
        total = np.abs(res[f'n_{state}'].values[:-1] - theirs).max()/theirs.max()
        by_age = {}
        for age,label in ages.items():
            theirs = np.array(ref[f'{state}_{age}'][1])[1:]
            by_age[age] = np.abs(res[f'n_{state}'].select(age=label).values[:-1] - theirs).max()/theirs.max()
        age = max(by_age, key=by_age.get)
        out[state] = (total, age, by_age[age], res[f'n_{state}'].values[:-1])
    return out


def show(label, sim):
    diffs = worst(sim)
    print(f'{label:28s} ' + '; '.join(f'{s} {d[0]:.2%} (worst age {d[1]}: {d[2]:.2%})' for s,d in diffs.items()))
    return diffs


if __name__ == '__main__':
    diffs = show('model.py (200 stages)', sim)
    I, theirs = diffs['I'][3], np.array(ref['I'][1])[1:] # Both from day 1
    print(f'  peak I {I.max():,.0f} on day {I.argmax() + 1} (original {theirs.max():,.0f} on day {theirs.argmax() + 1}); I on day 30 {I[29]:.1f} (original {theirs[29]:.1f})')
    show('without the workaround', variant('    history', '    # history'))
    for k in [50, 100, 400]:
        show(f'{k} stages', onset(ss.erlang(k=k, mean=ss.days(14))))
    show('ss.constant (50 stages)', onset(ss.constant(ss.days(14))))

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    print(f'one run: {tools.time_run(run, n=3):.3f} s (original: see ../../../examples/odin/seir_array/reference/timing.json)')
    built = sim.new(verbose=0).init()

    def rerun():
        built.restart()
        built.run()
    print(f'one run of a built sim: {tools.time_run(rerun, n=3):.3f} s')
