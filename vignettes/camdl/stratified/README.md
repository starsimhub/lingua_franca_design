# camdl SEIR by age and patch, in Starsim

The translation of [examples/camdl/stratified](../../../examples/camdl/stratified), the first model of wave 3. The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 35 | 15 | Three lines are over 100 characters, so count twice |
| One ODE run | 0.10 s | 0.023 s | Both in Python, with the import excluded; the original's time excludes building the model and Starsim's includes it |
| Results, ODE | | | **Agree.** The infectious in every cell within 0.24%, with and without vaccination |
| Results, stochastic | | | **Agree in size, not quite in timing.** Peaks agree (970 against 969 adults in the south), but with a step of a day the south's epidemic rises about a day sooner (586 infectious adults on day 39, against 521). With a quarter-day step both move, and the gap shrinks from 65 to 17, so it is the difference between the two chain-binomial schemes at a coarse step |

Measured on 14 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared: three transitions, two stratifications, the population by age and patch, a contact matrix, movement, and the vaccination as a delivery.

## Findings

- **Aging was off.** An age stratification is meant to make people age between its groups, but `use_aging` was set to off (because there were no births or deaths) before the stratification could turn it on, so no compartmental model aged. Fixed: an age stratification turns aging on unless the sim says otherwise. Children had 2% too many infections before the fix.
- **No contact matrix within places.** A contact matrix by age in a model with places raised `E804`. It now acts within each place, with commuting, visiting, or a moving force of infection applied to each age group, under every compartmental solver. As agents, a contact matrix still mixes people across places.
- **No population by two dimensions.** The original gives a population for each age group in each patch, which is not the product of a split by age and a split by patch. `split=` now takes an `ss.by` over several dimensions, and `ss.by` now has the forms the spec gives it (a product over several dimensions, or a table), plus an array with named axes (`ss.by([[3000, 1000], ...], dims=['age', 'patch'])`), which is how the original writes it. As agents, people's patch is drawn given their age.
- **The sum of two stratified results was wrong by group.** `(n_S + n_I).select(patch='north')` gave `n_S` alone. Arithmetic now keeps the values by group only when it can (sums, differences, and scaling by a number), and otherwise `select()` says the result is not stratified.
- **A condition on age needed a people object** (fixed). `where=(ss.People.age < 5) & seir.S` now works before there is a sim; this version first had to write `ss.People(1).age`.
- **Moving people between states once.** The original moves 60% of susceptible children to `R` on day 20. Here they are given a fully effective vaccine, so they stay in `S` but cannot be infected. The infections are the same, but the counts in `S` and `R` differ.
- **Results of many runs were not kept by group.** `sim.run(n_runs=200)` returned only totals. It now keeps the values of each group (unless they would take more than 500 MB), and `msim.results.seir.n_I.select(age='0-4', patch='north')` works as it does for one run.
