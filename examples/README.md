# Selected examples

`gate demo [directory]` installs `codeowners/`, then calls the ordinary `init`, `import codeowners` and declaration paths. The one rule outside its zone is intentional. `gate demo seam [directory]` installs `seam/`, then calls the ordinary contract and carrier declarations. `index.json` lists the input files; the one-file CLI embeds the same bytes at build time so these explicit entry points work without this checkout.

`gate demo org [directory]` installs `organization/` and imports its people and grants through the ordinary import path. The sample is selected by the command; neither publisher selects one for the reader. `gate publish <repository> -o <site>` uses the declared repository. The recorded interactive publisher is `bin/build-pages.py <site> --source <repository>`; `--worlds` selects only the pinned showcase catalog.

The browser walk belongs to `tests/roadtest.py` and `tests/roadtest.js`. Its mutations, refusal-before-save, reset and keyboard controls execute on a temporary publication of the CODEOWNERS example. They are never written to the deployed catalog. The example data is not a court policy.

The older `demo/` inputs remain fixtures for the import, tracker and CI controls. The installers read the declared recipes here; the battery holds the copied organization tables against those historical inputs.

The gate site selects the ordinary world at `codeowners/` for its root: `python3 bin/build-pages.py _site --source examples/codeowners --worlds`. The manifest declares its materialized Swift files. They were prepared explicitly with `gate init .`, `gate import codeowners CODEOWNERS --tree . --policy owners.csv -o ownership.swift`, and `gate mine ownership.swift --role forms`; publication executes none of these commands. `ownership.swift:89` retains the deliberate refusal shown on the cover. The recipe in `index.json` still lists only importer inputs; materialized site files do not enlarge the one-file CLI's embedded recipes. The camera and external roadtest read this same declared world.
