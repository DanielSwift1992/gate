/* The published worlds use the same wasm court as the bench. Definitions are
   the world's recorded inputs, not the judge's implicit copy of Primitive. */
"use strict";
(function (root) {
    // DocumentReaderV1 leaves Structure-valued builder bodies to Drawing.
    // This mask finds boundaries only. The original declaration text reaches
    // the wasm court, which still refuses unknown attributes and syntax.
    function documentDeclarations(source) {
        const text = source.replace(/\r\n|\r/g, '\n');
        const mask = text.split('');
        const blank = (a,b) => { for(let n=a;n<b;n++) if(mask[n]!=='\n')mask[n]=' '; };
        const failure = (at,why) => { throw Error('cannot read line '+(text.slice(0,at).split('\n').length)+': '+why); };
        let i=0;
        while(i<text.length) {
            if(text.startsWith('//',i)) { const end=text.indexOf('\n',i);const to=end<0?text.length:end;blank(i,to);i=to;continue; }
            if(text.startsWith('/*',i)) {
                const from=i;let depth=1;i+=2;
                while(i<text.length&&depth) {if(text.startsWith('/*',i)){depth++;i+=2;}else if(text.startsWith('*/',i)){depth--;i+=2;}else i++;}
                if(depth)failure(from,'unclosed comment');blank(from,i);continue;
            }
            let start=i, hashes=0;
            while(text[i+hashes]==='#')hashes++;
            if(text[i+hashes]==='"') {
                const quote=i+hashes,triple=text.startsWith('"""',quote),end=(triple?'"""':'"')+'#'.repeat(hashes);
                i=quote+(triple?3:1);let closed=false;
                while(i<text.length) {
                    if(text.startsWith('\\'+'#'.repeat(hashes)+'(',i))failure(i,'interpolated strings need the document reader for that form');
                    if(text.startsWith('\\'+'#'.repeat(hashes),i)){i+=hashes+2;continue;}
                    if(text.startsWith(end,i)){i+=end.length;closed=true;break;}
                    if(!triple&&text[i]==='\n')failure(i,'line break in a quoted string');
                    i++;
                }
                if(!closed)failure(start,'unclosed string');blank(start,i);continue;
            }
            if(text.startsWith('#/',i)||(text[i]==='/'&&text[i+1]&&!/\s/.test(text[i+1])))failure(i,'unsupported slash literal');
            i++;
        }
        const clean=mask.join('').split('\n'),lines=text.split('\n');
        const header=/^\s*(?:public\s+)?static\s+var\s+body\s*:\s*some\s+Structure(?:\s*&\s*\w+)*\s*\{\s*$/;
        for(i=0;i<clean.length;i++) {
            if(!header.test(clean[i]))continue;
            const first=i;let depth=1;
            while(++i<clean.length&&depth) {
                for(const c of clean[i]){if(c==='{')depth++;if(c==='}')depth--;}
                if(depth>0)lines[i]='';
                else if(clean[i].trim()!=='}')throw Error('cannot read line '+(i+1)+': DocumentReader needs a separate body closing line');
                if(!depth)break;
            }
            if(depth)throw Error('cannot read line '+(first+1)+': unclosed document body');
        }
        return lines.join('\n');
    }
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
    function verdict(court, groups, texts, definitions, plain, carried, layout, judgePlain, translate, fragments, guards, documents = []) {
        const refusals = [], unsupported = [];
        let checked = 0;
        const documentSet = new Set(documents);
        for (const group of groups) {
            const originals = group.map(f => texts[f] || "").join("\n");
            let text;
            try { text = group.map(f => {
                try { return documentSet.has(f) ? documentDeclarations(texts[f] || "") : texts[f] || ""; }
                catch (error) { error.file = f; throw error; }
            }).join("\n"); }
            catch (error) {
                const line = error.message.match(/cannot read line (\d+)/)?.[1] || '1';
                unsupported.push({id:error.file||group[0],address:(error.file||group[0])+':'+line,reason:'DocumentReader: '+error.message});
                continue;
            }
            const at = {};
            for (const f of group) (texts[f] || "").split("\n").forEach((line, i) => {
                const m = line.match(/^public (?:enum|protocol|typealias) (\w+)/);
                if (m && !at[m[1]]) at[m[1]] = f + ":" + (i + 1);
            });
            for (const m of originals.matchAll(/^\/\/ gate-unsupported: (\w+) \| (.+)$/gm)) {
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
                    let address = at[name] || group[0] + ":1";
                    const numbered = line.match(/cannot read line (\d+)/);
                    if (numbered) {
                        let offset = 0;
                        for (const f of group) { const length = (texts[f] || "").replace(/\r\n|\r/g,"\n").split("\n").length;
                            if (+numbered[1] <= offset + length) { address = f + ":" + (+numbered[1] - offset); break; }
                            offset += length;
                        }
                    }
                    const claim = line.replace(/^✗\s*/, "");
                    if (verb === "where" && answer.exit === 2 && claim.startsWith("THE WHERE: ")
                        && (group.some(f=>documentSet.has(f)) || (claim.includes("normalization limit reached at '") && claim.endsWith("; no impossibility inferred")))) {
                        if (!unsupported.some(r => group.some(f => r.address.startsWith(f + ":"))))
                            unsupported.push({ id: name || group[0], address, reason: claim });
                    } else refusals.push({ address, claim: verb === "where" && translate ? translate(claim, text) : claim });
                }
            }
        }
        const company = [];
        let nextLine = 1;
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
            const lines = text.split("\n").length;
            company.push({file: f, text, start: nextLine, lines});
            nextLine += lines;
        }
        if (company.length) {
            const answer = judgePlain(company[0].file, company.map(p => p.text).join("\n"));
            checked += answer.premises || 0;
            for (const r of answer.refusals) {
                const part = company.find(p => r.line >= p.start && r.line < p.start + p.lines);
                refusals.push({ address: (part ? part.file + ":" + (r.line - part.start + 1)
                    : company[0].file + ":" + r.line), claim: r.premise });
            }
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
    const api = { ask, question, verdict, documentDeclarations };
    if (typeof module !== "undefined") module.exports = api;
    else root.GateWorldCourt = api;
})(typeof window !== "undefined" ? window : globalThis);
