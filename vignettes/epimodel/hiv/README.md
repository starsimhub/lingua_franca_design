# EpiModel HIV with a care cascade and PrEP, in Starsim

The translation of [examples/epimodel/hiv](../../../examples/epimodel/hiv), EpiModel's wave 3 example. The model is `model.py`; `compare.py` checks it against the original's reference results.

## Comparison

| Measure | Original | Starsim | |
|---|---|---|---|
| Lines of model code | 405 | 62 | 50 lines, 12 of them over 100 characters, so counted twice; 10 of the 50 are the one remaining workaround (who is indicated for PrEP). It was 69 before findings 1, 2, and 4 were fixed |
| One run | 54 s | 2.5 s | The mean over the four scenarios (Starsim: 2.2 s with no intervention, 2.8 s with both). The original also takes 1.2 s to estimate the two networks first |
| Results | | | **Agree within the noise of the runs, with the cascade and with both interventions; the network differs slightly with no intervention and with PrEP alone** (below) |

Measured on 14 October 2026 (after the fixes below) with Starsim 4.0.0 (the `v4` branch) on a 20-core x86-64 Linux machine. Starsim's numbers are the means of 20 runs of each scenario, the original's of 10.

| Scenario | Cumulative infections | Final prevalence | Incidence per 100 person-years (second half) | Diagnosed, on ART, suppressed (second half) | PrEP among the HIV-negative |
|---|---|---|---|---|---|
| No intervention | 480 (original 459) | 16.4% (14.4%) | 2.06 (1.80) | | |
| Cascade | 75 (74) | 5.0% (5.1%) | 0.15 (0.14) | 97.1%, 91.3%, 89.1% (97.6%, 91.9%, 89.7%) | |
| PrEP | 237 (244) | 7.4% (7.3%) | 0.81 (0.80) | | 12.1% (12.0%) |
| Both | 42 (45) | 3.9% (3.8%) | 0.075 (0.074) | 98.2%, 92.3%, 90.2% (98.0%, 92.1%, 89.9%) | 12.1% (12.0%) |

Prevalence at 5 and 10 years agrees within 0.6 percentage points in every scenario. With no intervention, 239 ± 5 people have HIV at the end against 210 (the original's 10 runs range from 154 to 247, so its mean has a standard error of about 9); with PrEP alone, 115 ± 4 against 111. The likely cause is the casual network: Starsim's has the targets (a mean degree of 0.30, and 10.2% with two or more casual partners), while the original's undershoots them (0.28 and 8.9% with no intervention, 0.30 and 9.6% with PrEP). The main network is close in both (a mean degree of 0.49 to 0.50 against 0.49, and 4.0% to 4.1% with two main partners against 4.0% to 4.2%).

## What was declared and what was not

Declared: the four disease states, with the infectiousness of acute and AIDS on the states; transmission over both networks, with a probability per partnership for each; progression, AIDS deaths, other departures, and arrivals; the care cascade as a stratification of the infected states (undiagnosed, diagnosed, on ART, suppressed, and off ART after being on it) with seven transfers, and its effects on infectiousness, progression, and AIDS mortality as `adjust=`; both networks as `ss.PartnerNet` from the same targets as the original; PrEP as a vaccine with 95% efficacy that people stop taking, delivered to half of those indicated at the start and then to 1.5% of them a week; the scenarios.

Not declared (one workaround, marked in the code): who is indicated for PrEP, a function that reads both networks. Two earlier workarounds, a subclass of `ss.PartnerNet` for partnerships ended by departures and building the model twice with and without the cascade, are no longer needed (findings 1 and 2). The scenarios are now `pars=dict(cascade=1)` and the PrEP deliveries.

The original's six modules (305 lines of R) become the disease, the stratification, and two deliveries. Its two attributes for each person, a stage and a care state, are one state and one dimension here, and its history of ART (`art.time`, which decides whether someone starts or re-starts ART) is the level `off`.

## Findings

1. **Fixed: a parameter in the rate of a transfer is not a parameter of the sim, and a transfer cannot be modified.** Starsim now registers a parameter in a transfer's rate, and `ss.modify` can target a transfer, which is an attribute of the disease. The vignette builds the model once and switches the cascade with `pars=dict(cascade=1)`. Two things remain: the fix covers transfers given to `ss.Disease()` but not those given to `stratify()` (the same repro with the transfer passed to `d.stratify(v=[False, True], x=...)` still raises `E602`), so the transfers moved to the constructor; and since transfers are now attributes, one named `stop` collides with the module's `stop` time (see finding 9). Originally: The scenarios switch the cascade on and off, which would be `rate=cascade*week(0.015)` with `cascade = ss.par(0)` and `sim.new(pars=dict(cascade=1))`. But a transfer's parameters are not collected (`E602 UnknownParameter`), and `ss.modify(transfer, multiply=0)` raises `E504` (a transfer has no module), as does `ss.modify('hiv.test', ...)`, though 05-dimensions says a transfer "can be the target of `ss.modify`". Repro:

    ```python
    c = ss.par(0)
    S, I = ss.states(2)
    d = ss.Disease(inf=S >> I @ 0.1*I, x=ss.transfer(v=True, rate=c*0.2), init=dict(I=1))
    d.stratify(v=[False, True])
    ss.Sim(d, n_agents=100, stop=5, pars=dict(c=1)).run() # E602: "c" matches no parameter; parameters are d.beta
    ```

    The same happens with the transfer given to `stratify()`. Fix: collect the parameters of transfers (in the constructor and in `stratify()`) into `graph.pars`, and register transfers as named transitions of the module, so that `pars=`, `ss.modify(hiv.test, ...)`, and `ss.change` reach them.

2. **Fixed: `ss.PartnerNet` does not allow for partnerships ended by departures.** `ss.PartnerNet` now estimates the rate at which partners depart during the run and dissolves partnerships less often to make up for it, as EpiModel's `d.rate` does; with `dur=200` and `dur=26` and no subclass, the mean degree over the second half is 0.49 to 0.50 (main) and 0.30 (casual), on target. Originally: EpiModel's `dissolution_coefs(duration=200, d.rate=0.0005)` makes partnerships last 200 weeks in all, counting those ended when either partner departs, and its formation model keeps the mean degree at its target. `ss.PartnerNet` balances formation against its own dissolution rate only, so with departures the main network's mean degree fell from 0.5 to 0.41 to 0.42 (in single runs, with `dur` 200 or the corrected 250), and the epidemic was smaller. The workaround raises the seeking rate by the share of partnerships ended by departures. Fix: a `d_rate=` (or `depart=`) on `ss.PartnerNet` that is added to the dissolution rate in working out the seeking rate, as EpiModel does; or measure the rate at which partnerships end from all causes and balance against that.

3. **No conditions on the network** (awkward; a function). PrEP is indicated for HIV-negative people with two or more partners across both networks, or with a partner who has HIV. This is a 10-line function reading the edge lists. A condition such as `hiv.S & ((main.degree + casual.degree >= 2) | ss.partner_of(hiv.infected))`, usable in `eligible=` and `where=`, would declare it; 06-routes and 08-interventions have nothing on degree or partners as conditions (only contact tracing, which is not implemented).

4. **Fixed: a dict of networks is refused, and networks are not named from their variables.** `networks=dict(main=main, casual=casual)` now works, and an `ss.PartnerNet` is named from its variable. The two PrEP deliveries still need `name=`, since they are in a list. Originally: `ss.Sim(networks=dict(main=main, casual=casual))` raises "one of the keys must be "type"", and with `networks=[main, casual]` both are called `partnernet`, so `beta=dict(main=..., casual=...)` raises `E403`. Both needed `name=`. Two deliveries in a list are also both named `vaccinate` (with a warning). Fix: name networks and deliveries from their variables as diseases are, and accept a dict of modules keyed by name.

5. **No acts on `ss.PartnerNet`** (awkward, a small difference). EpiModel works out the chance of transmission over a partnership as `1 - (1 - p·m)^acts`, with `m` the infectiousness of the infected partner (5 if acute, 0.3 on ART, and so on). Here the probability for each network is `1 - (1 - p)^acts`, and Starsim multiplies it by `m`, which for an acute main partner gives 0.0374 against 0.0370. The networks with acts (`ss.SexualNetwork`) are the male-female ones. Fix: `acts=` on `ss.PartnerNet`, with `rel_trans` and `rel_sus` applied to the probability per act.

6. **Stopping a product at a rate is written as waning.** PrEP is stopped with a probability of 0.015 a week; that is `ss.Vaccine(waning=-1/np.log(1 - 0.015))`, a mean duration of protection. It works, but a product that people take and stop is not a vaccine, and the duration has to be worked out from the probability. An `ss.Treatment(efficacy=dict(acquisition=0.95), stop=ss.prob(0.015))`, or `waning=ss.prob(...)`, would say it.

7. **The networks' targets are better matched than the original's own.** EpiModel's casual network has a mean degree of 0.28 to 0.30 and 8.9% to 9.6% with two or more partners, against targets of 0.3 and 10%; `ss.PartnerNet` has 0.30 and 10.0%. This is probably why the epidemic with no intervention is about 10% larger here (about two standard errors). It is not a fault in either, but it means that agreement on the targets does not imply agreement on the network.

8. **Smaller differences.** EpiModel uses each rate as a probability per step, written here as `ss.prob` (aliased `week`). It starts its seed infections in stages drawn at random in proportion to 12:520:104; here the expected numbers (2, 98, and 20) are given. Its modules run in turn, each from a snapshot of the attributes at its start, so for example someone can be suppressed and stop ART in one step; here the transfers out of a level compete. None of these is visible in the results.

9. **New: a transition named `stop` breaks the sim** (blocks the run until renamed; renamed here to `stop_art`). Since transitions became attributes of the disease, a transition whose name is a module parameter is read as that parameter. Repro:

    ```python
    S, I = ss.states(2)
    d = ss.Disease(inf=S >> I @ 0.1*I, stop=I >> S @ 0.1, init=dict(I=1))
    ss.Sim(d, n_agents=100, stop=5).run() # TypeError: Failed to parse stop = Transition(I -> S @ 0.1): expecting ss.date, ss.dur, or None
    ```

    Fix: keep transitions apart from the module's own parameters (`start`, `stop`, `dt`, `unit`, ...), or refuse such a name when the disease is declared with an error that says which names are taken.
