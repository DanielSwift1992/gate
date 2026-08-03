# The cover's cost sentence, measured

`gate status` timed as a fresh process per run, judge included,
over 15 runs per world, on the machine that ran `python3 bin/bench.py` last. The worlds are generated grants
worlds: every claim is one `Owns` lookup.

| world | claims | p50 | p95 |
|---|---|---|---|
| 1x | 50 | 82 ms | 84 ms |
| 10x | 500 | 88 ms | 88 ms |

Ten times the claims cost 1.07x the p50 time. The run
includes python start-up and the judge process; the judgement
itself is the smaller share of every number above.
