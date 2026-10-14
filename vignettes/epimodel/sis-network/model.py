"""
The EpiModel introduction (examples/epimodel/sis-network), in Starsim: an SIS epidemic over
partnerships that form and dissolve, among 500 people
"""
import starsim as ss

sis = ss.Disease(
    infection = ss.transmission('S -> I', beta=ss.prob(1 - (1 - 0.4)**2)), # Two acts per partnership per step, each with a 40% chance
    recovery  = ss.progression('I -> S', rate=ss.prob(0.05)),
    init      = dict(I=10),
)
partners = ss.PartnerNet(n_contacts=0.7, concurrency=0.22, max_contacts=3, dur=50) # 175 partnerships among 500, 110 with two or more, none with four, lasting 50 steps
sim = ss.Sim(sis, networks=partners, n_agents=500, stop=500)

if __name__ == '__main__':
    msim = sim.run(n_runs=10)
    msim.plot()
