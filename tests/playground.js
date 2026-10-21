// The old page's vectors now read the showcase's records, not HTML literals.
"use strict";
const fs = require("fs"), path = require("path"), cp = require("child_process"), assert = require("assert"), crypto = require("crypto");
const here = path.resolve(__dirname, ".."), cache = process.argv[2], site = process.argv[3];
const sc = path.join(cache, "showcase"), base = process.argv[4], checks = path.join(sc, "Checks/Playground");
const read = p => fs.readFileSync(p, "utf8"), fixture = n => JSON.parse(read(path.join(checks, n + ".json")));
const { judge } = require("../bin/judge.js");
const { renderAll, kitVocabulary, canonicalShares, seedCount } = require("../bin/renderer.js");
const historicalRenderer = require(path.join(base, "renderer.js"));
const historicalJudge = judge;
const { lint } = require(path.join(site, "playground/basics/playground-lint.js")), { pageGuards } = require(path.join(site, "playground/basics/playground-guards.js"));
const worldCourt = require("../bin/world-court.js"), court = require("../bin/court-wasm/node/vi_court.js");
const record = JSON.parse(read(path.join(cache, "worlds.from")));
assert.strictEqual(read(path.join(here, "bin/playground-guards.js")), read(path.join(base, "guards.js")));
assert.strictEqual(read(path.join(here, "bin/playground-lint.js")), read(path.join(base, "lint.js")));
const definitions = [{ name: "Primitive.swift", text: read(path.join(cache, "theory/Sources/VerificationIsIdentification/Primitive.swift")) },
    { name: "Spectrum.swift", text: read(path.join(sc, "Sources/DocumentKit/Spectrum.swift")) }];
const renderFixture = fixture("renderer"), courtFixture = fixture("courts"), drawings = {}, reports = [];
const copy = fixture("copy-r3"), catalog = fixture("catalog-r4"), scaleCatalog = fixture("scale-catalog");
function updated(text, paths) {
    for (const c of copy.changes.filter(c => paths.includes(c.path))) {
        assert(text.includes(c.before), c.path + ": copy anchor lost");
        text = text.replace(c.before, c.after);
    }
    return text;
}
const hashes = arts => arts.map(c => ({name:c.name,bytes:Buffer.byteLength(c.svg),
    sha256:crypto.createHash("sha256").update(c.svg).digest("hex")}));
let vectors = 0;
function check(name, fn) { fn(); vectors++; reports.push(name); }
check("a refused certificate named budget stays a refusal", () => {
    const f = "Dictionary/Light.swift", c = courtFixture.cases.find(c => c.id === "light-halving");
    const text = read(path.join(sc, courtFixture.declaration_files.Light)).replace(...c.mutation)
        .replace("public typealias HalfFact =", "public typealias budget =");
    const answer = worldCourt.verdict(court, [[f]], {[f]:text}, definitions, [], [], "gate.manifest.swift", judge);
    assert.strictEqual(answer.verdict, "refused");
    assert.strictEqual(answer.unsupported.length, 0);
    assert(answer.refusals.some(r => r.claim.includes("budget")));
});
function draw(name, text, historical = false) {
    const p = (historical ? historicalJudge : judge)(name, text, kitVocabulary).parsed;
    const art = (historical ? historicalRenderer.renderAll : renderAll)(p.declarations, p.order, p.literals, p.topAliases);
    assert.deepStrictEqual(art.errors, [], name);
    return art.canvases;
}
const allDefinitions = Object.keys(record.theory.files).map(n => read(path.join(cache, "theory", n)))
    .concat(Object.keys(record.showcase.files).filter(n => n.startsWith("Sources/DocumentKit/") && n.endsWith(".swift"))
        .map(n => read(path.join(sc, n)))).join("\n");
const outside = new Set([...kitVocabulary.seeds, ...kitVocabulary.generics, ...kitVocabulary.bareSeeds,
    ...[...allDefinitions.matchAll(/\b(?:enum|protocol|typealias) (\w+)/g)].map(m => m[1]),
    "Close", "Open", "Never", "Given", "Structure", "Divides", "DividesY", "SoftShadow", "Female", "Male", "IndividualContributor", "Lead", "Manager",
    "Finance", "Engineering", "Sales", "People", "OnSite", "Hybrid", "Remote", "FinanceShare", "EngineeringShare", "SalesShare", "PeopleShare"]);
for (const [world, sources] of Object.entries(renderFixture.world_sources)) {
    const text = sources.map(n => read(path.join(sc, n))).join("\n");
    const original = [world + ".swift", ...(["Atom", "Light"].includes(world) ? [world + "Pages.swift"] : [])]
        .map(n => read(path.join(base, "corpus/worlds", n))).join("\n");
    check(world + " historical snapshots stay historical; current file orders agree", () => {
        const arts = draw(world, text), reverse = draw(world, [...sources].reverse().map(n => read(path.join(sc, n))).join("\n"));
        const pinned = fixture("r2-preservation").render.worlds[world];
        if (pinned) assert.deepStrictEqual(hashes(draw(world, original, true)),
            pinned.map(({name,bytes,sha256})=>({name,bytes,sha256})), world + " historical renderer");
        assert.deepStrictEqual(hashes(draw(world, updated(original, sources), true)), copy.drawings[world], world + " historical copy repair");
        assert.deepStrictEqual(reverse, arts, world);
        drawings[world] = arts.map(c => c.svg).join("");
        if (world !== "Company") assert(arts.length >= 1);
    });
    check(world + " lawful, known and guarded", () => {
        assert.deepStrictEqual(lint(world, text), []);
        const parsed = judge(world, text, kitVocabulary).parsed;
        assert.deepStrictEqual(pageGuards(parsed, text.split("\n"), outside), []);
        const known = new Set([...outside, ...parsed.declarations.keys(), ...parsed.topAliases.keys(), ...parsed.literals.keys()]);
        for (const d of parsed.declarations.values()) for (const p of d.params || []) known.add(p);
        for (const d of parsed.declarations.values()) for (const [key, alias] of d.aliases)
            for (const piece of alias.target.split(/[<>,\s]+/)) {
                const n = piece.split(".")[0];
                if (/^[A-Z]/.test(n)) assert(known.has(n), world + ": " + d.name + "." + key + " names " + n);
            }
    });
}
const company = fixture("company"), companyText = read(path.join(sc, company.world));
for (const name of ["Manifest", "Palette"]) check("Site/" + name + " preserves its source obligations and page guards", () => {
    const text = read(path.join(sc, "Worlds/Playground/Site", name + ".swift"));
    const original = read(path.join(base, "corpus", name + ".swift"));
    if (name === "Manifest") {
        const a = judge(name, original, kitVocabulary).parsed, b = judge(name, text, kitVocabulary).parsed;
        const links = p => [...p.declarations].map(([n,d]) => [n,[...d.aliases].map(([k,v]) => [k,v.target])]);
        const additions = [...catalog.added_declarations, ...Object.keys(scaleCatalog.added_declarations)];
        const expectedLinks = links(a);
        for (const change of scaleCatalog.changes) {
            const row = expectedLinks.find(([n])=>n===change.record);
            assert(row,change.record);
            for (const [key,value] of Object.entries(change.before)) assert.deepStrictEqual(row[1].find(([k])=>k===key),[key,value]);
            row[1] = row[1].filter(([k])=>!change.removed.includes(k)).map(([k,v])=>[k,change.after[k]||v]);
        }
        assert.deepStrictEqual(links(b).filter(([n])=>!additions.includes(n)), expectedLinks, "only the recorded Scale association changes");
        for (const [name,axes] of Object.entries(scaleCatalog.added_declarations)) assert.deepStrictEqual(Object.fromEntries(links(b).find(([n])=>n===name)[1]),axes);
        for (const [name,word] of Object.entries(scaleCatalog.words)) assert.strictEqual(b.literals.get(name).value,word);
        const expected = judge(name, updated(original, ["Worlds/Playground/Site/Manifest.swift"]), kitVocabulary).parsed;
        assert.deepStrictEqual([...b.literals].filter(([n])=>!additions.includes(n)).map(([n,x])=>[n,x.value]), [...expected.literals].map(([n,x])=>[n,x.value]), "only recorded phrases change");
    } else assert.strictEqual(read(path.join(checks, "origins/Palette.swift")), original);
    assert.deepStrictEqual(lint(name, text), []);
    assert.deepStrictEqual(pageGuards(judge(name, text, kitVocabulary).parsed, text.split("\n"), outside), []);
});
check("where budget remains unsupported at its original requirement addresses", () => {
    const ledger = fixture("palette-residue");
    let text = read(path.join(checks, "origins/Palette.swift"));
    for (const r of ledger.requirements) text = text.replace("public typealias " + r.id + " =",
        "// gate-unsupported: " + r.id + " | count v0.1 normalization budget (57 344)\npublic typealias " + r.id + " =");
    const answer = worldCourt.verdict(court, [["Palette.swift"]], {"Palette.swift":text}, definitions,
        [], [], "gate.manifest.swift", judge);
    assert.notStrictEqual(answer.verdict, "refused");
    assert.deepStrictEqual(answer.refusals, []);
    assert.deepStrictEqual(answer.unsupported.map(r => r.id).sort(), ledger.requirements.map(r => r.id).sort());
    for (const r of answer.unsupported) assert(/^Palette.swift:\d+$/.test(r.address));
});
check("all seventeen palette reading lies remain addressed in wasm", () => {
    const text = read(path.join(sc, "Worlds/Playground/Site/Palette.swift"));
    for (const row of fixture("palette-residue").requirements) {
        const line = new RegExp("^public typealias " + row.id + " = Legible<([^\\n]+)>$", "m");
        const m = text.match(line); assert(m, row.id);
        const args = m[1].split(", "); assert.strictEqual(args.length, 3);
        const wrong = "public typealias " + row.id + " = Legible<" + args[0] + ", " + args[1]
            + ", Plus<Unit, " + args[2] + ">>";
        const result = worldCourt.ask(court, "count", text.replace(m[0], wrong), definitions,
            {predicate:"PaletteContrastQuestion",encoding:"UnaryArithmeticEncoding",sigma:"PaletteLight"});
        assert.strictEqual(result.exit, 1, row.id);
        const refusals = (result.stdout + result.stderr).split("\n").filter(l => l.startsWith("✗"));
        assert.strictEqual(refusals.length, 1, row.id);
        assert(refusals[0].includes("'" + row.id + ".R1'"), refusals[0]);
    }
});
check("company's four vectors", () => {
    const clean = judge("Company.swift", companyText), want = company.golden.clean;
    for (const k of ["declarations", "lookups", "premises", "refusals"]) assert.deepStrictEqual(clean[k], want[k]);
    for (const [id, [anchor, lie]] of Object.entries(company.lies)) {
        assert(companyText.includes(anchor));
        const refusals = judge("Company.swift", companyText.replace(anchor, lie)).refusals;
        assert(refusals.every(r => r.file === "Company.swift"));
        assert.deepStrictEqual(refusals.map(({line, premise}) => ({line, premise})), company.golden[id]);
    }
});
check("historical native dynamics golden bytes", () => {
    const config = renderFixture.dynamics;
    const vocab = Object.fromEntries(Object.entries(config.gameKit).map(([k, v]) => [k, new Set(v)]));
    const text = read(path.join(checks, config.source)), p = judge("dynamics-world.swift", text, vocab).parsed;
    const result = historicalRenderer.renderAll(p.declarations, p.order, p.literals, p.topAliases);
    assert.deepStrictEqual(result.errors, []);
    assert.strictEqual(result.canvases[0].svg + "\n", read(path.join(checks, config.expected_svg)));
});
check("the page's four guards still object", () => {
    const f = fixture("guards"), text = f.files.map(n => read(path.join(sc, n))).join("\n");
    for (const c of f.cases) {
        const changed = (c.prefix || "") + text + (c.suffix || "");
        const objections = pageGuards(judge("Basics.swift", changed, kitVocabulary).parsed, changed.split("\n"), outside);
        assert.strictEqual(objections.filter(o => o.premise.includes(c.expect)).length, 1, c.id);
    }
});
check("light and atom colour vectors", () => {
    for (const [world, values] of [["Light", renderFixture.light_color_occurrences], ["Atom", renderFixture.atom_color_occurrences]])
        for (const [color, want] of Object.entries(values)) assert.strictEqual(drawings[world].split(color).length - 1, want, color);
});
check("the twenty-eight native vector plate observations", () => {
    const plate = read(path.join(checks, "goldens/vector-plate.txt")); let n = 0;
    for (const m of plate.matchAll(/^golden: (Rung\d)\.count = (\d+)$/gm)) { assert.strictEqual(seedCount.get(m[1]), +m[2]); n++; }
    for (const m of plate.matchAll(/^golden: (\w+) = [\w-]+ X=(\d+) Y=(\d+) Z=(\d+)$/gm)) { assert.deepStrictEqual(canonicalShares.get(m[1]), [+m[2], +m[3], +m[4]]); n++; }
    assert(drawings.Light.includes(plate.match(/^golden: XYZWrite\(full h-alpha\) = (.*)$/m)[1])); n++;
    const walk = plate.match(/^golden: PerceptualRung\(walk (\d{8})\) = (\d)$/m), lit = walk[1].indexOf("1");
    assert.strictEqual(lit < 0 ? "0" : String(8 - lit), walk[2]); n++;
    assert(plate.includes('data-vi-rules="PlateSet<PlateOn>"') && plate.includes('data-vi-rules="PlateSet"') && drawings.Light.includes('data-vi-rules="SetAlpha&lt;Unit&gt;"')); n++;
    assert(n >= renderFixture.vector_plate.minimum_checks);
});
check("every supported kit name and its native vector obligation", () => {
    const kit = fixture("kit");
    assert.deepStrictEqual([...kit.SUPPORTED].sort(), Object.keys(kit.GOLDENS).sort());
    for (const name of kit.SUPPORTED) assert(new RegExp("\\b(?:enum|protocol|typealias) " + name + "\\b").test(allDefinitions), name);
    for (const n of Object.values(kit.GOLDENS)) if (!n.startsWith("pending")) assert(fs.existsSync(path.join(checks, n)));
    assert.strictEqual(kit.SUPPORTED.filter(n => kit.GOLDENS[n].startsWith("pending")).length, 15);
});
for (const c of courtFixture.cases) check(c.id + " native and wasm", () => {
    const source = c.world === "Site/Palette" ? "Worlds/Playground/Site/Palette.swift" : courtFixture.declaration_files[c.world];
    let text = read(path.join(sc, source));
    if (c.mutation) { assert(text.includes(c.mutation[0]), c.id); text = text.replace(...c.mutation); }
    const answer = worldCourt.ask(court, c.court, text, definitions, c.question);
    assert.strictEqual(answer.exit, c.exit, c.id + ": " + answer.stdout + answer.stderr);
    const output = answer.stdout + answer.stderr;
    if (c.prefix) assert(output.includes(c.prefix), output);
    if (c.contains) assert(output.includes(c.contains), output);
    if (c.refusal_count !== undefined) assert.strictEqual(output.split("\n").filter(l => l.startsWith("✗")).length, c.refusal_count);
    for (const name of [...(c.refused || []), ...(c.additional_refused || []), ...(c.refused_readings || [])])
        assert(output.split("\n").some(l => l.startsWith("✗") && l.includes("'" + name)), c.id + ": " + name);
    if (c.left !== undefined) for (const name of c.refused_readings)
        assert(output.includes("'" + name + "' count Left = " + c.left + ", but Answer = " + c.answer), c.id);
    const args = [c.court, "world.swift", ...definitions.map(d => d.name)];
    if (c.question) for (const k of ["predicate", "encoding", "sigma"]) args.push("--" + k, c.question[k]);
    const temp = fs.mkdtempSync(path.join(require("os").tmpdir(), "gate-playground-court-"));
    try {
        fs.writeFileSync(path.join(temp, "world.swift"), text);
        for (const f of definitions) fs.writeFileSync(path.join(temp, f.name), f.text);
        const native = cp.spawnSync(path.join(here, "bin/gate-judge"), ["judge", ...args], { cwd: temp, encoding: "utf8" });
        assert.strictEqual(native.status, answer.exit, native.stdout + native.stderr);
        const claims = s => s.split("\n").filter(l => l.startsWith("✗") || l.startsWith("✓")).map(l => l.replace(/ · [\d.]+ ms/g, ""));
        assert.deepStrictEqual(claims(native.stdout + native.stderr), claims(output), c.id);
    } finally { fs.rmSync(temp, { recursive: true }); }
});
if (site) for (const id of fs.readdirSync(path.join(site, "playground"))) {
    const folder = path.join(site, "playground", id);
    if (!fs.statSync(folder).isDirectory() || !fs.existsSync(path.join(folder,"world.json"))) continue;
    check("published " + id + " reads the native snapshots and saves separately", () => {
        const snap = JSON.parse(read(path.join(folder, "snapshots.json"))), ctx = JSON.parse(read(path.join(folder, "world.json")));
        const files = JSON.parse(snap["/files"]), readable = files.files.filter(f => files.theirs?.[f]?.kind !== "CarriedFile"),
            texts = Object.fromEntries(readable.map(f => [f, snap["/world?f=" + f] || ""]));
        const result = worldCourt.verdict(court, files.worlds, texts, ctx.definitions,
            files.world_files, ctx.carried, files.layout, judge, null, ctx.plain_fragments, null, files.documents);
        const first = files.forms[0] || files.files[0], native = JSON.parse(snap["/verdict?f=" + first]);
        assert.strictEqual(result.verdict, native.verdict, id + ": " + JSON.stringify({result,native}));
        if (id === "site") { assert.strictEqual(result.verdict,"holds"); assert.strictEqual(result.checked,17); }
        const addresses = rs => rs.map(r => r.address).sort();
        assert.deepStrictEqual(addresses(result.refusals), addresses(native.refusals), id);
        assert.deepStrictEqual(result.unsupported.map(r => r.id).sort(), (native.unsupported || []).map(r => r.id).sort());
        const page = read(path.join(folder, "index.html"));
        assert(page.includes("gate.pages." + record.showcase.revision + "." + id + "."));
        assert(page.includes(record.theory.revision) && page.includes(record.judge.revision));
        assert(!page.includes('id="worldlist"') && page.includes('id="world-provenance"'));
        const shelf = JSON.parse(snap['/shelf']);
        assert(shelf.modules.includes('Site/Manifest'));
        assert.equal(snap['/shelf?m=Site/Manifest'], read(path.join(sc,'Worlds/Playground/Site/Manifest.swift')));
        assert.equal(shelf.inputs['Site/Manifest'].revision, record.showcase.revision);
        assert(!page.includes('id="world-tabs"') && !page.includes('position:fixed;top:0'));
        const tabs = JSON.parse(read(path.join(site, "playground/tabs.json")));
        assert.deepStrictEqual(tabs.map(t => shelf.inputs['Site/Manifest'].destinations[t.record]), tabs.map(t => t.id));
        if (id !== "scale") {
            const world = ctx.tab.world;
            if (world !== "Site") assert.deepStrictEqual(draw(world, readable.filter(f => f !== files.layout && !f.endsWith("my.swift"))
                .map(f => texts[f]).join("\n")).map(c => c.svg).join(""), drawings[world]);
        }
    });
}
console.log(JSON.stringify({ vectors, reports, worlds: Object.keys(drawings).length, primitives_equal:
    record.theory.files['Sources/VerificationIsIdentification/Primitive.swift'] === record.judge.primitive_sha256 }));
