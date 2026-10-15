# MEmilio SECIR, in Starsim

The translation of [examples/memilio/secir](../../../examples/memilio/secir). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 44 | 14 | |
| One run | 0.63 s | 0.06 s, or 0.001 s for a repeated run | The original is timed as a whole command; its `simulate()` call alone takes 0.08 ms. |
| Results | | | Within 73 people of 83,000 at every time, which is the error of the reference itself (it is interpolated between steps of about two days); deaths within 0.5 |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared. Each severity step is one transition with two destinations and a probability; deaths leave the model, so they are counted from the flow and the people who mix are the ones alive, as in the original.

## Findings

- **A value that varies in time is held for a whole step.** The original lowers contacts smoothly over day 29. A linear `ss.timeseries` between days 29 and 30 is read once at the start of each step, so it would stay at 1 for the whole of day 29; the translation gives that day its average (0.55) to match. The ODE solver should read time-varying values at the times it evaluates the rates.
- **Two states left out.** The original has two "confirmed" states that nothing flows into; they are not in the translation.
- **The dead are a flow, not a state.** `n_Dead` is `cum_death`.
