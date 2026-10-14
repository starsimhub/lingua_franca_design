"""
The LASER England and Wales measles model (examples/laser/england_wales), in Starsim: measles in
towns and cities (here the 53 within 100 km of Norwich), with births, deaths from a life table,
seasonal transmission, importations, and the force of infection moving between places by gravity
"""
import os
import sys
import numpy as np
import starsim as ss

folder = os.environ.get('LASER_DATA', os.path.join(os.path.dirname(__file__), '..', '..', '..', '_envs', 'laser', 'src', 'laser-generic-1.1.0', 'data'))
sys.path.insert(0, folder)
from EnglandWalesMeasles import data as engwal

# The run is scaled down in the same way in the original's reference: the places within 100 km of Norwich, for 10 years
center, radius, years = 'Norwich', 100, 10
distances = np.load(os.path.join(folder, 'EnglandWalesDistances.npy'))
keep = distances[engwal.placenames.index(center)] <= radius
distances = distances[np.ix_(keep, keep)]
names = np.array(engwal.placenames)[keep]
pop = np.array([engwal.places[name].population[0] for name in names], dtype=float)
mean_pop = np.array([place.population.mean() for place in engwal.places.values()]) # The birth rate is the mean over all places
cbr = 1000*np.sum(mean_pop*[np.mean(place.births/place.population) for place in engwal.places.values()])/mean_pop.sum()

# Seasonality: 26 values of log beta, each held for 14 days of a 365-day year
log_betas = np.array([0.155, 0.571, 0.46, 0.34, 0.30, 0.34, 0.24, 0.15, 0.31, 0.40, 0.323, 0.238, 0.202, 0.203, 0.074,
                      -0.095, -0.218, -0.031, 0.433, 0.531, 0.479, 0.397, 0.444, 0.411, 0.291, 0.509])
season = np.exp(log_betas - np.append(np.repeat(log_betas, 14), log_betas[-1]).mean())**1.310744
beta = ss.timeseries({14*i: ss.perday(3.865332*s) for i,s in enumerate(season)}, period=ss.days(365))

# Deaths: the age pyramid is the stable one for the birth rate, and the age at death is drawn from it
r = 365*((1 + cbr/1000)**(1/365) - 1)
pyramid = np.exp(-r*np.arange(89))
cum = np.append(0, pyramid.cumsum()) # Deaths before each year of age

def lifespan(sim):
    """ Workaround for LASER's estimator: each person's age at death is drawn once (at the start, or at birth), given their age """
    ppl = sim.people
    uids = ppl.auids[np.isnan(ppl.ti_dead[ppl.auids])]
    age = ppl.age[uids]
    year = np.floor(age).astype(int)
    died = np.searchsorted(cum, cum[year] + np.random.rand(len(uids))*(cum[-1] - cum[year]), side='right') - 1 # The year of age at death
    start = np.where(died > year, 0, age - year)
    ppl.ti_dead[uids] = sim.ti + np.round((died + start + np.random.rand(len(uids))*(1 - start) - age)*365)

def importation(sim):
    """ Workaround: three people, chosen at random from all the susceptible, become infectious every 30 days for 10 years """
    ti, m = sim.ti, sim.diseases.measles
    if 0 < ti < 10*365 and ti % 30 == 0:
        uids = ss.uids(np.random.choice(m.S.uids, 3, replace=False))
        m.S[uids] = False
        m.I[uids] = True
        m.ti_I[uids] = ti + 2 # From the next step, for ~8 days rather than the others' 7, as in the original

S, E, I, R = ss.states(4)
measles = ss.Disease(
    infection = ss.transmission('S -> E', beta=beta, source='I'),
    onset     = ss.progression('E -> I', dur=ss.erlang(k=40, mean=ss.days(10))),
    recovery  = ss.progression('I -> R', dur=ss.normal(7, 2, unit='days')), # 8 in the original, which loses a day, see README
    births    = ss.birth('-> S', rate=ss.peryear(r)),
    init      = dict(I=ss.by(patch=[3]*len(pop)), R=0.95),
    importation = importation,
    lifespan    = lifespan,
)
towns = ss.geo(names=names, pop=pop, distances=distances)
with np.errstate(divide='ignore'):
    gravity = pop**0.251464/distances**1.563193 # LASER's gravity model, with a=0
np.fill_diagonal(gravity, 0)
gravity *= 0.044565/gravity.sum(axis=1).mean() # Workaround: scaled so that the mean share exported is 0.0446,
gravity *= np.minimum(1, 0.2/gravity.sum(axis=1))[:, None] # and no place exports more than 0.2
measles.stratify(patch=towns, mobility=ss.Mobility(matrix=gravity, kind='force'))
sim = ss.Sim(measles, people=ss.People(int(pop.sum()), age_data=np.array([np.arange(89), pyramid]).T), unit='day', stop=years*365)

if __name__ == '__main__':
    sim.run()
    sim.plot()
