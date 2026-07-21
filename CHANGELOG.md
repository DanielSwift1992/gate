# Changelog

## Unreleased

The working prototype, end to end:

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
