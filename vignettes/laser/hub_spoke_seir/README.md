# LASER hub and spoke, in Starsim

The translation of [examples/laser/hub_spoke_seir](../../../examples/laser/hub_spoke_seir). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 50 | 16 | |
| One agent-based run | 0.78 s | 1.3 s | The original has 1,750,000 agents; the Starsim run has 175,000, each standing for ten people |
| Results | | | **Agree.** 1,533,300 recovered at the end, against 1,532,298, and within 2% in each place shown; peaks are within 4% in size (11% in Interim 1A, the smallest place shown) and 7 days in time (one run of each) |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared: the places, the model, the durations as distributions, and the mobility, which moves the force of infection between places (`kind='force'`), as LASER does. The same text runs as agents and as an ODE (with the durations as Erlang stages), and the two agree with each other.

## Findings

- **The two frameworks coupled places differently.** LASER moves the force of infection itself between places, unweighted by their size: `f[j] += Σ f[i]·network[i,j] − f[j]·Σ network[j,i]`. Starsim's commuting moves people, who mix where they are, and with it 80% were infected, against 88%. `ss.Mobility(..., kind='force')` is now LASER's form, and with it the results agree. The gravity matrix is the same in both (every row of LASER's is capped at 3/32, which is `away=3/32` here).
- **No initial conditions by place.** The epidemic starts in one town. `init=dict(I=ss.by(patch=[...]))` now does this.
- **Slower per agent.** With a tenth of the agents the run takes nearly twice as long (it was nearly four times): about 20 ns for each agent on each step, against about 1 ns in the original. As compartments the same model takes 0.6 s as an ODE, 2.2 s with `solver="binomial"`, and 6.7 s with `solver="tau"`, for all 1,750,000 people.
- **Distances.** The original measures great-circle distances between map coordinates; this version uses the same layout in kilometers on a plane, which is the same to within a fraction of a percent.
