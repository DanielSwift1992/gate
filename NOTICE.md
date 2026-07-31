# What is bundled with gate, and under what terms

gate is MIT licensed (see LICENSE). Every bundled piece is too:

- **bin/gate-judge**: built from the verification-is-identification corpus
  (MIT, © Daniil Strizhov), pinned by commit. `bin/build-judge.sh <pin>`
  builds the same judge; the battery checks a build, the hash names it. `.gate/README.md` states its sha256 when the
  tool is vendored, and `gate status` refuses a judge that is not the one
  stated.
- **codemirror.js, codemirror.css**: CodeMirror 5.65.16 (MIT, © Marijn
  Haverbeke and others), vendored unmodified from the minified distribution.
  https://codemirror.net/5/
- **judge.js, bin/judge-where.js**: our own line-for-line ports of the
  corpus's two courts, the plain judge and WhereJudge, MIT with the rest of
  gate. Each is held to the reference binary by the battery's parity
  vectors.
- **stdlib/*.swift**: ours, MIT. Materialize them into your repository and
  they are yours to change; drop the header and gate stops calling them ours.

Everything else in this repository is ours, under the same MIT. Nothing is
fetched at runtime, and that is checked rather than promised: the battery
greps the sources for outbound primitives.
