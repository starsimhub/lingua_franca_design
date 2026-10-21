# EpiModel SIS on a dynamic network, in Starsim

The translation of [examples/epimodel/sis-network](../../../examples/epimodel/sis-network). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 13 | 8 | |
| One run | 3.9 s | 0.45 s | The original also takes 0.66 s to estimate the network first |
| Results | | | **Agree, once the order within a step is allowed for**: 11.8 new infections a step at equilibrium, against 12.0, and 115 infected after step 50, against 113 (means of 100 runs each). Over the last 200 steps 237 of 500 are infected, against 227.5: EpiModel lets people recover in the step in which they are infected and counts them after that, which makes its count 5% lower for the same epidemic (237 × 0.95 = 225) |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared: two transitions and a network, described by the same targets as the original (`ssl.DegreeNet(n_contacts=0.7, concurrency=0.22, max_contacts=3, dur=50)`, from the library). Probabilities per step are written as `ss.prob`.

## Findings

- **The network could not be described the way EpiModel describes it.** The original fits a network to target statistics: 175 partnerships, 110 people with two or more partners, nobody with four or more. Starsim's random network took a number of partners per person and a duration, which matched the mean degree but gave about 98 people with two or more partners and up to 7 partners, and 193 infected at equilibrium. `ss.PartnerNet` now takes the same targets. People look for partners at a rate that depends on how many they have, chosen so that the targets are the network's stable state, and partnerships end at a constant rate; nobody has a fixed number of partners, as in EpiModel. It has 173 partnerships and 109 people with two or more (EpiModel's network has 177 and 111). It is not an ERGM: it matches the number of partners people have, and not other structure an ERGM can target, such as mixing by attribute or triangles.
- **No network diagnostics.** The original reports the edges, mean degree, concurrency, and partnership duration of the simulated network over time. `ss.PartnerNet` now records the mean number of partners and the share with two or more as results, and `net.check()` compares them with the targets over a few runs.
- **Durations could not be a distribution.** `ss.RandomNet(dur=ss.expon(...))` was refused, and a fixed duration makes every partnership formed at the start end on the same step. Fixed.
- **A probability with no unit failed.** `ss.prob(0.05)` in a sim that counts time in steps raised an error. It is now a probability per step.
- **A bare number as a network duration is in years.** `dur=50` in this sim, which has no unit, gave partnerships that never ended.
