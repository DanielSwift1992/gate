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
    const basics=open(root,"basics",storage), snap=snapshots("basics"), f="Dictionary/Basics.swift", original=snap["/world?f="+f];
    const ask=(text,file=f)=>basics.fetch("/verdict?f="+file,{method:"POST",body:text}).then(r=>r.json());
    const clean=await ask(original);assert.equal(clean.refusals.length,0,JSON.stringify(clean));
    assert.equal(clean.checked,0);assert(chip(clean).includes("no readings"));assert(chip(clean).includes("Swift bodies unchecked"));
    const mutations=[
        ["import NotInThePackage\n"+original,f+":1","imports are fixed"],
        [original+"\npublic extension MissingOwner {}",null,"MissingOwner"],
        [original+"\npublic typealias Probe = MissingTarget",null,"MissingTarget"],
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
    // The template's actual rail function, at the door and at a deep address.
    const world=JSON.parse(fs.readFileSync(path.join(root,"playground/basics/world.json")));
    for(const pathname of ["/gate/playground/","/gate/playground/basics/index.html"]){
        const ids=Object.fromEntries(["worlds-section","worldlist","world-provenance","world-inputs"].map(id=>[id,new Element("div")]));
        const ctx=vm.createContext({location:{pathname},document:{getElementById:id=>ids[id],createElement:tag=>new Element(tag)},world});
        vm.runInContext(implementation("buildWorldRail"),ctx);vm.runInContext("buildWorldRail(world)",ctx);
        assert.equal(ids.worldlist.children[0].textContent,world.tab.caption,"current instructions are visible, not just a hover title");
        assert.equal(ids.worldlist.children[0].className,"folder caption");
        const links=ids.worldlist.children.filter(e=>e.tag==="a");assert.equal(links.length,12);
        assert.deepEqual(links.map(l=>l.href),world.tabs.map(t=>(pathname.endsWith("basics/index.html")?"../":"")+t.id+"/index.html"));
        assert(links.every(l=>l.className.startsWith("file fact")));
        assert.equal(links.find(l=>l.attrs["aria-current"]==="page").href,pathname.endsWith("basics/index.html")?"../basics/index.html":"basics/index.html");
        assert.equal(ids["world-provenance"].hidden,false);assert.equal(ids["worlds-section"].hidden,false);
    }
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
