# Malaria and neglected tropical diseases

Malaria and the neglected tropical diseases (NTDs) are where much of the economic evaluation of transmission models in global health has been done, because the funders (Global Fund, PMI, WHO, Gates) need cost-effectiveness and investment-case numbers for interventions that are deployed at population scale: bed nets, indoor residual spraying (IRS), chemoprevention, vaccines, and mass drug administration (MDA). This file collects seven exemplars that span the range of how this is done in practice, from engines that accumulate a cost counter during the simulation (EMOD), to engines that only emit resource-use counts (OpenMalaria, malariasimulation), to models where spending is an input that drives coverage (Optima/Atomica), to NTD models where nearly all of the economics lives in the paper rather than the code. The striking common finding is that very few of these engines compute costs or DALYs internally; the dominant pattern is "simulate events, then apply unit costs and disability weights post hoc." Metric definitions (DALY, ICER, discounting) are in [metrics.md](metrics.md) and are not repeated here.

## OpenMalaria

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| *P. falciparum* (and *P. vivax*) malaria | Individual-based stochastic, 5-day or 1-day time step | C++, XML scenario files | [SwissTPH/openmalaria](https://github.com/SwissTPH/openmalaria) | [Tediosi et al. 2006](https://doi.org/10.4269/ajtmh.2006.75.131); [Tediosi et al. 2009](https://doi.org/10.1186/1475-2875-8-127); [Penny et al. 2016](https://doi.org/10.1016/S0140-6736(15)00725-4); [Galactionova et al. 2017](https://doi.org/10.1016/j.vaccine.2016.11.042) |

- **What is costed**: In the published analyses, health-system (provider) costs: intervention delivery (e.g. vaccine purchase, freight, wastage, distribution, storage, syringes, personnel, social mobilization) and case management (outpatient visits, inpatient days, drugs, diagnostics). Tediosi et al. 2009 used an ingredients-style per-dose build-up (their Table 1, "Vaccine delivery costs – routine EPI – US$ 2006") and case management costs from earlier Tanzanian costing studies, adjusted for inflation. The OpenMalaria wiki lists the case-management cost categories the clinical model was designed to support: "drugs medicated, including vomited doses but not doses skipped due to poor adherence; parasite (RDT and microscopy) diagnostics used; outpatient visits; patient hospital days, using fixed average lengths for stays resulting in recovery and stays ending with mortality; patient direct costs, including travel, medical and non-medical supplies" ([ScenarioHealthSystem wiki](https://github.com/SwissTPH/openmalaria/wiki/ScenarioHealthSystem)).
- **How costs attach to the model**: Post hoc, from event counts. Contrary to a common impression, current OpenMalaria (schema 50) has no cost or DALY outputs: there is no "DALY" or cost element in the current schema or the `model/` source. The wiki's [Terminology](https://github.com/SwissTPH/openmalaria/wiki/Terminology) page is explicit: costing is the "Determination of (financial) costs associated with deploying an intervention. This is calculated outside OpenMalaria." What the engine provides instead is a rich set of resource-use counters, selected per survey and stratified by age group and cohort, in [`model/mon/OutMeasures.h`](https://github.com/SwissTPH/openmalaria/blob/main/model/mon/OutMeasures.h): treatments by line (`nTreatments1/2/3`), hospital deaths, mass ITNs, EPI ITNs, IRS, MDA, vaccinations, and "expected" (probability-summed) deaths and sequelae. The decision-tree case-management model was explicitly designed around costing: drugs "are only costed when taken", and treatment modifiers historically carried an `affectsCost` attribute so that, e.g., poor-quality drugs could be modeled at standard cost (present up to [schema 32](https://github.com/SwissTPH/openmalaria/blob/main/schema/scenario_32.xsd), removed thereafter). Older drug-usage and diagnostic measures (`Clinical_DrugUsage`, `Clinical_RDTs`, `Clinical_Microscopy`) are now flagged as obsolete in `isObsoleteMeasure()`.
- **Health outcomes**: DALYs computed post hoc from simulated events. Tediosi et al. 2009: "years of life lived with disability are calculated on the basis of the duration of disability, and respective disability weights. Weights for different malaria attributable disease conditions have been obtained from the Global Burden of Disease (GBD) study", with "no age weighting", and YLLs from "the life-table from Butajira, Ethiopia, with an average life expectancy of 46.6 years at birth". Costs and benefits discounted at 3%. The same Butajira life table became the harmonized demography in the four-model RTS,S comparison ([Penny et al. 2016](https://doi.org/10.1016/S0140-6736(15)00725-4)), which reported "undiscounted disability-adjusted life-years (DALYs; driven mainly by mortality)".
- **Analyses supported**: ICERs per uncomplicated episode, severe episode, death, and DALY averted; vaccine "price" sensitivity (cost per dose at $1/$2/$10); case-management cost savings (offset costs); multi-seed and multi-model ensemble uncertainty. Country-specific CEAs across 43 African countries (Galactionova et al. 2017).
- **Example**: Selecting resource-use outputs in a scenario file ([`test/scenario2ITNs.xml`](https://github.com/SwissTPH/openmalaria/blob/main/test/scenario2ITNs.xml)):

```xml
<SurveyOptions>
  <option name="nHost" value="true"/>
  <option name="nPatent" value="true"/>
  <option name="sumlogDens" value="true"/>
  <option name="nTreatments1" value="true"/>
  <option name="nTreatments2" value="true"/>
  <option name="nTreatments3" value="true"/>
  <option name="annAvgK" value="true"/>
  <option name="nMassIRS" value="true"/>
  <option name="nMDAs" value="true"/>
  ...
</SurveyOptions>
```

And the measure definitions in [`OutMeasures.h`](https://github.com/SwissTPH/openmalaria/blob/main/model/mon/OutMeasures.h):

```cpp
/// number of blood-stage treatments (1st line)
{"nTreatments1", 11, false, Dim::Age | Dim::Cohort},
...
/// deaths in hospital
{"nHospitalDeaths", 17, false, Dim::Age | Dim::Cohort},
```

- **Strengths and limitations**:
  - Very detailed, mechanistic case-management decision trees produce exactly the resource-use counts (tests, drug doses actually taken, hospital days) that ingredients costing needs.
  - "Expected" outcome measures (summed probabilities rather than realized events) reduce stochastic noise in DALY and ICER denominators, a useful trick for any ABM.
  - Costing and DALYs are entirely outside the engine and live in project-specific scripts, so the unit-cost tables, life tables, and disability weights are not versioned with the model.
  - Cost hooks have been progressively removed from the schema (`affectsCost`, drug-usage measures), suggesting that maintaining cost semantics inside the engine was not worth the upkeep.

## malariasimulation, treasure, and postie (Imperial College)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| *P. falciparum* malaria | Individual-based stochastic (reimplementation of the Griffin et al. model) | R + C++ (`individual`) | [mrc-ide/malariasimulation](https://github.com/mrc-ide/malariasimulation); costing: [mrc-ide/treasure](https://github.com/mrc-ide/treasure); DALYs: [mrc-ide/postie](https://github.com/mrc-ide/postie); nets: [mrc-ide/netz](https://github.com/mrc-ide/netz) | [Winskill et al. 2017](https://doi.org/10.1136/bmjgh-2016-000090); [Winskill et al. 2019](https://doi.org/10.1186/s12936-019-2755-5); [Patouillard et al. 2017](https://doi.org/10.1136/bmjgh-2016-000176); [Sherrard-Smith et al. 2022](https://doi.org/10.1016/S2542-5196(21)00296-5); [Okell et al. 2014](https://doi.org/10.1038/ncomms6606) |

- **What is costed**: Provider perspective. Commodities (LLINs by type, RDTs, microscopy, ACT/chloroquine/primaquine doses, SMC, PMC, IPTp, RTS,S and R21 doses), delivery, IRS per person or per structure, active case detection, surveillance per person at risk, and outpatient/inpatient care. Unit-cost sources are cited per function in `treasure`: e.g. LLIN commodity cost from "The Global Fund Pooled Procurement Mechanism Reference Pricing" and delivery cost from Sherrard-Smith et al. 2022. Patouillard et al. 2017 costed the Global Technical Strategy investment targets with procurement prices plus freight/insurance and in-country delivery mark-ups.
- **How costs attach to the model**: Strictly post hoc, in a two-step "commodity then cost" pattern. malariasimulation itself has no cost parameters; it renders counts such as `n_treated` and per-dose vaccine counts (`n_pev_<strategy>_dose_<n>`). `treasure` then provides (1) `commodity_*` functions that convert model coverage or case outputs into quantities (e.g. `commodity_rdt_tests(n_cases, treatment_coverage, proportion_rdt, proportion_tested)`, `commodity_nets()` which inverts the `netz` usage → access → crop → distribution chain to get nets required), and (2) `cost_*` functions that multiply quantities by unit costs with CPI inflation adjustment (`inflation_adjust()`, defaulting to Sub-Saharan Africa CPI and a target year option) and `discount_future_values()`. The earlier papers used richer structures: Winskill et al. 2019 split costs into "Fixed costs: These represent programme costs (e.g., recurrent/management/training costs) and do not change with respect to coverage. Variable costs: These represent commodity costs (e.g., vaccine dose costs) and increase linearly with coverage", plus, for LLINs and treatment, "Variable non-linear costs: These represent inefficiencies or increasing marginal costs as coverage increases... characterized by a fitted hill function." Winskill et al. 2017 similarly contrasted linear costs with "non-linear relationships between coverage and unit costs" derived from net-retention dynamics.
- **Health outcomes**: `postie::dalys()` computes DALYs from malariasimulation age-banded clinical, severe, and mortality outputs: YLD uses GBD 2017 disability weights (mild 0.006, moderate 0.051 for under-5s, severe 0.133) times episode durations from Winskill et al. 2017; YLL uses UN WPP Africa life expectancy at the expected age within each band (assuming exponentially distributed ages). Discounting is applied separately (`treasure::discount_future_values`). Cases and deaths averted are also standard.
- **Analyses supported**: ICERs and stepwise expansion paths ("Starting from zero coverage of all interventions, the first intervention to be implemented at the lowest coverage band was selected as that with the lowest ICER", Winskill et al. 2019), budget-constrained prioritization, global and national investment cases (Patouillard et al. 2017), PSA with correlated cost draws ("Costs for treatment of severe and clinical cases were correlated"), and drug CEA (Okell et al. 2014).
- **Example**: Unit cost × commodity count with inflation, from [`treasure/R/bet_nets.R`](https://github.com/mrc-ide/treasure/blob/main/R/bet_nets.R):

```r
cost_llin <- function(n_llin, llin_unit_cost = 2.02, llin_delivery_cost = 1.50,
                      input_year = 2024, ...) {
  ...
  unit_cost <- llin_unit_cost + llin_delivery_cost
  unit_cost <- inflation_adjust(unit_cost, input_year, ...)
  cost <- n_llin * unit_cost
  return(cost)
}
```

And DALYs from simulation output, from [`postie/R/dalys.R`](https://github.com/mrc-ide/postie/blob/main/R/dalys.R):

```r
case_disability_weight = ifelse(.data$age <= 5, moderate_disability_weight, mild_disability_weight),
yld = .data$severe * severe_disability_weight * severe_episode_length +
  .data$clinical * .data$case_disability_weight * clinical_episode_length,
yll = .data$mortality * .data$life_expectancy,
dalys = .data$yld + .data$yll
```

- **Strengths and limitations**:
  - Clean separation of concerns: simulator → `postie` (epi metrics, DALYs) → `treasure` (commodities, costs), each a small versioned package. The README states the goal is "a transparent and version controlled repository for unit cost estimates that included detailed citations or references for cost sources", and warns users to pin a version for stable costing.
  - The explicit commodity layer (coverage → quantities) is the right abstraction: it is where non-linear delivery (net over-allocation, last-mile costs) is captured, separately from unit costs.
  - Fixed program costs and non-linear cost-coverage relationships from the papers did not make it into `treasure`, which is linear unit costs only.
  - Costs computed from aggregate outputs cannot reflect individual-level heterogeneity in resource use (e.g. repeat visits per episode) unless the simulator renders it.

## EMOD (Institute for Disease Modeling)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| Malaria (also HIV, TB, polio, etc.) | Individual-based stochastic with explicit vector model, spatial nodes | C++, JSON config/campaign (Python builders via emodpy) | [EMOD-Hub/EMOD](https://github.com/EMOD-Hub/EMOD) | [Penny et al. 2016](https://doi.org/10.1016/S0140-6736(15)00725-4) (EMOD-DTK was one of the four RTS,S models) |

- **What is costed**: Only a per-unit intervention "cost" that the user supplies; no categories, perspective, or currency semantics beyond a "USD" label on the output channel. The four-model RTS,S analysis applied harmonized provider costs (vaccine consumables, diagnostics, antimalarials, and care) outside all four engines.
- **How costs attach to the model**: During the simulation, unit cost × count of distributions. Every intervention class registers a `Cost_To_Consumer` parameter (e.g. `SimpleBednet` defaults to 3.75, `SimpleVaccine` to 10.0). When an individual intervention is distributed, the node is notified with `cost_per_unit`, weighted by the agent's Monte Carlo weight, and added to `node->Campaign_Cost`; node-level interventions add their unit cost once per node. The accumulated value is written as the `Campaign Cost` channel in the InsetChart report (and `Campaign_Cost` in the spatial report). The parameter description itself suggests a second use: "Setting **Cost_To_Consumer** to zero for all other interventions, and to a non-zero amount for one intervention, provides a convenient way to track the number of times the intervention has been applied in a simulation" ([`utils/iv_params.rc`](https://github.com/EMOD-Hub/EMOD/blob/main/utils/iv_params.rc)).
- **Health outcomes**: None built in for malaria (no DALY code in the engine); DALYs and cases averted are computed post hoc from report outputs, as in Penny et al. 2016.
- **Analyses supported**: Total campaign cost per node and time step; anything else (ICERs, CEACs, optimization) happens downstream.
- **Example**: Cost accumulation in [`campaign/Interventions.cpp`](https://github.com/EMOD-Hub/EMOD/blob/main/campaign/Interventions.cpp) and [`Eradication/NodeEventContext.cpp`](https://github.com/EMOD-Hub/EMOD/blob/main/Eradication/NodeEventContext.cpp):

```cpp
pICCO->notifyCampaignExpenseIncurred( cost_per_unit, pIndiv );
...
float cost = expenseIncurred;
if( pIndiv != nullptr )
{
    cost *= float( pIndiv->GetMonteCarloWeight() );
}
IncrementCampaignCost( cost );
```

And in a campaign file (from the EMOD regression suite, [`Regression/Vector/116_Vector_Serialization_DelayedIntervention/campaign.json`](https://github.com/EMOD-Hub/EMOD/blob/main/Regression/Vector/116_Vector_Serialization_DelayedIntervention/campaign.json)):

```json
{
    "class": "SimpleBednet",
    "Cost_To_Consumer": 1,
    "Repelling_Config": {...},
    "Blocking_Config": {...}
}
```

- **Strengths and limitations**:
  - The simplest possible in-simulation costing: a scalar on each intervention, summed with sampling weights. It costs nothing to maintain and is uniform across all interventions and diseases.
  - A single undifferentiated `Campaign Cost` channel mixes all interventions; separating costs by intervention requires either separate runs or the zero-out trick above, i.e. using cost as a counter.
  - No case-management costs (clinic visits, drugs given via health-seeking) unless those are modeled as campaign interventions, no fixed costs, no discounting, no currency year.
  - I could not verify a flagship EMOD-based malaria cost-effectiveness paper beyond its participation in the RTS,S model comparison; EMOD malaria economics appears to be done downstream in project code.

## Optima Malaria (and Atomica)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| Malaria (Atomica also covers TB, HIV, NCDs, etc.) | Deterministic compartmental (SEIR-type human, plus mosquito), stratified by population group and region | Python | Atomica: [atomicateam/atomica](https://github.com/atomicateam/atomica) (ships `malaria_framework.xlsx`); I could not confirm a public repository for the 2017 Optima Malaria code itself | [Scott et al. 2017](https://doi.org/10.1186/s12936-017-2019-1) |

- **What is costed**: Program spending on testing and treatment, LLINs, IRS, IPTp, SMC, larval source management, MDA, and behavior change communication. Scott et al. 2017 Table 1 gives Nigerian unit costs (e.g. "Testing: $1.95", LLIN "$2.61", IRS "$2.38", BCC "$0.03") from the literature, plus renewal times and "Assumed maximal achievable coverage with large resources".
- **How costs attach to the model**: Inverted relative to the other exemplars: spending is the input and coverage is the output. Each program has a unit cost, an optional capacity constraint, and an optional saturation level; at each time step the model computes the number reachable as spending ÷ unit cost, converts to fractional coverage of the eligible population through a saturating curve, and coverage then modifies model parameters (e.g. "LLINs have been shown to reduce the mosquito-biting rate by 56% for people who own and use them"). Program effects are conditional on utilization for LLINs and IPTp, and utilization is itself raised by the BCC program, so programs interact. In the paper: "As the distribution of spending changes, so does the coverage of each programme in the model according to the unit costs in Table 1 with maximum coverage constrained". Costs are thus computed during the simulation, as part of the forward model.
- **Health outcomes**: Incidence and malaria-attributable mortality (the optimization objectives). DALYs were discussed as a possible future objective but not used in Scott et al. 2017.
- **Analyses supported**: Allocative-efficiency optimization: "An adaptive stochastic descent optimization algorithm was used to incrementally shift funding between programmes, population groups and regions in order to find the allocation that minimized: (1) incidence; and, (2) mortality", for fixed budgets and incrementally more or less funding (yielding a budget-outcome curve), plus Monte Carlo sensitivity analysis over "the model's structural parameters, unit costs and the effects of programmes".
- **Example**: The cost-coverage machinery in Atomica's [`atomica/programs.py`](https://github.com/atomicateam/atomica/blob/main/atomica/programs.py):

```python
capacity = spending / unit_cost

if self.capacity_constraint.has_data:
    ...
    capacity = np.minimum(capacity_constraint, capacity)
...
if self.saturation.has_data:
    prop_covered = np.divide(capacity, eligible, out=np.full(capacity.shape, np.inf), where=eligible != 0)
    saturation = self.saturation.interpolate(tvec, method="previous")
    prop_covered = 2 * saturation / (1 + exp(-2 * prop_covered / saturation)) - saturation
```

- **Strengths and limitations**:
  - The only exemplar here where spending is a first-class model input, which makes "what is the best allocation of this budget?" a direct optimization over the forward model rather than a post hoc ranking of scenarios.
  - Saturation and capacity constraints give a parsimonious cost-coverage curve with diminishing returns, without needing a fitted production function per intervention.
  - A compartmental, region-stratified model is fast enough to optimize but cannot capture individual-level targeting or heterogeneous delivery costs.
  - Cost-coverage parameters (especially saturation) are often weakly identified from data and dominate the optimization result.

## Schistosomiasis and soil-transmitted helminths (NTD Modelling Consortium)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| *S. mansoni*, *S. haematobium*, STH | Deterministic age-structured worm-burden models; individual-based stochastic (SCHISTOX; the consortium `sch_simulation` model) | R, Python, Julia | [mattg3004/ntd-model-sch](https://github.com/mattg3004/ntd-model-sch); SCHISTOX: [mattg3004/Schistoxpkg.jl](https://github.com/mattg3004/Schistoxpkg.jl) | [Turner et al. 2017](https://doi.org/10.1186/s13071-017-2141-5); [Collyer et al. 2019](https://doi.org/10.1186/s13071-019-3749-4); [Graham et al. 2021](https://doi.org/10.1016/j.idm.2021.01.010) |

- **What is costed**: MDA delivery and drug (praziquantel) costs, school-based vs community-wide; economic costs including the opportunity cost of volunteer distributors; vaccine costs as an unknown to be solved for. Collyer et al. 2019 Table 3 took delivery costs from a WHO-linked regression tool (Fitzpatrick et al., "Benchmarks for the cost per person of mass treatment against neglected tropical diseases", [Shiny app](https://healthy.shinyapps.io/benchmark/)), e.g. delivery "US$0.75" (school, economic) vs "US$0.50" (community, economic), and PZQ at "2.5 × US$0.08 per child"; donated drugs carry zero financial cost but nonzero economic cost.
- **How costs attach to the model**: Post hoc from treatment counts, with a notable split between cost drivers: "The costs for MDA delivery were assumed proportional to the number targeted for treatment (and not the number subsequently treated); while the cost for PZQ tablets was directly dependent on how many were treated" (Collyer et al. 2019). Economies of scale enter because delivery cost per person depends on scale and coverage ("Due to the economies of scale, MDA becomes more cost-effective as coverage increases"). The models' code repositories contain no cost or DALY logic; economics is in paper-specific analysis.
- **Health outcomes**: Deliberately not DALYs. Turner et al. 2017 argue that applying a disability weight to prevalent-case years is "misleading" for estimating morbidity averted by an intervention "because the morbidity associated with schistosomiasis is complex and often not due merely to the presence or absence of infection", and so "did not attempt to estimate DALY averted"; they instead use worm-years averted, prevalent-case years averted, and heavy-infection case years averted (epg ≥ 400). Collyer et al. 2019 used "heavy-intensity infection years averted per US$ spent", discounted at 3% for both costs and effects.
- **Analyses supported**: Incremental cost-effectiveness planes using intermediate (non-DALY) outcomes; threshold analysis to find a "critical vaccination cost, a cost beyond which vaccination may not be economically favorable" relative to MDA; scenario comparison across transmission settings.
- **Example**: Effectiveness metric definition, from Collyer et al. 2019: "we counted the total number of days that each individual has a heavy-intensity infection (HII), as measured by the Kato–Katz test and recorded the total heavy-intensity infection years averted relative to the baseline of no intervention over a 30 year time horizon." This is a person-time-in-state metric computed directly from individual-based model output.
- **Strengths and limitations**:
  - Shows that the "right" effectiveness unit can be disease-specific and contested; a general library must support arbitrary person-time-in-state and event-count outcomes, not only DALYs.
  - The targeted-vs-treated split for cost drivers is a useful, generalizable distinction (cost per person targeted vs per dose consumed).
  - Natural-unit outcomes (heavy-infection years) cannot be compared across diseases, which limits use in priority-setting.
  - Economics is not encoded in the models, so each paper re-implements cost logic.

## Onchocerciasis (EPIONCHO and ONCHOSIM)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| Onchocerciasis (river blindness) | EPIONCHO: deterministic, later individual-based (EPIONCHO-IBM); ONCHOSIM: individual-based stochastic microsimulation | R (EPIONCHO-IBM); ONCHOSIM code not public as far as I could find | [mrc-ide/EPIONCHO.IBM](https://github.com/mrc-ide/EPIONCHO.IBM) | [Turner et al. 2014](https://doi.org/10.1093/cid/ciu467); [Turner et al. 2015](https://doi.org/10.1186/s13071-015-0779-4); [Kim et al. 2015](https://doi.org/10.1371/journal.pntd.0004056); [Kim et al. 2017](https://doi.org/10.1136/bmjgh-2016-000158) |

- **What is costed**: Community-directed treatment with ivermectin (CDTI), surveillance, and, in the Kim et al. work, health workforce and outpatient services and household out-of-pocket payments. Turner et al. 2014 used Ghanaian data: "the economic cost of annual community-directed treatment with ivermectin (CDTI) is $41 536 per target population of 100 000 individuals... and that this would increase by 60% when treating biannually", from the provider perspective including "volunteer community distributors". Kim et al. 2015 distinguished financial costs (what governments and donors pay) from economic costs, valuing donated ivermectin at "$1.5054 per treatment (three 3mg-tablets)" and volunteer time at an opportunity cost, using a micro-costing approach "that allows adjustment for time-variant resource utilization".
- **How costs attach to the model**: Post hoc. Per-population-per-year cost for each MDA frequency (Turner 2014) or per-treatment and per-surveillance unit costs (Kim 2015) are multiplied by the model-projected number of treatment years, which depends on when the model predicts treatment can stop (e.g. microfilarial prevalence below operational thresholds). This is the key coupling: the epidemiological model determines the duration of the program, and long-run savings come from ending MDA earlier.
- **Health outcomes**: DALYs from symptom prevalence. Turner 2014: DALYs "combining the burden of onchocercal disease resulting from blindness, visual impairment, troublesome itching, and premature death into a single metric", estimated with "a disease model that links the dynamic transmission model–derived prevalence and intensity of O. volvulus infection with the burden of onchocercal disease". Kim 2017 used ONCHOSIM symptom prevalence and disability weights of "0.187 for severe itching, 0.033 for low vision and 0.195 for blindness". Both discount at 3%; Turner 2014 used a 50-year time horizon.
- **Analyses supported**: ICERs of biannual vs annual MDA against World Bank thresholds; sensitivity to discount rate and the economic value of donated drugs; investment-case style benefit estimates including income gains ("$5.9 billion" and "$6.4 billion" in Kim 2017) and health workforce needs.
- **Example**: ICER definition from Turner et al. 2014, Table 2: "Incremental cost-effectiveness ratio of biannual MDA: The ratio between the incremental cost of biannual treatment and the incremental number of DALYs averted (ie, over and above those costs and benefits of annual treatment) compared with annual MDA."
- **Strengths and limitations**:
  - Clear financial vs economic cost distinction, essential where drugs are donated and distributors are volunteers.
  - Program duration (time to elimination) is the main cost driver, which ties economics tightly to stopping rules and surveillance logic in the model.
  - Morbidity sub-models (itch, vision loss) are separate layers fed by infection intensity, so DALY quality depends on a second, less validated model.
  - Costs are aggregated per population per year, which hides how cost scales with coverage or geography.

## Lymphatic filariasis (EpiFil, LYMFASIM, TRANSFIL)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| Lymphatic filariasis | EpiFil: deterministic; LYMFASIM and TRANSFIL: individual-based stochastic | Various; a C++ TRANSFIL implementation is at [jmarsh96/TRANSFIL](https://github.com/jmarsh96/TRANSFIL) (I did not find economic code in it) | EpiFil code not found publicly | [Stone et al. 2016](https://doi.org/10.1136/bmjgh-2015-000021) |

- **What is costed**: Programmatic costs "from the perspective of an LF-endemic country's health system": "advocacy, capacity strengthening, coordination and strengthening partnerships, data management, on-going surveillance, monitoring, evaluation and supervision, drug delivery, and administration", plus mapping; health-system savings from averted morbidity management; and worker productivity gains.
- **How costs attach to the model**: Post hoc. Country scale-up scenarios (from Kastner et al.) determine MDA rounds and populations treated over time, which are combined with country-level cost estimates; health-system savings come from model-projected averted morbidity combined with "treatment-seeking behaviour and morbidity management costs"; productivity gains multiply "estimated working days lost as a result of morbidity with country-specific per-worker agricultural wages."
- **Health outcomes**: The authors "extended a previously published deterministic model, EpiFil" to track chronic disease states (hydrocele and lymphoedema incidence) and translated these to DALYs: "symptomatic cases were assigned a DW of 0.11. Age-weighting was not considered in this study, but DALYs were discounted at 3% per year", over a 50-year horizon.
- **Analyses supported**: ICERs per scale-up scenario, probabilistic sensitivity analysis, cost-effectiveness acceptability curves, and monetary net benefit: "the monetary net benefits (MNB) were calculated as the mean incremental DALYs averted multiplied by the decision makers' maximum willingness to pay for a DALY averted minus the mean incremental cost for the scenario."
- **Example**: The extension of a transmission model with chronic-morbidity states purely to support the economic evaluation is itself the instructive pattern: "We extended an LF transmission model to track hydrocele and lymphoedema incidence in order to obtain estimates of the disability adjusted life years (DALYs) averted due to scaling up MDA over a period of 50 years."
- **Strengths and limitations**:
  - Full decision-analytic output set (ICER, CEAC, MNB, savings, productivity), a template for eradication investment cases.
  - Chronic sequelae with long lags mean most DALYs averted occur decades after costs are incurred, making results highly sensitive to discounting and horizon.
  - Costs are attached at country-program level, not to individual treatments, so they cannot respond to within-country targeting.

## Dengue (brief note)

Dengue economic evaluations are mostly done with separate microsimulation or state-transition models rather than with the transmission models that estimate efficacy. A recent example is the Wolbachia replacement CEA for seven Brazilian cities, which used "an individual-based microsimulation State Transition Model to simulate nearly 23 million individuals over a 20-year period" from a societal perspective including productivity costs ([Turner 2024 commentary](https://doi.org/10.1016/j.lana.2024.100789)); a scoping review found nine Wolbachia economic evaluations, mostly favorable for replacement in large urban settings ([Turner et al. 2026](https://doi.org/10.1371/journal.pntd.0014395)). The pattern (area-based intervention cost per km² or per person covered, case-level costs by severity including productivity) is similar to vector control in malaria, so I have not given it a full section.

## Open DALY calculation tools

- **DALY Calculator (`DALY` R package)** by Devleesschauwer et al. ([brechtdv/DALY](https://github.com/brechtdv/DALY)): "Graphical User Interface for Probabilistic DALY Calculation in R" (Tcl/Tk GUI), computing YLD, YLL, and DALYs per outcome with discount rate and uncertainty distributions on inputs; the methodology is described in [Devleesschauwer et al. 2014, "DALY calculation in practice: a stepwise approach"](https://doi.org/10.1007/s00038-014-0553-y). Version 1.5.1 dates from 2016, so it is stable but not actively developed.
- **`postie::dalys()`** (above) is a malaria-specific, simulator-coupled example: disability weights and episode durations as function defaults, life expectancy joined by age band.
- WHO also distributes DALY calculation templates for national burden-of-disease work; I did not verify a specific current URL, so treat this as unconfirmed.

## Cross-cutting patterns

- **Engines emit events; costs and DALYs are post hoc.** Of the seven exemplars, only EMOD (a scalar `Cost_To_Consumer` summed into `Campaign Cost`) and Atomica/Optima (spending → coverage) touch costs inside the simulation. OpenMalaria explicitly calculates costing "outside OpenMalaria" and has removed cost hooks over time; malariasimulation delegates to `postie` and `treasure`; the NTD models keep economics in paper-specific code. A general library should make event and resource-use counting first-class and make costing a thin, declarative layer on top, rather than baking unit costs into interventions.
- **Count what is consumed, not just who is covered.** OpenMalaria costs drugs "only... when taken"; Collyer et al. cost delivery per person targeted but drugs per person treated; `treasure` separates `commodity_*` (quantities) from `cost_*` (unit costs). The library needs distinct counters for targeted, reached, doses consumed, tests used, and visits, by age and subgroup.
- **The cost-coverage relationship is the main modeling choice.** Options seen: linear unit cost (treasure, EMOD); fixed + variable (Winskill 2019); fixed + variable + non-linear Hill-function marginal costs (Winskill 2019); saturating spending→coverage curve with capacity limits (Atomica); per-population-per-year program cost with a multiplier for frequency (Turner 2014). A library should support at least fixed, per-unit, and non-linear coverage-dependent components.
- **Program duration drives cost in elimination settings.** For oncho and LF, the model's predicted stopping time (and surveillance after it) dominates total cost, so stopping rules, surveillance, and post-elimination costs need to be part of intervention definitions.
- **Financial vs economic costs, and donated goods.** NTD work routinely reports both, valuing donated ivermectin and praziquantel and volunteer time at opportunity cost. A cost record should carry its perspective (provider, financial, economic, societal) and whether a payer actually pays it.
- **DALYs are layered on via separate morbidity sub-models and life tables.** Disability weights × episode duration (malaria), × symptom prevalence (oncho), × chronic-state person-time (LF), with YLL from a chosen life table (Butajira, UN WPP). These inputs should be versioned data alongside the model, not hard-coded per paper.
- **Not every disease wants DALYs.** Schistosomiasis modelers argue against prevalence-based DALYs and use worm-years or heavy-infection years. Outcomes should be definable as generic person-time-in-state or event counts, with DALYs as one weighted special case.
- **Expected-value outcomes reduce noise.** OpenMalaria's `expectedDirectDeaths` and `expectedSequelae` sum probabilities rather than realized events, which stabilizes ICER denominators in stochastic ABMs; the same applies to costs and is easy to support if outcomes can be accumulated as probabilities.
- **Analyses beyond ICERs.** Budget-constrained optimization (Optima), stepwise expansion paths (Winskill), threshold/critical-cost analysis (Collyer), CEACs and monetary net benefit (Stone), investment cases with productivity gains (Kim, Patouillard), and multi-model ensembles with harmonized costs (Penny). These all consume the same inputs (scenario × time × stratum tables of costs and outcomes), so a standard tidy output format matters more than any single built-in analysis.
- **Unit-cost provenance is fragile.** The best practice seen is `treasure`: each default unit cost carries its source and year, with explicit CPI inflation and a pinned package version. Cost year, currency, inflation index, and discount start year should be explicit metadata in any shared format.
