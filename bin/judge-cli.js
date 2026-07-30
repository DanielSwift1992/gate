#!/usr/bin/env node
// The port, speaking the words the binary speaks.
//
// `judge.js` is a line-for-line port of the corpus judge and it is held to the
// binary by parity checks on every run of the battery. The binary is native to one
// platform, so on any other machine the same court exists and nothing could reach
// it: this is the reach. Same arguments in, same lines out, so nothing downstream
// has to know which of the two answered.
//
// It serves the PLAIN court only. The certificate court, which the binary answers
// under `judge where`, is not in the port yet: the port refuses a page of forms as
// outside the fragment and never reaches a certificate. Asked for it, this says so
// on stderr and exits 2 rather than printing an empty verdict, because a court that
// did not sit may not look like a court that found nothing.
const fs = require("fs");
const path = require("path");
const { judge } = require(path.join(__dirname, "..", "judge.js"));

const args = process.argv.slice(2);
if (args[0] !== "judge") {
    console.error("judge-cli: usage: judge FILE... | judge where FILE");
    process.exit(2);
}
if (args[1] === "where") {
    console.error("judge-cli: the certificate court is not in this port. The binary "
                  + "answers it, and this machine has none that runs.");
    process.exit(2);
}

const files = args.slice(1);
let decl = 0, lookups = 0, premises = 0, ms = 0;
const refusals = [];
for (const f of files) {
    const r = judge(path.basename(f), fs.readFileSync(f, "utf8"));
    decl += r.declarations;
    lookups += r.lookups;
    premises += r.premises;
    ms += r.milliseconds;
    for (const x of r.refusals) refusals.push(x);
}
const t = ms.toFixed(1);
if (refusals.length) {
    console.log(`✗ THE JUDGE refuses ${refusals.length} claim(s) in ${t} ms:`);
    for (const x of refusals) console.log(`    ${x.file}:${x.line}  ${x.premise}`);
    process.exit(1);
}
console.log(`✓ THE JUDGE holds: ${decl} declarations · ${lookups} lookups · `
            + `${premises} premises · ${t} ms`);
