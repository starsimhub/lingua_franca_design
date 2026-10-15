# summer2 derived outputs in a stratified model, in Starsim

The translation of [examples/summer2/seir-age-clinical](../../../examples/summer2/seir-age-clinical). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 134 (55 for the model alone) | 15 | The original builds and runs the model seven times to request its outputs one group at a time; in Starsim every output but one is there without being asked for, by selecting groups of a result (the proportion in hospital is a division in `compare.py`) |
| One ODE run | 0.0008 s | 0.024 s, or 0.0002 s for a run of a sim that is already built | The original takes 3.5 s the first time, to import JAX and build and compile all seven models; after that, Starsim is about 4 times faster |
| Results, ODE | | | Every compartment within 0.0006 people of 1,000; every derived output within 0.005% of its peak. From the same start, the stratified model and the same model written as four states (`as_states()` in `compare.py`) agree to 2e-14 people |
| Results, other solvers | | | The mean of 100 stochastic runs ends with 554 recovered and the agent-based runs with 568, against 580 in the ODE, probably because the epidemic sometimes dies out from its 10 initial cases |

Measured on 14 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

The derived outputs are compared after converting them to summer2's conventions: a flow is divided by the step to give a rate, and is compared with the original's value at the end of the step. The original's cumulative deaths are 10 times the deaths (it sums rates without multiplying by the step; see the example's README), so they are compared with 10 times Starsim's. ## What was declared and what was not

Everything is declared: four transitions and two stratifications, as in the original. Nothing is a function or a `step()`. Every output of the original is a selection of the automatic results; only the proportion in hospital is a division of two of them, in `compare.py`, since a result expression cannot name a level of a dimension, and notifications are not declared as an outcome because a weight by level in an outcome fails (finding 11).

| Original | Starsim |
|---|---|
| `Stratification('age', ...)` | `seir.stratify(age=['young', 'old'], adjust={'incidence': [1, 1.1]})` |
| `Stratification('clinical', ..., ['I'])` | `seir.stratify(clinical=[...], states=['I'], ...)` |
| `incidence` adjusted by clinical status, given age (`source_strata`) | `split=ss.by([[...], [...]], dims=['age', 'clinical'])`, a row for each age, with the old's rows summing to 1.1 given as the `adjust` on age |
| `infection_death` with `Overwrite(0)` and `Multiply(2)` | `adjust={'infection_death': [0, 1, 1, 2]}` |
| `add_infectiousness_adjustments` | `adjust={'rel_trans': [0.5, 1, 0.2, 0.1]}` |
| `set_population_split` (everyone in `I` asymptomatic) | `init=dict(I=ss.by([[5, 0, 0, 0], [5, 0, 0, 0]], dims=['age', 'clinical']))` (finding 9) |
| `request_output_for_flow` by age | Automatic: `res.incidence.select(age='old')` |
| `request_output_for_flow` by clinical status, or both | Automatic: `res.incidence.select(age='old', clinical='hospital')` |
| `request_cumulative_output` | Automatic: `res.cum_infection_death.select(age='old')` |
| `request_aggregate_output` (notifications) | Automatic: `res.incidence.select(clinical=['isolated', 'hospital'])` |
| `request_output_for_compartments` (hospital occupancy) | Automatic: `res.n_I.select(clinical='hospital')` |
| `request_function_output` (proportion in hospital) | `res.n_I.select(clinical='hospital') / res.n_I` in `compare.py` |

An earlier version of this vignette wrote the clinical statuses as four states (`Ia`, `Is`, `Ii`, `Ih`), each entered by its own transition from `E` at a rate `ss.by(age=...)`, because the stratification could not be expressed (finding 1). That version agreed with the original to 0.0006 people in 18 lines; `compare.py` keeps it (`as_states()`) as a check of the stratification.

## Findings

Findings 1 to 7 were made with the first version, 9 with the second, and 10 with the third; all have since been fixed in Starsim. Finding 11 is open.

1. **Fixed: a stratification of some states could not be entered by a split that depends on another dimension (it blocked the faithful spelling).** People entering a state with a dimension their old state lacked went to its levels by one `split` for everyone, and an `adjust` on such a transition silently used the first level's multiplier for everyone. Fixed by `split=ss.by(table, dims=['age', 'clinical'])`, read as one row per age for those entering (rows normalized), and by `E306` for an `adjust` on a transition whose source has no level of the dimension. The rows for the old sum to 1.1 in the original; normalizing them, and giving the 1.1 as an `adjust` on age, is exact.

2. **Fixed: infectiousness by the level of a dimension needed a modifier for each level.** Fixed by `adjust={'rel_trans': [...]}` (and `rel_sus`) on `stratify()`, which runs in the kernels.

3. **Fixed: a sum of flows given to a disease as a result was silently dropped.** `ss.Disease(..., leaving=recovery + death)` is now an outcome.

4. **Fixed: an outcome was not stratified.** `select()` and `by()` now work on outcomes.

5. **Fixed: a set of states and a sum of states were not interchangeable.** A set is now its sum in arithmetic, and a sum can be the source of a transition.

6. **Fixed: `select()` did not chain with `by()`.** `res.n_I.select(age='young').by('clinical')` now works.

7. **Fixed: `transitions=` and `results=` were documented but not accepted.** `ss.Disease(transitions=[...], results=[...], init=...)` now works.

8. **Not a problem: no unit of time, and no overwrite.** The original names no unit, and neither version needs one. summer2's `Overwrite(0)` is the multiplier 0.

9. **Fixed: an initial value by level of a dimension of some states was wrong (it blocked agreement).** With the dimension on `I` only, `init=dict(I=ss.by(clinical=[10, 0]))` took the wrong number of people out of `S`, and with a split by age it also put the wrong number in `I` (12, not 10, in a small repro). Fixed: an initial count by level now puts exactly that many people in each level, spread over the other dimensions in proportion to the state's own split, and the first state gets the rest of the people in each of its groups. Since `I`'s own split is the entry split, `ss.by(clinical=[10, 0, 0, 0])` would put 5.95 young and 4.05 old people in `I`, not 5 and 5 as in the original, so the vignette gives the count by both dimensions: `ss.by([[5, 0, 0, 0], [5, 0, 0, 0]], dims=['age', 'clinical'])`.

10. **Fixed: a flow into a dimension of some states was recorded only at its first level.** `res.incidence.by('clinical')` gave everything at `asymptomatic`, because a flow was recorded in the groups of its source, and `E` has no clinical status, so `compare.py` had to work out incidence by clinical status and notifications from the change in `I` and the flows out of it. Fixed: such a flow is now recorded at the level people arrive at, under every solver, so `res.incidence.select(clinical='hospital')` works directly.

11. **Open, bug: a weight by level in an outcome fails.** Spec 09 says the weight of a flow in an outcome may be `ss.by(age=[...])`, which would declare notifications as `ss.outcome(ss.by(clinical=[0, 0, 1, 1]) * incidence)`. It raises `ValueError: operands could not be broadcast together with shapes (201,) (8,)` in `derived_outcomes()` in `solvers.py` (`amount = amount + flow*weight`), and the same with a weight by age on a model stratified by age alone (shapes `(201,) (2,)`): `ss.Disease(infection=ss.transmission('S -> E', beta=2, source='I'), incidence=incidence, recovery=ss.progression('I -> R', rate=0.3), notifications=ss.outcome(ss.by(age=[0, 1]) * incidence), init=dict(I=10)).stratify(age=['young', 'old'])`. Suggested change: multiply the weight by group into the flow by group before it is summed. Selecting the groups of the incidence result does the same job here, so this does not affect the vignette.
