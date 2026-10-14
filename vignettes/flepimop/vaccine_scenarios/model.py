"""
The flepiMoP vaccination scenarios (examples/flepimop/vaccine_scenarios), in Starsim: the SEIR in two
provinces with vaccination and waning, three scenarios that switch parts of it off, reported cases,
hospitalizations, and deaths, and ten runs of each with uncertain R0 and case detection
"""
import scipy.stats as sps
import starsim as ss

pop     = dict(large_province=9000, small_province=1000)
commute = [[0, 100/9000], [20/1000, 0]] # The share of each province's residents who go to the other
gamma   = 1/5

def truncnorm(mean, sd, a, b): # Workaround: Starsim has no truncated normal, so SciPy's
    return sps.truncnorm((a - mean)/sd, (b - mean)/sd, loc=mean, scale=sd)

Ro         = ss.par(2.5, prior=truncnorm(2.5, 0.1, 1.1, 3))
p_case     = ss.par(0.5, prior=truncnorm(0.5, 0.05, 0.3, 0.7))
nu_pess    = ss.par(0.01)
nu_opt     = ss.par(0.03)
omega_pess = ss.par(0.02)
omega_opt  = ss.par(0.01)

S, E, I, R, V = ss.states(5)
infection   = S >> E @ Ro*gamma*I
onset       = E >> I @ 1/4
recovery    = I >> R @ gamma
vaccination = S >> V @ nu_pess + nu_opt
waning      = V >> S @ omega_pess + omega_opt
cases       = ss.outcome(p_case*onset, delay=ss.days(5))
hosp        = ss.outcome(0.05*onset, delay=ss.days(7), duration=ss.constant(10, unit='days'))
deaths      = ss.outcome(0.2*hosp, delay=ss.days(14))
transitions = [infection, onset, recovery, vaccination, waning]
seir = ss.Disease(*transitions, cases, hosp, deaths, init=dict(E=ss.by(patch=[5, 0])))
away = [[0.5*share for share in row] for row in commute] # Travelers are away for half the day
seir.stratify(patch=list(pop), split=list(pop.values()), mobility=ss.Mobility(matrix=away, kind='visit'))
sim = ss.Sim(seir, total_pop=sum(pop.values()), start='2020-02-01', stop='2020-08-31')

# The scenarios: each switches off one vaccination program or both (Starsim's stop is the first day off)
off = lambda par: ss.modify(par, multiply=0, start='2020-02-01', stop='2020-09-01')
pess_vax  = [off(nu_opt), off(omega_opt)]
opt_vax   = [off(nu_pess), off(omega_pess)]
scenarios = dict(no_vax=pess_vax + opt_vax, pess_vax=pess_vax, opt_vax=opt_vax)


def draws(n_runs=10, seed=1):
    """ Workaround: the values for each run, drawn from the priors by hand """
    rvs = lambda par, offset: par.prior.rvs(n_runs, random_state=seed + offset)
    return [dict(Ro=r0, p_case=p) for r0,p in zip(rvs(Ro, 0), rvs(p_case, 1))]


def runs(draws=draws(), **kwargs):
    """ Every scenario, once with each draw """
    return [sim.new(label=name, pars=pars, interventions=mods, **kwargs)
            for name,mods in scenarios.items() for pars in draws]


if __name__ == '__main__':
    msim = ss.parallel(runs(), parallel=False)
    msim.plot()
