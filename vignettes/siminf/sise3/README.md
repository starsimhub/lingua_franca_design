# SimInf SISe3 in 1,600 herds, in Starsim

The translation of [examples/siminf/sise3](../../../examples/siminf/sise3). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 27 | 30 | 13 of the 30 read the data and turn SimInf's events, all four kinds, into a movement register, which the original gets from the package. The disease itself is 17 |
| One run | 0.10 s | 14 s | Gillespie's method on one thread in both, as compartments (whole animals by herd, with `phi` a real number). The original as one command, starting R and loading the events, takes 1.6 s; building the Starsim sim takes 4 s, most of it reading the events with pandas |
| Results | | | **Agree within a herd and in the demography; the spread between herds is about 25% slower.** Node 1 and every susceptible count agree on every day checked, and 86% to 98% of the runs are inside SimInf's 5% to 95% range for every series on every day. On day 1,457 the mean of 50 runs has 125 ± 12 herds infected (SimInf: 166, range 24 to 352) and 2,835 ± 267 animals (3,770; 519 to 8,138), about three standard errors low counting the error of SimInf's own mean |

Measured on 14 October 2026 with Starsim 4.0.0 (the `v4` branch, with uncommitted changes) on a 20-core x86-64 Linux machine. Earlier versions of this vignette ran as agents (150 s a run), and then as compartments with the aging as a custom intervention (60 lines), before findings 1 to 4 and 6 were fixed.

`compare.py` (50 runs one after another, about 12 minutes) gives, for the mean of the runs (± its standard error) against the mean of SimInf's 200:

| Day | Herds infected | Animals infected | `phi` in node 1 | Infected in node 1 | `S_1` |
|---|---|---|---|---|---|
| 92 | 1.16 ± 0.06 (1.16) | 39 ± 3 (41) | 2.18 ± 0.14 (2.28) | 37 ± 2 (40) | 17,089 (17,088) |
| 183 | 2.1 ± 0.2 (2.3) | 72 ± 3 (75) | 3.81 ± 0.09 (3.90) | 61 ± 1 (63) | 17,822 (17,822) |
| 365 | 3.1 ± 0.3 (3.4) | 85 ± 6 (88) | 2.36 ± 0.05 (2.39) | 45 ± 1 (44) | 12,085 (12,084) |
| 729 | 11.6 ± 1.2 (13.0) | 247 ± 23 (288) | 2.35 ± 0.05 (2.33) | 42 ± 1 (41) | 12,038 (12,036) |
| 1,093 | 40 ± 4 (49) | 876 ± 86 (1,059) | 2.41 ± 0.05 (2.32) | 44 ± 1 (43) | 11,968 (11,959) |
| 1,457 | 125 ± 12 (166) | 2,835 ± 267 (3,770) | 2.38 ± 0.05 (2.33) | 46 ± 1 (45) | 11,870 (11,819) |

With aging in the register, in SimInf's order (exits, entries, aging, then movements between herds), the susceptible counts now agree to within one or two animals in the calving season, where the custom intervention was off by 80. The herd and animal totals came only slightly closer (125 herds, from 119), so the ordering was not the cause of the slower spread, which is not yet explained: every quantity within a herd agrees, so it is in how infected animals get to new herds or how often they start an outbreak there.

## What was declared and what was not

Everything is declared. The six compartments are states, and the infectious pressure `phi` is a state that is not people, stratified by herd with the people, so that each herd has its own `phi`. Infection is a spontaneous transition at rate `upsilon * phi.n` (the herd's own `phi`), and recovery goes back to `S_k`. Shedding into `phi` is an inflow at rate `alpha * I.n / N.n`, and its decay an outflow at a seasonal rate, an `ss.timeseries` that repeats each year. The initial conditions are by herd (`ss.by`). All 783,773 events are one movement register: births have no `from`, deaths no `to`, movements a `from` and a `to`, and aging the same herd as `from` and `to` with `to_states` (`states='S_1,I_1'`, `to_states='S_2,I_2'`); `states` names the age category the animals are chosen from.

## Findings

1. **Fixed: a state that is not people was a whole number under the stochastic compartmental solvers.** Under Gillespie, `phi` was shed and decayed one unit at a time, so with values of 0 to 5 the infection died out, and only agents (150 s a run) could run the model. Starsim now keeps such a state real-valued under `gillespie`, `tau`, and `binomial`, with its flows as expected values, while the people are drawn, as SimInf does; Gillespie also now runs each place on its own between events when places do not affect each other within a step. This vignette now runs as compartments in 14 s.

    **1b. Fixed: Gillespie advanced `phi` with the bias of finding 2.** After the change that runs each place on its own, Gillespie settled the counts once a step, with an exact decay and an Euler inflow, which gave `phi` 4.96 at equilibrium in a one-herd repro where the ODE and SimInf give 4.44 to 4.49, and 20% too much `phi` in node 1 here. The stochastic solvers now integrate the counts over each step (or event interval) by RK4 with the people as they are; the repro gives 0.440 and 4.41 under Gillespie and 0.443 and 4.45 under tau, and node 1 agrees.

2. **Fixed: the agent-based solver advanced a count inconsistently, and a step ahead.** As agents, counts are now advanced by RK4 over each step with the people as they were at its start, and rates use the counts at the start of the step; the repro gives 0.449 and 4.50, with the ODE.

3. **Fixed: as agents, places were not given the populations they were given.** A `split=` is now assigned exactly (rounded to whole agents). It no longer matters here, since the model runs as compartments, where the initial conditions by herd were always exact.

4. **Fixed: a movement register could not move people between states.** SimInf's `intTrans` events, 40% of all the events, age animals from `S_1` to `S_2` and from `I_1` to `I_2`, which needed a 30-line custom intervention that wrote the engine's compartment array, used its own random numbers, and ran after the day's movements. The register now has a `to_states` column (paired in order with `states`, with `from` and `to` the same herd), under every solver, and the events happen in the order of the table, as in SimInf. A first version of it rejected any register where some rows had no `to_states` (blank cells read as `NaN` under pandas 3); that was fixed too.

5. **Still open: age categories as states need `people=True` (awkward).** With the age categories as six states, `S_2` to `I_3` are joined to `S_1` only by aging, which is in the register and not a transition, so without `people=True` they would be guessed to be counts. Making age a stratification instead (`age=['1', '2', '3']`, `use_aging=False`) would be more natural, but the register can name only states, not a level of another dimension. Suggested change: let a register choose and change the level of any dimension (columns named for the dimension, such as `age` and `to_age`), which would let the age categories be a dimension.

6. **Fixed: no yearly cycle for a step function.** The seasonal decay is now one line, `ss.timeseries({0: ss.perday(0.1), 182: ss.perday(0.125)}, period=ss.years(1))`.

7. **Speed.** 14 s a run, against 0.10 s for SimInf: from 150 s as agents. Building the sim takes another 4 s.

8. **Open: the spread between herds is about 25% slower than in SimInf** (125 ± 12 herds infected on day 1,457 against 166), though everything within a herd agrees. Not yet explained; it may be in how an animal that is moved carries its infection, or in how often one infected animal starts an outbreak in a clean herd, where `phi` starts at zero.
