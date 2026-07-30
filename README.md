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

The judge is built from a public corpus and says which revision it came from:
`gate --version` prints the commit, and `bin/build-judge.sh <commit>` reproduces
the same bytes. Bytes say what a thing is; only the revision says what it was
made from.

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

## Start with your own drift

If you publish an API and a client library for it, this takes two commands and
answers a question about your repositories, not ours. Nothing is uploaded and
nothing is fetched: both sides are read out of git on your machine.

```sh
git clone https://github.com/you/gate && cd gate      # 1. no install step
./gate drift ../api/openapi.json --client ../sdk-js   # 2. what has it been?
```

Every command below is written `gate`. Until it is on your path it is `./gate`,
run from the clone — there is nothing else to install, and nothing else to
undo.

**This observes; it does not judge.** The library has not entered gate's world,
and gate holds no court over a world that has not entered — so `drift` prints no
verdict. What it prints are facts you can re-run: a commit that first wrote a
string is named by its own hash, and every absence carries the bounds of the
walk that found it, so pointing at one file it skipped refutes the claim. That
is what makes it a claim.

```
drift: observation of sdk-js against openapi.json · behind on 24 names · median 28 days · worst 77
  in history · transferType · the contract's earliest revision saying it is 2025-04-29,
               the library's earliest commit writing it 2025-07-15 — 77 days
  in this walk · includeUsers · the contract declares it; no file walked writes it
  in this walk · /config · the contract declares this route; no file walked spells its segments
  note: … absence is a fact about this walk: 214 files under …, kinds .ts .js …, skipping …
```

Two honest notes. A shallow clone has no past to date anything with and is told
so rather than credited with a clean one — `git fetch --unshallow` first. And
the contract is read by a JSON parser; if yours is YAML, one line converts it,
and gate keeps saying plainly that it does not read YAML itself:

```sh
yq -o=json '.' openapi.yml > /tmp/openapi.json
```

In CI, the threshold is **yours**, declared by you, and the exit code carries
your rule rather than anybody's verdict:

```yaml
# .github/workflows/drift.yml
name: drift
on: [push, pull_request]
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/checkout@v4
        with: { repository: you/api,  path: .api  }      # the contract, brought here
      - uses: actions/checkout@v4
        with: { repository: you/gate, path: .gate }      # the tool travels too
      - run: .gate/gate drift .api/openapi.json --client . --fail-over 30
```

Judgement begins on the other side of the gate: when both sides are **declared**
into gate's own grammar, a disagreement between them is refused with an address,
and the refusal is about two declarations rather than about anybody's code.

## Quick start

```sh
gate import codeowners CODEOWNERS --tree . --policy owners.csv   # your own ownership, judged
gate demo && cd gate-demo                                       # the same, on a repo we make
gate demo seam                               # two sides, one disagreement, one command
gate serve                                   # the bench opens: change a fact, watch the judge
```

The first line is the one to run in a repository you already have. Who owns
which paths is a fact you already keep — in a file that cannot say whether an
owner exists, whether a pattern still matches anything, or whether an owner is
reaching outside the area they were given — and it becomes a judged world
without you writing a line.

`owners.csv` is two columns, `owner,zone`, and it is the thing CODEOWNERS
cannot say: which area each person may keep. Without it every rule is its own
authority, the zone equalities cannot fail, and gate says `observed` rather
than `holds` — a verdict nobody could have broken is not a verdict, and this
tool will not print one. Ghost paths are still named either way, because those
are read from your tree.

`gate demo` is that same line with the repository supplied: three source areas,
a docs folder, a CODEOWNERS, and a one-line policy saying which zone each owner
keeps. One rule reaches past its zone, and the demo prints the refusal with the
CODEOWNERS line that makes it before you have chosen anything — the thing this
is all about, on the screen in the first breath. Everything it made is committed
the moment it is made, so `git checkout .` is the whole way back.

`gate demo seam` is the shorter road if you came here because a client and a
contract disagree rather than because of who owns what — it prints what each
side owes the other and where they part, and leaves the pieces on disk to drive
by hand. `gate demo org` is the same machinery on people, ranks and departments:
a domain that needs no repository at all, for reading rather than for your own
rows.

Or start from your own rows:

```sh
git init myworld && cd myworld
gate init .                      # the hook wires itself, and a letter lands: yours
mkdir tables                     # your own data, any source, and nothing else
cp ~/exports/people.csv tables/
cp ~/exports/grants.csv tables/
gate status                      # first print + first verdict, in ms
```

`gate serve` in a repository that has no world yet still opens, and `gate log`
reads the repository itself, with nothing to translate.

**Full**, **Bare** and **Table** are three ways to look at one file, and a file
may say which of them it should first be met in — `// opens: bare` in its own
head line, the same act as `// role:` one line above it. A letter opened in
Full reads as code; a ledger opened in Bare reads as prose. The bench opens on
the first row your layout declares, so the front door is whichever file you put
first.

## Mine and theirs

Everything here is an emitted view of somebody's source, and nobody is special.
Your world is a view of your facts. Their spec is a view of theirs. The judge in
`bin/` is a view of the corpus — `bin/build-judge.sh` clones at a revision,
builds, and writes the revision down beside the binary, which is the same act
this page describes, spelled in `sh`.

So there are two verbs, and every node has both:

```sh
gate mine   people.swift                     # I emit it, and I answer for it
gate theirs api.swift --at openapi@3f2a1c9   # I took it, at what I took it at
```

Both write one document, and the document is entirely yours. It has three
columns: **whose source** a file is, **which court** reads it, and — for
anything taken — **the revision** it was taken at.

It is written the way every record in this world is written: the columns are
**axes** to declared atoms, and the one string is the `typeName` literal that
spells a name. A revision is an atom of its own, so two rows taken at the same
revision say the same **name**, not the same text.

```swift
// gate.manifest.swift
public protocol Role {}
public enum WorldFile: Role {}
public enum SeamFile: Role {}

public protocol Mine {}
public enum People: Mine {
    public typealias Kind = WorldFile
}
extension People { public static var typeName: String { "people.swift" } }

public protocol Theirs {}
public enum Rev_openapi_3f2a1c9 {}
extension Rev_openapi_3f2a1c9 { public static var typeName: String { "openapi@3f2a1c9" } }
public enum TheContract: Theirs {
    public typealias Kind = SeamFile
    public typealias At = Rev_openapi_3f2a1c9
}
extension TheContract { public static var typeName: String { "api.swift" } }
```

**The role names a court, so it is not optional.** `world` is judged with the
rest of your world, by the plain court. `seam` is judged where it meets yours
and nowhere else. `forms` — the grammar a world is written in, and the
certificates over it — is judged by the `where` court: invent a word in your own
fork of your own forms, say something true about it and it holds, say something false
and it is refused at the line. `judge` is the court itself, held by a
reproducible build rather than by judgement. `carried` is anything brought here
unchanged — a vendored library, an editor — held by its source's name and
version and by no court of this world; the row exists so that nothing you depend
on is unaccounted for, including the thing you type into. A row gate cannot place is
refused at its own line — never swept quietly into your world, which is what
happened the one time this document was read by guessing.

**What is taken is taken at a revision, and there are no ranges.** That is the
whole reason no version solver exists here: the problem is not solved, it cannot
be stated. To move, take it again at a newer revision. Two takes of the same name
do not get resolved by a heuristic — they are refused with both addresses:

```
status: refused 1
  b-forms.swift:2 · `Thermal` is declared twice: once at a-forms.swift:2 and again
                    here. One name, one declaration
```

Nothing appears in the rail because it was lying in the folder. `gate declare
carrier … --theirs` writes the row for you, taking the pin from the `against`
block the declaration already carries — nobody types a second copy of a fact.

**The words a world speaks are not a file at all.** `Department`, `Ranked`,
`Site` are not files your world is made of. A world speaks them with no file of
that name anywhere near it; a copy put beside the world is read by nothing; and
a copy declared as a world row is refused — not because the words live anywhere
privileged, but because the judge's FRAGMENT knows five shapes and `public
protocol` is not one of them. A world is records; forms are the grammar records
are written in. `gate stdlib` prints, and what it prints is a
printout. `gate --version` names the revision those words were compiled from, and
that revision — not any file — is what a world depends on.

The rail says two things, because there are two: **mine** and **theirs**. The
judge is a row of what was taken, at the revision it was taken at, beside the
words it carries — not a section of its own. It is theirs like anything else,
and a privileged entity in the rail would be a privileged entity in the head.

## gate is the first inhabitant

This repository has a `gate.manifest.swift` of its own, and it is not a
demonstration. The tool's facts about its own surface — the palette it paints
with, the ladder of lengths its page is spaced on, the atoms its bench is made
of — are its world, declared in the same columns as yours and judged by the same
judge. Break an equality in `stdlib/bench-metrics.swift` and `gate status` in
this repository refuses at the line, exactly as it would in yours. Its badge is
not a sample; it is its life.

**And self-application is not self-certification.** The judge does not judge the
judge. No self-reference is the floor this whole theory stands on, and a court
that certified itself would be worth nothing — so the judge's row is accounting,
not a verdict. What holds it is a build anybody can repeat: take the pin, run
`bin/build-judge.sh <commit>`, compare the bytes. That check lives outside this
world on purpose.

gate lives under its own court everywhere a court is possible, and names the one
place where it is not. At the time of writing, the single refusal this repository
carries is that one: the judge's revision is unrecorded, because the binary in
`bin/` predates the recording. Running `bin/build-judge.sh` ends it. The tool
does not exempt itself from the rule it holds you to, and does not pretend the
exemption away either.

**How the other side finds out** is a pull request, and nothing else. gate never
fetches and never sends: the other side's declaration arrives because you brought
it — a checkout in CI, a copy, whatever you already trust. To let them know
somebody depends on them, put your file and its two manifest lines in **their**
repository. From then on their own CI parts the seam the day they touch what you
carry, with an address, and no registry has to exist for it. Unsubscribing is
deleting the file: a commit like any other — visible, dated, and nobody's to do
quietly.

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
diff · apply · import/export · verify · guard · library · survey · drift ·
badge · mine · theirs · declare · seam · attention · serve · report · stdlib · my ·
demo · findings · --version`. A refusal
exits non-zero, so hooks and CI need no wrappers — and `drift`, which judges
nothing, exits non-zero only on a threshold you declare yourself.

**The full reference is a world, not a page.** `gate stdlib show readme` prints
every verb as a record — what it touches, which court it calls, a note in its
own words — judged with this repository's own world and held to the dispatch by
name in both directions: a verb with no record and a record with no verb are
each refused at a line. Eleven of them carry a certificate that they change
nothing, `Run<V>: Safe where V.Does == Reads`; the judge refuses that line if
the verb admits to writing, and the battery runs every one of them and holds
the working copy byte-identical afterwards. A list in prose could promise the
same thing and drift from it the same afternoon.

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
  read from your world and its forms, so your own domain describes itself with
  no dictionary of ours to write.
- **Offers every way to fill a hole, and only those.** Every axis in a forms file
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
- **What a library has been, observed and never judged.** `gate drift
  openapi.json --client ./sdk` measures a world that has not entered: the day
  the contract first declared a name, the day the library first wrote it, the
  names no walked file writes, the routes no walked file spells. It prints no
  verdict, because no court sat — nothing outside the gate can be judged, since
  nobody there has spoken for anything. Each line says which kind of fact it is:
  a commit is an object and carries its own hash; an absence is a walk and
  carries its bounds. On weaviate's TypeScript client it reads: behind on 24 of
  71 names, median 28 days, and two the library has never written. The exit code
  is a threshold you declare with `--fail-over`, never a judgement.
- **A green must say how wide it is.** `gate badge -o gate.svg` counts the
  claims the judge counted — nothing stores that number — and replays every
  commit that touched the world back through the same judge until one does not
  hold, so the days on it are earned rather than declared. It will not say "no
  silent error", because that is precisely what nobody saw. It speaks for a
  world, and for nothing else: a badge over an observation would be a verdict
  wearing a number, and no court sat.
- **And judgement begins at the gate.** `gate declare` is the crossing: a
  contract emits a view of the document it publishes, a library emits — from its
  own build, with its own tools — a small declaration of what it carries, and
  states its own name for a field only where that name does not follow. Both are
  views of what each side already keeps, so neither can drift from its source.
  `gate seam` is the one court over the pair: a disagreement is refused at an
  address, naming each side in the words that side used, and a field nobody
  claimed is named beside the judgement rather than inside it — a claim never
  made cannot be refused. Nothing is read out of anybody's source: reaching
  across the gate for a premise is how a court ends up reasoning honestly about
  an invented world, and the reader that did it is gone.

  ```sh
  gate declare contract openapi.json -o api.swift        # the API's own word
  gate declare carrier  sdk.json     -o sdk.swift        # what their build emitted
  gate seam api.swift sdk.swift
  # seam: refused 1 · 5.8 ms
  #   /scrape · waitFor · the contract declares it count; SdkJS declares it text
  ```
- **And what waits for a word is a different question from what changed.** History
  is git's, and anybody can arrange it for themselves; `gate attention` is the
  other cut — a standing account of who owes whom a sentence. It is two-sided by
  construction rather than by design, since an unanswered axis sits with whoever
  owes the answer: the same movement shows a client what its contract waits for
  and the contract what the client waits for, and a sensor opens a hole for a
  technologist exactly as a client opens one for a contract.

  Intention is declared, never guessed. A divergence somebody said out loud is a
  fact with an author; one nobody said is unintended by construction. But a
  declaration without a term is an amnesty, so a declared divergence **cites
  something that can close** — and when the tracker says it closed, the exception
  stops holding and the item comes back first and loudest, its ground gone. The
  honest path stays the cheap one: fixing costs nothing, and setting something
  aside costs a name, a reason, and an expiry that arrives on its own.
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
- **A journal, from git itself.** `gate log` projects
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
- **Forms are the unit, and today they arrive by two roads.** A domain has
  one vocabulary — the forms and axes a world of that kind is written in —
  and it ships as a real Swift file in `stdlib/`, judged by the product's
  own judge in its own battery. Where they come from is a fact about this
  moment, not a principle, and the two roads are said apart. The corpus's
  forms are carried **by the judge we ship**, which is a differential arbiter
  for one reference world: its own header says the table it holds is that
  world's policy stated a second time, on purpose, so two encodings can check
  each other. A world speaks `Department` with no file of that name beside it,
  `gate --version` names the revision, and a copy of the printout declared as a
  world row is refused — because the judge's fragment knows five file shapes and
  `public protocol` is not one of them. Forms of
  your **own** are presented by file and judged as a `forms` row: invent a
  word in your fork, say something true about it and it holds, say something
  false and it is refused at the line. The goal is one road — an empty prism,
  where every form is presented and nothing is built in — and that is a debt
  on this project, not a claim about it. So the language is one command away
  to *read*: `gate stdlib show forms-organization`, and `materialize` writes
  the printout out for offline reading. In the bench, hold ⌘ and every name
  in the file underlines: click one and it opens where it is declared,
  whether that is your own file or the judge's own page. Nothing a printed
  world says is left without a home, and a check keeps it that way. Hidden
  is not secret.

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
stdlib/         the judge's own words, printed as real Swift files, self-judged
judge.js        the browser judge (byte-parity port) for the bench
ui.html         the workbench
codemirror.*    the editor (CodeMirror 5, MIT, vendored)
demo/           runnable worlds: CODEOWNERS + policy, CSV org, K8s RBAC
tests/smoke.py   the battery — 308 end-to-end checks, the definition of green
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
declared layout · more domain forms.
