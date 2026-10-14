# flepiMoP vaccination scenarios, in Starsim

The translation of [examples/flepimop/vaccine_scenarios](../../../examples/flepimop/vaccine_scenarios), flepiMoP's wave 3 model. The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 141, plus 10 lines of CSV | 36 | One Starsim line is over 100 characters, so counts twice; 8 lines are workarounds (the truncated normal and the draws for each run). Was 38 before the fixes below |
| 30 runs (3 scenarios of 10) | 96 s | 6.5 s | Both in one process. The original is timed as a whole command, once; after its first run each takes 2.6 s. Each Starsim run takes 0.22 s, of which 0.16 s is building it and 0.02 s running it (it was 0.26 s, 0.10 s of it running, before finding 6 was fixed): see finding 6 |
| Results, with the original's draws | | | **Agree exactly, by province.** Run with the values of `Ro` and of the share of cases detected that the original drew, the mean, 5%, and 95% of all 28 series in each province (5 compartments, 5 incidences, and the 4 outcomes, including the number in hospital) agree within 1e-9 of their largest value in all three scenarios |
| Results, with Starsim's own draws | | | **Agree in distribution.** With 100 runs of each scenario, the mean peak of `I` in the large province is 1,107, 472, and 17 (original, from 10 runs: 1,064, 495, and 16), and the mean deaths are 89.1, 60.2, and 2.2 (88.4, 61.1, and 2.1) |

Measured on 14 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Declared: the five states and five transitions (the vaccination and waning rates as sums of two named parameters), the four outcomes by province (one chained from another, and the stay in hospital as a fixed duration), the stratification by province with visiting, the three scenarios as `ss.modify` with a start and a stop, stacked by putting them in a list, and the uncertainty in `Ro` and the share of cases detected, as `prior=` on `ss.par`.

Not declared, and marked as workarounds in `model.py`:

- **Drawing the parameters for each run.** A prior is used only by calibration, so `draws()` draws ten values from each prior by hand, and `runs()` makes a sim for each scenario and draw with `sim.new(pars=...)`.
- **The truncated normal** is SciPy's, since Starsim has none.

## Findings

Findings 3 and 4 blocked agreement; the others are awkwardness. Findings 3 to 8 have been fixed in Starsim since this vignette was first written, and the vignette now uses the fixes; 1 and 2 are still workarounds.

1. **No parameter uncertainty in forward runs.** flepiMoP draws `Ro` (and an outcome's probability) from a distribution once for each run. The spec has two meanings for a distribution: a value that varies between agents, and a prior used only by calibration (04, "A distribution as a value, a distribution as a prior"); it has nothing for a value drawn once for each run. Suggested change: `ss.parallel(sim, n_runs=10, priors=True)` (or `sim.run(n_runs=10, priors=True)`) draws every `ss.par` that has a `prior=` once for each run, from that run's seed, records the values with the run (e.g. `msim.pars`, a table of runs by parameter), and uses `sim.restart(pars=...)` where the sim allows. This would remove `draws()` and `runs()` (6 lines) and make the 30 runs one call.
2. **No truncated normal.** Starsim has `ss.normal` but nothing bounded, and flepiMoP's `truncnorm` is its usual way of writing an uncertain parameter. Suggested change: `ss.truncnorm(mean, std, low, high)`, or `bounds=` on `ss.normal`.
3. **Outcomes are not kept by group** (blocks agreement by province). In a stratified model, every state and transition is a result with a dimension for each stratification, but outcomes are totals: `res.cases.select(patch='a')` raises `ValueError: The result "cases" is not stratified, so there is nothing to select`. The spec says that after stratifying, a result is "still one result, now with a dimension for each stratification" (09, "Selecting strata"), and does not except outcomes. flepiMoP gives every outcome by province, so at first only the totals over the two provinces could be compared. Suggested change: in `Compartmental.step_outcomes()` (`solvers.py`), keep `pending` and `n` for each group, computed from the flows by group (`flow_groups`) rather than `flowcounts`, and fill `res[name].strata` as for flows. Repro:

    ```python
    S, I, R = ss.states(3)
    infection = S >> I @ 0.3*I
    sir = ss.Disease(infection, I >> R @ 0.1, ss.outcome(0.5*infection, name='cases'), init=dict(I=ss.by(patch=[5, 0])), name='sir')
    sir.stratify(patch=['a', 'b'])
    ss.Sim(sir, total_pop=1000, unit='day', stop=50).run().results.sir.cases.select(patch='a') # ValueError
    ```

    **Fixed:** outcomes are now stratified, with their delays, durations, and reporting periods kept by group (in the kernels, in Python, and as agents). Every outcome now agrees by province.

4. **A fixed `duration=` on an outcome is exponential** (blocked agreement of `currHosp` until worked around). `delay=ss.days(7)` shifts by exactly seven days, but `duration=ss.days(10)` makes people leave at a rate of 1/10 a day, which put the peak in hospital 4 days later and up to 15% off. flepiMoP's duration is exactly 10 days. A distribution is not accepted either: `duration=ss.constant(10, unit='days')` raises `TypeError: unsupported operand type(s) for /: 'float' and 'constant'` from `init_outcomes()`. The spec says only that `duration=` gives the number currently in the outcome (09). Suggested change: treat `duration=` as `delay=` is treated: a fixed value is a stay of exactly that long, a distribution gives a kernel of the share still in after each number of steps, and `n_<name>` is the admissions convolved with it (an exponential stay is then `duration=ss.expon(...)`). The workaround was `discharges = ss.outcome(hosp, delay=ss.days(10))` and `np.cumsum(hosp - discharges)`, which matched to 1e-9. **Fixed:** `duration=` now takes a distribution, and `duration=ss.constant(10, unit='days')` is a fixed stay, which agrees to 1e-9 by province, so the workaround is gone. A plain `duration=ss.days(10)` is still an exponential stay, unlike `delay=ss.days(10)`; whether it should be fixed too is still open.
5. **Is `stop=` the last day or the first day after?** flepiMoP's `period_end_date` is the last day a modifier applies. Starsim's `stop=` is the first day it does not, so `stop='2020-08-31'` let vaccination run on the last day of `no_vax`: no one was in `V` at the start of any day, but 37 people flowed into it on 31 August (in the first run). The spec (07) says only "the period it applies in". Here `stop='2020-09-01'` matches. Suggested change: say in the spec and the docstring that the period is `[start, stop)`, and perhaps accept `end=` for an inclusive last day, since dates in data and in other frameworks usually are inclusive. **Fixed:** `stop=` is now documented as exclusive (`[start, stop)`); the vignette keeps `stop='2020-09-01'`.
6. **Modifiers make runs 25 times slower.** With the four `ss.modify`, a run is stepped from Python and takes 0.26 s (0.15 s to build and 0.10 s to run); the same scenarios written as `pars=dict(nu_opt=0, ...)` take 0.05 s (3 ms to run, in one call to the kernel), and 2.5 ms each with `sim.restart(pars=...)`. A modifier that applies for the whole run is just a parameter value, and one with a start and a stop is a time series, both of which the kernel already handles. Suggested change: when a modifier on a parameter has a constant amount and no `where=` or `when=`, tabulate it into the parameter's values over time when the sim is built, so that `kernel_only()` stays true (this is the open item "A whole run in the kernel with modifiers" in the implementation plan). **Fixed:** a modifier that depends only on time is now tabulated before the run, so the sim stays in one call to the kernel (`sim.kernel_only()` is true) and a run takes 0.02 s, from 0.10. **Still slow:** building is three times slower with four modifiers (0.16 s against 0.05 s with `pars=`). A profile shows most of it in `sc.search` over the sim (from `link_timepars()` in each modifier's `init_pre()`, and in `Dists.init()`), which each modifier adds to; finding the time parameters and distributions once for the sim, not once for each module, would remove most of it.
7. **Four modifiers called `modify`.** Without `name=`, each `ss.modify` after the first gives `RuntimeWarning: Module name "modify" is already used, so renaming this module "modify_1"`. Since the target is known, the default name could be `<target>_<op>` (e.g. `nu_opt_multiply`), as the vignette wrote by hand. **Fixed:** they are now named that way (`nu_opt_multiply`), and the vignette no longer names them.
8. **`describe()` calls `Ro` a rate.** In `infection = S >> E @ Ro*gamma*I`, `describe()` shows `Ro = 2.5 per day`, although it is the product `Ro*gamma` that is a rate and `Ro` has no unit. The type of a parameter comes from its slot (04), and here the slot holds a product; only the whole product should be typed. **Fixed:** `describe()` now shows `Ro = 2.5`.
