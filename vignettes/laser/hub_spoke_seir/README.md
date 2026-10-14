# LASER hub and spoke, in Starsim

The translation of [examples/laser/hub_spoke_seir](../../../examples/laser/hub_spoke_seir). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 50 | 16 | |
| One agent-based run | 0.78 s | 1.9 s | The original has 1,750,000 agents; the Starsim run has 175,000, each standing for ten people |
| Results | | | **Do not agree.** 80% are infected, against 88%; the city peaks on day 190, against day 162 |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared: the places, the model, the durations as distributions, and the mobility. The same text runs as agents and as an ODE (with the durations as Erlang stages), and the two agree with each other.

## Findings

- **The two frameworks couple places differently.** LASER moves the force of infection itself between places, unweighted by their size: `f[j] += Σ f[i]·network[i,j] − f[j]·Σ network[j,i]`. Starsim's commuting moves people, who mix where they are. The gravity matrix is the same in both (every row of LASER's is capped at 3/32, which is `away=3/32` here), and the results still differ, because of this. LASER's version infects more people than a well-mixed epidemic with the same R0 would. There is no way to ask Starsim for it.
- **No initial conditions by place.** The epidemic starts in one town. `init=dict(I=ss.by(patch=[...]))` now does this.
- **Slower per agent.** With a tenth of the agents the run takes more than twice as long (it was nearly four times): about 25 ns for each agent on each step, against about 1 ns in the original. What is left is NumPy passes over all the agents for each state on each step, where the original has one compiled loop.
- **Distances.** The original measures great-circle distances between map coordinates; this version uses the same layout in kilometers on a plane, which is the same to within a fraction of a percent.
