"""
The epydemix tutorial on population data (examples/epydemix/sir_kenya), in Starsim: an SIR in
Kenya's population, with contact matrices between five age groups
"""
import os
import numpy as np
import sciris as sc
import starsim as ss

# Starsim has no bundled population data, so this reads what epydemix downloaded
here = os.path.dirname(os.path.abspath(__file__))
data = sc.loadjson(os.path.join(here, '..', '..', '..', 'examples', 'epydemix', 'sir_kenya', 'reference', 'population.json'))
matrix = sum(np.array(layer) for layer in data['contacts'].values()) # School, work, home, and community

sir = ss.Disease(
    infection = ss.transmission('S -> I', beta=0.04),
    recovery  = ss.progression('I -> R', rate=0.1),
    init      = dict(I=10),
)
sir.stratify(age=[0, 5, 20, 50, 65], split=data['Nk'])
sim = ss.Sim(sir, networks=ss.contacts(age=matrix), total_pop=sum(data['Nk']), start='2019-12-01', stop='2020-04-01', solver='binomial', use_aging=False)

if __name__ == '__main__':
    msim = sim.run(n_runs=100)
    msim.plot()
