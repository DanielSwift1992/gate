# gate

**Git gave your code an integrity guarantee. gate gives the same guarantee
to your facts.**

Your repository is full of sentences that must match something, and nobody
checks the match. The schema must match the service that writes it. The
rota must match who actually answers. CODEOWNERS must match the tree it
divides. Each pair held the day somebody wrote it down, and nothing tells
you the day the two stopped matching.

One case, to be concrete. CODEOWNERS hands `/src/api` to @alice. The folder
was renamed to `/services/api` in the spring. The rule now matches nothing,
reviews still go to Alice, and no tool reports a problem. You find out at
an audit, or the day somebody merges what nobody reviewed.

That gap has a name: drift. Two records of one fact, coming apart in
silence, while both still get obeyed.

The usual cure is to pick one place and call it the source of truth. But a
source has a direction: everything downstream must watch it, and it watches
nothing. The folder was renamed in a pull request that never read the file.
A file everyone must keep current is a chore for everyone, so it is a chore
for nobody, and the chosen file goes stale like any other. gate starts from
the opposite fact: there is no source, so there is no direction. The team
that owns the folders declares them, once. The review rule declares the
folder it points at. Two declarations about one folder cannot differ in
silence. Either they are equal, or you get the exact point of contact:

```
$ gate status
status: refused 1
  ownership.swift:82 · Owns_3_carol · Zone_docs against Zone_src: an owner and
                       the path they own must share one zone
```

That is a CODEOWNERS rule, translated once, judged on every change: carol
keeps `docs`, and one line hands her a folder in `src`. The file that made
the rule is named, at its line, with both sides of the disagreement. A diff
compares two texts. This compares two claims about one thing.

The check is one lookup per claim and nothing else: no search, no solver,
no build. Milliseconds on a real repository, and still milliseconds when
the repository is ten times the size, which is what lets it run on every
keystroke, in every commit, and in CI, with nobody waiting on it.

No server. No runtime. No new formats. Nothing leaves your repository.

## What changes

Every question below is one somebody answers today by searching: greping
repositories, opening tickets, asking whoever remembers. Here each is a
lookup, answered in milliseconds against the file itself:

| The question | Today | Here |
|---|---|---|
| May this person read this document? | ask the owner, or read the ACLs by hand | `gate check view Emp0042 FinanceShare` |
| What breaks if we move them to Sales? | find out after the move | `gate diff transfer Emp0042 Sales` |
| Who may merge this, and since when? | convention, and memory | `gate guard merge` · `gate log` |
| Which commit broke this rule? | bisect by hand, if anyone notices | `git bisect run gate status` |
| Is anything inconsistent right now? | an audit, quarterly | `gate status`, on every keystroke |

The names in the examples come from a sandbox this repository can make for
you; your own commands use your own names. You pay once, per atom:
translating N people and documents is the work. Every question after that
is a composition of what you already translated, and compositions are
free. That is the opposite of a reporting tool, where each new question is
new work.

## Quick start

```sh
git clone https://github.com/DanielSwift1992/gate && cd gate    # no install step
./gate import codeowners CODEOWNERS --tree .   # your own ownership, judged
./gate drift openapi.json --client ../sdk-js   # your contract against your client
./gate serve                                   # the same facts as a live page
```

The first two lines are the ones to run in repositories you already have.
Ownership is a fact you already keep, in a file that cannot say whether an
owner exists or whether a pattern still matches anything: it becomes a
judged world without you writing a line (`owners.csv`, two columns, adds
the one thing CODEOWNERS cannot express: which zone each owner keeps).
`drift` reads an API contract and a client library out of git on your
machine, and prints what the copies have been doing to each other: nothing
is uploaded, nothing is fetched, and it observes rather than judges, so
its exit code follows a threshold you declare (`--fail-over 30`), never a
verdict of ours.

No repository of your own at hand? `gate demo` makes one: a small tree
with a CODEOWNERS whose one rule reaches outside its zone, so the first
thing you see is the refusal above. Everything it makes is committed the
moment it is made, and `git checkout .` is the whole way back.

Every command here is written `gate`. Until it is on your path it is
`./gate`, run from the clone: nothing else to install, nothing else to
undo.

## Find your drift

Yours is wherever two places state one fact. Take a thing you shipped this
month and ask: where is this written down, and where else? Who checks the
two against each other, and when did anybody last do it? The pairs you
cannot answer for are your drift, and every team has them: the schema and
the service that writes it, the contract and the client, the rota and the
pager, the config nobody dares delete.

You are looking for pairs, not objects: one fact always has more than one
record. And the loudest marker is anything that calls itself the source of
truth: a self-declared source is the record nobody compares to the others
any more, so that is usually where drift collects.

The quick first look is one command, over the git history already in your
clone. `gate findings` prints plain sentences: who changed which facts,
across how many commits, and whether any hook or workflow checked those
edits. Nothing to set up, and nothing judged yet: these are readings, not
verdicts.

Something drifts? Gate it.

## Gate it

To gate a pair: put your half of it in a file, once. From then on every
change is checked against it, and the other side sees it the next time
they check.

If your half is already a table (CODEOWNERS, a CSV), one command puts it
in, your file stays the source it always was, and `gate export` prints it
back so you can watch the diff against the original come up empty. If it
is not a table, you write it as a file yourself: a page of plain
declarations, translated by hand, once. The rules are small, and they are
yours to read. That is the upkeep, all of it.

The files are bare Swift: the same language with the ceremony stripped,
and no DSL. Records are declarations, rules are type constraints in the
same text, so a record that violates a rule does not get flagged: it fails
to exist. And because it is plain Swift, a second, independent reader
exists whenever you want one: `swiftc -typecheck` passes on these files as
they are, with no project and no build. Git keeps doing what it already
does best: history, authorship, review, rollback.

A domain's vocabulary, the forms a world of that kind is written in, is a
unit of its own, and today forms arrive by two roads: shipped on the shelf
in `stdlib/` and judged in this repository's own battery, or declared in a
file of your own beside your world. The goal is one road, an empty prism
where every form is presented and nothing is built in, and that is a debt
on this project, not a claim about it. `gate stdlib show forms-organization`
prints any shelf page exactly as it shipped.

The porcelain is deliberately git-shaped: `init · status/fsck · log ·
check · diff · apply · import/export · verify · guard · library · survey ·
drift · badge · mine · theirs · declare · seam · attention · serve ·
report · stdlib · my · demo · findings · --version`. A refusal exits
non-zero, so hooks and CI need no wrappers. Twelve of these carry a
certificate that they change no files, which is why you can run them on a
clone you care about. Every command ends by naming the one step that comes
next, so nobody holds the whole ladder in their head.

## What this does not touch

A difference between two records is visible at a glance, text against
number, and the judge refuses it at a line. A difference in what two
people mean by one record is another thing: no check turns two readings
into one. What gate offers there is its one move: each side writes its
half down separately, and the judge says whether the two match, and where
they part when they do not. Whether a rule *should* say what it says is a
claim you can state too: write it as policy, let the other side write
theirs, and the verdict says if you agree. Agreement here is not assumed.
It is stated twice, and confirmed.

## Death to drift

Every pair you gate is one thing you stop keeping in your head. The
checking does not pile up: each claim is one lookup, so a hundred pairs
cost what ten did. Once your pairs are in, the picture is concrete: the
rename goes red on the renamer's screen, not on yours. The intern's access
is a one-line diff somebody has to approve. Deleting the old config takes
an afternoon, not a season of asking around, because the readers it still
has are a list, not a guess. Nothing got faster. What went away is the
asking.

## Carrying gate in your repository

`gate init . --vendor` puts the tool itself into `.gate/` with a `./gatew`
shim, the way a project carries `./gradlew`. Commit it, and everybody who
pulls has gate: no installation step to ask anyone to take, nothing
fetched from anywhere. A security review reads it as what it is: code in
their own repository, pinned by a commit, reviewed like any other change,
not a script piped into a shell. The judge is pinned with it, so an old
commit is judged by the judge it was written with, which is what makes
`git bisect` over facts exact. And it is pinned twice over: `.gate/`
carries its `sha256` (what is here) and its corpus revision (what it was
made from); `bin/build-judge.sh <pin>` builds the same judge from the
public corpus, checked by the battery rather than by the hash.

## Nothing leaves your machine

gate makes no outbound connection, at any time, for any reason: no
telemetry, no update check, no licence ping. That is a contract, not a
default. Verify it yourself, in about a minute:

```sh
# 1. air-gap it: turn off the network and run the whole battery
python3 tests/smoke.py                      # all green, offline

# 2. read the source for outbound primitives; the battery greps for these
grep -nE "urllib\.request|socket\.socket|http\.client|requests\.(get|post)" gate
grep -nE "XMLHttpRequest|new WebSocket|fetch\(['\"]https?:" ui.html judge.js

# 3. the server listens on the loopback, and nowhere else
grep -n 'HTTPServer((' gate                 # 127.0.0.1
lsof -iTCP -sTCP:LISTEN -P | grep 4744      # while `gate serve` runs

# 4. the judge binary links nothing that opens a socket
otool -L bin/gate-judge                     # ldd on Linux

# 5. build the judge yourself and compare: it comes from a public corpus
bin/build-judge.sh <pin>
```

The bench declares a Content-Security-Policy with `connect-src 'self'`, so
the browser refuses any external request even if one were ever written.
Everything above is a check in the battery, so it stays true. What gate
reads is your working copy and `git`; what it writes is your working copy.
The CLI is one file of standard-library Python and the bench is one file
of HTML: small enough that reading them is a reasonable afternoon, which
is the point. A tool that checks by reading should be checkable by
reading.

## Where it plugs in

gate adds no process of its own. It sits inside the four you already have:

- **Commit**: `gate init` wires a pre-commit hook, so a claim that stopped
  holding is not committed. It names the git setting it changed and how to
  undo it.
- **CI**: a red verdict exits non-zero, so no wrapper is needed:

  ```yaml
  - run: ./gatew status          # or: gate status
  ```

- **Review**: put `gate.swift` and `gate.policy.swift` in `CODEOWNERS`,
  and changing a fact or who may merge requires the review your host
  already enforces. No bot, no token, no permissions of ours.
- **Editor**: refusals are `file:line · claim`, the shape editors already
  parse, so a VS Code problem matcher underlines them with no extension of
  ours to install.

## Layout and ownership

- `gate.swift` is where a world starts. Declare a multi-file layout in
  `gate.manifest.swift` and gate obeys it: judgement runs the declared
  list, and both halves are named at their line, a row whose file is not
  there and a file beside them with no row.
- Tables are inputs and views, never truth: a later CSV edit cannot
  silently reprint the world.
- Policy is a fact, so it lives beside the world in `gate.policy.swift`: an
  identity ties an email to a person, and `MergePolicy` states the rank
  merging demands. Both go through review and carry a history, and `status`
  guards the file: an identity that names nobody is refused by line rather
  than obeyed. The CSVs only seed them. (The file sits beside the judged
  list, like the manifest: the reference judge does not read its extension
  form yet, so the guard keeps it.)
- Every change, facts and rules alike, is a working-copy edit; history,
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
tests/smoke.py   the battery: 347 end-to-end checks, the definition of green
```

## Status

Working prototype under active development, MIT licensed: see LICENSE,
and NOTICE.md for what it carries and under what terms. Free, and nothing
in it is paid. The judge is a native binary with a versioned verdict
contract (canon v2); the CLI is python and will be rewritten in Swift to
ship as a single static binary (the way git is one tool). Problems with a
verdict are the ones we most want to hear about: see SECURITY.md.

**Where it runs, measured rather than assumed.** The CLI is one python3 file and
the bench is a page, so both go anywhere. The judge is a native binary built for
one platform: `bin/gate-judge` here is `Mach-O arm64`, and on any other machine
it does not execute. Where it cannot run and node is installed, the plain court
is answered by `bin/judge-cli.js`, the same judge ported line for line and held
to the binary byte for byte by the battery. The certificate court, which
`judge where` runs, is the binary's alone: on a machine without one, `gate
status` names the forms rows it could not judge instead of printing a green over
them, and `gate --version` names the port as the court that ran. macOS is
measured every run. Linux is the same two pieces and the same port. Windows is
neither measured nor claimed yet.

Roadmap, next: single-binary Swift CLI (Linux/Windows included) · the
bare-Swift diff view (`gate diff` shows the stripped form, `--full` the
whole text) · editable bare view in the bench · apply routing over the
declared layout · more domain forms.

Something drifts? Gate it.
