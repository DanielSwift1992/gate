# Changelog

## Unreleased

The working prototype, end to end:

- The certificate court runs in the port. `bin/judge-where.js` is a
  line-for-line translation of the corpus's WhereJudge, answering
  `judge where` wherever the binary cannot run: the same lines out, byte
  for byte, held to the binary by the battery on every page of the shelf.
  `gate status` stops naming forms rows as unjudged on such machines,
  `gate.cmd` runs the CLI on Windows, and `tests/windows.py` walks the
  reviewer's road there in CI, from entry to a red line.

- What a library has been, observed and never judged. `gate drift` reads an
  OpenAPI document out of git, every revision of it, and walks a client
  library once, and prints two kinds of fact with their kinds named: the day the
  contract first declared a name against the day the library first wrote it (a
  commit, carrying its own hash), and the names and routes no walked file writes
  (a walk, carrying its bounds, so that pointing at one skipped file refutes the
  claim). It prints no verdict: the library never entered gate's world, and
  nothing outside the gate can be judged, because nobody there has spoken for
  anything. The exit code belongs to a threshold the operator declares.

  It replaced a door that judged shapes by reading a client's own source. That
  door was honest reasoning over invented premises: a certificate is only as
  true as what it is built on, and its premises were reached for across the gate
  by a regular expression. Fifteen special cases went into making the reading
  better and it never became right: prose read as a type, a wire encoding read
  as a name, a docstring read as a declaration. Judgement returns when both
  sides are declared, in `gate stdlib show forms-contract`, and then a refusal is
  about two declarations rather than about anybody's code.

- A citation may not outlive the thing it cites. `gate import refs` reads a
  tracker's own export and every `TODO(KEY)` your code writes, and judges them as
  one world: a note whose ticket was closed is refused at the line that writes
  it, and one naming a ticket the tracker never heard of is refused too. Both
  refusals fall out of the grammar rather than a rule written for them, and there
  is deliberately no way to write "this citation is exempt". One line in the CI
  you already run; the export may sit in another checkout, because nothing is
  fetched, only read; and what it prints is the check, not a file to keep.

- The bench is a closed input, not a text box. Bare and Table now answer the
  same way Full does: every value is a slot, and a slot is a closed question
  asked from the grammar: what an axis accepts, an atom of that kind or a path
  through an axis the record already has. What a record still owes is drawn as
  a row and stays a row until a whole line can be written, so `typealias X = `
  never exists in the buffer for a keystroke. A record is born from a form
  offering the shapes the world has actually lived, its name is the one free
  step and is refused while it is taken, and a claim is added to a body that
  already exists with every argument closed. Removal is by whole units, and the
  judge, not the bench, names what it cost, by address. One bridge carries
  every one of these from a parsed fact to a place in the text; a slot it cannot
  place is read-only and says so.
- A comment is a note on a fact. Consecutive `///` above a declaration belong to
  that record and travel with it into Bare and into Table, where the note column
  exists only where notes do. A blank line ends a note, and comments that belong to
  nobody keep the document's own order.
- Colour answers one question and weight another. A hue says where a name is
  from, what this world declares against what the shelf does, and the weight
  says whether anything may still answer to it: a kind is open, a record is
  itself. Both are read from the domain's own conformers, and the battery holds
  the bench to parting what the judge parts: two worlds one judged fact apart
  are never painted the same.
- The palette and the metrics are judged worlds of their own. Every colour is a
  contrast certificate on a ladder spelled from Unit. Every neutral is held
  within two percent of the achromatic line, so a tint cannot creep back.
  Every gap on the page is a whole step of the reading line, and the rail
  keeps one edge. The journal gives back the colours that belong to the judge and to the
  hand: red and green are the verdict's alone.
- The first paint is the answer rather than a guess: the bench keeps the
  theme the world declared on this machine, and the world overwrites it on
  every read.
- Fixed: a kind declared with its body on one line, `public enum FinanceShare:
  Document { … }`, carried that body into its name, so the shelf knew four
  documents and every offer for a document was empty.

- A personal world (`gate my`, and the bench on first run): yours, in your
  own git at `~/.gate/me`, one per repository, never in the shared repo:
  colleagues and CI do not have it. It holds what your bench shows you
  (`MyJournal` is a declaration, so editing it changes the journal) and
  claims you want to keep true, judged against the shared world: when a
  colleague changes a fact you depend on, the judge names the line in your
  file. Privacy is the repository boundary, not a policy.
- Policy is a fact: an identity ties an email to a person and `MergePolicy`
  states what merging demands, both declared in `gate.policy.swift` beside
  the world instead of read from unjudged CSVs, and guarded by `status`: an
  identity that names nobody is refused by line. (Beside, not inside: the
  reference judge does not read the extension form within a world, a
  recorded gap, so the guard keeps the file, the way the manifest is kept.)
- Zero egress: the battery greps the runtime
  sources for outbound primitives, confirms the loopback-only bind, and
  confirms the bench's Content-Security-Policy. The README says how to
  verify all of it without trusting us.
- A commit reads as the facts it changed (`Emp9000 · Rank: Manager → Lead`),
  not as a diff wrapped in git plumbing.
- A refusal belongs to the file that makes the claim: given several files
  the judge repeats each refusal once per file, and files that never make
  the claim are no longer blamed at lines they may not have.
- The journal view (`gate log`, and the bench rail): the repository's own
  history projected: commit, author, open/closed, and the world files a
  commit touches. A pure function of the clone: no server state, no
  hosting, and whoever can read the repo sees it. Observed, never judged
  (open/closed is reachability from the default branch). A commit that
  touches a world file opens its diff in the bench; clicking an author
  filters the journal. The world file takes the tool's name (`gate.swift`,
  `gate.manifest.swift`), the Dockerfile pattern.
- The workbench (`ui.html`, served by `gate serve`): a CodeMirror editor
  with declared-name highlighting. Three views in one row: Full, Bare
  (no enum/typealias/braces, scope by indentation, read-only, with
  jump-to-declaration), and Table (the world projected as sortable
  relations and ledgers). A draggable file rail over the declared layout
  with a per-file verdict dot. The verdict docked at the bottom,
  Xcode-style, with cross-file judgement over unsaved text and addresses
  refined to the subject line.
- No state of our own, and only a holding world is written: an edit goes
  to the working-copy file, but the file is written only when the judge
  holds: a refused (invalid) world never reaches the file, so git
  reflects only worlds that hold. The invalid state lives in the editor
  buffer until it holds again. git is the only state: commit or discard
  with git; there is no hidden "unsaved buffer".

- The world: the source lives in `gate.swift`, a declared multi-file
  layout (`gate.manifest.swift`) with two-way guards, cross-file
  judgement.
- Verbs (git-shaped porcelain): init, status/fsck, check, diff, apply
  (transfer/grant/revoke/hire), import/export with round-trip proof,
  verify (differential and --self), guard merge, guard deps (sketch),
  library with vocabulary diff, survey, serve, report, stdlib
  (show/materialize with drift guard).
- Domain worlds: Kubernetes RBAC via `import rbac` (namespace invariant,
  stale roleRef, cross-namespace binding, named by k8s source).
- The workbench (`/ui`): keystroke judgement, live tables, declared-layout
  file selector, cross-file verdict over unsaved text.
- The shelf: `stdlib/*.swift` as real, self-judged source files.
- The judge: native binary with a versioned verdict contract (canon v2),
  rebuilt from the public theory corpus by pin.
- The battery: `tests/smoke.py`, the end-to-end checks the README counts.
