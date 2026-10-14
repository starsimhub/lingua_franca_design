"""
The camdl age- and patch-structured SEIR (examples/camdl/stratified), in Starsim: contacts by age
within each patch, aging, movement between patches, and children vaccinated on day 20
"""
import starsim as ss

contacts = [[12, 4, 1], [4, 8, 2], [1, 2, 3]]
pop = ss.by([[3000, 1000], [5000, 2000], [2000, 500]], dims=['age', 'patch'])

seir = ss.Disease(
    infection = ss.transmission('S -> E', beta=ss.perday(0.04), source='I'),
    onset     = ss.progression('E -> I', dur=ss.days(5)),
    recovery  = ss.progression('I -> R', rate=ss.perday(0.1)),
    init      = dict(I=ss.by(age=[10, 0, 0], patch=[1, 0])),
)
seir.stratify(age=[0, 5, 50]) # Children, adults, and elders, who age at 1/5 and 1/45 a year
seir.stratify(patch=['north', 'south'], kind='space', split=pop, mobility=ss.Mobility(matrix=[[0, 0.01], [0.01, 0]], kind='migrate'))
vaccinate = ss.vaccinate(ss.Vaccine(efficacy=1.0), years=[20], coverage=0.6, eligible=(ss.People(1).age < 5) & seir.S)
sim = ss.Sim(seir, networks=ss.contacts(contacts, age=[0, 5, 50]), total_pop=13_510, unit='day', stop=150)

if __name__ == '__main__':
    ss.parallel(novax=sim, vax=sim.new(interventions=vaccinate)).plot()
