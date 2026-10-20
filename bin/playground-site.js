"use strict";
const fs = require("fs");
const { judge } = require("./judge.js");
const { kitVocabulary } = require("./renderer.js");
const { makeBigCompany } = require("./playground-company.js");
if (process.argv[2] === "--names") {
    const names = new Set();
    for (const file of process.argv.slice(3)) {
        const parsed = judge(file, fs.readFileSync(file, "utf8"), kitVocabulary).parsed;
        for (const n of [...parsed.declarations.keys(), ...parsed.topAliases.keys()]) names.add(n);
    }
    console.log(JSON.stringify([...names].sort()));
} else {
const source = fs.readFileSync(process.argv[2], "utf8");
if (process.argv[3] === "--company") {
    process.stdout.write(makeBigCompany(12800, source));
} else {
    const p = judge("Manifest.swift", source, kitVocabulary).parsed;
    const axis = (n, k) => p.declarations.get(n)?.aliases.get(k)?.target;
    const word = n => p.literals.get(n)?.value;
    const tabs = p.order.filter(n => axis(n, "Id")).map(n => {
        const read = axis(n, "Reads"), seed = axis(n, "Seeds");
        const row = Object.fromEntries(["Id", "Title", "Shown", "Caption"].map(k => [k.toLowerCase(), word(axis(n, k))]));
        row.record = n;
        row.reads = read;
        row.group = word(axis(axis(n, "Group"), "Name"));
        row.generated = read === "GeneratedText";
        row.world = word(axis(row.generated ? seed : read, "File"));
        if (Object.values(row).some(v => v === undefined) || !/^[a-z][a-z0-9-]*$/.test(row.id))
            throw Error("unreadable tab " + n);
        return row;
    });
    if (!tabs.length || new Set(tabs.map(t => t.id)).size !== tabs.length) throw Error("no unique tabs");
    console.log(JSON.stringify(tabs));
}

}
