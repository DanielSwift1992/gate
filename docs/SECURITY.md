# Reporting a problem

If gate prints `holds` while two records it judges disagree, you found
the bug we care about most. The whole tool is one claim, *a disagreement
is refused at its line*, and a false green breaks it.

Please report it privately first, by opening a
[security advisory](https://github.com/DanielSwift1992/gate/security/advisories/new) on the
repository, or by email to the maintainer. Include the world (or a reduced
one), the command you ran, and what you expected the verdict to be. A
reproduction that fits in a single file is worth more than a description.

We will confirm what we can reproduce, and say plainly what we cannot.

## What gate does with your data

Nothing leaves your machine. gate makes no outbound connection at any time:
no telemetry, no update check, no licence ping. The bench binds to the
loopback alone. The battery checks it, and you can too: **Nothing leaves
your machine** in [DETAILS.md](DETAILS.md) has the commands,
about a minute, offline.

## Scope

In scope: a false verdict (a world that should be refused and holds), a
refusal pointing at the wrong file or line, either ported court (`judge.js`,
`bin/judge-where.js`) disagreeing with the reference binary, a carried judge that is not the one
`.gate/README.md` states, or any outbound connection at all.

Out of scope: what a translated world *means*. gate checks that your facts
agree with each other and with the rules you wrote. Whether the rules say
what you meant is a question for a human reading the file, and the file is
written to be read.
