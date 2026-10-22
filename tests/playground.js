// The old page's vectors now read the showcase's records, not HTML literals.
"use strict";
(async () => {
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
const contexts = require('../bin/court-contexts.js'), grammar = require('../bin/grammar-policy.js');
const {Worker} = require('node:worker_threads');
// These independent comparisons retain every original input and exact reply.
// At most three cases run together; the battery's time limits stay unchanged.
async function mapCases(values, action) {
    let next = 0;
    await Promise.all(Array.from({length:Math.min(3, values.length)}, async () => {
        while (next < values.length) { const index = next++; await action(values[index]); }
    }));
}
function wasmCall(operation, input) {
    return new Promise((resolve, reject) => {
        const worker = new Worker(path.join(__dirname, 'court-call-worker.js'), {workerData:{operation,input}});
        let answered = false, reply;
        worker.once('message', value => { answered = true; reply = value; });
        worker.once('error', reject);
        worker.once('exit', code => code === 0 && answered ? resolve(reply) : reject(Error('Court worker did not answer: ' + code)));
    });
}
const notationCourt = {source_notation: input => wasmCall('source_notation', input)};

function declaredPlan(world) {
    const id = world.split('/')[0].toLowerCase();
    const snapshot = JSON.parse(read(path.join(site, 'playground', id, 'snapshots.json')));
    return JSON.parse(snapshot['/grammar-contexts']);
}
async function declaredRequest(world, source, text, question, selector) {
    const plan = declaredPlan(world), ownPath = path.relative('Worlds/Playground/' + world.split('/')[0], source);
    const context = plan.contexts.find(c => c.court && c.court.sources.some(s => s.input === ownPath));
    assert(context, source + ': no declared source context');
    const prepared = await contexts.requests(notationCourt, context, {[ownPath]:text}, JSON.parse(plan.policy), grammar);
    assert.deepStrictEqual(prepared.refusals, []);
    const selected = prepared.requests.filter(r => r.arguments[0] === question && (!selector ||
        ['predicate','encoding','sigma'].every(k => r.arguments[r.arguments.indexOf('--' + k) + 1] === selector[k])));
    assert.strictEqual(selected.length, 1, source + ': question must be declared exactly once');
    return selected[0];
}
async function nativeAnswer(request) {
    const temp = fs.mkdtempSync(path.join(require('os').tmpdir(), 'gate-playground-court-'));
    try {
        for (const file of request.files) {
            const target = path.join(temp, file.name); fs.mkdirSync(path.dirname(target), {recursive:true});
            fs.writeFileSync(target, file.text);
        }
        return await new Promise((resolve, reject) => cp.execFile(path.join(here, 'bin/gate-judge'), ['judge', ...request.arguments],
            {cwd:temp, encoding:'utf8', maxBuffer:8*1024*1024}, (error, stdout, stderr) => {
                if (error && typeof error.code !== 'number') reject(error);
                else resolve({exit:error ? error.code : 0, stdout, stderr});
            }));
    } finally { fs.rmSync(temp, {recursive:true, force:true}); }
}
let vectors = 0;
async function check(name, fn) {
    const start = performance.now();
    process.stderr.write('PLAYGROUND START ' + name + '\n');
    await fn(); vectors++; reports.push(name);
    process.stderr.write('PLAYGROUND PASS ' + name + ' ' + ((performance.now()-start)/1000).toFixed(3) + 's\n');
}
await check("a refused certificate named budget stays a refusal", async () => {
    const c = courtFixture.cases.find(c => c.id === "light-halving"), source = courtFixture.declaration_files.Light;
    const text = read(path.join(sc, source)).replace(...c.mutation).replace("public typealias HalfFact =", "public typealias budget =");
    const request = await declaredRequest('Light', source, text, 'where');
    const answer = JSON.parse(await wasmCall('judge',JSON.stringify({arguments:request.arguments, files:request.files})));
    const report = await contexts.bound(request, answer);
    assert.equal(report.outcome, 'not-established');
    assert(report.results.some(r => r.diagnostics.some(d => d.includes('budget'))));
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
    // Historical fixtures keep their old paths. The current Drawing owner
    // names the live composition, including a separately declared data file.
    const drawingCase = JSON.parse(read(path.join(sc, "Contracts/Drawing/v0.1/manifest.json"))).cases.find(c =>
        c.target && c.sources.every(n => n.startsWith("Worlds/Playground/" + world + "/")));
    const currentSources = drawingCase ? drawingCase.sources : sources;
    const text = currentSources.map(n => read(path.join(sc, n))).join("\n");
    const original = [world + ".swift", ...(["Atom", "Light"].includes(world) ? [world + "Pages.swift"] : [])]
        .map(n => read(path.join(base, "corpus/worlds", n))).join("\n");
    await check(world + " historical snapshots stay historical; current file orders agree", () => {
        const arts = draw(world, text), reverse = draw(world, [...currentSources].reverse().map(n => read(path.join(sc, n))).join("\n"));
        const pinned = fixture("r2-preservation").render.worlds[world];
        if (pinned) assert.deepStrictEqual(hashes(draw(world, original, true)),
            pinned.map(({name,bytes,sha256})=>({name,bytes,sha256})), world + " historical renderer");
        assert.deepStrictEqual(hashes(draw(world, updated(original, sources), true)), copy.drawings[world], world + " historical copy repair");
        assert.deepStrictEqual(reverse, arts, world);
        drawings[world] = arts.map(c => c.svg).join("");
        if (world !== "Company") assert(arts.length >= 1);
    });
    await check(world + " lawful, known and guarded", () => {
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
for (const name of ["Manifest", "Palette"]) await check("Site/" + name + " preserves its source obligations and page guards", () => {
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
await check("where budget remains unsupported at its original requirement addresses", () => {
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
await check("all seventeen palette reading lies remain addressed in wasm", async () => {
    const text = read(path.join(sc, "Worlds/Playground/Site/Palette.swift"));
    await mapCases(fixture("palette-residue").requirements, async row => {
        const line = new RegExp("^public typealias " + row.id + " = Legible<([^\\n]+)>$", "m");
        const m = text.match(line); assert(m, row.id);
        const args = m[1].split(", "); assert.strictEqual(args.length, 3);
        const wrong = "public typealias " + row.id + " = Legible<" + args[0] + ", " + args[1]
            + ", Plus<Unit, " + args[2] + ">>";
        const request = await declaredRequest("Site/Palette", "Worlds/Playground/Site/Palette.swift",
            text.replace(m[0], wrong), "count",
            {predicate:"PaletteContrastQuestion",encoding:"UnaryArithmeticEncoding",sigma:"PaletteLight"});
        const result = JSON.parse(await wasmCall('judge',JSON.stringify({arguments:request.arguments,files:request.files})));
        assert.strictEqual(result.exit, 1, row.id);
        const report = await contexts.bound(request, result), refusals = report.results.flatMap(r => r.diagnostics);
        assert.strictEqual(refusals.length, 1, row.id);
        assert(refusals[0].includes("'" + row.id + ".R1'"), refusals[0]);
    });
});
await check("company's four vectors", () => {
    const clean = judge("Company.swift", companyText), want = company.golden.clean;
    for (const k of ["declarations", "lookups", "premises", "refusals"]) assert.deepStrictEqual(clean[k], want[k]);
    for (const [id, [anchor, lie]] of Object.entries(company.lies)) {
        assert(companyText.includes(anchor));
        const refusals = judge("Company.swift", companyText.replace(anchor, lie)).refusals;
        assert(refusals.every(r => r.file === "Company.swift"));
        assert.deepStrictEqual(refusals.map(({line, premise}) => ({line, premise})), company.golden[id]);
    }
});
await check("historical native dynamics golden bytes", () => {
    const config = renderFixture.dynamics;
    const vocab = Object.fromEntries(Object.entries(config.gameKit).map(([k, v]) => [k, new Set(v)]));
    const text = read(path.join(checks, config.source)), p = judge("dynamics-world.swift", text, vocab).parsed;
    const result = historicalRenderer.renderAll(p.declarations, p.order, p.literals, p.topAliases);
    assert.deepStrictEqual(result.errors, []);
    assert.strictEqual(result.canvases[0].svg + "\n", read(path.join(checks, config.expected_svg)));
});
await check("the page's four guards still object", () => {
    const f = fixture("guards"), text = f.files.map(n => read(path.join(sc, n))).join("\n");
    for (const c of f.cases) {
        const changed = (c.prefix || "") + text + (c.suffix || "");
        const objections = pageGuards(judge("Basics.swift", changed, kitVocabulary).parsed, changed.split("\n"), outside);
        assert.strictEqual(objections.filter(o => o.premise.includes(c.expect)).length, 1, c.id);
    }
});
await check("light and atom colour vectors", () => {
    for (const [world, values] of [["Light", renderFixture.light_color_occurrences], ["Atom", renderFixture.atom_color_occurrences]])
        for (const [color, want] of Object.entries(values)) assert.strictEqual(drawings[world].split(color).length - 1, want, color);
});
await check("the twenty-eight native vector plate observations", () => {
    const plate = read(path.join(checks, "goldens/vector-plate.txt")); let n = 0;
    for (const m of plate.matchAll(/^golden: (Rung\d)\.count = (\d+)$/gm)) { assert.strictEqual(seedCount.get(m[1]), +m[2]); n++; }
    for (const m of plate.matchAll(/^golden: (\w+) = [\w-]+ X=(\d+) Y=(\d+) Z=(\d+)$/gm)) { assert.deepStrictEqual(canonicalShares.get(m[1]), [+m[2], +m[3], +m[4]]); n++; }
    assert(drawings.Light.includes(plate.match(/^golden: XYZWrite\(full h-alpha\) = (.*)$/m)[1])); n++;
    const walk = plate.match(/^golden: PerceptualRung\(walk (\d{8})\) = (\d)$/m), lit = walk[1].indexOf("1");
    assert.strictEqual(lit < 0 ? "0" : String(8 - lit), walk[2]); n++;
    assert(plate.includes('data-vi-rules="PlateSet<PlateOn>"') && plate.includes('data-vi-rules="PlateSet"') && drawings.Light.includes('data-vi-rules="SetAlpha&lt;Unit&gt;"')); n++;
    assert(n >= renderFixture.vector_plate.minimum_checks);
});
await check("every supported kit name and its native vector obligation", () => {
    const kit = fixture("kit");
    assert.deepStrictEqual([...kit.SUPPORTED].sort(), Object.keys(kit.GOLDENS).sort());
    for (const name of kit.SUPPORTED) assert(new RegExp("\\b(?:enum|protocol|typealias) " + name + "\\b").test(allDefinitions), name);
    for (const n of Object.values(kit.GOLDENS)) if (!n.startsWith("pending")) assert(fs.existsSync(path.join(checks, n)));
    assert.strictEqual(kit.SUPPORTED.filter(n => kit.GOLDENS[n].startsWith("pending")).length, 15);
});
await mapCases(courtFixture.cases, c => check(c.id + " native and wasm", async () => {
    const source = c.world === "Site/Palette" ? "Worlds/Playground/Site/Palette.swift" : courtFixture.declaration_files[c.world];
    let text = read(path.join(sc, source));
    if (c.mutation) { assert(text.includes(c.mutation[0]), c.id); text = text.replace(...c.mutation); }
    const request = await declaredRequest(c.world, source, text, c.court, c.question);
    const answer = JSON.parse(await wasmCall('judge',JSON.stringify({arguments:request.arguments,files:request.files})));
    assert.strictEqual(answer.exit, c.exit, c.id + ': ' + answer.stdout + answer.stderr);
    assert.deepStrictEqual(await nativeAnswer(request), answer, c.id + ': exact native/wasm response');
    const report = await contexts.bound(request, answer), objections = report.results.flatMap(r => r.diagnostics);
    for (const key of ['equalities','memberships','readings']) if (c[key] !== undefined)
        assert.equal(report.results.reduce((sum,r) => sum+r[key],0), c[key], c.id + ': ' + key);
    if (c.refusal_count !== undefined) assert.equal(objections.length, c.refusal_count, c.id);
    for (const name of [...(c.refused || []), ...(c.additional_refused || []), ...(c.refused_readings || [])])
        assert(objections.some(d => d.includes("'" + name)), c.id + ': ' + name);
    for (const [name, expected] of Object.entries(c.reading_counts || {}))
        assert(objections.some(d => d.includes("'" + name + "' count Left = " + expected.left + ', but Answer = ' + expected.answer)), c.id + ': ' + name);
    if (c.stitch_refusals) {
        const stitches = ['ThirdFloorStitch.Right','SecondFloorStitch.Right','GroundFloorStitch.Right','TwoRoadsOneDrop.Right'];
        assert.deepEqual(stitches.filter(name => objections.some(d => d.includes("'" + name + "'"))).sort(), [...c.stitch_refusals].sort());
    }
}));

if (site) for (const id of fs.readdirSync(path.join(site, "playground"))) {
    const folder = path.join(site, "playground", id);
    if (!fs.statSync(folder).isDirectory() || !fs.existsSync(path.join(folder,"world.json"))) continue;
    await check("published " + id + " reads the native snapshots and saves separately", async () => {
        const snap = JSON.parse(read(path.join(folder, "snapshots.json"))), ctx = JSON.parse(read(path.join(folder, "world.json")));
        const files = JSON.parse(snap["/files"]), readable = files.files.filter(f => files.theirs?.[f]?.kind !== "CarriedFile"),
            texts = Object.fromEntries(readable.map(f => [f, snap["/world?f=" + f] || ""]));
        const plan = JSON.parse(snap['/grammar-contexts']), contextual = new Set((plan.contexts || []).flatMap(c =>
            c.court ? c.court.sources.filter(s => s.role === 'own').map(s => s.input) : []));
        const groups = files.worlds.map(group => group.filter(f => !contextual.has(f))).filter(group => group.length);
        const result = worldCourt.verdict(court, groups, texts, ctx.definitions,
            files.world_files, ctx.carried, files.layout, judge, null, null, files.documents);
        if (contextual.size) {
            // Taking receipt rows must not change the full question's hash.
            // This also holds for Scale: unchanged input never invokes judge.
            for (const context of plan.contexts || []) for (const request of context.requests || []) {
                const digest = await contexts.sha(contexts.canonical(request));
                assert((context.receipts || []).some(r => r.request_sha256 === digest), id + ": owner receipt does not bind this exact published question");
            }
            let fresh = 0;
            const carrier = {...court, judge: request => { fresh++; return court.judge(request); }};
            const read = await contexts.read(carrier, plan, texts);
            assert.strictEqual(fresh, 0, id + ": unchanged question was recomputed instead of taking its owner receipt");
            result.checked += read.checked; result.refusals.push(...read.refusals); result.unsupported.push(...read.unsupported);
            result.verdict = result.refusals.length ? 'refused' : result.unsupported.length
                ? (result.checked ? 'partial' : 'unsupported') : result.checked ? 'holds' : 'empty';
        }
        const first = files.forms[0] || files.files[0], native = JSON.parse(snap["/verdict?f=" + first]);
        assert.strictEqual(result.verdict, native.verdict, id + ": " + JSON.stringify({result,native}));
        if (id === "site") { assert.strictEqual(result.verdict,"holds"); assert.strictEqual(result.checked,18); }
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
        const ownerRecord = JSON.parse(read(path.join(sc, 'Worlds/Playground', ctx.tab.world, '.gate/forms-definitions.json')));
        const catalogInput = ownerRecord.files.find(f => f.source_path === 'Worlds/Playground/Site/Manifest.swift');
        assert(catalogInput, id + ': owner declares the catalog input');
        assert.equal(shelf.inputs['Site/Manifest'].revision, catalogInput.revision);
        assert.equal(shelf.inputs['Site/Manifest'].sha256, catalogInput.sha256);
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

})().catch(error => { console.error(error); process.exitCode = 1; });
