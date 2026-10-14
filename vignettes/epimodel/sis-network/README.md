# EpiModel SIS on a dynamic network, in Starsim

The translation of [examples/epimodel/sis-network](../../../examples/epimodel/sis-network). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 13 | 8 | |
| One run | 3.9 s | 0.38 s | The original also takes 0.66 s to estimate the network first |
| Results | | | **Do not agree.** About 193 of 500 are infected at equilibrium, against 227; and the epidemic gets there sooner (181 infected at step 50, against 113) |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared: two transitions and a network. Probabilities per step are written as `ss.prob`.

## Findings

- **The network cannot be described the way EpiModel describes it.** The original fits a network to target statistics: 175 partnerships, 110 people with two or more partners, nobody with four or more. Starsim's random network takes a number of partners per person and a duration, so it matches the mean degree (0.73 against 0.71) and the mean duration (53 steps against 50), and not the rest: it has about 98 people with two or more partners, and up to 7 partners. Which of these accounts for the difference in results has not been established.
- **No network diagnostics.** The original reports the edges, mean degree, concurrency, and partnership duration of the simulated network over time. Here they had to be measured by hand to write the line above.
- **Durations could not be a distribution.** `ss.RandomNet(dur=ss.expon(...))` was refused, and a fixed duration makes every partnership formed at the start end on the same step. Fixed.
- **A probability with no unit failed.** `ss.prob(0.05)` in a sim that counts time in steps raised an error. It is now a probability per step.
- **A bare number as a network duration is in years.** `dur=50` in this sim, which has no unit, gave partnerships that never ended.
