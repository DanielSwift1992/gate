# gate

**Git gave your code an integrity guarantee. gate gives the same guarantee
to your facts.**

Who may read what, who owns which directory, who reports to whom: the facts
your company runs on are written down in five places — a spreadsheet, a
wiki page, CODEOWNERS, an IAM console, somebody's memory — and every copy
drifts from the others quietly. Nothing checks them against each other, so
the drift is found by an audit, or by an incident.

gate makes one of those copies the source and judges it. The facts become a
typed world in your own git repository, where an inconsistency is
impossible to express: the judge re-reads every claim in milliseconds, and
a refusal names the exact line of your own file.

No server. No runtime. No new formats. Nothing leaves your repository.

```
$ gate status
status: refused 1 · 18 declarations · 84 premises · 1.1 ms
  gate.swift:212 · VerifiedView requires Emp9005.Home == FinanceShare.Home:
                    Engineering against Finance
```

## What changes

Every question below is one somebody answers today by searching — greping
repositories, opening tickets, asking whoever remembers. Here each is a
lookup, answered in milliseconds against the file itself:

| The question | Today | Here |
|---|---|---|
| May this person read this document? | ask the owner, or read the ACLs by hand | `gate check view Emp0042 FinanceShare` |
| What breaks if we move them to Sales? | find out after the move | `gate diff transfer Emp0042 Sales` |
| Who may merge this, and since when? | convention, and memory | `gate guard merge` · `gate log` |
| Which commit broke this rule? | bisect by hand, if anyone notices | `git bisect run gate status` |
| Is anything inconsistent right now? | an audit, quarterly | `gate status`, on every keystroke |

You pay once, per atom: translating N people and documents is the work.
Every question after that is a composition of what you already translated,
and compositions are free — which is the opposite of a reporting tool,
where each new question is new work.

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
gate demo && cd gate-demo        # a world of people and grants, in one command
gate serve                       # the bench opens: break a fact, watch the judge
```

Or start from your own rows:

```sh
git init myworld && cd myworld
gate init .                      # skeleton; the pre-commit hook wires itself
cp ~/exports/people.csv tables/  # your own data, any source
cp ~/exports/grants.csv tables/
gate status                      # first print + first verdict, in ms
```

`gate serve` in a repository that has no world yet still opens: the journal
reads the repository itself, with nothing to translate.

From then on:

```sh
gate check view Emp0042 FinanceShare   # may X read Y?  answered in ms
gate diff  transfer Emp0042 Sales      # what would break (changes nothing)
gate apply transfer Emp0042 Sales      # edits the world; writes only on holds
gate guard merge                       # repo policy: the HEAD author must hold
                                       # the rank gate.policy.swift states
gate survey                            # read-only: unwritten links mined from
                                       # your own git history — before any
                                       # translation at all
```

The porcelain is deliberately git-shaped: `init · status/fsck · log · check ·
diff · apply · import/export · verify · guard · library · survey · serve ·
report · stdlib · my · demo · findings · --version`. A red verdict exits non-zero, so hooks and
CI need no wrappers.

Every command ends with the one step that comes next, chosen by what your
repository already has — the journal before any translation, then the hook,
then a policy, then CI — so nobody has to hold the whole ladder in their
head. A refusal points at its address instead.

## What you get

- **The inside of a body is total too.** The judge refuses anything outside
  its grammar at the top of a file, an unknown form inside a body, and an
  argument that resolves to nothing. One thing it cannot refuse is an entry
  that never closes: it swallows what follows and drops those claims without
  a word. So every line inside a body must belong to a whole entry — a form,
  its arguments, and the `>.self;` that ends it — and a line that does not is
  named. Comment out one bracket and six claims stop being checked; that now
  says so instead of holding.
- **One name, one declaration.** Two declarations of a name are two truths
  about it, and only one can be read: the fast tier says so at a keystroke,
  naming both lines, which is what the compiler would say at a build.
- **Refusals with addresses.** Never "validation failed" — always
  `file:line`, both names, and what must hold: the line you broke, not one
  near it. On imported data the address points into *your* CSV.
- **The cursor on a name says what it is.** A thin line under the bar names
  whatever the cursor rests on: a record and what it conforms to, a value and
  its kind, an axis and what it takes, a gate and its arguments. Every word is
  read from your world and its genre, so your own domain describes itself with
  no dictionary of ours to write.
- **Offers every way to fill a hole, and only those.** Every axis in a genre
  says what it accepts, so an empty slot after `Sex =` offers Male, Female
  *and* `Given.Sex` — an atom of that kind, or a path through an axis this
  record already has whose own axis is of that kind. Type a dot and it offers
  what stands after it. Not Manager, and not a name that merely looks
  similar: what the bench suggests is what the judge will accept.
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
- **A client may not fall behind its contract unseen.** `gate import contract
  openapi.json --client ./sdk` reads what the contract declares and what a
  library actually carries, and judges them as one world: a field carried as the
  wrong sort of thing is refused with both shapes named, and one the library does
  not carry at all is named beside it. Types cannot do this — they make each side
  self-consistent and say nothing about the other, which is why a hand-written
  client lags a contract for releases while its own checker stays happy. The only
  other thing that ties them is a generator, one pipeline per language; this
  leaves the client hand-written. A library that forwards an untyped bag is told
  so plainly rather than accused of lagging on every field: it lags on nothing,
  and it helps nobody.
- **A citation may not outlive the thing it cites.** `gate import refs
  tickets.json --code .` reads a tracker's own export and every place your code
  names a ticket, and judges them as one world: a `TODO(PROJ-42)` whose ticket
  was closed months ago is refused at the line that writes it, and one naming a
  ticket the tracker has never heard of is refused too. Neither system reads the
  other today, which is exactly why the two copies of "this is still open" drift
  — the tracker does not read your repository, and your repository does not read
  the tracker. Nothing leaves the machine: the export is a file you already have.
  It is one line in the CI you already run — the export may sit in another
  checkout entirely, because nothing is fetched, only read — and it exits
  non-zero on a stale citation, so no wrapper is needed:

  ```sh
  gate import refs ../tracker-export.json --code .
  ```

  What it prints is the check, not a file to keep: unless you ask for it by name
  with `-o`, it is judged where nothing keeps it and your repository is left as
  it was.
- **One question, three doorways.** Grants, Kubernetes RBAC and CODEOWNERS
  are the same question — who may do what, where — so they share one
  crystal and differ only in the importer. `gate import rbac` judges the
  namespace invariant (a stale roleRef and a cross-namespace binding, named
  by their k8s source). `gate import codeowners` judges the thing CODEOWNERS
  itself cannot say: state who may own which zone, and a rule reaching
  outside it is refused at the line of your own CODEOWNERS, while a pattern
  no file matches is named beside it.
- **A workbench, not an IDE.** `gate serve` + `/ui` opens a local bench:
  the world on the left, verdict and live tables on the right, judged on
  every keystroke. It obeys your declared file layout and judges across
  files — an unsaved lie in one file is caught against a roster in
  another.
- **Three views of one file, and one way to answer.** Full is the Swift you
  already have; Bare is the same text with the ceremony gone; Table projects
  it as relations. They are not three editors — every value in every one of
  them is the same closed question, asked from the grammar: click it and the
  offer is what that axis accepts, an atom of the kind or a path through an
  axis this record already has. What a record still owes is a row before it is
  a line, and nothing is written until a whole line can be: pick a value and
  the axis, the `=` and the value go in together. A new record is offered the
  shapes the world has already lived, and the only free step is its name,
  refused while it is taken. Removal is by whole units, and what it costs is
  not our guess: the judge reads the file again and names every reader by
  address. One bridge carries all of it from a parsed fact to a place in the
  text, so a slot it cannot place says `edit in Full` instead of guessing.
- **A comment is a note on a fact.** Consecutive `///` lines standing directly
  above a declaration are what you wrote about that record, and they travel
  with it: in Bare above the record, in Table as a column that exists only
  where notes do. A blank line ends a note rather than spanning it, and the
  comments that belong to nobody stay where the document put them.
- **The theme is a declaration, not a toggle.** `MyBench` in your own world
  states which theme the bench wears, so the choice is a fact in your git with
  a date on it, not a setting somewhere. With nothing declared the operating
  system decides. There is no switch: a button that duplicates a declaration
  would be a second truth about it.
- **Findings, before anything is translated.** `gate findings` reads a
  clone and says what is true of it in sentences: who changes the facts and
  whether anything checked those edits, owners CODEOWNERS names that the
  history has not seen for hundreds of commits, work that lives in one
  person's head. What the judge checked is marked as checked; what was only
  read from git says so. `--md` prints the same as a note. It needs no
  world, no configuration and no network — which makes it the first useful
  thing gate does in any repository.
- **A journal, from git itself.** `gate log` (and the bench rail) projects
  the repository's own history — commit, author, open or closed — with no
  translation at all: any clone already carries it. A view is a pure
  function of the clone, so whoever can read the repo sees it; nothing is
  hosted, nothing is stored. Observed, never judged: open/closed is
  reachability from the default branch, not a verdict.
- **A world of your own, if you want one.** Everybody's bench has one more
  file, `my.swift`, and until somebody writes in it there is nothing: it
  reads as a comment saying what it is for, and it is stored nowhere. Write
  a claim you want to keep true and it becomes a file in *your* git
  (`~/.gate/me`, one per repository), judged together with the shared world
  and never in it: when somebody changes a fact your claim depends on, the
  judge names the line in your file, and their pipeline stays about the
  shared world alone. Clear it and it is gone again. Privacy is the
  repository boundary, not a policy; sharing is moving a declaration into
  the shared world and committing it.
- **A shelf of genres, and a genre is the unit.** A domain has one
  vocabulary — the forms and axes a world of that kind is written in — and
  it ships as a real Swift file in `stdlib/`, judged by the product's own
  judge in its own battery. An imported world names the genre it is written
  in, so the language is one command away: `gate stdlib show
  genre-organization`, and `materialize` lands it in your repo where it
  becomes yours. In the bench, hold ⌘ and every name in the file underlines:
  click one and it opens where it is declared, whether that is your own file
  or the genre on the shelf. Nothing a printed world says is left without a
  home, and a check keeps it that way. Hidden is not secret.

## Carrying gate in your repository

`gate init . --vendor` puts the tool itself into `.gate/` with a `./gatew`
shim, the way a project carries `./gradlew`. Commit it, and everybody who
pulls has gate — there is no installation step to ask anyone to take, and
nothing is fetched from anywhere:

```sh
git clone your/repo && cd repo
./gatew status          # judged, immediately
```

Three things follow. A security review reads it as what it is: code in
their own repository, pinned by a commit, reviewed like any other change —
not a script piped into a shell. The judge is pinned with it, so an old
commit is judged by the judge it was written with, which is what makes
`git bisect` over facts exact. And the binary is reproducible: `.gate/`
carries its `sha256`, and `bin/build-judge.sh <pin>` rebuilds it from the
public corpus for anyone who wants to check.

## Security posture

gate makes no outbound connection, at any time, for any reason: no
telemetry, no update check, no licence ping. That is a contract, not a
default — and it is what lets an engineer install it the way they install
`ripgrep`. Verify it yourself, in about a minute:

```sh
# 1. air-gap it: turn off the network and run the whole battery
python3 tests/smoke.py                      # all green, offline

# 2. read the source for outbound primitives — the battery greps for these
grep -nE "urllib\.request|socket\.socket|http\.client|requests\.(get|post)" gate
grep -nE "XMLHttpRequest|new WebSocket|fetch\(['\"]https?:" ui.html judge.js

# 3. the server listens on the loopback, and nowhere else
grep -n 'HTTPServer((' gate                 # 127.0.0.1
lsof -iTCP -sTCP:LISTEN -P | grep 4744      # while `gate serve` runs

# 4. the judge binary links nothing that speaks a network
otool -L bin/gate-judge                     # ldd on Linux

# 5. build the judge yourself and compare: it comes from a public corpus
bin/build-judge.sh <pin>
```

The bench also declares a Content-Security-Policy with `connect-src
'self'`, so the browser refuses any external request even if one were ever
written. Everything above is a check in the battery, so it stays true.

There is no server, no account, no telemetry endpoint, and no data of yours
anywhere but your own repository. What gate reads is your working copy and
`git`; what it writes is your working copy. The CLI is one file of standard
library Python and the bench is one file of HTML — small enough that reading
them is a reasonable afternoon, which is the point: a tool that checks by
reading should be checkable by reading.

## Where it plugs in

gate adds no process of its own. It sits inside the four you already have:

- **Commit** — `gate init` wires a pre-commit hook, so a lie cannot be
  committed. It names the git setting it changed and how to undo it.
- **CI** — a red verdict exits non-zero, so no wrapper is needed:

  ```yaml
  - run: ./gatew status          # or: gate status
  ```

- **Review** — put `gate.swift` and `gate.policy.swift` in `CODEOWNERS`,
  and changing a fact or who may merge requires the review your host
  already enforces. No bot, no token, no permissions of ours.
- **Editor** — refusals are `file:line · claim`, the shape editors already
  parse, so a VS Code problem matcher underlines them with no extension of
  ours to install.

## Layout and ownership

- `gate.swift` is the source. Declare a multi-file layout in
  `gate.manifest.swift` and gate obeys it: judgement runs the declared
  list, a ghost file and a shadow file are both named.
- Tables are inputs and views, never truth: a later CSV edit cannot
  silently reprint the world.
- Policy is a fact, so it lives beside the world in `gate.policy.swift`: an
  identity ties an email to a person, and `MergePolicy` states the rank
  merging demands. Both go through review and carry a history, and `status`
  guards the file — an identity that names nobody is refused by line rather
  than obeyed. The CSVs only seed them. (The file sits beside the judged
  list, like the manifest: the reference judge does not read its extension
  form yet, so the guard keeps it.)
- Every change — facts and rules alike — is a working-copy edit; history,
  review and rollback belong to git. gate keeps no state of its own.

## Repository

```
LICENSE         MIT · NOTICE.md says what travels with gate
gate            the CLI (python prototype; the judge does the judging)
bin/gate-judge  the judge, one static binary (built from the public
                theory corpus: bin/build-judge.sh [pin])
stdlib/         the shelf: definitions as real Swift files, self-judged
judge.js        the browser judge (byte-parity port) for the bench
ui.html         the workbench
demo/           runnable worlds: CSV org, K8s RBAC with two real breaks
judge.js         the browser judge (byte-parity port) for the bench
codemirror.*     the editor (CodeMirror 5, MIT, vendored)
tests/smoke.py   the battery — 165 end-to-end checks, the definition of green
```

## Status

Working prototype under active development, MIT licensed — see LICENSE,
and NOTICE.md for what it carries and under what terms. Free, and nothing
in it is paid. The judge is a native binary with a versioned verdict
contract (canon v2); the CLI is python and will be rewritten in Swift to
ship as a single static binary (the way git is one tool). Problems with a
verdict are the ones we most want to hear about: see SECURITY.md.

Roadmap, next: single-binary Swift CLI (Linux/Windows included) · the
bare-Swift diff view (`gate diff` shows the stripped form, `--full` the
whole text) · editable bare view in the bench · apply routing over the
declared layout · more domain genres.
