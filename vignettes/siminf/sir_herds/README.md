# SimInf SIR in 1,600 herds, in Starsim

The translation of [examples/siminf/sir_herds](../../../examples/siminf/sir_herds). The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 12 | 23 | 7 of the 23 turn SimInf's table of events into a movement register, and 4 read the data, which the original gets from the package |
| One run | 0.08 s | 9.5 s | Gillespie's method in both, on one thread. The original as one command, starting R and loading the events, takes 2.3 s; building the Starsim sim takes 0.05 s, after 1.9 s to read the data |
| Results | | | **Agree.** The mean of 20 runs is within two standard errors of the original's mean of 200 at every day checked, for the totals, the number of herds infected, and the first herd |

Measured on 13 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared. The herds are a stratification by place, with an SIR in each that mixes only within the herd, and the 466,692 events are a movement register (`ss.Mobility(data=...)`): a row with a `from` and a `to` moves animals between herds, one with no `from` adds them (births), and one with no `to` removes them (deaths). The same text runs as agents, one for each of the 196,169 animals (`sim.new(solver='abm', n_agents=196_169)`), in 108 s.

## Findings

- **Scheduled events were missing, and are now a register.** SimInf's `exit`, `enter`, and `extTrans` events, with their `select` matrix, become one table with named columns: `date`, `from`, `to`, `n`, and `states` (here `S` for the animals that enter, and blank, meaning every state, for the rest). An event happens at the start of the first step on or after its date, before that step's transitions, so SimInf's day `t` is Starsim's `n[t]` with no shift. The events of a day happen in the order of the table, which for this table is SimInf's order (exits, then entries, then movements).
- **A whole number is a count.** `ss.by(herd=u0.I)` gives one infected animal in the first herd. It used to read the 1 as a fraction, which infected the whole herd; a whole number of 1 is now one person, as it already was for a single value.
- **Gillespie is slow with many groups.** Starsim works out every rate again after each event, over all 1,600 herds, which is about 18 µs an event; SimInf runs each herd on its own between events, since herds do not mix within a day. Doing the same where places do not mix within a step would close most of the gap.
- **Births as agents.** Building this found that `ss.birth()` added nobody in an agent-based run, and that a sim with no dimensions crashed once its agents grew past the space first set aside for them. Both are fixed.
