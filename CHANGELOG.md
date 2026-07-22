# Changelog

## Unreleased

The working prototype, end to end:

- A personal world (`gate my`, and the bench on first run): yours, in your
  own git at `~/.gate/me`, one per repository, never in the shared repo —
  colleagues and CI do not have it. It holds what your bench shows you
  (`MyJournal` is a declaration, so editing it changes the journal) and
  claims you want to keep true, judged against the shared world: when
  somebody changes a fact you depend on, the judge names the line in your
  file. Privacy is the repository boundary, not a policy.
- Policy is a fact: an identity ties an email to a person and `MergePolicy`
  states what merging demands, both declared in `gate.policy.swift` beside
  the world instead of read from unjudged CSVs, and guarded by `status`: an
  identity that names nobody is refused by line. (Beside, not inside: the
  reference judge does not read the extension form within a world — a
  recorded gap — so the guard keeps the file, the way the manifest is kept.)
- Zero egress, checked rather than asserted: the battery greps the runtime
  sources for outbound primitives, confirms the loopback-only bind, and
  confirms the bench's Content-Security-Policy. The README says how to
  verify all of it without trusting us.
- A commit reads as the facts it changed (`Emp9000 · Rank: Manager → Lead`),
  not as a diff wrapped in git plumbing.
- A refusal belongs to the file that makes the claim: given several files
  the judge repeats each refusal once per file, and files that never make
  the claim are no longer blamed at lines they may not have.
- The journal view (`gate log`, and the bench rail): the repository's own
  history projected — commit, author, open/closed, and the world files a
  commit touches. A pure function of the clone: no server state, no
  hosting; whoever can read the repo sees it. Observed, never judged
  (open/closed is reachability from the default branch). A commit that
  touches a world file opens its diff in the bench; clicking an author
  filters the journal. The world file takes the tool's name (`gate.swift`,
  `gate.manifest.swift`), the Dockerfile pattern.
- The workbench (`ui.html`, served by `gate serve`): CodeMirror editor
  with declared-name highlighting; three views in one row — Full, Bare
  (the bare form: no enum/typealias/braces, scope by indentation,
  read-only but highlighted with jump-to-declaration), Table (the world
  projected as sortable relations and ledgers); a draggable file rail
  over the declared layout with a per-file verdict dot; the verdict
  docked at the bottom, Xcode-style; cross-file judgement over unsaved
  text, addresses refined to the subject line.
- No state of our own, and only a holding world is written: an edit goes
  to the working-copy file, but the file is written ONLY when the judge
  holds — a refused (invalid) world never reaches the file, so git
  reflects only worlds that hold. The invalid state lives in the editor
  buffer until it holds again. git is the only state — commit or discard
  with git; there is no hidden "unsaved buffer".

- The world: the source lives in `gate.swift`, a declared multi-file
  layout (`gate.manifest.swift`) with two-way guards, cross-file
  judgement.
- Verbs (git-shaped porcelain): init, status/fsck, check, diff, apply
  (transfer/grant/revoke/hire), import/export with round-trip proof,
  verify (differential and --self), guard merge, guard deps (sketch),
  library with crystal diff, survey, serve, report, stdlib
  (show/materialize with drift guard).
- Domain worlds: Kubernetes RBAC via `import rbac` (namespace invariant,
  stale roleRef, cross-namespace binding — named by k8s source).
- The workbench (`/ui`): keystroke judgement, live tables, declared-layout
  file selector, cross-file verdict over unsaved text.
- The shelf: `stdlib/*.swift` as real, self-judged source files.
- The judge: native binary with a versioned verdict contract (canon v2),
  rebuilt from the public theory corpus by pin.
- The battery: 25 end-to-end checks (`tests/smoke.py`).
