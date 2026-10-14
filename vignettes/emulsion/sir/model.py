"""
The EMULSION SIR (examples/emulsion/sir), in Starsim: one model, run as compartments and as individuals
"""
import starsim as ss

sir = ss.Disease(
    infection = ss.transmission('S -> I', beta=ss.perday(0.5)),
    recovery  = ss.progression('I -> R', rate=ss.perday(0.1)),
    init      = dict(I=1),
)
compartment = ss.Sim(sir, total_pop=100, stop=ss.days(100), solver='binomial')
ibm         = ss.Sim(sir, total_pop=100, stop=ss.days(100), solver='abm')

if __name__ == '__main__':
    msim = ss.parallel(compartment=compartment, ibm=ibm)
    msim.plot()
