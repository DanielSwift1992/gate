# gate · death to drift

Your repository is full of sentences that must match something, and nobody
checks the match. The schema must match the service that writes it. The
rota must match who actually answers. Each pair held the day you or a
colleague wrote it down, and nothing tells you the day the two stopped
matching.

One case, to be concrete. CODEOWNERS hands `/src/api` to @alice. The folder
was renamed to `/services/api` in the spring. The rule now matches nothing,
reviews still go to Alice, and no tool reports a problem. You find out at
an audit, or the day a colleague merges what nobody reviewed.

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
  ownership.swift:84 · Owns_3_carol · Zone_docs against Zone_src: an owner and
                       the path they own must share one zone
```

That is a CODEOWNERS rule, translated once, judged on every change: carol
keeps `docs`, and one line assigns her a folder in `src`. The refusal
names the file, the line, and both sides of the disagreement. A diff
compares two texts. This compares two claims about one thing.

The same refusal on the live page (`gate serve`), at its line. The picture
is a door, and so is this line: [the same bench, live in your
browser](https://danielswift1992.github.io/gate/?f=ownership.swift:84),
over the demo, judged as you type.

[![the bench: the refusal at its line, re-read on every keystroke](docs/bench.png)](https://danielswift1992.github.io/gate/?f=ownership.swift:84)

The check is one lookup per claim and nothing else: no search, no solver,
no build. The cost is linear in the number of claims: milliseconds on a
real repository, and still milliseconds when the repository is ten times
the size. That is what lets it run on every keystroke, in every commit,
and in CI, with nobody waiting on it.

No server. No runtime. No new formats. Nothing leaves your repository.

## What changes

Every question below is one you answer today by searching: greping
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
you. Your own commands use your own names. You pay once, per name you
translate. Every question after that is a composition of what you already
translated, and compositions are free. That is the opposite of a
reporting tool, where each new question is new work. And the table is one
example. The tool itself is general. What varies is which pair you point
it at: a Jira ticket and the TODO that cites it, k8s RBAC and the cluster
it describes, an API contract and a client in another language.

## Quick start

```sh
git clone https://github.com/DanielSwift1992/gate && cd gate    # no install step
./gate import codeowners CODEOWNERS --tree . --policy owners.csv   # your own ownership, judged
./gate drift ../api/openapi.json --client ../sdk-js   # your contract, your client
./gate serve                                   # the same facts as a live page
```

Run the first two lines in repositories you already have. Ownership is a
fact you already keep, in a file that cannot say whether an
owner exists or whether a pattern still matches anything. The command
turns it into a judged world, and you write none of it: it writes one
small Swift file, `ownership.swift`, and no Swift toolchain is involved,
because the judge reads it directly. `owners.csv` is two columns, and it
adds the one thing CODEOWNERS cannot express: which zone each owner
keeps.

`drift` reads an API contract and a client library out of git on your
machine, and prints what the copies have been doing to each other.
Nothing is uploaded and nothing is fetched. It observes rather than
judges: the exit code follows a threshold you declare (`--fail-over 30`),
never a verdict of ours.

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
in, and your file stays in place: whatever read it keeps reading it. What
enters gate is a second record of the same fact, the kind of pair this
tool exists to hold. A CSV round-trips: `gate export` prints the tables
back, and the diff against the originals is empty. A CODEOWNERS is judged
against your tree as it lands: the refusal at the top of this page is
exactly that, a rule reaching outside its zone, and a pattern that
matches no file is named beside the verdict. And the two stay compared:
the world names its source on its own `from:` line, every `gate status`
translates the file again and holds the two together, and a line changed
on either side alone is named at its line. If your half is not a table,
you write it as a file yourself: a page of plain declarations, translated
by hand, once. The rules are small, and they are yours to read. That is
the upkeep, all of it.

Written out, a pair is nine lines. From the demo's `ownership.swift`: the
zone, a path in it, an owner posted to it, and the claim that ties them:

```swift
public enum Zone_docs: Realm {}
public enum Path_2_docs_: Room {
    public typealias Place = Zone_docs
}
public enum Owner_carol: Keeper {
    public typealias Post = Zone_docs
    public typealias Key = WardenKey
}
public typealias Owns_2_carol = Owns<Owner_carol, Path_2_docs_>
```

Nothing else is in the language: names, claims between names, and the
rules the claims must satisfy.

The files are bare Swift: the same language with the ceremony stripped,
and no DSL. Records are declarations, rules are type constraints in the
same text, so a record that violates a rule does not get flagged: it fails
to exist. And because it is plain Swift, a second, independent reader
exists whenever you want one: `swiftc -typecheck` passes on these files as
they are, with no project and no build. Git keeps doing what it already
does best: history, authorship, review, rollback.

A domain's vocabulary is the forms a world of that kind is written in. It
is a unit of its own, and today forms arrive by two roads: shipped on the
shelf in `stdlib/` and judged with the rest of this repository, or
declared in a file of your own beside your world. The goal is one road, a
shelf where every form is presented and nothing is built in, and that is
a debt on this project, not a claim about it. `gate stdlib show
forms-organization` prints any shelf page exactly as it shipped.

The porcelain is deliberately git-shaped: `init · status/fsck · log ·
check · diff · apply · import/export · verify · guard · library · survey ·
drift · badge · mine · theirs · declare · seam · attention · serve ·
report · stdlib · my · demo · findings · --version`. A refusal exits
non-zero, so hooks and CI need no wrappers, and every command ends by
naming the one step that comes next, so the whole ladder stays out of
your head.

## What this does not touch

A difference between two records is visible at a glance, text against
number, and the judge refuses it at a line. A difference in what two
people mean by one record is another thing: no check turns two readings
into one. What gate offers there is its one move: each side writes its
half down separately, and the judge says whether the two match, and where
they part when they do not. If CODEOWNERS hands the payments folder to an
intern, the rule holds and every record agrees with it. Whether it should
is a claim you can state too: write it as policy, let the other side
write theirs, and the verdict says if you agree. Agreement here is not
assumed. It is stated twice, and confirmed.

## Death to drift

Every pair you gate is one thing you stop keeping in your head. The
checking does not pile up: each claim is one lookup, so a hundred pairs
cost what ten did. Once your pairs are in, the picture is concrete: the
rename goes red on the renamer's screen, not on yours. A new hire's access
is a one-line diff an owner has to approve. Deleting the old config takes
an afternoon, not a season of asking around, because the readers it still
has are a list, not a guess. Nothing got faster. What went away is the
asking.

## The rest, one page deep

The cover you just read is the product. The pieces below are one file
away, each where you would look for it:

- [docs/DETAILS.md](docs/DETAILS.md): carrying gate vendored in your
  repository, verifying the zero-egress contract yourself, where it plugs
  in (hook, CI, review, editor), layout and ownership.
- [SECURITY.md](SECURITY.md): what a verdict promises, and where to
  report a wrong one.
- [CHANGELOG.md](CHANGELOG.md): what exists, in the order it came to be.
- After `gate init`, your repository is met by a letter of its own:
  `stdlib/readme.swift`, beside your files and judged with them.

## Repository

```
LICENSE         MIT · NOTICE.md lists the bundled pieces and their terms
gate            the CLI (python prototype; the judge does the judging)
gate.cmd        the same CLI on Windows
bin/gate-judge  the judge, one static binary, built at a pin from the
                public theory corpus, verification-is-identification:
                github.com/DanielSwift1992/verification-is-identification
                (bin/build-judge.sh [pin] rebuilds it)
bin/judge-cli.js · bin/judge-where.js
                both courts as a node port, for machines the binary
                was not built for, held to it line for line
stdlib/         the judge's own words, printed as real Swift files, self-judged
judge.js        the browser judge (byte-parity port) for the bench
ui.html         the workbench
codemirror.*    the editor (CodeMirror 5, MIT, vendored)
demo/           runnable worlds: CODEOWNERS + policy, CSV org, K8s RBAC
docs/           DETAILS.md, and the cover's picture with its provenance
tests/smoke.py   the battery: 356 end-to-end checks, the definition of green
tests/windows.py the Windows measure: the reviewer's road as asserts
```

## Status

Working prototype under active development, MIT licensed: see LICENSE,
and NOTICE.md for the bundled pieces and their terms. Free, and nothing
in it is paid. The judge is a native binary with a versioned verdict
contract (canon v2); the CLI is python and will be rewritten in Swift to
ship as a single static binary (the way git is one tool). We want to hear
about a wrong verdict before anything else: see SECURITY.md.

**Where it runs, measured rather than assumed.** The CLI is one python3 file and
the bench is a page, so both go wherever python3 and a browser go. The judge is a native binary built for
one platform: `bin/gate-judge` here is `Mach-O arm64`, and on any other machine
it does not execute. Where it cannot run and node is installed, both courts run
in the port: the plain court in `bin/judge-cli.js`, the certificate court
in `bin/judge-where.js`, the same judge ported line for line and held to
the binary's own lines by the battery, and `gate --version` names the port
as the court that ran. macOS is measured every run: the full battery, on
every push. Windows is measured on every push too, by its own road: the
walk in `tests/windows.py`, entry to a red line under the port, on a
Windows runner in CI. Linux runs the same pieces under the same port, and is not
measured in CI yet.

Roadmap, next: single-binary Swift CLI (Linux/Windows included) · the
bare-Swift diff view (`gate diff` shows the stripped form, `--full` the
whole text) · editable bare view in the bench · apply routing over the
declared layout · more domain forms.

Something drifts? Gate it.
