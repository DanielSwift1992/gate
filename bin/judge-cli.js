#!/usr/bin/env node
// The port, speaking the words the binary speaks.
//
// `judge.js` is a line-for-line port of the corpus judge and it is held to the
// binary by parity checks on every run of the battery. The binary is native to one
// platform, so on any other machine the same court exists and nothing could reach
// it: this is the reach. Same arguments in, same lines out, so nothing downstream
// has to know which of the two answered.
//
// It serves BOTH courts. The plain court is judge.js, the line-for-line port
// of the corpus judge; the certificate court, which the binary answers under
// `judge where`, is judge-where.js beside this file, the same translation of
// the corpus's WhereJudge. The battery holds each to the binary's own lines.
const fs = require("fs");
const path = require("path");
const { judge } = require(path.join(__dirname, "judge.js"));

const args = process.argv.slice(2);
if (args[0] !== "judge") {
    console.error("judge-cli: usage: judge FILE... | judge where FILE");
    process.exit(2);
}
if (args[1] === "where") {
    const { runWhere } = require(path.join(__dirname, "judge-where.js"));
    process.exit(runWhere(args.slice(2)));
}
if (args[1] === "parse") {
    // ONE GRAMMAR, ONE READER. This hands the judge's own parse out as
    // JSON, so nothing beside him grows a regex over the worlds: the CLI
    // and the battery ask here, or they do not read swift at all. The
    // wrapper speaks it, not the port: judge.js stays the corpus's mirror,
    // and this is only the parse it already made, carried to stdout.
    const out = {};
    for (const f of args.slice(2)) {
        const r = judge(path.basename(f), fs.readFileSync(f, "utf8"),
                        { seeds: new Set(), generics: new Set() });
        const p = r.parsed;
        out[path.basename(f)] = {
            declarations: [...p.declarations.values()].map((d) => ({
                name: d.name, qualified: d.qualified, parent: d.parent,
                conformances: d.conformances, params: d.params || [],
                paramKinds: d.paramKinds || [], line: d.line,
                aliases: Object.fromEntries([...d.aliases].map(
                    ([k, v]) => [k, { target: v.target, line: v.line }])),
                typeName: (p.literals.get(d.name) || {}).value !== undefined
                    ? p.literals.get(d.name).value : null,
                // ── AND WHAT A RECORD IS MADE OF TRAVELS WITH IT. The bare view
                // shows a record's claims, the clause a gated form conforms
                // under, and the holes a protocol opens; this handed out the
                // name, its axes and its literal, and stopped there. A reader
                // built on that would have had to grow a regex over the world
                // for the rest, which is the one thing this route exists
                // against. The parse has held all of it all along.
                entries: (d.entries || []).map((e) => ({
                    head: e.head, args: e.args || [], line: e.line })),
                whereText: d.whereText || null,
                axes: d.axes || [], axisKinds: d.axisKinds || {},
                kind: d.kind || null,
            })),
            topAliases: Object.fromEntries([...p.topAliases].map(
                ([k, v]) => [k, { target: v.target, line: v.line,
                                  params: v.params || [] }])),
        };
    }
    process.stdout.write(JSON.stringify(out) + "\n");
    process.exit(0);
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
