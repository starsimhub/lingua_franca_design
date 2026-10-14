"""
The summer2 mixing-matrix example (examples/summer2/sir-age-location), in Starsim: an SIR
stratified by age and by location, with a mixing matrix for each
"""
import starsim as ss

sir = ss.Disease(
    infection       = ss.transmission('S -> I', beta=2),
    recovery        = ss.progression('I -> R', rate=1/3),
    infection_death = ss.death('I ->', rate=0.05),
    init            = dict(I=10),
)
sir.stratify(age=['young', 'old'])
sir.stratify(location=['urban', 'rural'], split=[0.7, 0.3], adjust={'infection_death': [1, 3]}) # Rural people have worse health care

mixing = ss.contacts(age=[[0.2, 0.3], [0.5, 0.7]], location=[[0.8, 0.2], [0.2, 0.8]])
sim = ss.Sim(sir, networks=mixing, total_pop=1000, dt=0.1, stop=20)

if __name__ == '__main__':
    sim.run()
    sim.plot()
