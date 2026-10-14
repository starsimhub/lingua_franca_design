"""
The EMULSION quickstart model (examples/emulsion/quickstart), in Starsim: 100 animals, each with
an age group, a gestation cycle, and a health state, where gestation needs adulthood, every
farrowing gives a newborn (infected or protected by maternal antibodies, by the mother's health),
infectious mothers may abort, and sick animals are quarantined from April to September while
the quarantine has room
"""
import numpy as np
import starsim as ss

dt = 7 # Days
adult_age = 30 # Days: the YAML gives adult_age twice, and EMULSION uses the second


def stay(mod, state, dur, rate, after=True):
    """
    Workaround for EMULSION's duration, a minimum stay in a state that gates the other ways out:
    a rate that applies only once an agent has been in the state that long (or, with after=False,
    only until then), in whole steps as EMULSION rounds it
    """
    def func(sim, uids):
        stayed = sim.ti - sim.diseases[mod][f'ti_{state}'][uids] >= round(dur/dt)
        return (rate(sim, uids) if callable(rate) else rate)*(stayed == after)
    return func


class Life(ss.Disease):
    """ Workaround for actions on crossing a transition: a newborn for each farrowing, and a count of abortions """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.define_states(ss.FloatArr('nb_abortions', default=0.0))
        self.vertical = ss.bernoulli(p=0.3) # Vertical transmission, from a mother who is E, I, or Q

    def init_post(self):
        super().init_post()
        # Workaround: EMULSION's animals start in NG before the first step, not during it
        self.ti_NG[self.NG.uids] = -1
        return

    def init_results(self):
        super().init_results()
        self.define_results(ss.Result('nb_total_abortions', label='Abortions of the living', scale=False))
        return

    def step_state(self):
        super().step_state() # Before health's, as in EMULSION's order of processes
        sim, events = self.sim, self.engine.events
        growth, health = sim.diseases.growth, sim.diseases.health
        self.nb_abortions[events.get('abortion', ss.uids())] += 1
        mothers = events.get('farrowing', ss.uids())
        if len(mothers):
            infected = np.isin(mothers, self.vertical.filter(mothers[(health.E | health.I | health.Q)[mothers]]))
            new = sim.people.grow(len(mothers))
            sim.people.age[new] = 0
            for mod,state,uids in [(growth, 'J', new), (self, 'NG', new), (health, 'I', new[infected]), (health, 'M', new[~infected])]:
                mod[state][uids] = True
                mod[f'ti_{state}'][uids] = self.ti
        return

    def update_results(self):
        super().update_results()
        self.results.nb_total_abortions[self.ti] = self.nb_abortions[self.sim.people.alive].sum()
        return


# Uniform up to adult_age, plus the step EMULSION ages them by before its first test, in years
ppl = ss.People(100, age_data=ss.uniform(low=dt/365, high=(adult_age + dt)/365))
J, A = ss.states('J A')
# Workaround for "as soon as": a very high rate
growth = ss.Disease(maturity=ss.Transition(J, A, rate=ss.perday(1e9), where=ppl.age >= adult_age/365))

S, E, I, R, Q, M = ss.states('S E I R Q M')
dates = {'2021-01-01': 0, '2021-04-01': 1, '2021-09-02': 0, '2022-04-01': 1, '2022-09-02': 0}
quarantine = ss.par(ss.timeseries(dates))
health = ss.Disease(
    infection   = S >> E @ ss.perday(0.1)*I.n/(S + E + I + R + Q + M).n,
    onset       = ss.Transition(E, I, rate=stay('health', 'E', 10, 0.3)),
    recovery    = I >> R @ ss.perday(0.01),
    detection   = I >> Q @ ss.perday(0.01)*quarantine*(Q.n < 20),
    release     = Q >> R @ ss.constant(ss.days(30)),
    waning      = R >> S @ ss.perday(0.01),
    loss        = ss.Transition(M, S, rate=stay('health', 'M', adult_age, 0.04)),
    deaths      = (S | R) >> ss.null @ ss.perday(0.002),
    sick_deaths = (I | Q) >> ss.null @ ss.perday(0.004),
    M_deaths    = ss.Transition(M, ss.null, rate=stay('health', 'M', adult_age, 0.002, after=False)),
    E_deaths    = ss.Transition(E, ss.null, rate=stay('health', 'E', 10, 0.004, after=False)),
    init        = dict(I=10),
)

NG, G = ss.states('NG G')
abortion = -np.log((1 - 0.2)**(1/240)) # Per day, for infectious mothers only: a 20% chance over a gestation
life = Life(
    # Workaround: where=growth.A (and where=health.I) raise a TypeError
    conception = ss.Transition(NG, G, rate=stay('life', 'NG', 90, 0.05), where=lambda sim: sim.diseases.growth.A),
    farrowing  = G >> NG @ ss.constant(ss.days(240)),
    abortion   = ss.Transition(G, NG, rate=ss.perday(abortion), where=lambda sim: sim.diseases.health.I),
)
sim = ss.Sim([growth, life, health], people=ppl, unit='day', dt=dt, start='2021-01-01', stop=ss.days(735), use_aging=True, solver='abm')

if __name__ == '__main__':
    sim.run()
    sim.plot()
