# MEmilio age-resolved SECIR, in Starsim

The translation of [examples/memilio/secir_ageres](../../../examples/memilio/secir_ageres), MEmilio's wave 3 example. The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 45 | 21 | 18 lines, three of them over 100 characters, so counted twice |
| One run | 0.47 s | 0.086 s, or 0.2 ms restarted | The original is timed as a whole command; its `simulate()` call alone takes 0.1 ms. Starsim's time is nearly all building the sim; the run is one kernel call, and `sim.restart()` works |
| Results | | | **Agree.** Within 1.5 people of 10,000 at every time (1.3 in `Susceptible`, 1.5 in `Recovered`), the same with a step of a day or a tenth of a day, which is the error of the reference itself (it is interpolated between solver steps); deaths within 0.02 |

Measured on 14 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared: the seven states and seven transitions (as in [the wave 1 vignette](../secir)), the three age groups and their contact matrix, the initial counts (split evenly between the groups), seasonality as an `ss.seasonal`, the cut in contacts as an `ss.timeseries` with `mode='cosine'`, and the rise in the risk of infection from symptomatic people as testing and tracing is overwhelmed, as an expression of the count in `INS` (`np.clip` and `np.cos` of `INS.n`) used as the weight of `ISy`.

Left out, as having no effect here: the two confirmed states (nothing flows into them), the ICU capacity (unlimited), and `DeathsPerSevere` (0). The dead leave the model, as in the wave 1 vignette.

## Findings

1. **A value that varies in time was held for a whole step** (blocked exact agreement; fixed). The ODE read `ss.seasonal` and `ss.timeseries` once at the start of each step, while MEmilio evaluates them at every stage of its solver, which gave differences of 9 people at a step of a day (against the original's equations with those values held for each day, Starsim agreed to 0.015 people). Fixed in Starsim: the ODE now reads smoothly varying values at each RK4 stage, and the results no longer depend on the step.
2. **A rate could not clip or smooth a count** (was awkward and slow; fixed). The risk is 0.25 below a threshold of the count in `INS`, 0.45 above five times it, and half a cosine between. This was a Python function of the sim, so the run was stepped from Python (0.15 s), `sim.restart()` refused (saying the sim was not "nothing but compartments", though it was), and `describe()` showed only `risk`. Fixed in Starsim: rates now accept NumPy functions and comparisons on count expressions (`np.clip`, `np.cos`) and compile them into the kernels, so the risk is two declared lines, a run is one kernel call (0.086 s, nearly all building), `sim.restart()` works (0.2 ms), and `describe()` prints the whole formula.
3. **A state's count cannot be read inside a function through the state itself** (awkward; no longer needed here, but still open). In a function of the sim, a declared state's `INS.n` is a symbolic expression, not a number, so `np.clip(INS.n, 0, 1)` inside a function raises `TypeError: '>=' not supported between instances of 'BinOp' and 'int'`; the function has to use `sim.diseases.secir.INS.n`. The smallest fix: when a function is called at run time, let the declared states it closes over evaluate to their current counts, or give the error a hint pointing to `sim.diseases.<name>.<state>.n`.
4. **The threshold is on a flow, which has to be written again as a count** (awkward; open). MEmilio's quantity to trace is the number becoming symptomatic each day, the flow of `symptoms` to `ISy`. Starsim has no way to name a transition's current flow in a rate, so the expression writes it as `0.91/2*INS.n`, repeating the probability and the time from `symptoms`. A `symptoms.flow` that can be used in an expression would remove the repetition.
5. **A change in contacts smoothed over a day** (was awkward; fixed). MEmilio smooths every damping over the day before it, along half a cosine; the translation gave day 29 its average (0.65). Fixed in Starsim: `ss.timeseries` has `mode='cosine'`, so the cut is written as MEmilio's damping, `ss.timeseries({0: 1.0, 29: 1.0, 30: 0.3}, mode='cosine')`.
6. **`describe()` said homogeneous mixing when there is a contact matrix** (minor; fixed). It now says the exposure is through the contact matrices.
7. **Seasonality relative to a start day** (fine, but obscure). MEmilio places day 0 at `StartDay = 60` of a 365-day year; with no dates, `ss.seasonal` starts at the beginning of a year, so the peak on day 0 of the year is written `peak=-60/365`. It matches exactly. Giving the sim a start date (2 March) and `peak=0` should say the same more clearly; that was not tried.
8. **Age groups as labels** (worked). The groups are named `'0'`, `'1'`, and `'2'`, as MEmilio numbers them; Starsim treats them as labels, not ages, and does not age anyone.
