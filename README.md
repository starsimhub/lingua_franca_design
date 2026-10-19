# A lingua franca for epi modeling

**Version:** 1.3 | **Date:** 2026.10.19 | **Status:** Implementation in progress

## Introduction

This project describes the design of a _lingua franca_ for epi modeling. The lingua franca should:

- Capture the best aspects of all existing epi models (in terms of flexibility, simplicity, and elegance), and improve upon them when possible. In other words, **a model should always be easier to write with the lingua franca than without it**. A concrete definition of this is that compared to existing epi models, implementing a model in the lingua franca should require no more lines of code than the original, and be as fast or faster.
- Be AI-native, serving as a rigorous-yet-simple and deterministic representation of modeling concepts (as expressed as prose or using other modeling frameworks) into code.
- Provide a unified representation across different modeling paradigms, including at least:
    - Compartmental/ODE models
    - Stochastic compartmental/SDE models
    - Metapopulation models
    - Agent-based models
- Allow interconversion between modeling frameworks (e.g. EpiModel to epydemix) and paradigms (e.g. compartmental to agent-based).

## Motivation

Why do we need a lingua franca? Why can't LLMs just write disease models directly? Two main reasons:

- AI is most efficient and accurate as a thin wrapper for code that already provides most desired functionality; imagine an LLM trying to correctly do a dataframe merge without access to R or `pandas`.
- A lingua franca serves as a rigorous source of truth for comparing other models to, and provides a robust endpoint (MCP) to develop AI skills, guardrails, and evals against. If a compartmental model written in R with EpiModel gives a different result than an agent-based model written in Python in Vivarium, currently it's extremely difficult to understand why. A lingua franca allows the differences between models to be clarified and explored.

While AI is not always very creative, we can be certain that the lingua franca can do *at least as well* as existing models. AI is the perfect tool for this: it can easily review all existing models, see who did it best, and at minimum copy that implementation (and improve upon it as possible).

We used Starsim as the base for the lingua franca because agent-based modeling is the most complex paradigm; all other models can be expressed as agent-based models, and of course real diseases act on agents (humans). The lingua franca will be released as Starsim v4. You can see the [current code](https://github.com/starsimhub/starsim/tree/v4) and the draft [PR #1437](https://github.com/starsimhub/starsim/pull/1437).

## Project structure

The lingua franca was built up in stages:

| | Section | What it is |
|---|---|---|
| 1 | [Approaches](approaches/) | A review of the current approaches used in the epi modeling landscape, based on the [disease modeling landscape](https://starsim.org/disease_modeling_landscape) |
| 2 | [Best practices](best-practices/) | A distillation of the modeling landscape into best practices for each aspect of building disease models |
| 3 | [Design](design/) | The design of the language, written as an extension of Starsim |
| 4 | [Examples](examples/) | Other frameworks' own example models, and their translations into Starsim v4 |
| 5 | [Compare](webapp/) | A tool for comparing example models between the original source and the lingua franca |

The [status page](admin/implementation.md) tracks how much has been implemented so far.

## AI disclaimer

AI tools (mostly Claude) were used to summarize information, compare and assess frameworks, extract code examples, and create vignettes. Assessments and design decisions are owned by the humans.
