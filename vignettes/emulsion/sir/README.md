# EMULSION SIR, in Starsim

The translation of [examples/emulsion/sir](../../../examples/emulsion/sir). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 81 (compartments), 86 (individuals) | 8 | The original is one YAML file per paradigm; here one model is run two ways |
| One compartmental run | 0.81 s | 0.017 s | The original is timed as a whole command, which is mostly startup; it reports 0.06 s for the run itself |
| Results, compartments | | | Mean of 200 runs: peak of 37 infectious on day 18, against 37 on day 18; 85 recovered at the end, against 85 |
| Results, individuals | | | **Lower.** 77 recovered at the end, against 81, because more runs die out early (22%, against about 19%) |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared, once. The paradigm is the `solver=` argument of the sim, where the original changes `aggregation_type` and adds a level and prototypes to the file.

## Findings

- **Initial numbers were random for agents.** `init=dict(I=1)` gave each agent a 1% chance of starting infected, so over a third of runs started with nobody infected. The number in each state at the start is now exact, as it is in a compartmental run.
- **Agents die out a little too often.** An agent's time in a state is rounded to whole steps, so about 5% of infected agents recover before they have had a step in which to infect anyone. In a population of 100 starting from one case, that is enough to see. It is the known issue about half a step of dwell time in `admin/implementation.md`.
- **No hybrid.** The original's third form (groups that hold individuals) has no counterpart, and for this model none is needed: its three forms are statistically the same.
- **The original's files are mostly presentation.** About a quarter of the YAML is names, descriptions, and colors.
