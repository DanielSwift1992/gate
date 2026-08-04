# gate, the details

The cover ([README](../README.md)) is the product in one read. These are
the pieces you look up when you need them. Each was on the cover once and
moved here so the cover stays a cover.

## Carrying gate in your repository

`gate init . --vendor` puts the tool itself into `.gate/` with a `./gatew`
shim, the way a project carries `./gradlew`. Commit it, and everybody who
pulls has gate: no installation step to ask anyone to take, and nothing
is fetched. A security review reads it as what it is: code in
their own repository, pinned by a commit, reviewed like any other change,
not a script piped into a shell. The judge is pinned with it, so an old
commit is judged by the judge it was written with, which is what makes
`git bisect` over facts exact. And it is pinned twice over: `.gate/`
carries its `sha256` (what is here) and its corpus revision (what it was
made from), and `bin/build-judge.sh <pin>` builds the same judge from the
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
grep -nE "XMLHttpRequest|new WebSocket|fetch\(['\"]https?:" web/ui.html bin/judge.js \
    bin/judge-where.js bin/judge-cli.js

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
reads is your working copy and `git`. What it writes is your working copy.
The CLI is one file of standard-library Python and the bench is one file
of HTML: small enough that reading them is a reasonable afternoon, which
is the point. A tool that checks by reading should be checkable by
reading.

Two more facts a review leans on, both held by the battery. The CLI's
imports are a white list, named in the battery itself: eighteen modules of
the standard library, with no package manager and no lockfile in the
repository. And the one piece that is not text, `bin/gate-judge`, is
not a dependency: delete it and every court still answers through the node
ports, which are ordinary files in `bin/` you can read. CI rebuilds the
binary from the pinned public corpus on every push and runs the whole
battery on what it built, so the vendored binary is a convenience with a
warrant, not a thing you are asked to trust. The recorded hash names the
bytes present; the check is rebuilding from the pin and running the
battery on what you built.

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
- Every change, facts and rules alike, is a working-copy edit. History,
  review and rollback belong to git. gate keeps no state of its own.

## Why the declarations are Swift

The reason is the second reader. A claim language of our own would have
exactly one reader, the tool it ships with, and every verdict would rest
on trusting that reader. Swift already has an independent one:
`swiftc -typecheck` accepts these files as they are, with no project and
no build, and official Swift toolchains exist for macOS, Linux and
Windows. The judge reads the same small subset directly, in milliseconds,
so the same text has two readers, one of them ours and one of them not,
and a bug in either is visible against the other. Records are
declarations and rules are type constraints, so a record that breaks a
rule does not get flagged: it fails to exist. And the subset is small on
purpose: type declarations only, no functions, no bodies, nothing runs.
The theory behind the judge ships the same way: compiler-checked
constructions and executable witnesses, with the arguments carried by
the papers beside them.

## What this road does not judge

The second reader above is the reason this section exists. `swiftc`
accepts these files, and this tool never runs it: what gate holds and
what Swift holds are not the same list, and only one of them runs when
you type `gate status`.

Two courts sit here. The plain court reads your world file and holds the
claims in it. It does not read forms you declare yourself: a protocol at
the top of a world file is outside its fragment and it says so at that
line. The where court reads the files declared as forms and holds the
certificates written over them, which are equalities between axes: the
zone a keeper is posted to against the zone a room stands in, and the
refusal on the cover is one of those.

What neither of them held, the where court holds now: a gate's
requirement that an axis conform to a class. `Enter` asks that a keeper
carry a key that writes and `Owns` that it administer; a key that is
not a key, or a name nobody declared at all, is refused at its
certificate, resolved through the world's own tables and walked up the
ladder of protocols the world itself presents (the membership court,
at the judge's pin). This paragraph said the opposite once, and the
battery held that sentence to a real run: the day the court arrived,
this page went red instead of going stale, which is this tool's law
applied to its own prose.

The rule under both: a court holds what it carries. Forms this judge was
built with are checked to their last axis; forms you present are checked
where a certificate compares two of them, and nowhere else.

## The picture on the cover

`docs/bench.png` is taken by `bin/shoot-bench.sh`: a fresh `gate demo`
world, `gate serve` on a free port, one headless Chrome shot of
`/ui?f=ownership.swift:85`. That door is not the camera's: any refusal
address pastes into the browser bar as `?f=file:line`, and the bench
opens that file at that line. Beside it, `docs/bench.png.from` records the
sha256 of `web/ui.html` as photographed, and the battery holds that hash to
the working copy: change the bench and the battery goes red until the
picture is retaken. CI takes a fresh shot on every run and attaches it as
an artifact.
