// Execute the published fetch shim itself. No browser or second storage rule.
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm"), assert = require("assert");
const court = require("../bin/court-wasm/node/vi_court.js"), { judge } = require("../bin/judge.js");

const {kitVocabulary} = require("../bin/renderer.js");
const GateWorldCourt = require("../bin/world-court.js");
const GateCourtContexts = require("../bin/court-contexts.js");
const root = process.argv[2], record = JSON.parse(fs.readFileSync(path.join(root, "worlds.from")));
const storage = Object.create({ getItem(k) { return this[k] ?? null; }, setItem(k,v) { this[k] = String(v); }, removeItem(k) { delete this[k]; } });
function open(id, options = {}) {
    const folder = id === "demo" ? root : path.join(root, "playground", id);
    const {lint} = fs.existsSync(path.join(folder, "playground-lint.js")) ? require(path.join(folder, "playground-lint.js")) : {};
    const {pageGuards} = fs.existsSync(path.join(folder, "playground-guards.js")) ? require(path.join(folder, "playground-guards.js")) : {};
    const page = fs.readFileSync(path.join(folder, "index.html"), "utf8");
    const at = page.indexOf("wasm_bindgen.initSync("), start = page.lastIndexOf("<script>", at) + 8, end = page.indexOf("</script>", at);
    assert(at >= 0 && end > start);
    const scope = { localStorage: storage, wasm_bindgen: { ...court, initSync() {} }, VI_COURT_WASM_BASE64: "",
        Uint8Array, atob, Response, Map, GateWorldCourt, GateCourtContexts, judge, lint, pageGuards, kitVocabulary, location: { search: "" }, fetch: async () => { throw Error("unexpected network"); } };
    scope.document = {addEventListener(){}};
    scope.window = scope;
    if (options.fileWorker) {
        // Run the finished file-page shim and its actual carried Blob body.
        // Node supplies the thread, not a replacement Court or transport rule.
        const {Worker: Thread} = require("worker_threads"), urls = new Map(), workers = [];
        let sequence = 0;
        scope.location.protocol = "file:";
        scope.Blob = class { constructor(parts) { this.source = parts.join(""); } };
        scope.URL = {createObjectURL(blob) { const url = "blob:fixture/" + ++sequence; urls.set(url, blob.source); return url; },
            revokeObjectURL(url) { urls.delete(url); }};
        scope.Worker = class {
            constructor(url) {
                this.pending = []; workers.push(this);
                // Loading happens after construction; the URL must remain live.
                setImmediate(() => {
                    if (this.closed) return;
                    try {
                        assert(urls.has(url), "file worker URL retired before its source was read");
                        const source = "const {parentPort}=require('worker_threads');global.self=global;self.postMessage=data=>parentPort.postMessage(data);\n"
                            + urls.get(url) + "\nparentPort.on('message',data=>self.onmessage({data}));";
                        this.thread = new Thread(source, {eval:true});
                        this.thread.on("message", data => this.onmessage?.({data}));
                        this.thread.on("error", error => this.onerror?.({message:error.message}));
                        for (const message of this.pending) this.thread.postMessage(message);
                        this.pending = [];
                    } catch (error) { this.onerror?.({message:error.message}); }
                });
            }
            postMessage(message) { if (this.thread) this.thread.postMessage(message); else this.pending.push(message); }
            terminate() { this.closed = true; return this.thread?.terminate(); }
        };
        scope.__workerFixture = {workers, urls, stop:() => Promise.all(workers.map(w => w.terminate()))};
        assert(page.includes("worker-src 'self' blob:"));
        // The finished artifact supplies the same wasm bytes to its Blob.
        vm.runInNewContext(fs.readFileSync(path.join(folder,"court/vi_court_bytes.js"),"utf8"), scope);
    }
    vm.runInNewContext(page.slice(start, end), scope);
    return scope;
}
(async () => {
    const a = open("readme"), b = open("basics"), file = "ReadMePages.swift", basicsFile = "BasicsPages.swift";
    await a.fetch("/world?f=" + file, { method: "PUT", body: "intro text" });
    await b.fetch("/world?f=" + basicsFile, { method: "PUT", body: "basics text" });
    assert.strictEqual(await (await a.fetch("/world?f=" + file)).text(), "intro text");
    assert.strictEqual(await (await b.fetch("/world?f=" + basicsFile)).text(), "basics text");
    const otherPin = "gate.pages.other-pin.readme." + file;
    storage.setItem(otherPin, "another revision");
    a.__resetWipe();
    open("demo").__resetWipe();
    assert.strictEqual(await (await b.fetch("/world?f=" + basicsFile)).text(), "basics text");
    assert.strictEqual(storage.getItem(otherPin), "another revision");
    assert.strictEqual(storage.getItem("gate.pages." + record.showcase.revision + ".readme." + file), null);
    // P6-other-write-routes also runs over the finished HTML, including the
    // ordinary selected root. No acknowledged structural write may be a no-op.
    for (const id of ["demo", "readme", "basics", "atom"]) {
        const page = open(id), before = await (await page.fetch("/files")).text();
        const layout = JSON.parse(before).layout, kept = JSON.stringify(storage);
        for (const url of ["/world?f="+encodeURIComponent(layout), "/value?name=Width&to=1",
                           "/declare?f=New.swift&role=forms", "/world?f=NoSuchFile.swift"]) {
            const r = await page.fetch(url,{method:"PUT",body:"not written"}), said = await r.json();
            assert([405,409].includes(r.status) && said.address && said.reason && said.next);
            assert.strictEqual(await (await page.fetch("/files")).text(),before);
            assert.strictEqual(JSON.stringify(storage),kept);
        }
    }
    // The selected gate root is an ordinary world, not a showcase context.
    // Its deliberately red reading must now survive in the same draft format.
    const note = page => page.match(/<div id="published-note">([\s\S]*?)<\/div>/)?.[1];
    const rootNote = note(fs.readFileSync(path.join(root, "index.html"), "utf8"));
    assert(rootNote && rootNote.includes("draft and verdict saved in this browser, including refusals"),
        "the finished root must say that refused reader drafts are saved");
    assert(!rootNote.includes("saved on green"));
    for (const id of ["readme", "basics", "atom"])
        assert.strictEqual(note(fs.readFileSync(path.join(root,"playground",id,"index.html"),"utf8")), rootNote,
            "all published snapshots use the same base note");
    const ordinary = open("demo"), rootFiles = await (await ordinary.fetch("/files")).json();
    const rootFile = rootFiles.forms[0];
    const rootEdit = await (await ordinary.fetch("/world?f="+rootFile)).text() + "\n// reader's ordinary-world edit\n";
    assert.strictEqual((await (await ordinary.fetch("/files")).json()).save_policy,"reader-draft");
    assert((await ordinary.fetch("/world?f="+rootFile,{method:"PUT",body:rootEdit})).ok);
    const ordinaryRow = JSON.parse(storage.getItem("gate.reader-draft.v1."+rootFile));
    assert.strictEqual(ordinaryRow.text,rootEdit);
    assert.strictEqual(ordinaryRow.verdict.verdict,"refused");
    assert.strictEqual(await (await open("demo").fetch("/world?f="+rootFile)).text(),rootEdit);
    ordinary.__resetWipe();
    for (const id of ["light", "atom", "site"]) {
        const page = open(id), folder = path.join(root, "playground", id);
        const snapshots = JSON.parse(fs.readFileSync(path.join(folder, "snapshots.json")));
        const files = JSON.parse(snapshots["/files"]), f = files.forms[0];
        const native = JSON.parse(snapshots["/verdict?f=" + f]);
        const live = await (await page.fetch("/verdict?f=" + f, {method:"POST",body:snapshots["/world?f=" + f]})).json();
        assert.deepStrictEqual(live.refusals, native.refusals, id);
        assert.deepStrictEqual(live.unsupported, native.unsupported, id);
        assert.strictEqual(live.verdict, native.verdict, id);
        assert.strictEqual((await (await page.fetch("/gitstatus?f=" + encodeURIComponent(f))).json()).git, "source");
    }
    // Execute tick itself against the real shim. A refused Atom count change
    // survives reopening, together with its red receipt; the repository policy
    // still withholds a red file. No unconditional write is hidden in a stub.
    const atom = open("atom"), snaps = JSON.parse(fs.readFileSync(path.join(root,"playground/atom/snapshots.json")));
    const f = "Dictionary/Atom.swift", before = snaps["/world?f=" + f];
    const ui = fs.readFileSync(path.join(__dirname,"../web/ui.html"),"utf8");
    const refusalStart = ui.indexOf("function showWriteRefusal("), refusalEnd = ui.indexOf("\n}",refusalStart) + 2;
    atom.esc = s=>String(s).replaceAll("<","&lt;");
    vm.runInContext(ui.slice(refusalStart,refusalEnd),atom);
    const start = ui.indexOf("async function tick("), end = ui.indexOf("\n}",start) + 2;
    // Charged -> Trapped is a declared SlotRule transition. EdgeSame guards
    // rendering in an excluded function body; it is not a nominal where gate.
    const station = before.replace("Electron = Charged", "Electron = Trapped");
    assert.notStrictEqual(station,before);
    const stationVerdict = await (await atom.fetch("/verdict?f="+f,{method:"POST",body:station})).json();
    assert.strictEqual(stationVerdict.verdict,"holds");
    assert.deepStrictEqual(stationVerdict.refusals,[]);
    assert.deepStrictEqual(stationVerdict.unsupported,[]);
    const state = { file:f, text:before.replace("BalmerAlphaDrop = Plus<U16, U4>", "BalmerAlphaDrop = Plus<U16, Plus<U4, U1>>") };
    assert.notStrictEqual(state.text, before);
    const flag = await (await atom.fetch("/files")).json();
    assert.strictEqual(flag.save_policy, "reader-draft");
    let writes = 0;
    const el = {};
    Object.assign(atom, { active:f, editor:{value:state.text}, readerDrafts:true, lastRefusals:[], layoutFile:"gate.manifest.swift",
        paintUngranted(){}, refreshGit(){}, readFiles(){}, document:{getElementById(){return el;}},
        render:async()=>{ const r = await (await atom.fetch("/verdict?f=" + f,{method:"POST",body:atom.editor.value})).json();
            atom.lastRefusals=r.refusals.map(r=>({file:r.address.split(":")[0]}));
            assert.strictEqual(r.verdict,"refused"); assert.deepStrictEqual(r.unsupported,[]);
            assert.strictEqual(r.refusals.length,2);
            for(const name of ["SecondFloorStitch.Right","TwoRoadsOneDrop.Right"])
                assert(r.refusals.some(row=>row.claim.includes(name)),name); }
    });
    const fetch = atom.fetch;
    atom.fetch = (...args)=>{ if(args[1]?.method === "PUT") writes++; return fetch(...args); };
    vm.runInContext(ui.slice(start,end), atom);
    await atom.tick(true);
    assert.strictEqual(writes,1);
    const reopened = open("atom");
    assert.strictEqual(await (await reopened.fetch("/world?f="+encodeURIComponent(f))).text(), state.text);
    const key = "gate.pages." + record.showcase.revision + ".atom." + f;
    const kept = JSON.parse(storage.getItem(key));
    assert.strictEqual(kept.text,state.text); assert.strictEqual(kept.verdict.verdict,"refused");
    assert(kept.verdict.refusals.length > 0);
    atom.readerDrafts = false;
    await atom.tick(true); assert.strictEqual(writes,1); assert(el.innerHTML.includes("refused: nothing written"));
    // A later edit while a verdict is outstanding must not save a text with
    // somebody else's receipt. The next scheduled tick handles the new buffer.
    atom.readerDrafts = true;
    atom.render = async()=>{atom.editor.value += "\n// newer edit";};
    await atom.tick(true); assert.strictEqual(writes,1);
    // A deep edit in the final owner part fits a small reader record,
    // reopens byte-for-byte, and retains its refusal. A second edit is still
    // based on the pin, not an unrecorded intermediate buffer.
    const scale = open("scale"), scaleSnap = JSON.parse(fs.readFileSync(path.join(root,"playground/scale/snapshots.json")));
    const scaleFile=JSON.parse(scaleSnap['/files']).files.find(f=>(scaleSnap['/world?f='+f]||'').includes('VerifiedView<Emp12799, PeopleShare>'));
    assert(scaleFile);
    const big = scaleSnap["/world?f="+scaleFile], needle = "VerifiedView<Emp12799, PeopleShare>";
    assert(big.length >= 300000, "exercise compact drafts on a large owner part");
    const wrong = big.replace(needle,"VerifiedView<Emp12799, FinanceShare>"); assert.notStrictEqual(wrong,big);
    await scale.fetch("/world?f="+scaleFile,{method:"PUT",body:wrong});
    const bigKey = "gate.pages." + record.showcase.revision + ".scale."+scaleFile;
    assert(storage.getItem(bigKey).length < 100000);
    assert.strictEqual(JSON.parse(storage.getItem(bigKey)).verdict.verdict,"refused");
    assert.strictEqual(await (await open("scale").fetch("/world?f="+scaleFile)).text(),wrong);
    const heading = "// reader's heading\n" + wrong;
    await scale.fetch("/world?f="+scaleFile,{method:"PUT",body:heading});
    const twice = heading + "\n// reader's ending";
    await scale.fetch("/world?f="+scaleFile,{method:"PUT",body:twice});
    assert.strictEqual(await (await open("scale").fetch("/world?f="+scaleFile)).text(),twice);
    assert(storage.getItem(bigKey).length < 100000);
    for (const id of ["readme", "basics", "atom"]) {
        const page = open(id), snapshots = JSON.parse(fs.readFileSync(path.join(root, "playground", id, "snapshots.json")));
        const listed = JSON.parse(snapshots["/files"]), taken = Object.keys(listed.theirs || {});
        assert(taken.length > 0);
        assert(!listed.files.some(f => f.endsWith(".ttf")));
        for (const f of taken) {
            assert(listed.files.includes(f));
            const pinned = snapshots["/world?f=" + f];
            const key = "gate.pages." + record.showcase.revision + "." + id + "." + f;
            storage.setItem(key, JSON.stringify({format: 1, text: "forged prior draft"}));
            assert.strictEqual(await (await page.fetch("/world?f=" + encodeURIComponent(f))).text(), pinned);
            const wrote = await page.fetch("/world?f=" + encodeURIComponent(f), {method:"PUT", body:"forged write"});
            assert.strictEqual(wrote.status, 409);
            assert.strictEqual(await (await open(id).fetch("/world?f=" + encodeURIComponent(f))).text(), pinned);
            storage.removeItem(key);
        }
    }
    // Storage failure is a failed write, never a cheerful saved receipt.
    storage.setItem = ()=>{throw Error("quota");};
    const failed = await reopened.fetch("/world?f="+encodeURIComponent(f),{method:"PUT",body:state.text});
    assert.strictEqual(failed.status,507);
    atom.render = async()=>{};
    await atom.tick(true); assert(el.textContent.includes("not saved: " + f) && el.textContent.includes("browser storage unavailable"));
    delete storage.setItem;
    reopened.__resetWipe(); assert.strictEqual(storage.getItem(key),null);
    const fromFile = open("atom", {fileWorker:true}), fixture = fromFile.__workerFixture;
    try {
        const changed = before.replace("public typealias BalmerAlphaDrop = Plus<U16, U4>",
            "public typealias BalmerAlphaDrop = Plus<U16, Plus<U4, U1>>");
        assert.notStrictEqual(changed,before);
        const answer = await (await fromFile.fetch("/verdict?f="+encodeURIComponent(f),{method:"POST",body:changed})).json();
        assert.strictEqual(answer.verdict,"refused"); assert.deepStrictEqual(answer.unsupported,[]);
        assert.strictEqual(answer.refusals.length,2);
        for (const name of ["SecondFloorStitch.Right","TwoRoadsOneDrop.Right"])
            assert(answer.refusals.some(r => r.claim.includes(name)),name);
        assert.strictEqual(fixture.workers.length,1); assert.strictEqual(fixture.urls.size,0);
    } finally { await fixture.stop(); }
    console.log("PLAYGROUND STORAGE GREEN: refused Atom draft and verdict survive reload; native red withholds; stale text, quota and scoped reset");

})().catch(e => { console.error(e); process.exitCode = 1; });
