"""
The flepiMoP two-population tutorial (examples/flepimop/seir_2pop), in Starsim: an SEIR in a large
and a small province, whose residents spend part of each day in the other
"""
import starsim as ss

pop     = dict(large_province=9000, small_province=1000)
commute = [[0, 100/9000], [20/1000, 0]] # The share of each province's residents who travel to the other
gamma   = 1/5

seir = ss.Disease(
    infection = ss.transmission('S -> E', beta=2.5*gamma, source='I'),
    onset     = ss.progression('E -> I', rate=1/4),
    recovery  = ss.progression('I -> R', rate=gamma),
    init      = dict(E=ss.by(patch=[5, 0])),
)
away = [[0.5*share for share in row] for row in commute] # Travelers are away for half the day
seir.stratify(patch=list(pop.keys()), split=list(pop.values()), mobility=ss.Mobility(matrix=away, kind='visit'))
sim = ss.Sim(seir, total_pop=sum(pop.values()), start='2020-02-01', stop='2020-08-31')

if __name__ == '__main__':
    sim.run()
    sim.plot()
