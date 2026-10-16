# Tuberculosis and vaccines

Tuberculosis and vaccine-preventable diseases are where global-health economic evaluation is most industrialized: WHO investment cases, Gavi's [Vaccine Investment Strategy](https://www.gavi.org/our-alliance/strategy/vaccine-investment-strategy), and country introduction decisions all rest on a small number of reusable models whose outputs are converted into costs and DALYs. This file collects eight exemplars, chosen to span the main ways costing is attached to a disease model: a GUI planning tool with an ingredients-based costing module (TIME), a dynamic transmission model with a post hoc cost layer (tbvax), decision trees with costs on the nodes (HEdtree), a cross-model output standard (VIMC/Montagu), a dynamic model that emits that standard (DynaMICE), and three static or integrated vaccine tools (PRIME, UNIVAC, and the Kid Risk polio model). Metric definitions (DALY, ICER, net monetary benefit, discounting) are in [metrics.md](metrics.md) and are not repeated here.

## TIME (TB Impact Model and Estimates)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| TB (with HIV and drug resistance) | Deterministic compartmental transmission model, plus a separate costing module | Spectrum (Windows desktop suite from Avenir Health) | Not open source; distributed as a free tool within Spectrum | [Houben et al. 2016, BMC Med](https://doi.org/10.1186/s12916-016-0608-4) (TIME Impact); [TIME Economics slides, TB-MAC 2019](https://tb-mac.org/wp-content/uploads/2019/11/TIME-Econ_TB-Mac-.pdf) |

TIME is a set of TB tools inside Spectrum, the same suite that hosts DemProj, AIM (HIV), and the OneHealth Tool. TIME Impact is the transmission model; TIME Economics is a costing and cost-effectiveness layer built on top of it. Implementation and country support [moved from LSHTM to KNCV and Avenir in 2020](https://www.kncvtbplus.com/articles/news/kncv-takes-over-time-implementation).

- **What is costed**: Service-delivery costs for diagnosis, treatment, and monitoring, built bottom-up from drugs and supplies, personnel time, outpatient visits, and inpatient days; plus "above service delivery" program costs (HR, training, supervision, M&E, infrastructure, TB/HIV activities, etc.), which are entered as a percentage or directly. Default inputs come from the WHO/GTB TB planning and budgeting tool, the OneHealth Tool intervention costing databases, and WHO-CHOICE costs per outpatient visit and inpatient day, with stated plans to incorporate Global Health Cost Consortium (GHCC) and Value TB data ([slides](https://tb-mac.org/wp-content/uploads/2019/11/TIME-Econ_TB-Mac-.pdf)). The perspective is essentially that of the provider/national TB program.
- **How costs attach to the model**: An ingredients approach, summarized on the slides as `Costs = Price per unit * Quantities`. The quantity side comes from five inputs: target population, population in need, delivery channel, intervention coverage, and treatment inputs per service. The key coupling is that target populations are chosen from drop-down lists of TIME Impact outputs (e.g. notified cases by risk group, number of tests by type from the diagnostic algorithm tool), "ensur[ing] consistency between costing and impact assumptions". Costing is therefore computed after the epidemiological projection, from its outputs, inside the same GUI.
- **Health outcomes**: Cases, deaths, and DALYs from TIME Impact for each intervention package.
- **Analyses supported**: Comparison of intervention packages, ICERs and ACERs (average cost-effectiveness ratios versus a null), budgeting for national strategic plans, and investment cases. Country plans have used TIME Impact for impact alongside the OneHealth Tool for costing (e.g. [Sierra Leone's 2016–2020 TB plan costing](https://portal.mohs.gov.sl/wp-content/uploads/2021/04/national-leprosy-and-tb-strategic-plan-costing-2016-2020.pdf)).
- **Example**: From the [TIME Economics slides](https://tb-mac.org/wp-content/uploads/2019/11/TIME-Econ_TB-Mac-.pdf): "Intervention costing • Costs = Price per unit * Quantities • Inputs for TIME Econ to calculate costs 1. Target population 2. Population in need 3. Delivery channel 4. Intervention coverage 5. Treatment inputs e.g. medicines, health personnel".
- **Strengths and limitations**:
    - Strength: the costing module selects its quantities directly from model outputs, so a scenario change in coverage automatically changes both cost and impact.
    - Strength: designed for national TB program staff; every input is editable but defaults allow ballpark results.
    - Limitation: closed, GUI-only, Windows; there is no scriptable API, so batch PSA or reproducible pipelines are hard.
    - Limitation: above-service-delivery costs are a percentage or a lump sum, not linked to model quantities.

## tbvax and the LMIC TB vaccine CEA (WHO investment case)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| TB (with HIV), novel vaccines (M72/AS01E, BCG revaccination) | Deterministic age-structured compartmental transmission model, calibrated per country with history matching/emulation; separate post hoc CEA script | R (model specified in XML) | [lshtm-tbmg/tbvax-pub](https://github.com/lshtm-tbmg/tbvax-pub) (archived on [Zenodo](https://doi.org/10.5281/zenodo.6421372)) | [Clark et al. 2023, Lancet Glob Health](https://doi.org/10.1016/s2214-109x(23)00045-1) (epi); [Portnoy et al. 2023, PLOS Med](https://doi.org/10.1371/journal.pmed.1004155) (CEA); [Portnoy et al. 2023, BMJ Glob Health](https://doi.org/10.1136/bmjgh-2023-012466) (equity, financial protection); [WHO 2022 investment case](https://www.who.int/publications/i/item/9789240064690) |

This is the model behind the WHO-commissioned investment case for new TB vaccines (LSHTM with Harvard), applied to 105 low- and middle-income countries. The epidemiological model and the economic model are separate programs connected by output files.

- **What is costed**: Vaccine price ($4.60/dose base case), injection supplies ($0.11), 5% wastage, country-specific delivery costs (infant vs adolescent/adult), one-time introduction costs per targeted individual; TB diagnosis and treatment (drug-susceptible and rifampicin-resistant separately); ART; and, for the societal perspective, patient non-medical costs and productivity losses. Unit costs come from GHCC and WHO patient cost surveys via meta-regressions on GDP per capita, inflated to 2020 USD ([Portnoy et al. 2023](https://doi.org/10.1371/journal.pmed.1004155)). Two perspectives: health system and societal.
- **How costs attach to the model**: Unit cost × service-volume indicator, computed post hoc. The ODE model is instrumented with "counter" compartments: every transition whose volume matters for costing is duplicated into an absorbing `...count` stage with the same rate, so the flow into that stage is the number of events (notifications, treatment initiations). The XML switches on `econ.output="true"` to write population, deaths, and vaccinations per year and single year of age. The CEA script ([`cea-LMIC/tb_cea.R`](https://github.com/lshtm-tbmg/tbvax-pub/blob/66cb4841139a3590ef29b080d9fcd5dc6eefca75/cea-LMIC/tb_cea.R)) then multiplies yearly notifications by per-country unit-cost draws (one CSV column per PSA draw) and vaccinations by price + supplies + delivery, with introduction costs in year one.
- **Health outcomes**: DALYs = YLL + YLD. YLLs use GBD 2019 reference life expectancy at age of death, discounted to the time of death in continuous time; YLDs are person-time in TB (and HIV/ART) states × GBD disability weights (drawn per PSA run). Costs and DALYs are discounted at 3% to the vaccine introduction year (2028), over 2028–2050.
- **Analyses supported**: ICERs under both perspectives versus no new vaccine; thresholds at 1× GDP per capita, opportunity-cost-based thresholds, and $100/DALY; cost-saving classification; incremental net monetary benefit; PSA via 1,000 Monte Carlo draws; extensive scenario analysis (price, coverage, delivery strategy, efficacy, duration). The companion repositories also run equity (by wealth quintile) and macroeconomic analyses.
- **Example**: Counter compartments in the model input ([XML](https://github.com/lshtm-tbmg/tbvax-pub/blob/66cb4841139a3590ef29b080d9fcd5dc6eefca75/single-country-IND/countries/IND/parameters/M72econ/XMLinput_M72_AI_POD_50_10yr_med_2030.xml#L197-L199)), then unit cost × count in the CEA script ([L344–L349](https://github.com/lshtm-tbmg/tbvax-pub/blob/66cb4841139a3590ef29b080d9fcd5dc6eefca75/cea-LMIC/tb_cea.R#L344-L349), [L267–L269](https://github.com/lshtm-tbmg/tbvax-pub/blob/66cb4841139a3590ef29b080d9fcd5dc6eefca75/cea-LMIC/tb_cea.R#L267-L269)):

```xml
      <treatment.matrix name="init">
        <transition from="Dc" to="T" rate="eta*j4/(1-pE)"/>
        <transition from="Dc" to="DcTcount" rate="eta*j4/(1-pE)"/>
```

```r
      ## Calculate testing and treatment costs by scenario, DS/RR
      output_year$test_ds_und <- notif_DS_year*test_ds_cty[,counter+4]
      output_year$test_rr_und <- notif_RR_year*test_rr_cty[,counter+4]
      output_year$treat_ds_und <- notif_DS_year*treat_ds_cty[,counter+4]
      output_year$treat_rr_und <- notif_RR_year*treat_rr_cty[,counter+4]
...
      YLL_working$YLL_raw <- YLL_working$ALLdeaths*YLL_working$CLE
      # Discount YLLs to time of death using continuous time discounting
      YLL_working$YLL_dtod <- YLL_working$ALLdeaths*((1 - exp(-r * YLL_working$CLE)) / r)
```

- **Strengths and limitations**:
    - Strength: full dynamic (herd) effects of vaccination flow through to costs averted, and cost uncertainty is propagated by indexing each epidemiological run against a matching cost draw.
    - Strength: the counter-compartment trick is a clean, generic way to make an ODE emit event counts without changing the dynamics.
    - Limitation: the cost layer is a monolithic script with hard-coded scenario branches (e.g. a separate `if` per delivery scenario for vaccine costs), so adding a cost category means editing code in several places.
    - Limitation: the link between model and economics is file names and column positions (`counter+4`), not a typed interface.

## HEdtree decision-tree TB CEAs (Dodd et al.)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| Pediatric TB diagnosis, household contact management, TPT | Decision trees evaluated over PSA samples, with discounted life-years from life tables | R (`data.tree`, `data.table`) | [petedodd/HEdtree](https://github.com/petedodd/HEdtree), [petedodd/discly](https://github.com/petedodd/discly); applications [petedodd/TBSdecent](https://github.com/petedodd/TBSdecent), [petedodd/tippi](https://github.com/petedodd/tippi) | [d'Elbée et al. 2024, eClinicalMedicine](https://doi.org/10.1016/j.eclinm.2024.102528) (TB-Speed decentralization); [TIPPI CEA, PLOS Med 2023](https://doi.org/10.1371/journal.pmed.1004285) |

Pete Dodd's (Sheffield) TB economic evaluations mostly avoid transmission models altogether: care cascades are written as decision trees in an indented text format, each node carries a probability expression and a cost expression (as strings referencing named parameters), and the tree is compiled into vectorized R functions that are evaluated over a PSA table.

- **What is costed**: Health-system costs of each cascade step: screening assessments, reassessment, clinical exam, chest X-ray, Xpert testing and sample collection, TB treatment, TPT, contact investigation. Unit costs are country-specific and come from the trial-based costing studies (e.g. [`TBS.DECENT.costs.csv`](https://github.com/petedodd/TBSdecent/blob/c1ee99c2332649c7d0091b7c3c6745c9629cc398/indata/TBS.DECENT.costs.csv) lists low/high values per activity for seven countries); TIPPI separates standard-of-care and incremental unit costs per activity.
- **How costs attach to the model**: Costs are attributes of tree nodes. `getAQ()` walks the tree and builds a string expression for the expected value of any node attribute, `cost + Σ p_child × (expected cost of child)`, which `makeTfuns()` parses into a function of a data frame of parameters. The same mechanism handles any accumulating quantity (deaths, treatment initiations, number screened), so the cost "model" and the outcome "model" are the same tree with different attribute names. Per-node labels are read from a CSV, so a cost attaches to the node at which the resource is used. Everything is computed post hoc, in a single vectorized pass over all PSA rows.
- **Health outcomes**: DALYs averted approximated by discounted life-years lost from TB deaths: deaths at each node × discounted remaining life expectancy at that age, from `discly()` (UN life tables, exponential discounting, optional mortality hazard ratio). Both 0% and 3% discounted values are computed.
- **Analyses supported**: Incremental cost per DALY averted (and per death averted, per treatment initiation), cost-effectiveness acceptability curves, PSA (`makePSA()` builds the sample from a parameter table of distributions), and a separate budget-impact run (`decent_run.R` takes `BIA` or `CEA` as its first argument).
- **Example**: The generic tree evaluator ([`getAQ.R`](https://github.com/petedodd/HEdtree/blob/afe21215618b350cacb1b5dd4025d97d6919fa40/R/getAQ.R#L15-L26)), and rows of the TB-Speed tree with probability and cost expressions per node ([`IDHd1.csv`](https://github.com/petedodd/TBSdecent/blob/c1ee99c2332649c7d0091b7c3c6745c9629cc398/indata/CSV/IDHd1.csv), first columns only):

```r
getAQ <- function(node,qnt='cost') {
    ss <- node[[qnt]]
    if(!node$isRoot & is.null(node$p))
      stop(paste0('Probability not found for node:', node$name,'!'))
    if(is.null(ss)) ss <- '0'
    if( node$leafCount > 0 ){
        for( kid in node$children ){
            ss <- paste0(ss,'+(',kid$p,')*(',getAQ(kid,qnt=qnt),')')
        }
    }
    ss
}
```

```
levelName,p,cost,deaths,lives,...
 ¦   ¦--Systematic TB screening      ,d.idh.dh.assess,c.d.idh.dh.sassess,0,0,...
 ¦   ¦   ¦--Presumptive TB           ,d.dh.prsmptv*d.idh.dh.presumed,0,0,0,...
```

- **Strengths and limitations**:
    - Strength: costs and outcomes share one mechanism (an attribute on a node, accumulated by probability-weighted sums), which makes adding a new cost line or counter trivial.
    - Strength: trees are data, not code; the cascade structure is reviewable by non-programmers.
    - Limitation: no transmission or time dynamics, so indirect effects of better case finding are absent (the papers discuss this explicitly); long-run outcomes are collapsed into a single discounted life-years number.
    - Limitation: expressions are strings evaluated with `eval`, so typos surface only at run time.

## VIMC / Montagu standardized burden outputs

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| 10+ vaccine-preventable diseases (HepB, Hib, HPV, JE, measles, MenA, PCV, rotavirus, rubella, YF, ...) across ~112 countries | Model-agnostic output standard; each disease has 2+ independent models (static and dynamic) | Any (templates are CSV); post-processing in R | [vimc/montagu](https://github.com/vimc/montagu) (platform), [vimc/vimpact](https://github.com/vimc/vimpact) (impact calculation), [vimc/vimcheck](https://github.com/vimc/vimcheck) (diagnostics) | [Li et al. 2021, Lancet](https://doi.org/10.1016/S0140-6736(20)32657-X); [Toor et al. 2021, eLife](https://doi.org/10.7554/eLife.67635) |

The Vaccine Impact Modelling Consortium (VIMC), jointly funded by Gavi and the Gates Foundation, coordinates about 20 independent modeling groups. VIMC itself does not cost anything; its contribution is a rigid output contract that makes burden from heterogeneous models additive and comparable, and that downstream economic analyses and Gavi's investment decisions can consume.

- **What is costed**: Nothing within VIMC. Coverage scenarios ("touchstones") are provided to groups through Montagu; groups return burden; costing and ROI are separate downstream analyses that take VIMC deaths and DALYs averted as inputs.
- **How costs attach to the model**: Indirectly, through a standard output schema. Every model, whatever its internal structure, must report the same rows: disease × year × single year of age × country, with `cohort_size`, `cases`, `deaths`, `dalys` (and optionally `yll` or disease-specific outcomes such as HepB cirrhosis deaths), for each scenario including no-vaccination. Each group computes DALYs its own way; VIMC fixes only the format and runs checks (e.g. `vimcheck` compares `cohort_size` against UN WPP). Impact is then computed centrally by `vimpact` as baseline minus focal burden, attributed by one of four methods: calendar year, birth year (lifetime impact of a birth cohort), or year of vaccination by activity type or by birth cohort (the latter two divide impact by fully vaccinated persons (FVPs) to give impact ratios per FVP that can be applied to new coverage forecasts).
- **Health outcomes**: Deaths, DALYs, cases, and YLL averted; groups submit central estimates and, in some rounds, stochastic (PSA) runs.
- **Analyses supported**: Deaths/DALYs averted by country, year, and cohort; impact per FVP; model ensembles across groups; inputs for Gavi VIS, ROI, and investment cases. Not ICERs directly.
- **Example**: The central burden template shipped with [`vimcheck`](https://github.com/vimc/vimcheck/blob/822ad66940d241060f5c80c35deb362b90d5283c/inst/extdata/central-burden-template.csv), and the impact calculation in [`vimpact`](https://github.com/vimc/vimpact/blob/ca37541f9445bf5ef20431964537f5c438c46a4f/R/impact_central.R#L346-L351):

```
"disease","year","age","country","country_name","cases","dalys","deaths","yll","cohort_size"
"dummy_disease",2000,0,"RFP","Request for Proposal",NA,NA,NA,NA,NA
"dummy_disease",2001,0,"RFP","Request for Proposal",NA,NA,NA,NA,NA
```

```r
  ## Calculate impact outside of Postgres otherwise get
  ## precision errors on 0 value entries
  out %>%
    dplyr::mutate(impact = baseline_val - focal_val) %>%
    dplyr::select(-baseline_val, -focal_val)
```

- **Strengths and limitations**:
    - Strength: a long-format, age × year × country table is the lowest common denominator that both static cohort and dynamic transmission models can fill, so ensembles become possible.
    - Strength: impact attribution (calendar vs birth cohort vs year of vaccination) is made explicit and computed once, centrally, rather than by each group.
    - Limitation: no resource-use outputs (doses, visits, hospitalizations) are in the template, so downstream costing has to re-derive service volumes, typically from coverage × target population rather than from the models.
    - Limitation: DALY methods (disability weights, life tables, durations) are left to each group, so DALYs are less harmonized than deaths.

## DynaMICE (measles)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| Measles (routine MCV1/MCV2 and SIAs) | Deterministic, finely age-stratified SIRV compartmental transmission model | R with Fortran-95 core | [lshtm-vimc/dynamice](https://github.com/lshtm-vimc/dynamice) | [Fu et al. 2021, BMC Med](https://doi.org/10.1186/s12916-021-02157-4); [Verguet et al. 2015, Vaccine](https://doi.org/10.1016/j.vaccine.2014.11.050) |

DynaMICE (Dynamic Measles Immunisation Calculation Engine) is one of VIMC's two measles models and illustrates how a dynamic model is wrapped to emit the VIMC template.

- **What is costed**: Nothing directly; it produces burden for VIMC and for WHO/Gavi analyses of SIA strategy.
- **How costs attach to the model**: The transmission model produces cases only. Deaths and DALYs are attached in a separate post-processing function, `estimate_deaths_dalys()`, which joins case-fatality ratios (two alternative CFR sources, one time-varying by country and year) and remaining life expectancy onto the case table, then reshapes to `data_template`, the VIMC template. This is the hook where a cost layer would attach (cost per case by age, cost per SIA dose), though DynaMICE does not do it.
- **Health outcomes**: Deaths = cases × CFR (by under-5/over-5); DALYs = YLD + YLL with a flat 0.002 DALYs per nonfatal case and remaining life expectancy per death. PSA runs vary a mortality multiplier alongside the CFR draws. No discounting in the template (VIMC outputs are undiscounted).
- **Analyses supported**: Deaths, DALYs, and cases averted by scenario and cohort; sensitivity to evidence updates (CFR, contact matrices, vaccine efficacy by age, SIA targeting).
- **Example**: The DALY step ([`R/functions.R`](https://github.com/lshtm-vimc/dynamice/blob/6701cc8dd52ff736005ec1f5ae099d659ce97e8e/R/functions.R#L1408-L1411)):

```r
  # ----------------------------------------------------------------------------
  # DALYs
  # ----------------------------------------------------------------------------
  # calculate dalys = (ylds) + (ylls)
  burden [, dalys := ((cases - deaths) * 0.002) + (deaths * remain_lexp)]
```

- **Strengths and limitations**:
    - Strength: a clean separation of epidemiology (cases) from valuation (CFR, DALYs), so outcome assumptions can be swapped without rerunning the transmission model.
    - Strength: the same pattern (model → event table → join valuation tables → standard template) generalizes directly to costs.
    - Limitation: the valuation is crude (a single YLD constant; CFR halved above age 5), which is typical when burden rather than cost-effectiveness is the target.
    - Limitation: the Fortran core and R wrapper make the model hard to extend beyond its measles-specific structure.

## PRIME (HPV)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| HPV / cervical cancer | Static, proportional-impact cohort model (single-age cohorts of girls) | R (originally an Excel tool) | [lshtm-vimc/prime](https://github.com/lshtm-vimc/prime) | [Jit et al. 2014, Lancet Glob Health](https://doi.org/10.1016/S2214-109X(14)70237-2) |

PRIME (Papillomavirus Rapid Interface for Modelling and Economics) is the canonical "rapid" static vaccine CEA: for each country it takes age-specific cervical cancer incidence and mortality, applies them to a vaccinated birth cohort through a life table, and reduces them in proportion to effective coverage. It is also one of VIMC's HPV models.

- **What is costed**: Vaccine cost per fully vaccinated girl (price + delivery, entered as one number) and cervical cancer treatment cost per case (country-specific, from a bundled dataset, with an option to adjust). Health-system perspective.
- **How costs attach to the model**: Cost per event × expected events, entirely within a static cohort table. `RunCohort()` builds a pre-vaccination table by age with incidence, mortality, YLL, YLD, and `cost.cecx = incidence * cost_cancer`; the post-vaccination table is the same table multiplied by `(1 - effective_coverage)`. `analyseCosts()` then sums over age, takes vaccine cost = vaccinated cohort × `vaccine_cost`, nets off treatment costs saved, and forms ratios. Because the model is linear, costs and outcomes are computed in the same pass, with no separate simulation.
- **Health outcomes**: Cervical cancer cases and deaths prevented; life-years saved (YLL from remaining life expectancy at age of death); DALYs with GBD 2001 or GBD 2017 disability weights for diagnosis, control, metastatic, and terminal phases. Discounting (default 3% for both costs and health) is applied from the age of vaccination; YLLs use the continuous-time formula `(1 - exp(-r*L))/r`.
- **Analyses supported**: Cost per death, life-year, and DALY averted; cost-effectiveness against 1× and 3× GDP per capita; a threshold ("cut-off") vaccine cost at which vaccination would be cost-effective; PSA via Latin hypercube sampling (`lhs` dependency); batch runs over all countries and VIMC coverage files.
- **Example**: The static cohort table and proportional impact ([`R/functions.R`](https://github.com/lshtm-vimc/prime/blob/e69720b427f46db7c1a53e9cb06ecb6cd71b331a/R/functions.R#L1432-L1450)), and the threshold price ([L2456–L2471](https://github.com/lshtm-vimc/prime/blob/e69720b427f46db7c1a53e9cb06ecb6cd71b331a/R/functions.R#L2456-L2471)):

```r
  # expected number of cases, deaths, dalys, and costs (static)
  out.pre <- data.table (
    age         = ages,
    cohort_size = cohort * lifetab [, lx.adj],
    vaccinated  = rep (0, length(ages)),
    immunized   = rep (0, length(ages)),
    inc.cecx    = incidence,
    mort.cecx   = mortality_cecx,
    lifey       = mortality_cecx * lexp,
...
    disability  = yld,
    cost.cecx   = incidence * cost_cancer,
    prev.cecx   = prevalence
  )

  out.post                   <- out.pre
  out.post                   <- out.post * (1 - coverage [, effective_coverage])
```

```r
    costeffect [variable == "Cut-off price", d] <-
      (unlist (costeffect [variable == "Costs saved",
                           d,
                           with = FALSE],
               use.names = FALSE) +
         (unlist (costeffect [variable == "Life years saved",
                              d,
                              with = FALSE],
                  use.names = FALSE) +
            unlist (costeffect [variable == "Nonfatal DALYs prevented",
                                d,
                                with = FALSE],
                    use.names = FALSE) ) *
         gdp_per_capita) /
      unlist (costeffect [variable == "Vac cohort size",
```

- **Strengths and limitations**:
    - Strength: transparent and fast enough to run for 179 countries; the threshold vaccine cost falls out in closed form because the model is linear.
    - Strength: costs, outcomes, discounted and undiscounted variants all live as columns of one age-indexed table, which is easy to audit.
    - Limitation: no herd effects, no screening interaction, lifelong protection assumed; static models understate the benefit of high-coverage HPV programs.
    - Limitation: vaccine cost is a single per-girl number, so delivery-strategy costing (school vs facility, number of doses) is outside the model.

## UNIVAC (and TRIVAC, ProVac)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| Rotavirus, pneumococcus, Hib, HPV, RSV (maternal vaccine and infant mAb), and others | Proportionate-outcomes static cohort model, by week of age to age 5, over the lifetime of target birth cohorts | Excel + VBA (per the 2023 paper; the [TechNet-21 listing](https://technet-21.org/en/resources/tool/univac) indicates a newer R-based interface, not verified here) | Not public on GitHub; distributed via PAHO ProVac and LSHTM training | [Clark et al. 2013, Vaccine](https://doi.org/10.1016/j.vaccine.2013.05.045) (TRIVAC); [Debellut et al. 2019, Lancet Glob Health](https://doi.org/10.1016/s2214-109x(19)30439-5) (rotavirus, 73 Gavi countries); [Mahmud et al. 2023, BMC Med](https://doi.org/10.1186/s12916-023-02827-5) (RSV) |

UNIVAC (Andrew Clark, LSHTM) grew out of TRIVAC, the Hib/pneumococcal/rotavirus tool developed with PAHO's [ProVac Initiative](https://www.paho.org/en/provac-toolkit) to support national immunization technical advisory groups. It is the workhorse behind many Gavi-country vaccine introduction CEAs, including the rotavirus re-evaluation by Debellut, Clark, Pecenka et al.

- **What is costed**: Intervention program costs (price per dose; wastage of doses, syringes, and safety boxes; international handling and transport fees; incremental health-system delivery and introduction costs) and healthcare costs averted (per clinic visit and per hospital admission, by severity). Government and/or societal perspective; adherence to WHO guidelines for economic evaluation of immunization programs is recommended, with a standard WHO reporting checklist ([Mahmud et al. 2023](https://doi.org/10.1186/s12916-023-02827-5)).
- **How costs attach to the model**: Unit cost × count of events, in a static cohort. Disease event rates (cases, clinic visits, admissions, deaths, by severity) per 100,000 under-5s are entered once, distributed across 260 weeks of age by a parametric (Burr) age distribution, and multiplied by person-years at risk in the cohort, then reduced by coverage × efficacy in each week of age (with dose timeliness and waning). Each resulting count is multiplied by its unit cost; healthcare costs saved are subtracted from program costs to give incremental net cost. All of this is computed in the spreadsheet in one pass; there is no simulation.
- **Health outcomes**: Cases, visits, admissions, deaths, and DALYs averted (YLD from disability weights and durations by severity; YLL from life expectancy at age of death), discounted (typically 3%) over the cohort lifetime.
- **Analyses supported**: Cost per DALY averted, cost-saving classification, comparison against GDP-based or opportunity-cost thresholds, built-in sensitivity analysis options with automatically generated charts, multi-cohort intervention periods (e.g. 2025–2034), and cross-model comparison (the RSV paper benchmarks UNIVAC against PATH's Stata static cohort model).
- **Example**: The core event equation, from [Mahmud et al. 2023](https://doi.org/10.1186/s12916-023-02827-5): for a given week w of age, the number of disease events is `PY * D * Aw * ( 1 - ( C1w * E1w ) )`, "where PY is the number of person-years lived between birth and age 5.0 years in birth cohort of interest ...; D is the disease event rate (per 100,000 per year) among children < 5 years of age before the introduction of a maternal vaccine or infant mAb; Aw is the proportion of disease events < 5 years of age in week w of age; C1w is the intervention coverage estimated in week w of age (after considering realistic delays in dose administration/timeliness), and E1w is the efficacy estimated in week w of age, adjusted for any waning from the time of dose administration."
- **Strengths and limitations**:
    - Strength: one generic equation covers many vaccines; differences between diseases are data (event rates, age distributions, unit costs), not code.
    - Strength: built for country ownership, which is the main reason static cohort tools dominate national introduction decisions.
    - Limitation: no indirect effects; acceptable for rotavirus or RSV mAbs but conservative for pneumococcal or measles vaccines.
    - Limitation: spreadsheet distribution makes version control, batch PSA, and reuse in other pipelines difficult.

## Kid Risk integrated polio model (Thompson, Duintjer Tebbens, Kalkowska)

| Disease(s) | Paradigm | Language | Code | Key papers |
|---|---|---|---|---|
| Poliovirus (WPV, VDPV, VAPP; OPV/IPV policies) | Integrated model: differential-equation-based (DEB) global poliovirus transmission and OPV-evolution model, run deterministically and as stochastic realizations, coupled to cost and valuation components | Java (Eclipse), run on AWS EC2 | Not public | [Duintjer Tebbens et al. 2011, Vaccine](https://doi.org/10.1016/j.vaccine.2010.10.026); [Thompson & Kalkowska 2021, Risk Anal](https://doi.org/10.1111/risa.13665) |

The Kid Risk models are the longest-running integrated dynamic-economic vaccine models in global health, used to estimate the incremental net benefits (INB) of the Global Polio Eradication Initiative (GPEI) and of post-eradication OPV cessation strategies.

- **What is costed**: Routine immunization and supplementary immunization activity (SIA) costs (vaccine and delivery, by OPV/IPV), surveillance, outbreak response, stockpiles, containment, and global program costs (historical costs from the GPEI external funds database and financial resource requirements, with an assumed 1:1 ratio of domestic to external contributions); treatment costs for paralytic cases; and a societal willingness-to-pay per case to capture productivity loss. All are stratified by World Bank income level (WBIL), converted to constant USD, and discounted at 3%.
- **How costs attach to the model**: Unit cost × modeled activity counts (doses by schedule and SIA, by subpopulation and year) plus cost per paralytic case × modeled cases; global program costs are allocated to income groups in proportion to the number of children. The transmission model and the economic accounting run in the same Java program, so each stochastic realization (e.g. with or without a post-cessation outbreak) carries its own outbreak-response costs.
- **Health outcomes**: Paralytic polio cases prevented, and DALYs per case by year and income group (from population-weighted life expectancy); deaths in some analyses.
- **Analyses supported**: ICERs per case prevented and per DALY saved, reported only by income group "given the potential for misleading ratios when aggregated over different income groups"; INB with each DALY valued at GNI per capita; threshold values of cost per case for positive net benefits; 100 stochastic iterations per policy option; scenario analyses on discount rate and eradication date.
- **Example**: The valuation rule, verbatim from [Duintjer Tebbens et al.](https://doi.org/10.1016/j.vaccine.2010.10.026): "WHO recommends that 'in the absence of data, analysts might use estimates of the gross national income (GNI) or GDP per capita to value lost time,' ... Consequently, we value each DALY saved as equal to one year of per capita income". [Thompson & Kalkowska 2021](https://doi.org/10.1111/risa.13665) keep the same INB method but also apply health opportunity cost thresholds of 0.2, 0.2, and 0.6 × GNI per capita for low, lower-middle, and upper-middle income groups.
- **Strengths and limitations**:
    - Strength: true dynamic-economic coupling, including the costs of stochastic tail events (outbreaks after OPV cessation), which a post hoc cost layer on mean outputs would miss.
    - Strength: cost-benefit (INB) rather than only cost-effectiveness, which is the relevant framing for eradication.
    - Limitation: closed code; results are reproducible only through extensive appendices.
    - Limitation: costs and valuation are by income group, not by country, which limits country-level budget impact use.

## Cross-cutting patterns

- **Costing is almost always post hoc on event counts.** In every open exemplar (tbvax, HEdtree, PRIME, UNIVAC, DynaMICE's DALY step), the disease model emits counts of events by year and age (doses, notifications, treatment starts, cases, deaths) and a separate layer multiplies them by unit costs and valuation weights. Only the polio model computes costs inside the simulation, and it does so to capture costs that depend on stochastic events. A general library needs first-class, typed event counters (what tbvax fakes with duplicate `...count` compartments) far more than it needs in-loop cost arithmetic.
- **Three cost mechanisms cover nearly everything**: unit cost × event count (doses, tests, treatment initiations, visits, admissions); cost per person-time in a state (ART-years, time on treatment); and fixed or one-time costs (introduction cost per targeted person, program overheads as a percentage or lump sum). The polio and TIME examples add allocation rules (global costs split by number of children or by delivery channel). tbsim already gestures at the first by documenting `cost=` on `ss.Vaccine` and `ss.Treatment` ([source](https://github.com/starsimhub/tbsim/blob/v1.0.0/tbsim/interventions/prevention.py)).
- **Static cohort vs dynamic transmission is the main methodological split**, and it maps to purpose: country-owned introduction decisions use static cohort tools (UNIVAC, PRIME, ProVac), while global investment cases and anything with herd effects use dynamic models (tbvax, DynaMICE, Kid Risk, and the typhoid conjugate vaccine CEA of [Bilcke et al. 2019](https://doi.org/10.1016/s1473-3099(18)30804-1), which combined an age-structured transmission model with country-level costs). A library that can run both paradigms from one model specification, with the same cost layer on top, would let analysts quantify the indirect-effects gap rather than argue about it.
- **The long-format age × year × location × scenario table is the de facto interchange format.** VIMC formalizes it; DynaMICE, PRIME, and tbvax all produce something equivalent internally. Costs, DALYs, and impact attribution are then joins and group-bys on this table. Matching that schema (and VIMC's column names) as an export target would make a library's outputs immediately usable by existing economic pipelines.
- **Impact attribution is a choice that must be explicit.** Calendar-year, birth-cohort (lifetime), and year-of-vaccination attribution (`vimpact`) give different answers, and static cohort tools implicitly use birth-cohort attribution while dynamic models naturally report by calendar year. Costs must use the same attribution as health outcomes, and discounting must use a stated reference year (tbvax discounts to the introduction year; PRIME to the age of vaccination; polio to 1988 or 2019).
- **DALYs are computed in at least four slightly different ways**: YLL from GBD reference life expectancy vs national life tables; YLL discounted in continuous time to the time of death (`(1 - exp(-r*L))/r`, used verbatim in both PRIME and tbvax) vs undiscounted (VIMC); YLD as person-time in a state × disability weight (tbvax) vs a constant per case (DynaMICE) vs phase durations (PRIME). Post-TB sequelae, which [Menzies et al. 2021](https://doi.org/10.1016/s2214-109x(21)00367-3) estimate account for nearly half of lifetime TB DALYs, are usually omitted. A library should let the DALY recipe be a swappable component with these options, rather than a single hard-coded formula.
- **Uncertainty is propagated by pairing epi draws with cost draws.** tbvax stores unit costs as one CSV column per PSA draw indexed alongside epidemiological runs; HEdtree builds one PSA table containing both; PRIME uses Latin hypercube samples. The common need is a run identifier that ties together a parameter draw, its simulated event counts, and its cost and valuation draws.
- **Analyses requested are remarkably consistent**: ICER vs a comparator (health-system and societal perspectives), cost-saving classification, threshold comparisons (GDP-based, opportunity-cost-based, or fixed like $100/DALY), threshold (maximum) vaccine cost, CEACs, budget impact, and, for eradication and investment cases, net monetary benefit and return on investment. All are simple functions of discounted incremental costs and outcomes, so a library can provide them generically once costs and outcomes are standardized.
- **Spreadsheet and GUI tools dominate country use** (TIME, UNIVAC, ProVac, the original PRIME), and their key design feature is that every unit cost and rate is an editable, documented input with defaults. A code library aiming to replace or feed them needs a similarly flat, tabular input format for unit costs (activity × location × value, with uncertainty), like TB-Speed's `TBS.DECENT.costs.csv`, not costs buried as arguments in code.
