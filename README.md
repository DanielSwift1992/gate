# gate

**Git gave your code an integrity guarantee. gate gives the same guarantee
to your facts.**

Access grants, org rosters, configuration, RBAC bindings — the facts your
company runs on live as copies across systems, drift silently, and get
audited by hand. gate turns them into a single typed world inside your own
git repository, where an inconsistency is impossible to express: the judge
re-reads every claim in milliseconds and a refusal names the exact line of
your own file.

No server. No runtime. No new formats. Nothing leaves your repository.

```
$ gate status
status: refused 1 · 18 declarations · 84 premises · 1.1 ms
  gate.swift:212 · VerifiedView requires Emp9005.Home == FinanceShare.Home:
                    Engineering against Finance
```

## How it works

Your facts become one Swift file — `gate.swift` — the **single source**,
readable by everything at once: `git diff`, a human, the judge, and the
Swift compiler. There is no DSL: what you write is **bare Swift** — the
same language with the ceremony stripped (write only the differences,
printing restores the full form), and **full Swift** is always one view
away, sitting right there in the file. Rules are type constraints in the same text, so a record
that violates a rule is not flagged — it fails to exist. Two independent
arbiters check every claim: the judge — a second, compiler-grade arbiter
that reads instead of building (milliseconds, on every keystroke) — and
the Swift compiler itself (seconds, in CI). Git carries what it already
carries best: history, authorship, review, rollback.

You never migrate your systems. You translate one domain — the tables you
already export — and everything else keeps talking to the world through
the verbs below.

## Quick start

```sh
git init myworld && cd myworld
gate init .                      # skeleton; the pre-commit hook wires itself
cp ~/exports/people.csv tables/  # your own data, any source
cp ~/exports/grants.csv tables/
gate status                      # first print + first verdict, in ms
```

From then on:

```sh
gate check view Emp0042 FinanceShare   # may X read Y?  answered in ms
gate diff  transfer Emp0042 Sales      # what would break (changes nothing)
gate apply transfer Emp0042 Sales      # edits the world; writes only on holds
gate guard merge                       # repo policy: the HEAD author must hold
                                       # the rank stated in tables/guard.csv
gate survey                            # read-only: unwritten links mined from
                                       # your own git history — before any
                                       # translation at all
```

The porcelain is deliberately git-shaped: `init · status/fsck · check ·
diff · apply · import/export · verify · guard · library · survey · serve ·
report · stdlib`. A red verdict exits non-zero, so hooks and CI need no
wrappers.

## What you get

- **Refusals with addresses.** Never "validation failed" — always
  `file:line`, both names, and what must hold. On imported data the
  address points into *your* CSV.
- **Millisecond judgement at any size.** 2 000 records judged in ~100 ms;
  the merge cycle benches at ~7 merges/s on one queue — thousands of times
  a CI-gated queue. Judgement is linear and local.
- **Verification without trust.** Any translator — an engineer, an LLM
  agent — may produce the world: `export` proves the fact translation
  byte-for-byte (round-trip diff must be empty) and `verify` seeds
  violations to prove the rule translation against your old checker.
- **Git, amplified.** The judge is a `git bisect run` predicate (the
  breaking commit found automatically), a merge guard (textually clean,
  semantically broken merges get named), and a free audit journal
  (`git log` over grants, signed commits as signed grants).
- **Domain worlds.** `gate import rbac` reads `kubectl get
  roles,clusterroles,rolebindings -A -o json` and judges the Kubernetes
  namespace invariant itself: a stale roleRef and a cross-namespace
  binding are named by their k8s source in milliseconds.
- **A workbench, not an IDE.** `gate serve` + `/ui` opens a local bench:
  the world on the left, verdict and live tables on the right, judged on
  every keystroke. It obeys your declared file layout and judges across
  files — an unsaved lie in one file is caught against a roster in
  another.
- **A shelf that is source.** Built-in definitions (git atoms, domain
  genres) are real Swift files in `stdlib/`, judged by the product's own
  judge in its own battery. `gate stdlib show` prints any of them;
  `materialize` lands the file in your repo, where it becomes yours.
  Hidden is not secret.

## Layout and ownership

- `gate.swift` is the source. Declare a multi-file layout in
  `gate.manifest.swift` and gate obeys it: judgement runs the declared
  list, a ghost file and a shadow file are both named.
- Tables are inputs and views, never truth: a later CSV edit cannot
  silently reprint the world.
- Every change — facts and rules alike — is a working-copy edit; history,
  review and rollback belong to git. gate keeps no state of its own.

## Repository

```
gate            the CLI (python prototype; the judge does the judging)
bin/gate-judge  the judge, one static binary (built from the public
                theory corpus: bin/build-judge.sh [pin])
stdlib/         the shelf: definitions as real Swift files, self-judged
judge.js        the browser judge (byte-parity port) for the bench
ui.html         the workbench
demo/           runnable worlds: CSV org, K8s RBAC with two real breaks
judge.js         the browser judge (byte-parity port) for the bench
codemirror.*     the editor (CodeMirror 5, MIT, vendored)
tests/smoke.py   the battery — 25 end-to-end checks, the definition of green
```

## Status

Working prototype under active development. The judge is a native binary
with a versioned verdict contract (canon v2); the CLI is python and will
be rewritten in Swift to ship as a single static binary (the way git is
one tool). Not yet accepting external contributions; license to be
determined before the first public release.

Roadmap, next: single-binary Swift CLI (Linux/Windows included) · the
bare-Swift diff view (`gate diff` shows the stripped form, `--full` the
whole text) · editable bare view in the bench · apply routing over the
declared layout · more domain genres.
