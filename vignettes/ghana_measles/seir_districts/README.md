# Ghana measles, in Starsim

The translation of [examples/ghana_measles/seir_districts](../../../examples/ghana_measles/seir_districts), one of the two models named for wave 3. The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 89 | 20 | Three lines are over 100 characters, so count twice; two read the data |
| One run | 0.84 s | 1.37 s | Both with the data already loaded; Starsim's time includes building the sim |
| Results | | | **Agree.** Over 2010 to 2025, 3,046,322 infections against 3,041,691 and 15,240 reported cases against 15,197 (means of 20 and 50 runs); monthly means correlate at 0.999; infections from 2020 in each of the 16 regions within chance (from −2.6 to +1.7 standard errors) |

Measured on 14 October 2026 with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine.

## What was declared and what was not

Everything is declared: seven transitions, an outcome, the districts as a geography, and the mixing between them as visiting (`ss.Mobility(ss.gravity(c=1.5), kind='visit', away=0.01)`), which is the original's form: residents are exposed to the prevalence where they make their contacts, and do not change who is present there.

## Findings

- **Nothing was missing.** This is the first wave 3 model that needed no change to Starsim. The pieces it uses (places with latitudes and longitudes, gravity, seasonality, births into two states, deaths from every state, a reporting share at onset) were all added for waves 1 and 2.
- **Importation is awkward to write.** The original adds a fixed number of infections per person in the population. A transition's rate is per person in its source, so this is written as `ss.peryear(0.01/1000) * (S + E + I + R).n / S.n`. An inflow into a state from outside the population would read better, but `ss.null >> E` would add people rather than move them.
- **Slower, not much.** A run of 5,844 daily steps over 260 districts takes 1.4 s, against 0.84 s for the original's NumPy loop.
