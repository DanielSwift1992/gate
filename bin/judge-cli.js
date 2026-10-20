#!/usr/bin/env node
// Plain verdicts carry the pinned company's fragment. Organization contracts
// v0.1 and v0.2 check exit and output on frozen cases, not general equivalence.
// The where/count doors use the separate Rust/WASM implementation of their
// contract. The parse door is richer inspection for gate's own consumers.
const fs = require("fs");
const path = require("path");
const { judge, judgeFiles } = require(path.join(__dirname, "judge.js"));

const args = process.argv.slice(2);
if (args[0] !== "judge") {
    console.error("judge-cli: usage: judge FILE... | judge where FILE");
    process.exit(2);
}
if (args[1] === "where" || args[1] === "count") {
    // the certificate court and the count court are the contract's Rust
    // sample built for wasm32 at the pin bin/court-wasm.from records, by
    // bin/build-court-wasm.sh; judge-wasm.js is its door and speaks the
    // binary's words, held to them by the suite and the battery, so this
    // file hands them over and adds nothing
    const { main } = require(path.join(__dirname, "judge-wasm.js"));
    process.exitCode = main(args);
    return;
}
if (args[1] === "parse") {
    // Rich inspection records are outside the organization verdict contract.
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
if (!files.length) {
    process.stderr.write("✗ THE JUDGE needs the files it reads: `swift run ShowcaseTools judge <path>…`\n");
    process.exit(2);
}
// A file that is not there, or whose bytes are not UTF-8, is a corpus the
// court cannot read: the binary says so in one line and exits 2, and the port
// says the same words rather than stop on a stack trace (the organization
// court's contract, missing-file). Strict decoding, as the binary reads.
const sourceDecoder = new (require("util").TextDecoder)("utf-8", { fatal: true, ignoreBOM: true });
const texts = [];
for (const f of files) {
    try {
        texts.push(sourceDecoder.decode(fs.readFileSync(f)));
    } catch (error) {
        process.stderr.write("✗ THE JUDGE cannot read the corpus\n");
        process.exit(2);
    }
}
const r = judgeFiles(files.map((f, i) => ({ file: path.basename(f), text: texts[i] })));
const { declarations: decl, lookups, premises, milliseconds: ms, refusals } = r;
const t = ms.toFixed(1);
if (refusals.length) {
    console.log(`✗ THE JUDGE refuses ${refusals.length} claim(s) in ${t} ms:`);
    for (const x of refusals.slice(0, 20)) console.log(`    ${x.file}:${x.line}  ${x.premise}`);
    process.exit(1);
}
console.log(`✓ THE JUDGE holds: ${decl} declarations · ${lookups} lookups · `
            + `${premises} premises · ${t} ms`);
