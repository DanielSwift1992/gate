# Changelog

## Unreleased

The working prototype, end to end:

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

- The world: single-source canon (`world.swift`), declared multi-file
  layout (`world.manifest.swift`) with two-way guards, cross-file
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
