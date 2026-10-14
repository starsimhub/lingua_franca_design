"""
An age- and patch-structured SEIR: free indices make families of transitions,
cm.sum() binds an index, and a.next walks along a dimension.
"""

import matplotlib.pyplot as plt
import pycamdl as cm

m = cm.Model(time_unit='days')

age, patch = m.dimensions(age=['child', 'adult', 'elder'], patch=['north', 'south'])
S, E, I, R = m.compartments('S', 'E', 'I', 'R')
m.stratify(age)
m.stratify(patch)

beta, gamma, move = m.parameters(
    beta  = cm.rate(0.04),
    gamma = cm.rate(0.1),
    move  = cm.rate(0.01, doc='rate of moving between patches'),
)
contacts, pop, stay = m.tables(
    contacts = cm.table([[12, 4, 1], [4, 8, 2], [1, 2, 3]], age, age),
    pop      = cm.table([[3000, 1000], [5000, 2000], [2000, 500]], age, patch),
    stay     = cm.table([5, 45, 30], age, unit='years'),  # Time spent in each age band
)

a, b = age.indices('a', 'b')
p, q = patch.indices('p', 'q')
N = cm.let(S[a, p] + E[a, p] + I[a, p] + R[a, p], a, p)   # A family: N[b, p] is the total for age b in patch p
foi = cm.let(beta * cm.sum(contacts[a, b] * I[b, p] / N[b, p], b), a, p)

m.transitions(
    infection = S[a, p] >> E[a, p] @ foi[a, p] * S[a, p],
    onset     = E[a, p] >> I[a, p] @ E[a, p] / cm.days(5),
    recovery  = I[a, p] >> R[a, p] @ gamma * I[a, p],
)
for c in [S, E, I, R]: # Everyone ages and moves, whatever their infection state
    m.transitions({
        f'aging_{c.name}': c[a, p] >> c[a.next, p] @ c[a, p] / stay[a],
        f'move_{c.name}':  (c[a, p] >> c[a, q] @ move * c[a, p]).where(p != q),
    })

m.interventions(
    vaccinate = cm.transfer(S['child', p] >> R['child', p], fraction=0.6, at=[cm.days(20)]),
)
m.init({S[a, p]: pop[a, p], I['child', 'north']: 10})
m.simulate(stop=cm.days(150))


if __name__ == '__main__':
    m.summary()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    cells = ['I_child_north', 'I_child_south', 'I_adult_north', 'I_adult_south']
    m.run(n=20, seed=1).plot(cells, ax=axes[0])
    m.run(n=20, seed=1, enable=['vaccinate']).plot(cells, ax=axes[1])
    axes[0].set_title('No vaccination')
    axes[1].set_title('Children vaccinated on day 20')
    plt.show()
