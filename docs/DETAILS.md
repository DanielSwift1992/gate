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
grep -nE "URLSession|NWConnection|^[[:space:]]*import Network|getaddrinfo" bin/gate-cli.swift
grep -nE "urllib\.request|^[[:space:]]*import socket|socket\.socket|http\.client|requests\.(get|post|put)" gate
grep -nE "XMLHttpRequest|new WebSocket|fetch\([[:space:]]*['\"\`]https?:|(src|href)[[:space:]]*=[[:space:]]*['\"]https?:" \
    web/ui.html bin/judge.js bin/judge-cli.js bin/judge-wasm.js \
    bin/court-wasm/node/vi_court.js bin/court-wasm/web/vi_court.js

# 3. the server listens on the loopback, and nowhere else
grep -n '0x7f00_0001' bin/gate-cli.swift    # 127.0.0.1, written in, not configured
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
The CLI is one file of Swift, built against the platform's own library,
and the bench is one file of HTML: small enough that reading them is a
reasonable afternoon, which is the point. A tool that checks by reading
should be checkable by reading.

Two more facts a review leans on, both held by the battery. The CLI's
imports are a white list, named in the battery itself: four modules of
the platform's own library, with no package manager and no lockfile in
the repository. And the one piece that is not text, `bin/gate-judge`, is
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

## The arithmetic

Why a judged pair pays is a count, not an opinion. Every line below
is a number measured in this repository, a number you can count on
your own month, or an identity: a rearrangement of terms.

A question, priced. Answered by hand, a question costs the search
every time: the grep, the ticket, the person who remembers. Call that
c: yours is somewhere between fifteen minutes and an hour. Answered
by a judged pair, it costs one translation, T, and then a lookup: the
cover's milliseconds, reprinted on your machine by `python3
bin/bench.py`. The pair pays for itself after T / c questions. For a
table you already keep, T is one `import` command, minutes, and the
break-even is under one question. For a page of declarations written
by hand, T is an hour, and the break-even is a handful.

A divergence, timed. Unwatched, a divergence lives until the next
time somebody compares the two records: a quarterly audit makes that
up to ninety days. Under a judge that runs on every change, it lives
one commit. The ratio is hundreds. And it is measured, not assumed:
`gate findings --history` walks your own commits and draws when your
pair diverged and when, if ever, it came back. It folds that walk into
one line: where it parted, how long ago in days and in commits carrying
the pair, and how many are still apart today. Where the parting is
older than the window it read, the line says how far back it looked
instead of guessing, and it never calls a pair that has never agreed a
pair that parted. Every number there is git's own, and the counting is
of commits on the first-parent line, not of merges or reviews: those
would be claims about a forge, and this reads git. This repository ran it
on itself and found one excursion, eight rows wide, seven commits
long, standing beside a green battery; commit 3be3cf1 tells that
story and carries the guard it produced.

A repeated question, free. The names you translate are paid for once;
every question after them is a composition of names already paid, and
a composition is a lookup. The average price of a question falls
toward the lookup with every question asked. A reporting tool prices
every new question as new work; here the hundredth question costs
what the second did.

Knowing before measuring. "Is anything divergent" stops at the first
divergent address, and that is what runs in milliseconds on every
keystroke. "How far apart" walks both records whole and costs
accordingly, so it stands behind its own verb, `drift`, with a
threshold you declare. The cheap question runs everywhere, always;
the expensive one announces itself.

Reading against writing. Count your own month: the lines you wrote,
and the lines you had to read and answer for: reviews, audits,
onboarding. More people read a line than wrote it, a record is read
for years after the day it was written, and every agent you adopt
moves your written count toward zero while it grows your read one. A
world here is built for the reading side: a declaration is one
question, does it hold, and the judge answers with a line. Your cost
is the claim, not the execution you would otherwise replay in your
head.

## Layout and ownership

- `gate.swift` is where a world starts. Declare a multi-file layout in
  `gate.manifest.swift` and gate obeys it: judgement runs the declared
  list, and both halves are named at their line, a row whose file is not
  there and a file beside them with no row.
- The forms rows of a layout are judged as worlds: a row joins every row
  that declares a name it uses and does not declare itself, so a
  certificate whose gate stands in the next file is judged with that file,
  and two pages that each declare their own word stay two worlds. The
  bench page in a browser takes these worlds from `gate serve` when the
  page is built; an edit made in the page does not recompute them.
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

## Forms, and the two roads they arrive by

A domain's vocabulary is the forms a world of that kind is written in.
Today forms arrive by two roads: shipped on the shelf in `stdlib/` and
judged with the rest of this repository, or declared in a file of your
own beside your world. The goal is one road, a shelf where every form is
presented and nothing is built in, and that is a debt on this project,
not a claim about it. `gate stdlib show forms-organization` prints any
shelf page exactly as it shipped.

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

`docs/bench.png` is taken by `bin/shoot-bench.sh`: a copy of the declared `examples/codeowners` world
world, `gate serve` on a free port, one headless Chrome shot of
`/ui?f=ownership.swift:89`. That door is not the camera's: any refusal
address pastes into the browser bar as `?f=file:line`, and the bench
opens that file at that line. Beside it, `docs/bench.png.from` records the
sha256 of `web/ui.html` as photographed, and the battery holds that hash to
the working copy: change the bench and the battery goes red until the
picture is retaken. CI takes a fresh shot on every run and attaches it as
an artifact.

## Pinned playground worlds

`python3 bin/build-pages.py _site --source examples/codeowners --worlds` publishes gate's declared root and the showcase catalog, at `playground/<id>/index.html`. The pinned `Worlds/Playground/Site/Manifest.swift` stands in THEIRS of every world, including Site. Open it in Bare or Table and follow a record name to `playground/<id>/`; the first ten associations stay in order and the Company and Site source records follow them. The repository site root opens the declared `examples/codeowners` world, with `ownership.swift` and its intentional refusal at line 89, as shown on the cover. `playground/` opens Read me from showcase. For an explicitly selected repository, use `python3 bin/build-pages.py _site --source /path/to/repository`; this command has no default sample. The two options compose: source selects the root, worlds adds the showcase catalog under playground/. With only worlds, the root is not published. World inputs are disclosed beside the judge in the rail. The rail has only MINE and THEIRS; no added tab/provenance strip.

`bin/playground-worlds.from` names the showcase revision, every selected file's SHA-256, the world's compiler theory, the judge and the wasm bytes. `bin/playground-worlds.sh` fetches those revisions directly, with LF checkouts, and checks the files again when its cache is warm. `SHOWCASE_SOURCE` selects a local checkout at the recorded revision; the built site's `worlds-source.json` then says local. A changed selected file is refused.

The compiler uses theory b61433ab, the judge b57037b7. Both Primitive files have SHA-256 c2700f5d176d4f30159b9996cbe41d33fc2f14dfb6e7ad355e081014f8c4482a. The world supplies its Primitive and Spectrum explicitly through `.gate/forms-definitions.json`; these are input files, not claims. `shelf_overrides: false` keeps a standalone dictionary from restating the bench's same-named colours. Organization declares company data and its page in separate files. Company readers consume complete WorldFiles and retain their source addresses; DocumentFiles and DrawingInputs declare the page boundary. `plain_fragments` is reserved empty: absent and `[]` are accepted; nonempty requests, wrong types and repeated fields refuse at the record line with a hint to split data and page.

The page saves reader drafts and their verdicts under their showcase revision, world and file, including refusals. A red Atom edit survives a reload and stays red; the repository bench still writes on holds. Reset clears only that world's texts and layout. Large files keep a lossless splice against the pinned source, so a small edit does not duplicate five megabytes into browser storage. A storage failure is reported as an unsaved draft. The reopened world is judged again; a saved receipt is not evidence about later edits.

The showcase palette introduced at 9026431 preserves its seventeen integer contrast relations as count readings, and Site holds. The generic where normalization-limit route remains unsupported with its requirement IDs and addresses. Atom keeps four nominal refusals alongside ten successful count readings. A compiled page at the pin is not a compiler check of an edit in the browser; the generated company has no new Swift check at these pins.

At scale keeps all 136,513 lines in the editor and in the court's input. Full uses CodeMirror's virtual viewport; Bare and Table project 2,000 source lines at a time, with Previous/Next controls and original addresses. Projection pages change neither the buffer nor the scope of judgement. The drawing engine still reads the whole world.

`tests/playground.py`, called by the battery, replays the transferred page and kit vectors, compares the original drawing hashes with playground 400b667 and the current drawings with the explicit phrase repair in copy-r3.json, checks native/wasm answers and all seventeen palette slack controls, builds the actual benches through serve, and executes their fetch shim and paged projection functions under node. `tests/bench-width.py` measures the finished pages in headless Chrome or Chromium at 375 and 1280 in both themes; restoring the old no-wrap answer must overflow again. Source and drawing keep their own scrolling surfaces. The live browser walk belongs to review.

The canvas keeps its declared width and height in screen units; the surface scrolls when that world is wider than the pane. This preserves the drawing's text metrics, not a claim that the world has an adaptive layout. The copy note discloses installation and storage instructions on demand, leaving reset available. On a narrow panel a refusal's address precedes its full explanation. Full uses Snug at the reading row and number-to-text seam and Near outside its number; history uses the same Control register as the other gestures. These are explicit layout choices inside the spacing and register contracts, checked at the recorded viewports, not consequences of contrast arithmetic.

The published live path calls the same pageGuards and lint as the vectors, over all owned files with original file/line addresses. Imported names come from the selected pinned module sources and the shared kit vocabulary. The badge distinguishes no readings, supported readings that hold, refusals and an unsupported remainder; edited Swift bodies remain unchecked. Finished HTML and every CSS pass bench_styles.py: interface palette/register declarations come only from the native ladder.css, and editor scroll/measurement constants are named in web/bench-technical.json. Drawing roles belong to the world's explicitly declared profile.

A manifest may name one pinned DrawingProfileFile. The owner computes its role CSS with native DocumentKit and emits an input receipt; native serve and publish authenticate those bytes without an external runtime. The CSS and receipt name explicit roles in both themes, the palette's Legible witnesses and the font's measured table. A stale or damaged input refuses before publication replaces its output; intact unsupported measurements remain unsupported. Font, stylesheet, license and owner receipt have shared content addresses. The finished-site law checks every consumer. [The input format and live MINE boundary](DRAWING-PROFILE.md).

The accepted Drawing contract is pinned by its SHA-256 in bin/drawing-contract.from. Empty and unaccepted contracts retain not-compared with a reason, null contract_pin, zero cases and an actual inputs_digest. Exact owner cases and other inputs keep their separate Drawing comparison; a green relation verdict does not compare a picture with Swift. The palette port is used only for a live MINE edit whose owner receipt has become stale; static publication keeps this structure read-only.

The publisher fetches only the showcase and theory inputs in `bin/playground-worlds.from`. The archived typed-playground 400b667 is migration evidence, fetched only by `tests/playground-baseline.py` from `tests/fixtures/playground-baseline.from`; hashes are checked on cache hits too. Its original corpus, guards, lint and renderer still hold the historical parity and security replay controls. Current guard and lint obligations run against the finished site’s shipped scripts and live edit path. The CODEOWNERS road test is `tests/roadtest.py` with `tests/roadtest.js`: it reads the declared example (or the site named by its `--site` option) and injects its test walk only into a temporary copy. CI runs it before deploying the clean catalog.

## Grouped live readings

The live bench advertises `batch_readings` in `/files`; `POST /world` takes a JSON array of file names and returns a name-to-reading map with `status` and `text`. It is a read operation. The single-file `GET /world?f=` uses the same delivery check. An unavailable or changed taken file has status 409 and an addressed refusal, without source bytes. Older servers and static snapshots keep the single-file path.

A response resolves its v2 input plan once and owns the verified byte buffers until that response ends. A resource request authenticates its requested inputs; the file list and whole-world verdict authenticate the full set. A changed unrelated input does not prevent delivery of a still verified resource, and never earns a whole-world verdict. Structural record errors remain global. The resolver is keyed by the exact manifest and record bytes and layout rows within this operation. Every new request starts empty. Before sending a taken file, the delivery reader hashes the actual buffer it sends; replacement or loss after resolution refuses. Size, mtime and inode are never proof of unchanged bytes. A file can change after the final read: the response describes those verified bytes, not continuous filesystem state at the browser's later display time.

Startup shares an operation's readings across vocabulary and the first opened file. Other neighbors are read after the first projection, in one fresh group. Another opening requests fresh readings. Memory costs the input buffers and the requested text packet for the response; there is no retained server cache of successful reads, TTL or filesystem watcher. The declared record and server process remain trusted; this does not authenticate a malicious owner's choice of new pins or protect a compromised process. Courts and mutable local files do not become an atomic multi-file transaction.
