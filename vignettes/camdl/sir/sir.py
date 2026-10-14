"""
The camdl SIR (examples/camdl/sir), in Starsim: a closed epidemic, observed through weekly reported cases
"""
import starsim as ss

beta  = ss.par(ss.perday(0.4),  bounds=[0.05, 1.0], prior=ss.lognorm_im(mean=-1.0, sigma=0.5), doc='transmission rate')
gamma = ss.par(ss.perday(0.15), bounds=[0.01, 0.5], prior=ss.lognorm_im(mean=-2.0, sigma=0.5), doc='recovery rate')
rho   = ss.par(0.6, doc='reporting fraction')

S, I, R = ss.states(3)
infection = S >> I @ beta * I
recovery  = I >> R @ gamma
cases     = ss.outcome(rho * infection, every=ss.weeks(1))

sir = ss.Disease(infection, recovery, cases, init=dict(I=10))
sim = ss.Sim(sir, total_pop=10_000, unit='day', stop=ss.weeks(12))

if __name__ == '__main__':
    sim.run()
    sim.plot()
