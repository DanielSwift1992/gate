"use strict";
const fs=require("fs"), path=require("path"), vm=require("vm"), assert=require("assert");
const {open}=require("./published-bench.js");
const root=process.argv[2], ui=fs.readFileSync(path.join(__dirname,"../web/ui.html"),"utf8");
const storage={getItem(){return null;}, setItem(){}, removeItem(){}};
const snapshots=id=>JSON.parse(fs.readFileSync(path.join(root,"playground",id,"snapshots.json")));
function implementation(name) {
    const at=ui.indexOf("function "+name+"("), end=ui.indexOf("\n}",at);
    assert(at>=0 && end>at,name);return ui.slice(at,end+2);
}
function chip(answer) {
    const ctx=vm.createContext({r:answer,broken:(answer.refusals||[]).filter(r=>!/states none/.test(r.premise||r.claim||"")),escAttr:s=>String(s).replaceAll('"','&quot;')});
    vm.runInContext(implementation("readingChip"),ctx);
    return vm.runInContext("readingChip(r,broken)",ctx);
}
class Element {
    constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.hidden=true;}
    append(...items){this.children.push(...items);}
    appendChild(item){this.children.push(item);}
    setAttribute(k,v){this.attrs[k]=v;}
}
(async()=>{
    // A new door without a per-file view still applies the bench's default.
    // The selected button and the visible surface must answer the same word.
    const start=ui.indexOf('        setMode(theirsFiles[first]?.kind');
    const end=ui.indexOf('        await loadFile(first);',start);
    assert(start>=0 && end>start,'door selects its view before reading the file');
    const initial=ui.slice(start,end);
    for(const perFile of [null,'bare','table','full'])for(const askedView of [null,'bare','table','full','unknown']){
        const ids=Object.fromEntries(['editor-host','bare','table-host','canvas-host'].map(n=>[n,{style:{}}]));
        const selected={};
        const ctx=vm.createContext({mode:'bare',drawingSnapshot:null,lastParsed:null,opensAs:perFile?{first:perFile}:{},first:'first',askedView,theirsFiles:{},
            document:{getElementById:n=>ids[n],querySelectorAll:()=>['bare','table','full','drawing'].map(m=>({dataset:{m},classList:{toggle:(_,on)=>selected[m]=on}}))},
            syncProjection(){},buildTables(){},drawCanvases(){},cm:{refresh(){}}});
        vm.runInContext(implementation('setMode'),ctx);vm.runInContext(initial,ctx);
        const expected=['bare','table','full'].includes(askedView)?askedView:perFile||'bare';assert(selected[expected]);
        assert.equal(ids['editor-host'].style.display,expected==='full'?'':'none');
        for(const [id,m] of [['bare','bare'],['table-host','table'],['canvas-host','drawing']])assert.equal(ids[id].style.display,expected===m?'block':'none');
    }
    const basics=open(root,"basics",storage), snap=snapshots("basics"), f="Dictionary/Basics.swift", original=snap["/world?f="+f];
    const ask=(text,file=f)=>basics.fetch("/verdict?f="+file,{method:"POST",body:text}).then(r=>r.json());
    const clean=await ask(original);assert.equal(clean.refusals.length,0,JSON.stringify(clean));
    assert.equal(clean.checked,0);assert.equal(clean.verdict,"empty");assert(chip(clean).includes("empty · no declared applications"));assert(chip(clean).includes("Swift bodies unchecked"));
    const mutations=[
        ["import NotInThePackage\n"+original,f+":1","imports are fixed"],
        [original+"\npublic extension MissingOwner {}",null,"MissingOwner"],
        [original+"\npublic typealias Probe = MissingTarget",null,"MissingTarget"],
        [original+"\npublic typealias Probe = ReadMeTab",null,"ReadMeTab"],
        [original+"\npublic enum ProbeRow: HFlow {\npublic typealias Given = U512\npublic static var body: some Structure & Divides {\nAir<U2>.self\n}\n}",null,"StructureBuilder"],
        [original+"\nlet runtime = 1",null,"rule 0"]
    ];
    for(const [text,at,reason] of mutations){
        const result=await ask(text);assert.equal(result.verdict,"refused",reason);
        assert(result.refusals.some(r=>(at?r.address===at:r.address.startsWith(f+":"))&&r.claim.includes(reason)),JSON.stringify(result));
        assert(chip(result).includes('class="chip bad"'));assert(!chip(result).includes('class="chip ok"'));
    }
    const pages="BasicsPages.swift", carried=await ask("import NotInThePackage\n"+snap["/world?f="+pages],pages);
    assert(carried.refusals.some(r=>r.address===pages+":1"));
    for(const id of ["light","site"]){
        const page=open(root,id,storage), s=snapshots(id), file=JSON.parse(s["/files"]).forms[0];
        const answer=await (await page.fetch("/verdict?f="+file,{method:"POST",body:s["/world?f="+file]})).json();
        assert.equal(answer.refusals.length,0,JSON.stringify(answer));assert(answer.checked>0);assert(chip(answer).includes(">holds</span>"));
    }
    assert(chip({checked:0,coverage:{readings:0},unsupported:[{id:"waiting",reason:"budget"}]}).includes(">unsupported ·"));
    const empty={premise:"Home states none"}, broken={premise:"a claim disagrees"};
    assert(!chip({refusals:[empty]}).includes('class="chip bad"'));
    assert(chip({refusals:[broken]}).includes('>refuses 1</span>'));
    assert(chip({refusals:[empty,broken]}).includes('>refuses 1</span>'));
    assert(ui.includes('const waits = pending.length') && ui.includes('+ waits;'));
    // Provenance reports the pin beside the existing judge row, not a third rail category.
    const world=JSON.parse(fs.readFileSync(path.join(root,"playground/basics/world.json")));
    for(const pathname of ["/gate/playground/","/gate/playground/basics/index.html"]){
        const ids=Object.fromEntries(["world-provenance","world-inputs"].map(id=>[id,new Element("div")]));
        const ctx=vm.createContext({location:{pathname},document:{getElementById:id=>ids[id],createElement:tag=>new Element(tag)},world});
        vm.runInContext(implementation("showWorldInputs"),ctx);vm.runInContext("showWorldInputs(world)",ctx);
        assert.equal(ids["world-provenance"].hidden,false);
        assert.equal(ids["world-inputs"].children.filter(e=>e.tag==="a").length,2);
    }
    assert(!ui.includes('id="worlds-section"') && !ui.includes('data-fold="worlds"'));
    await require("./playground-catalog.js")(root);
    // Both theme paths remain the bench's declaration and OS mechanism.
    for(const dark of [false,true]){
        let theme;
        const ctx=vm.createContext({darkMedia:{matches:dark},declaredTheme:null,localStorage:storage,document:{documentElement:{setAttribute:(k,v)=>theme=v}}});
        for(const name of ["effectiveTheme","paintTheme"])vm.runInContext(implementation(name),ctx);
        vm.runInContext("paintTheme()",ctx);assert.equal(theme,dark?"dark":"light");
        vm.runInContext("declaredTheme='light';paintTheme()",ctx);assert.equal(theme,"light");
        vm.runInContext("declaredTheme='dark';paintTheme()",ctx);assert.equal(theme,"dark");
    }
    console.log("PLAYGROUND UI GREEN: real published mutations, addressed guards/lint, honest reading chips, shared rail and both bench themes");
})().catch(e=>{console.error(e);process.exitCode=1;});
