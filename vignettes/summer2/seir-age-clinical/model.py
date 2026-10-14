"""
The summer2 derived-outputs example (examples/summer2/seir-age-clinical), in Starsim: an SEIR by
age, in which the infectious are asymptomatic, symptomatic, isolated, or in hospital, with outputs
by age and by clinical status
"""
import starsim as ss

seir = ss.Disease(
    infection       = ss.transmission('S -> E', beta=2, source='I'),
    incidence       = ss.progression('E -> I', rate=0.5),
    recovery        = ss.progression('I -> R', rate=0.3),
    infection_death = ss.death('I ->', rate=0.05),
    init            = dict(I=ss.by([[5, 0, 0, 0], [5, 0, 0, 0]], dims=['age', 'clinical'])),
)
seir.stratify(age=['young', 'old'], adjust={'incidence': [1, 1.1]}) # The old's shares sum to 1.1
seir.stratify( # Clinical status, which those who fall ill take by age
    clinical = ['asymptomatic', 'symptomatic', 'isolated', 'hospital'],
    states   = ['I'],
    split    = ss.by([[0.4, 0.3, 0.2, 0.1], [0.3, 0.3, 0.2, 0.3]], dims=['age', 'clinical']),
    adjust   = {'infection_death': [0, 1, 1, 2], 'rel_trans': [0.5, 1, 0.2, 0.1]},
)
sim = ss.Sim(seir, total_pop=1000, dt=0.1, stop=20)

if __name__ == '__main__':
    sim.run()
    sim.plot()
