# summer2 mixing matrices, in Starsim

The translation of [examples/summer2/sir-age-location](../../../examples/summer2/sir-age-location). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 35 | 12 | One Starsim line is over 100 characters, so counts twice |
| One ODE run | 0.0003 s | 0.038 s, or 0.0008 s for a repeated run | The original takes 1.4 s the first time, to build and compile; after that it is about 2.5 times faster than a repeated Starsim run (it was 280 times) |
| Results, ODE | | | Every compartment within 0.08 people of 1,000 |
| Results, other solvers | | | The stochastic and agent-based runs give the same number recovered, to within 1% (mean of 100 runs) |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared: three transitions, two stratifications, one adjustment, and the mixing.

## Findings

- **Contact matrices were for ages only.** `ss.contacts` took one matrix with its own age groups. It now also takes a matrix for each of the model's dimensions (`ss.contacts(age=..., location=...)`), multiplied together as summer2 does.
- **Age groups as labels broke an agent-based run.** `age=['young', 'old']` clashed with the age every agent already has. A labeled age dimension is now kept apart from it, and nobody ages between its groups.
- **No unit of time.** The original names none, and neither version needs one: both run in steps of 0.1.
- **Slower after the first run.** summer2 compiles each model with JAX. Starsim now flattens the model into arrays that one Numba kernel runs, which needs no compiling for each model and is about 2.5 times slower per run.
