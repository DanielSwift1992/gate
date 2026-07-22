# What travels with gate, and under what terms

gate is MIT licensed (see LICENSE). Everything it carries is too:

- **bin/gate-judge** — built from the verification-is-identification corpus
  (MIT, © Daniil Strizhov), pinned by commit and reproducible with
  `bin/build-judge.sh <pin>`. `.gate/README.md` states its sha256 when the
  tool is vendored, and `gate status` refuses a judge that is not the one
  stated.
- **codemirror.js, codemirror.css** — CodeMirror 5.65.16 (MIT, © Marijn
  Haverbeke and others), vendored unmodified from the minified distribution.
  https://codemirror.net/5/
- **judge.js** — our own line-for-line port of the corpus's judge, MIT with
  the rest of gate. Held to the reference binary word for word by the
  battery.
- **stdlib/*.swift** — ours, MIT. Materialize them into your repository and
  they are yours to change; drop the header and gate stops calling them ours.

Nothing else is bundled, and nothing is fetched at runtime.
