// Execute the published fetch shim itself. No browser or second storage rule.
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm"), assert = require("assert");
const court = require("../bin/court-wasm/node/vi_court.js"), { judge } = require("../bin/judge.js");
const {lint} = require("../bin/playground-lint.js"), {pageGuards} = require("../bin/playground-guards.js");
const {kitVocabulary} = require("../bin/renderer.js");
const GateWorldCourt = require("../bin/world-court.js");
const root = process.argv[2], record = JSON.parse(fs.readFileSync(path.join(root, "worlds.from")));
const storage = Object.create({ getItem(k) { return this[k] ?? null; }, setItem(k,v) { this[k] = String(v); }, removeItem(k) { delete this[k]; } });
function open(id) {
    const page = fs.readFileSync(id === "demo" ? path.join(root, "index.html") : path.join(root, "playground", id, "index.html"), "utf8");
    const at = page.indexOf("wasm_bindgen.initSync("), start = page.lastIndexOf("<script>", at) + 8, end = page.indexOf("</script>", at);
    assert(at >= 0 && end > start);
    const scope = { localStorage: storage, wasm_bindgen: { ...court, initSync() {} }, VI_COURT_WASM_BASE64: "",
        Uint8Array, atob, Response, Map, GateWorldCourt, judge, lint, pageGuards, kitVocabulary, location: { search: "" }, fetch: async () => { throw Error("unexpected network"); } };
    scope.document = {addEventListener(){}};
    scope.window = scope;
    vm.runInNewContext(page.slice(start, end), scope);
    return scope;
}
(async () => {
    const a = open("readme"), b = open("basics"), file = "same.swift";
    await a.fetch("/world?f=" + file, { method: "PUT", body: "intro text" });
    await b.fetch("/world?f=" + file, { method: "PUT", body: "basics text" });
    assert.strictEqual(await (await a.fetch("/world?f=" + file)).text(), "intro text");
    assert.strictEqual(await (await b.fetch("/world?f=" + file)).text(), "basics text");
    const otherPin = "gate.pages.other-pin.readme.same.swift";
    storage.setItem(otherPin, "another revision");
    a.__resetWipe();
    open("demo").__resetWipe();
    assert.strictEqual(await (await b.fetch("/world?f=" + file)).text(), "basics text");
    assert.strictEqual(storage.getItem(otherPin), "another revision");
    assert.strictEqual(storage.getItem("gate.pages." + record.showcase.revision + ".readme." + file), null);
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
    // Execute tick itself against the real shim. A refused Atom key change
    // survives reopening, together with its red receipt; the repository policy
    // still withholds a red file. No unconditional write is hidden in a stub.
    const atom = open("atom"), snaps = JSON.parse(fs.readFileSync(path.join(root,"playground/atom/snapshots.json")));
    const f = "Dictionary/Atom.swift", before = snaps["/world?f=" + f];
    const ui = fs.readFileSync(path.join(__dirname,"../web/ui.html"),"utf8");
    const start = ui.indexOf("async function tick("), end = ui.indexOf("\n}",start) + 2;
    const state = { file:f, text:before.replace("Electron = Charged", "Electron = Trapped") };
    assert.notStrictEqual(state.text, before);
    const flag = await (await atom.fetch("/files")).json();
    assert.strictEqual(flag.save_policy, "reader-draft");
    let writes = 0;
    const el = {};
    Object.assign(atom, { active:f, editor:{value:state.text}, readerDrafts:true, lastRefusals:[], layoutFile:"gate.manifest.swift",
        paintUngranted(){}, refreshGit(){}, readFiles(){}, document:{getElementById(){return el;}},
        render:async()=>{ const r = await (await atom.fetch("/verdict?f=" + f,{method:"POST",body:atom.editor.value})).json();
            atom.lastRefusals=r.refusals.map(r=>({file:r.address.split(":")[0]})); assert(r.refusals.length > 0); }
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
    // A deep edit in the five-megabyte source fits a small reader record,
    // reopens byte-for-byte, and retains its refusal. A second edit is still
    // based on the pin, not an unrecorded intermediate buffer.
    const scale = open("scale"), scaleSnap = JSON.parse(fs.readFileSync(path.join(root,"playground/scale/snapshots.json")));
    const big = scaleSnap["/world?f=Company.swift"], needle = "VerifiedInDepartment<Emp12796, Finance>";
    const wrong = big.replace(needle,"VerifiedInDepartment<Emp12796, Sales>"); assert.notStrictEqual(wrong,big);
    await scale.fetch("/world?f=Company.swift",{method:"PUT",body:wrong});
    const bigKey = "gate.pages." + record.showcase.revision + ".scale.Company.swift";
    assert(storage.getItem(bigKey).length < 100000);
    assert.strictEqual(JSON.parse(storage.getItem(bigKey)).verdict.verdict,"refused");
    assert.strictEqual(await (await open("scale").fetch("/world?f=Company.swift")).text(),wrong);
    const heading = "// reader's heading\n" + wrong;
    await scale.fetch("/world?f=Company.swift",{method:"PUT",body:heading});
    const twice = heading + "\n// reader's ending";
    await scale.fetch("/world?f=Company.swift",{method:"PUT",body:twice});
    assert.strictEqual(await (await open("scale").fetch("/world?f=Company.swift")).text(),twice);
    assert(storage.getItem(bigKey).length < 100000);
    // Storage failure is a failed write, never a cheerful saved receipt.
    storage.setItem = ()=>{throw Error("quota");};
    const failed = await reopened.fetch("/world?f="+encodeURIComponent(f),{method:"PUT",body:state.text});
    assert.strictEqual(failed.status,507);
    atom.render = async()=>{};
    await atom.tick(true); assert.strictEqual(el.textContent,"draft not saved: browser storage unavailable");
    delete storage.setItem;
    reopened.__resetWipe(); assert.strictEqual(storage.getItem(key),null);
    console.log("PLAYGROUND STORAGE GREEN: refused Atom draft and verdict survive reload; native red withholds; stale text, quota and scoped reset");

})().catch(e => { console.error(e); process.exitCode = 1; });
