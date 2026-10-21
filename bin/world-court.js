/* The published worlds use the same wasm court as the bench. Definitions are
   the world's recorded inputs, not the judge's implicit copy of Primitive. */
"use strict";
(function (root) {
    function ask(court, verb, text, definitions, question) {
        const files = [{ name: "world.swift", text }, ...definitions];
        const args = [verb, ...files.map(f => f.name)];
        if (question) for (const key of ["predicate", "encoding", "sigma"])
            args.push("--" + key, question[key]);
        return JSON.parse(court.judge(JSON.stringify({ arguments: args, files })));
    }
    function question(text) {
        const m = text.match(/public enum \w+<[^{}]*>:\s*PredicateReading\s*\{([^}]*)\}/);
        if (!m) return null;
        const out = {};
        for (const key of ["Predicate", "Encoding", "Sigma"]) {
            const value = m[1].match(new RegExp("typealias " + key + " = (\\w+)"));
            if (!value) return null;
            out[key.toLowerCase()] = value[1];
        }
        return out;
    }
    function verdict(court, groups, texts, definitions, plain, carried, layout, judgePlain, translate, fragments, guards) {
        const refusals = [], unsupported = [];
        let checked = 0;
        for (const group of groups) {
            const text = group.map(f => texts[f] || "").join("\n");
            const at = {};
            for (const f of group) (texts[f] || "").split("\n").forEach((line, i) => {
                const m = line.match(/^public (?:enum|protocol|typealias) (\w+)/);
                if (m && !at[m[1]]) at[m[1]] = f + ":" + (i + 1);
            });
            for (const m of text.matchAll(/^\/\/ gate-unsupported: (\w+) \| (.+)$/gm)) {
                unsupported.push({ id: m[1], address: at[m[1]] || group[0] + ":1", reason: m[2] });
                if (!new RegExp("^public typealias " + m[1] + "\\b", "m").test(text))
                    refusals.push({ address: at[m[1]] || group[0] + ":1",
                        claim: "unsupported requirement '" + m[1] + "' lost its declared relation" });
            }
            const q = question(text);
            for (const verb of q ? ["where", "count"] : ["where"]) {
                const answer = ask(court, verb, text, definitions, verb === "count" ? q : null);
                const output = answer.stdout + answer.stderr;
                const measure = verb === "where" ? output.match(/(\d+) equalities and (\d+) memberships/)
                    : output.match(/(\d+) source-bound readings checked/);
                if (measure) checked += +measure[1] + (verb === "where" ? +measure[2] : 0);
                const lines = output.split("\n").filter(l => l.startsWith("✗")
                    && !l.includes("no equalities or memberships were judged"));
                if (!measure && !/THE WHERE|COUNT|✗/.test(output))
                    refusals.push({ address: group[0] + ":1", claim: "the court did not answer in its own canon" });
                for (const line of lines) {
                    const name = (line.match(/'(\w+)/) || [])[1];
                    const address = at[name] || group[0] + ":1";
                    const claim = line.replace(/^✗\s*/, "");
                    if (verb === "where" && answer.exit === 2 && claim.startsWith("THE WHERE: ")
                        && claim.includes("normalization limit reached at '") && claim.endsWith("; no impossibility inferred")) {
                        if (!unsupported.some(r => group.some(f => r.address.startsWith(f + ":"))))
                            unsupported.push({ id: name || group[0], address, reason: claim });
                    } else refusals.push({ address, claim: verb === "where" && translate ? translate(claim, text) : claim });
                }
            }
        }
        for (const f of plain) {
            if (f === layout || carried.includes(f)) continue;
            let text = texts[f] || "";
            const fragment = (fragments || []).find(r => r.path === f);
            if (fragment) {
                const pieces = text.split(fragment.marker);
                if (pieces.length !== 2) {
                    refusals.push({address: f + ":1", claim: "the declared company fragment marker is missing or repeated"});
                    continue;
                }
                text = "\n".repeat(pieces[0].split("\n").length - 1) + fragment.marker + pieces[1];
            }
            const answer = judgePlain(f, text);
            checked += answer.premises || 0;
            for (const r of answer.refusals)
                refusals.push({ address: f + ":" + r.line, claim: r.premise });
        }
        let guarded = 0;
        if (guards) {
            const names = new Set([...(guards.names || []), "Never",
                ...guards.vocabulary.seeds, ...guards.vocabulary.generics, ...guards.vocabulary.bareSeeds]);
            const parsed = {};
            for (const [f, text] of Object.entries(texts)) {
                if (f === layout) continue;
                parsed[f] = judgePlain(f, text, guards.vocabulary).parsed;
                // Extension literals do not declare their owner. Adding them
                // here would let the orphan extension prove its own existence.
                for (const name of [...parsed[f].declarations.keys(), ...parsed[f].topAliases.keys()]) names.add(name);
            }
            for (const [f, p] of Object.entries(parsed)) {
                const text = texts[f];
                for (const r of guards.pageGuards(p, text.split("\n"), names))
                    refusals.push({ address: f + ":" + r.line, claim: "page guard: " + r.premise });
                for (const r of guards.lint(f, text))
                    refusals.push({ address: f + ":" + r.line, claim: r.rule + ": " + r.premise });
                guarded++;
            }
        }
        const result = { verdict: refusals.length ? "refused" : unsupported.length
            ? (checked ? "partial" : "unsupported") : (checked ? "holds" : "empty"), refusals, unsupported, checked };
        if (result.verdict === "empty") result.reason = "no declared applications";
        if (guards) result.coverage = { readings: checked, guarded_files: guarded, swift_bodies: "not checked" };
        return result;
    }
    const api = { ask, question, verdict };
    if (typeof module !== "undefined") module.exports = api;
    else root.GateWorldCourt = api;
})(typeof window !== "undefined" ? window : globalThis);
