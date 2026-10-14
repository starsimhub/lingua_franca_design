"""
The odin stochastic SIR with arrays (examples/odin/stochastic_sir_arrays), in Starsim: an SIR in
1,001 people, run 100 times. The original holds the 100 runs in an array; here they are 100 runs
"""
import starsim as ss

sir = ss.Disease(
    infection = ss.transmission('S -> I', beta=0.2),
    recovery  = ss.progression('I -> R', rate=0.1),
    init      = dict(I=1),
)
sim = ss.Sim(sir, total_pop=1001, stop=100, solver='binomial')

if __name__ == '__main__':
    msim = sim.run(n_runs=100)
    msim.plot()
