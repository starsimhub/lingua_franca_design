# odin stochastic SIR with arrays, in Starsim

The translation of [examples/odin/stochastic_sir_arrays](../../../examples/odin/stochastic_sir_arrays). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 27 | 7 | |
| 100 runs | 0.002 s | about 4 s | The original takes 0.7 s to compile first. One Starsim run takes 0.043 s |
| Results | | | The mean of 2,000 runs is within 4.4 people of 1,001 at every time, against the original's 20,000 |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared. The original writes out the binomial draws and the update of each compartment by hand; here the stochastic solver does the same thing from two transitions.

## Findings

- **Many runs are many sims.** The original's array is 100 independent copies of the epidemic, stepped together in compiled code. Starsim builds and runs a sim for each, which is about 2,000 times slower for this model. Runs as a dimension of one sim would close most of that gap.
- **The arrays are not groups.** This example was chosen as a step up from odin's deterministic SIR, but its arrays hold replicates, not coupled groups, so it exercises nothing about stratification. No odin vignette has a coupled stochastic array model.
