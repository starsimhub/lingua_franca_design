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

example = os.path.join(root, 'examples', 'summer2', 'seir-age-clinical')
ref = {k:np.array(v[1]) for k,v in tools.read_results(example).items()}
ages = ['young', 'old']
clinical = ['asymptomatic', 'symptomatic', 'isolated', 'hospital']
names = dict(zip(clinical, ['Ia', 'Is', 'Ii', 'Ih'])) # As four states


def flow(values):
    """ A flow in each step as summer2 reports it: a rate per unit of time, at the end of the step """
    return np.append(0, values[:-1]/0.1)


def stock(values):
    """ A number in a state at each of the original's times: Starsim's at index k is the number after step k, and the start is not a result """
    return np.append(np.nan, values[:-1])


def start():
    """ The number in I at the start, by age and clinical status """
    return sim.new(verbose=0).init().diseases.seir.I.values.reshape(len(ages), len(clinical))


def as_states():
    """ The same model with the clinical statuses as four states, started as the stratified model is, as a check of the stratification """
    S, E, Ia, Is, Ii, Ih, R = ss.states(7)
    starts = start()
    init = {names[c]:ss.by(age=[starts[i, j]/500 for i in range(len(ages))]) for j,c in enumerate(clinical)} # As fractions of each age group
    seir = ss.Disease(
        infection  = S >> E @ 2 * (0.5*Ia + Is + 0.2*Ii + 0.1*Ih),
        a          = E >> Ia @ 0.5 * ss.by(age=[0.4, 0.3]),
        s          = E >> Is @ 0.5 * ss.by(age=[0.3, 0.3]),
        i          = E >> Ii @ 0.5 * ss.by(age=[0.2, 0.2]),
        h          = E >> Ih @ 0.5 * ss.by(age=[0.1, 0.3]),
        recovery   = (Ia | Is | Ii | Ih) >> R @ 0.3,
        death      = (Is | Ii) >> ss.null @ 0.05,
        hosp_death = Ih >> ss.null @ 0.1,
        init       = init,
        name       = 'seir',
    )
    return ss.Sim(seir.stratify(age=ages), total_pop=1000, dt=0.1, stop=20, verbose=0).run().results.seir


if __name__ == '__main__':
    res = sim.new(verbose=0).run().results.seir

    # Compartments, by age and clinical status
    ours = dict()
    for age in ages:
        for state in 'SER':
            ours[f'{state}_{age}'] = stock(res[f'n_{state}'].select(age=age).values)
        for name in clinical:
            ours[f'I_{age}_{name}'] = stock(res.n_I.select(age=age, clinical=name).values)
    stocks = {k:np.abs(v[1:] - ref[k][1:]).max() for k,v in ours.items()}

    # The derived outputs: summer2's flows are rates, and its cumulative deaths sum those rates without multiplying by the step, so are 10 times the deaths
    hosp = res.n_I.select(clinical='hospital').values
    outputs = dict(hospital_occupancy=stock(hosp), prop_infected_hosp=stock(hosp/res.n_I.values), notifications=flow(res.incidence.select(clinical=['isolated', 'hospital']).values))
    for age in ages:
        outputs[f'accum_death_{age}'] = np.append(0, res.cum_infection_death.select(age=age).values[:-1]) / 0.1
        outputs[f'incidence_{age}'] = flow(res.incidence.select(age=age).values)
        for name in clinical:
            outputs[f'incidence_{age}_{name}'] = flow(res.incidence.select(age=age, clinical=name).values)
    for name in clinical:
        outputs[f'incidence_{name}'] = flow(res.incidence.select(clinical=name).values)
    assert sorted(outputs) == sorted(k for k in ref if k not in ours), 'Every output of the original should be compared'
    rel = {k:np.abs(v[1:] - ref[k][1:]).max()/np.abs(ref[k]).max() for k,v in outputs.items()}
    for label,d,unit in [('compartment', stocks, ' people (of 1,000)'), ('derived output', rel, ' of its peak')]:
        worst = max(d, key=d.get)
        print(f'largest difference in any {label}: {d[worst]:.3g}{unit} ({worst})')
    end = {k:abs(v[-1] - ref[k][-1])/abs(ref[k][-1]) for k,v in (ours | outputs).items()}
    print(f'largest difference at time 20: {max(end.values()):.1%} ({max(end, key=end.get)})')
    print(f'starting in I: {start().sum(axis=0).round(2)}; the original starts everyone asymptomatic')

    # The stratification against the same model as four states, from the same start
    states = as_states()
    check = max(np.abs(res.n_I.select(age=a, clinical=c).values - states[f'n_{names[c]}'].select(age=a).values).max() for a in ages for c in clinical)
    print(f'stratified against four states, from the same start: {check:.2g} people')

    for solver in ['binomial', 'abm']:
        runs = sim.new(verbose=0, solver=solver, **(dict(n_agents=1000) if solver == 'abm' else {})).run(n_runs=100).results.seir
        print(f'{solver}: recovered at the end {runs.n_R.values.mean(axis=0)[-2]:.0f} (ODE {res.n_R[-2]:.0f})')

    def run():
        ss.Sim(sim.inputs, verbose=0).run()
    built = sim.new(verbose=0).run()
    print(f'one ODE run: {tools.time_run(run):.3f} s, or {tools.time_run(built.restart):.5f} s for a run of a sim that is already built')
