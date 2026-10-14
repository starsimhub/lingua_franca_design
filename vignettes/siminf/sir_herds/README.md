# SimInf SIR in 1,600 herds, in Starsim

The translation of [examples/siminf/sir_herds](../../../examples/siminf/sir_herds). **Not written yet: Starsim cannot express this model.**

## What is missing

The original is 12 lines: the built-in `SIR()` model, the initial number in each of 1,600 herds, and a table of 466,692 scheduled events. Each event adds one animal to a herd (182,685), removes one (182,535), or moves one from one herd to another (101,472), on a given day, chosen at random from the compartments the event names.

- **No scheduled events.** There is no way to say that on day 37 one animal leaves herd 12 for herd 480. `ss.Mobility(data=...)`, the movement register in the design, is not implemented, and it would cover only the transfers: animals entering and leaving need the same thing for `ss.birth` and `ss.death`.
- **Initial numbers by place work.** `init=dict(S=ss.by(patch=[...]))` and a spatial stratification with 1,600 levels cover the rest of the model, with `solver='gillespie'` for the dynamics within each herd.

## What the comparison will need

The reference holds the mean and 5% to 95% range of 200 runs for the totals, the number of herds with any infection, and three named herds. Events are applied at the end of each day, after that day's dynamics, and the order within a day is exits, entries, then transfers.
