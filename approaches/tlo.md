# Thanzi La Onse (TLOmodel)

|  |  |
|---|---|
| **Language** | Python (pandas-backed population table) |
| **Paradigms** | Agent-based microsimulation, discrete-event scheduling; a whole health system |
| **Specification style** | Python `Module` subclasses with declared `PARAMETERS` and `PROPERTIES` dicts; behavior as `Event` and `HSI_Event` subclasses; parameters read from resource files |
| **Version reviewed** | `main` at commit `3d8fdb7` (2026-10-14) |
| **License** | MIT |
| **Code** | <https://github.com/UCL/TLOmodel> |
| **Docs** | <https://www.tlomodel.org/> (module write-ups at <https://www.tlomodel.org/writeups.html>) |
| **Paper** | Hallett et al., "Estimates of resource use in the public-sector health-care system and the effect of strengthening health-care services in Malawi during 2015–19: a modelling study (Thanzi La Onse)", *Lancet Global Health* (2025) |

## What it's for

Thanzi La Onse ("health for all" in Chichewa) is a model of the whole of Malawi's health system: about 30 diseases and conditions (HIV, TB, malaria, maternal and newborn health, childhood illness, cancers, cardiometabolic disease, injuries, depression, and more) running in one simulated population, together with the health system that treats them, with staff time by cadre and facility level, consumables, beds, and equipment. It answers questions about health-system investment: what a given budget, staffing level, or package of services buys in DALYs averted, across all conditions at once.

It is in this review for that **health-system layer**: care as a resource-constrained event that the disease modules request and the health system grants, defers, or refuses. No infectious disease framework here models that. It is also, like Vivarium, a large multi-module model built by many independent teams, so it shows how cross-module coupling works at that scale.

## How a model is specified

A module declares its parameters and the per-person properties it owns, reads parameter values from resource files (CSV or Excel sheets in `resources/`), and schedules events. From the toy module `Mockitis`:

```python
class Mockitis(Module, GenericFirstAppointmentsMixin):
    INIT_DEPENDENCIES = {'Demography', 'SymptomManager'}
    CAUSES_OF_DEATH = {'Mockitis': Cause(label='Mockitis_Disability_And_Death')}

    PARAMETERS = {
        'p_infection': Parameter(Types.REAL, 'Probability that an uninfected individual becomes infected'),
        'p_cure': Parameter(Types.REAL, 'Probability that a treatment is successful'),
    }
    PROPERTIES = {
        'mi_is_infected': Property(Types.BOOL, 'Current status of mockitis'),
        'mi_status': Property(Types.CATEGORICAL, 'N=never; C=currently; P=previously', categories=['N', 'C', 'P']),
        'mi_date_infected': Property(Types.DATE, 'Date of latest infection'),
    }

    def initialise_simulation(self, sim):
        sim.schedule_event(MockitisEvent(self), sim.date + DateOffset(months=1))
```

A simulation registers modules and runs to a date:

```python
sim = Simulation(start_date=Date(2010, 1, 1), seed=0, resourcefilepath='resources')
sim.register(*fullmodel())
sim.make_initial_population(n=100_000)
sim.simulate(end_date=Date(2030, 1, 1))
```

Properties are columns of one shared pandas DataFrame (`sim.population.props`), prefixed by module by convention (`mi_`, `hv_`, `tb_`). Any module can read or write any column.

Behavior is events. A `RegularEvent` with `PopulationScopeEventMixin` runs on a fixed frequency over the whole table (the usual place for incidence); an `Event` with `IndividualScopeEventMixin` runs once for one person on a scheduled date (a death, a progression). Time is calendar dates and `DateOffset`s, not a fixed step: events sit in a priority queue, and each module chooses its own cadence (monthly for most incidence, daily for the health system).

## Core abstractions

- **`LinearModel` and `Predictor`.** Most risk equations are declared rather than written: a model type (additive, multiplicative, or logistic), an intercept, and predictors that map a property's values to effect sizes. `Predictor("age_years").when("<15", 0.0).when("<49", 1.0).otherwise(0.0)` and `Predictor("li_is_circ").when(True, p["rr_circumcision"])` from the HIV module. The conditions are pandas query strings evaluated over the table, so one declaration serves the whole population.
- **`HSI_Event` (health-system interaction).** Care is an event a disease module asks the health system to run, with a `TREATMENT_ID`, an appointment footprint (`{'Over5OPD': 1, 'NewAdult': 1}`), an accepted facility level, a priority, and a window (`topen`, `tclose`). Inside `apply()` the event requests consumables by item code, and gets back whether they were available. `did_not_run()` says what happens when the health system refuses it.
- **The health system as a scheduler with capacity.** Appointment footprints convert to minutes of staff time by cadre and facility. In mode 1 constraints are elastic (everything runs if any staff exist); in mode 2 they are hard, and events compete by priority each day, with the rest deferred or dropped. Consumables, beds, and equipment each have availability tables that can be set to `default`, `all`, or `none`; `service_availability` turns treatment IDs on and off by wildcard (`'Hiv_*'`).
- **`SymptomManager` and health seeking.** Diseases add symptoms to people; a central health-seeking module decides who presents for care, and generic first appointments (`GenericFirstAppointmentsMixin`) let each disease module react when someone with its symptoms arrives. Care-seeking is shared machinery, not something each disease reimplements.
- **Declared causes, and the burden ledger.** Each module declares `CAUSES_OF_DEATH` and `CAUSES_OF_DISABILITY` mapped to GBD labels; deaths go through one `InstantaneousDeath` event with a cause; `HealthBurden` calls each module's `report_daly_values()` monthly and accrues YLD and YLL per person. DALYs are a first-class output of every run.
- **Declared dependencies and metadata.** `INIT_DEPENDENCIES`, `OPTIONAL_INIT_DEPENDENCIES`, and `METADATA` flags (`DISEASE_MODULE`, `USES_HEALTHSYSTEM`, ...) let the framework order initialization and check that a module's requirements are registered. Modules can be swapped for simplified versions (`SimplifiedBirths`, a health system with everything available) to run a disease on its own.
- **Scenarios.** A `BaseScenario` subclass lists the modules and draws parameter overrides per draw and run; the batch runner fans these out to Azure Batch, and structured logs are parsed afterwards.

## Randomness

The simulation holds a NumPy `SeedSequence`; each module gets its own `RandomState` stream from it. Draws are made per event and per call, so streams are per module but not per agent or per decision: adding a person or a draw upstream shifts everything after it, and there are no common random numbers across scenarios beyond the shared seed.

## Strengths

- **The only model here with a health system that can say no.** Care costs staff time and consumables, capacity is finite, requests have priorities and windows, and what happens to a refused request is declared. This is what makes health-system questions (staffing, supply chains, service packages) answerable, and it is the right shape for the costing work in [costing/](../costing/README.md).
- **Burden accounting is built in and exact.** Per-person YLD and YLL accrual, declared causes mapped to GBD, and one death pathway with a cause.
- **Declarative risk equations.** `LinearModel` gets a lot of epidemiology out of imperative code, and it reads like the regression tables the parameters come from.
- **Shared care-seeking.** Symptoms and first appointments are central, so a person presenting with a fever is seen once and assessed for malaria, pneumonia, and others, rather than each disease running its own care cascade.
- **Scale of composition.** Thirty-odd modules by different teams run together, and many have simplified stand-ins for running one disease alone.
- **Documentation per module.** Every module has a write-up of its structure, parameters, and calibration, and resource files carry their data sources.

## Limitations

- **Very large and code-heavy.** About 68,000 lines across 56 files in `methods/`, plus the resource files. The health system alone is over 3,000 lines. There is no smaller way in: a model is Python modules, and a new disease means a new module of several hundred lines.
- **pandas and per-person events are slow.** One shared DataFrame, `df.loc` writes, and many individual-scope events (each death, each appointment) make runs of tens of thousands of people take hours; production runs go to Azure Batch.
- **No ownership of state.** Every module can write every column; the prefix convention is the only guard. Cross-module effects are direct reads of another module's properties inside a linear model or an event, so dependencies are visible only by reading the code.
- **Malawi-shaped.** Facility levels, districts, cadres, the consumables list, and demography come from Malawian data, and the resource files assume that structure. Other settings mean replacing much of `resources/`.
- **Parameters live in spreadsheets, set in code.** `read_parameters()` loads resource files and then often sets or overrides values in Python, so the parameter set of a run is not one inspectable object.
- **No transmission or contact structure in general.** Infectious diseases (HIV, TB, malaria, measles) compute their own force of infection inside their modules, mostly as aggregate rates over the population table; there are no networks or shared mixing machinery.
- **No inference layer.** Calibration is done outside the framework, by scenario sweeps and comparison with data.

## Implications for the lingua franca

1. **Care should be a delivery that can fail.** TLO's `HSI_Event` is the model for interventions that need capacity: a request with a footprint, a priority, and a window, granted or refused by a capacity model, with a declared fallback when refused. The lingua franca's deliveries with `capacity=` ([design/08-interventions.md](../design/08-interventions.md)) are the same idea; TLO shows what a full version needs: several resources at once (staff by cadre, consumables, beds), priority among competing requests, and the elastic versus hard modes as a switch rather than a rewrite.
2. **Count, then value.** TLO records appointments, staff time, and consumables used during the run and costs them afterwards, and accrues DALYs per person from declared causes. That is the principle in [costing/spec.md](../costing/spec.md), and TLO is the largest working example of it.
3. **Declared risk equations are worth having.** `LinearModel` is a narrow, readable declarative form for "rate as a function of person attributes", which is most of what a chronic-disease module contains. The lingua franca's rate expressions should cover it, and the `.when()` chain is a good spelling to compare against.
4. **Shared care-seeking is a module, not a convention.** Symptoms owned by diseases and care-seeking owned centrally is the right split for multi-disease models; it is the same pattern as Vivarium's value pipelines, applied to a person's route into care.
5. **Declare state ownership.** TLO's prefix convention is what happens without it: thirty modules, one table, and dependencies discovered by grep. Like Vivarium's `PopulationView`, this argues for declared reads and writes.
6. **A test of the whole library, not a corpus example.** A full TLO model is too large and too data-bound to be one of the corpus examples, and most of it would stay as its own code and data. But it should be possible to rebuild it on the lingua franca, and faster: if TLO cannot be represented, that is a gap in the lingua franca, not in TLO.
