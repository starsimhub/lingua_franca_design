# flepiMoP two populations, in Starsim

The translation of [examples/flepimop/seir_2pop](../../../examples/flepimop/seir_2pop). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 42, plus 10 lines of CSV | 15 | One Starsim line is over 100 characters, so counts twice |
| One run | 8.4 s | 0.040 s, or 0.0008 s for a repeated run | The original is timed as a whole command, about 7 s of which is compiling, on every run |
| Results | | | Every compartment in both provinces within 0.05 people |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared. The populations and the travel between them are written in the script; the original keeps them in three CSV files.

## Findings

- **A third way of coupling places.** In flepiMoP, people who travel are exposed to the residents of the place they go to, and do not infect anyone there. Starsim's commuting has them do both, which brought the epidemic to the small province 12 days sooner. `ss.Mobility(kind='visit')` is new, and matches the original exactly.
- **Half a day is hard-coded.** flepiMoP multiplies the travel matrix by 0.5; here that is written out.
- **The step does not matter here.** The original takes one RK4 step a day and Starsim subdivides the day when rates are high; at these rates they agree to 12 digits.
