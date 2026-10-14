# Atomica SIR demo, in Starsim

The translation of [examples/atomica/sir](../../../examples/atomica/sir). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 62 | 17 | The original is counted as rows of its two spreadsheets, plus three lines of Python |
| One run | 0.0024 s | 0.026 s | The original does not count reading the spreadsheets (about 0.1 s) |
| Results | | | Every compartment identical, to rounding error |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared. The force of infection is an ordinary expression of counts and parameters, not a function.

## Findings

- **The step is part of the model.** Atomica takes one forward Euler step a year. Matching it needs `integrator='euler', substeps=1`; with Starsim's default integrator there are 18 infected at the end, not 11.
- **A constant inside the force of infection.** The original multiplies it by one minus the death rate. A typed rate (`ss.peryear(0.008)`) cannot be subtracted from 1 in an expression, so the number is written again.
- **Initial conditions as given.** The databook gives the susceptible number, the total, and the prevalence, and Atomica solves for the rest; here the solved values are written in.
- **The data is not in a spreadsheet.** The original's point is that the structure and the data live in spreadsheets a non-programmer can edit. This version is code, and does not test that.
