// P6-other-write-routes: execute the delivered shim and the actual UI gestures.
"use strict";
const assert = require("assert"), fs = require("fs"), vm = require("vm");
function implementation(ui, name) {
    const start = ui.search(new RegExp("(?:async )?function " + name + "\\("));
    assert(start >= 0, name);
    return ui.slice(start, ui.indexOf("\n}", start) + 2);
}
function storage() {
    const s = Object.create(null);
    Object.defineProperties(s, {
        getItem:{value:k=>s[k] ?? null}, setItem:{value:(k,v)=>{s[k]=String(v);}},
        removeItem:{value:k=>{delete s[k];}}
    });
    return s;
}
async function check(source) {
    const names = ["gate.manifest.swift", "Facts.swift", "Borrowed.swift"];
    for (const context of [null, {pin:"pin",world:"island"}]) {
        const files = {files:names,layout:names[0],forms:[names[1]],worlds:[[names[1]]],
            theirs:{"Borrowed.swift":{address:"gate.manifest.swift:9",kind:"CarriedFile"}}};
        const snap = {"/files":JSON.stringify(files),"/version":"{}"};
        for (const f of names) { snap["/world?f="+f] = "owner " + f; snap["/verdict?f="+f] = "{}"; }
        const kept = storage(), nodes = {verdicts:{},gitstate:{}};
        const c = vm.createContext({Response,Uint8Array,atob,localStorage:kept,
            VI_COURT_WASM_BASE64:"",wasm_bindgen:{initSync(){}},
            judge(){return {refusals:[]};},kitVocabulary:{},lint(){},pageGuards(){},
            GateWorldCourt:{verdict(){return {verdict:"holds",refusals:[]};}},
            document:{addEventListener(){},getElementById:id=>nodes[id]},location:{},
            fetch:async()=>{throw Error("unexpected network");}});
        c.window = c;
        let script = source.shim.replace(/^<script[^>]*>.*<\/script>\s*$/gm, "")
            .replace(/^<\/?script>\s*$/gm, "");
        for (const [k,v] of Object.entries({__SNAP__:snap,__CONTEXT__:context,__STORAGE__:"draft.",
            __FORMS__:files.forms,__WORLDS__:files.worlds,__LAYOUT__:files.layout,__ALL__:names,
            __COURT_WORKER_GLUE__:"",__COURT_WORKER_HANDLER__:""}))
            script = script.split(k).join(JSON.stringify(v));
        vm.runInContext(script, c);
        const before = await (await c.fetch("/files")).text();
        for (const [method,url] of [
            ["PUT","/world?f=gate.manifest.swift"], ["PUT","/value?name=Width&to=1"],
            ["PUT","/declare?f=New.swift&role=forms"], ["PUT","/unknown"],
            ["PUT","/worlds?f=Facts.swift"], ["PUT","/world?f=Missing.swift"],
            ["PUT","/world?f=%xx"], ["PUT","/world"],
            ["PATCH","/world?f=Facts.swift"], ["DELETE","/world?f=Facts.swift"],
            ["POST","/world?f=Facts.swift"]]) {
            const r = await c.fetch(url,{method,body:"must not land"});
            assert([405,409].includes(r.status), method + " " + url + " returned " + r.status);
            const said = await r.json();
            assert(said.address && said.reason && said.next.includes("gate serve"));
            assert.strictEqual(await (await c.fetch("/files")).text(), before);
            assert.strictEqual(Object.keys(kept).length, 0);
            for (const f of names) assert.strictEqual(await (await c.fetch("/world?f="+f)).text(), snap["/world?f="+f]);
        }
        // A supported file draft still writes and reopens.
        const wrote = await c.fetch("/world?other=x&f=Facts.swift",{method:"put",body:"reader draft"});
        assert(wrote.ok);
        assert.strictEqual(await (await c.fetch("/world?f=Facts.swift")).text(), "reader draft");
        assert.strictEqual((await c.fetch("/world?f=Borrowed.swift",{method:"PUT",body:"no"})).status,409);

        // Every gesture displays the host's reason and address, without following
        // the success path, and treats hostile words as text.
        let refreshed = 0;
        Object.assign(c, {esc:s=>String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;"),
            undeclaredView:"New.swift",active:names[0],editor:{value:"new manifest"},lastRefusals:[],readerDrafts:true,
            layoutFile:names[0],render:async()=>{},paintUngranted(){},refreshGit(){refreshed++;},
            readFiles(){throw Error("refusal followed the success path");},loadFile(){throw Error("refusal opened a file");}});
        for (const name of ["showWriteRefusal","declareHere","sayValue","tick"])
            vm.runInContext(implementation(source.ui,name),c);
        await c.declareHere("forms");
        assert(nodes.verdicts.innerHTML.includes("PUT /declare?") && nodes.verdicts.innerHTML.includes("gate serve"));
        const box = {value:"1",focus(){},select(){},remove(){}};
        c.document.createElement = ()=>box;
        const cell = {textContent:"",appendChild(){},classList:{add(){}}};
        await c.sayValue("Width",0,cell);
        box.value = "1";
        // The event handler starts the asynchronous write; drain that request.
        let pending;
        const fetch = c.fetch;
        c.fetch = (...args)=>(pending=fetch(...args));
        box.onkeydown({key:"Enter",preventDefault(){}});
        await pending; await new Promise(resolve=>setImmediate(resolve));
        assert(nodes.verdicts.innerHTML.includes("PUT /value?") && nodes.verdicts.innerHTML.includes("gate serve"));
        await c.tick(true);
        assert(nodes.gitstate.textContent.includes("not saved: gate.manifest.swift:1"));
        assert(nodes.verdicts.innerHTML.includes("cannot change its manifest"));
        assert.strictEqual(refreshed,0);
        c.showWriteRefusal({address:"<img>",reason:"<script>",next:"<svg>"},"","refused");
        assert(!nodes.verdicts.innerHTML.includes("<img>") && nodes.verdicts.innerHTML.includes("&lt;script&gt;"));
    }
    console.log("WRITE REFUSAL GREEN: P6-other-write-routes; immutable structure; supported drafts; UI address/reason/next");
}
if (require.main === module) {
    let input="";
    process.stdin.on("data",s=>input+=s);
    process.stdin.on("end",()=>check(JSON.parse(input)).catch(e=>{console.error(e);process.exitCode=1;}));
}
module.exports = {check};
