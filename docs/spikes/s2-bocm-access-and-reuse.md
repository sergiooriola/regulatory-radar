# S2. BOCM access and reuse

- **Issue:** [#3](https://github.com/sergiooriola/regulatory-radar/issues/3)
- **Risk:** R04
- **Status:** in progress
- **Code:** [`spikes/s2/`](../../spikes/s2/), throwaway

## Question

Can the Comunidad de Madrid's official bulletin be read by a program every publication day, and
do its terms allow automated reuse?

## Threshold, as fixed in the [spike plan](README.md#s2-bocm-access-and-reuse)

20 of 20 days retrieved, the three hand checks match item for item, and the terms allow
automated reuse. Otherwise BOCM is left out of the first version and every notice says so (risk
R04).

## Hand-check days, chosen before the run

The 20 days are the 20 most recent bulletins up to 2026-10-20. Three are checked by hand, chosen
to cover a weekday, a Saturday and the largest bulletin of the window:

| Date | Bulletin | Why |
| --- | --- | --- |
| 2026-10-20 | 250 | Today's bulletin, a weekday |
| 2026-10-17 | 248 | A Saturday, a smaller bulletin |
| 2026-10-09 | 241 | The largest bulletin of the window by number of items |
