# epydemix SIR in Kenya, in Starsim

The translation of [examples/epydemix/sir_kenya](../../../examples/epydemix/sir_kenya). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 7 | 10 | Not counting the lines that load the data, in either |
| One stochastic run | 0.006 s | 0.035 s, or 0.0008 s for a repeated run | In process, without imports or loading the data. 100 runs take 0.56 s in the original and 0.07 s as `sim.run(n_runs=100)` |
| Results | | | The mean of 100 runs: peaks within 0.3%, a day apart at most; final size the same (99.63%) |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared. The population and the contact matrices are read from the file that the original's run wrote.

## Findings

- **Longer than the original.** epydemix has the SIR model predefined and the population bundled, so the whole example is seven lines. Starsim has neither: `ss.contacts('Kenya')` raises `E605`, and the population sizes and matrices have to be supplied.
- **A result of many runs cannot be selected by age group.** `msim.results.sir.n_I.select(age='0-4')` fails, so the comparison does it run by run.
- **Aging had no switch.** Stratifying by age turns aging on in a compartmental run; `use_aging=False` now turns it off, which is what the original assumes.
- **Ten infected, not eight.** The original spreads ten infections over the age groups and rounds each down, starting with eight. Starsim starts with ten, which accounts for the peak arriving up to a day sooner.
