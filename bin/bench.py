#!/usr/bin/env python3
# The cover says milliseconds, and says the cost stays flat when the world
# grows tenfold. This measures that sentence and writes the numbers down:
# a world of N claims and a world of 10N, `gate status` timed cold over
# repeated runs, p50 and p95 printed to docs/BENCH.md. Run it yourself:
#
#     python3 bin/bench.py
#
# The worlds are built fresh in a temp directory on every run; the tool
# under test is this clone's own ./gate with its own judge.
import os, re, statistics, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(HERE, "gate")
RUNS = 15


def world(claims):
    # an organization world: the forms come from the shipped shelf, the
    # file holds records alone, and every record is claims the plain
    # court looks up one by one
    lines = []
    for i in range(claims):
        lines += [f"public enum Emp_{i}: Employee {{",
                  "    public typealias Rank = Manager",
                  "    public typealias Home = Engineering",
                  "}"]
    return "\n".join(lines) + "\n"


def measure(claims):
    d = tempfile.mkdtemp(prefix=f"gate-bench-{claims}-")
    subprocess.run(["git", "init", "-q", d], capture_output=True)
    open(os.path.join(d, "gate.swift"), "w").write(world(claims))
    times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        r = subprocess.run([sys.executable, GATE, "status", "--json"],
                           cwd=d, capture_output=True, text=True)
        times.append((time.perf_counter() - t0) * 1000)
        assert '"verdict": "holds"' in r.stdout, r.stdout[:200]
    times.sort()
    return {"claims": claims,
            "p50": statistics.median(times),
            "p95": times[int(len(times) * 0.95) - 1],
            "runs": RUNS}


def main():
    check = "--check" in sys.argv
    small, large = measure(50), measure(500)
    out = ["# The cover's cost sentence, measured",
           "",
           "`gate status` timed as a fresh process per run, judge included,",
           f"over {RUNS} runs per world, on the machine that ran "
           "`python3 bin/bench.py` last. The worlds are generated grants",
           "worlds: every claim is one `Owns` lookup.",
           "",
           "| world | claims | p50 | p95 |",
           "|---|---|---|---|"]
    for m in (small, large):
        out.append(f"| {m['claims'] // 50}x | {m['claims']} "
                   f"| {m['p50']:.0f} ms | {m['p95']:.0f} ms |")
    ratio = large["p50"] / small["p50"]
    out += ["",
            f"Ten times the claims cost {ratio:.2f}x the p50 time. The run",
            "includes python start-up and the judge process; the judgement",
            "itself is the smaller share of every number above."]
    open(os.path.join(HERE, "docs", "BENCH.md"), "w").write("\n".join(out) + "\n")
    print(f"1x p50 {small['p50']:.0f}ms · 10x p50 {large['p50']:.0f}ms "
          f"· ratio {ratio:.2f} · wrote docs/BENCH.md")
    # --check holds the cover's sentence on every push: ten times the claims
    # may cost more, and not by a different order. The bound is generous
    # because CI machines are shared; a superlinear regression clears it.
    if check and ratio > 3.0:
        sys.exit(f"bench: 10x the claims cost {ratio:.2f}x the p50, over the 3.0 bound")


if __name__ == "__main__":
    main()
