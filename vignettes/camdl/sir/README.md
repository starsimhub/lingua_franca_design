# camdl SIR, in Starsim

The translation of [examples/camdl/sir](../../../examples/camdl/sir). The model is `sir.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 30 | 13 | Two lines are over 100 characters, so count twice |
| One ODE run | 0.009 s | 0.022 s, or 0.0006 s for a repeated run | The original is timed as a whole command; Starsim without the import. Nearly all of the 0.022 s is building the sim; a sim that is already built is restarted and run in 0.6 ms |
| Results, ODE | | | Compartments and weekly cases within 0.02% |
| Results, stochastic | | | Mean of 200 runs within about 1% (chain-binomial in both) |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared: three states, two transitions, and one outcome with its likelihood. Nothing needed a function or a `step()` method.

## Findings

- **A likelihood on an outcome.** The original says the weekly cases are negative binomial around `rho` times the infections, with dispersion `k`. This was accepted by `ss.outcome(likelihood=)` but not used; it now is: `likelihood=ss.nbinom(n=k)` makes the model's value the mean, `k` becomes a parameter of the disease, and `sim.calibrate()` maximizes the likelihood when every series has one, fitting `k` with the rest if it has bounds. Fitted to weekly cases drawn around the original's ODE cases (with `k` = 10), it gives `beta` 0.43, `gamma` 0.20, and `k` 31; twelve weekly counts say little about `k`. The priors are still used by nothing, since there is no posterior method yet.
- **A parameter could not multiply a flow.** `rho * infection` failed when `rho` was an `ss.par`, and `rho` was not registered as a parameter of the disease. Both are fixed.
- **Slow to build, quick to run again.** Building the sim takes about 0.02 s, twice as long as the original takes for everything. The run itself was 0.045 s when the rate expressions were evaluated in Python at each stage of the integrator; the whole run is now one call to a Numba kernel, and a repeated run (`sim.restart(pars=...).run()`, or `sim.run(n_runs=...)`) takes 0.6 ms, and 100 runs as `sim.run(n_runs=100)` take 0.07 s in all.
- **The unit comes from `stop=`.** With `stop=ss.weeks(12)` and no `unit=`, the sim runs in weeks, although the rates are per day. The original states `time_unit = 'days` once; here `unit='day'` does the same.
