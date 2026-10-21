// The owner parts recover the former large source for the projection regression.
// The actual published files below are judged together with their source addresses.
// Run the real UI projection functions without a browser or a second parser.
"use strict";
const fs=require("fs"), path=require("path"), vm=require("vm"), assert=require("assert"), {performance}=require("perf_hooks");
const {judge}=require("../bin/judge.js"), {kitVocabulary,renderAll}=require("../bin/renderer.js");
const root=process.argv[2], snap=JSON.parse(fs.readFileSync(path.join(root,"playground/scale/snapshots.json")));
const owner=JSON.parse(fs.readFileSync(path.join(process.argv[3],"Checks/Playground/scale-court.json")));
const companyFiles=owner.company_files.map(p=>p.replace('Worlds/Playground/Scale/',''));
const texts=Object.fromEntries(companyFiles.map(f=>[f,snap['/world?f='+f]]));
const text=companyFiles.map((f,i)=>i?texts[f].split('\n').slice(5).join('\n'):texts[f]).join(''), lines=text.split("\n"), measurements={};
assert.equal(require('crypto').createHash('sha256').update(text).digest('hex'),owner.canonical_company_sha256);
function timed(name,fn) {const at=performance.now(), result=fn();measurements[name]=+(performance.now()-at).toFixed(1);return result;}
const parsed=timed("parse_ms",()=>judge("Company.swift",text,kitVocabulary)).parsed;
assert.strictEqual([...parsed.declarations.keys()].filter(n=>/^Emp\d+$/.test(n)).length,12800);
const ui=fs.readFileSync(path.join(__dirname,"../web/ui.html"),"utf8"), els={};
const scope={lastRefusals:[],bareSlots:[],unresolved:new Set(),lastParsed:parsed,recordBoundaries:new WeakMap(),projectionLines:2000,projectionPage:0,
    cm:{lineCount:()=>lines.length,getLine:n=>lines[n]}, mode:"bare",document:{getElementById:id=>els[id]??(els[id]={})},
    reading:()=>false, layoutOrActive:()=>parsed.declarations, protoAxes:{},worldAliases:new Map(),language:{names:{}},
    esc:t=>String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"),
    codeOfLine:n=>(lines[n]||"").split("//")[0]};
vm.createContext(scope);
vm.runInContext(ui.slice(ui.indexOf('const esc ='), ui.indexOf('// Bare:', ui.indexOf('const esc ='))), scope);
for (const name of ["projectionRange","projected","syncProjection","aliasValueRange","locateSlot","nameTokens","axesOfHost","holesOf",
    "attachNotes","freeComments","noteProse","countTerm","termArgs","shownTerm","recordEnd","bareForm","buildScopes","admits","scopesAt","noteStartAt","placeAt","ungrantedOpenerAt","paintUngranted"]) {
    const at=ui.indexOf("function "+name+"("), end=ui.indexOf("\n}",at)+2;
    assert(at>=0 && end>at,name);vm.runInContext(ui.slice(at,end),scope);
}
const first=timed("first_bare_ms",()=>scope.bareForm(parsed,text));
assert(first.includes("Emp00000"));assert(!first.includes('data-jump="Emp12799"'));
assert.strictEqual(els["projection-pages"].hidden,false);
assert((first.match(/class="rec"/g)||[]).length < 2100);
// Walk every line window: no declaration falls out between pages, addresses
// remain those of the full source, and the editor's document never changes.
const seen=new Set(), total=scope.projectionRange().total;
for(let page=0;page<total;page++) {
    scope.projectionPage=page;
    for(const [name,d] of parsed.declarations) if(scope.projected(d.line)) seen.add(name);
}
assert.strictEqual(seen.size,parsed.declarations.size);
const last=timed("last_bare_ms",()=>scope.bareForm(parsed,text));
assert(last.includes("Emp12799"));assert(!last.includes('data-jump="Emp00000"'));
const d=parsed.declarations.get("Emp12799"), alias=d.aliases.get("Home");
const slot=scope.locateSlot({kind:"alias",line:alias.line,host:d.name,axis:"Home"});
assert.strictEqual(slot.from.line,alias.line-1);assert(slot.from.line>lines.length * 0.75);
assert.strictEqual(lines[slot.from.line].slice(slot.from.ch,slot.to.ch),alias.target);
assert(text.includes("public typealias Home = " + alias.target));
const list=JSON.parse(snap["/files"]), drawScope={files:list.files,theirsFiles:list.theirs||{}};
vm.createContext(drawScope);
const selectionAt=ui.indexOf("function drawingFiles("),selectionEnd=ui.indexOf("\n}",selectionAt)+2;
vm.runInContext(ui.slice(selectionAt,selectionEnd),drawScope);
const parts=drawScope.drawingFiles(null).map(file=>({file,text:snap["/world?f="+file]}));
const whole=timed("drawing_parse_ms",()=>judge("scale",parts.map(p=>p.text).join("\n"),kitVocabulary)).parsed;
// The completion/note walker shares line prefixes at a document generation;
// moving the viewport deep in the file must not rescan its prefix per line.
Object.assign(scope,{SCOPES:[],NESTS:{},LINE_OPENERS:{},LINE_MODS:{},LINE_CONTINUERS:new Set(),FORM_ROWS:{line:{},gate:{}},SLOT_SPELLING:{},
    formsFiles:new Set(),active:"Company.swift",momentMarks:[]});
scope.buildScopes(judge("grammar.swift",fs.readFileSync(path.join(__dirname,"../stdlib/grammar.swift"),"utf8"),kitVocabulary).parsed);
let generation=1, reads=0, marks=0;
Object.assign(scope.cm,{getLine:n=>{reads++;return lines[n];},changeGeneration:()=>generation,
    getViewport:()=>({from:alias.line-3,to:alias.line+4}),markText:()=>{marks++;return {clear(){}};}});
timed("deep_scope_first_ms",()=>scope.scopesAt({line:alias.line-1,ch:0}));
reads=0;
timed("visible_openers_ms",()=>scope.paintUngranted());
assert(reads<100,"visible openers reuse the prefix, not the entire source per line");
const prior=lines[d.line-1];lines[d.line-1]=prior.replace("{","");generation++;
const changed=scope.placeAt({line:alias.line-1,ch:0});assert.notStrictEqual(changed.host?.name,d.name);
lines[d.line-1]=prior;generation++;
assert.strictEqual(scope.placeAt({line:alias.line-1,ch:0}).host.name,d.name);
const rendered=timed("drawing_ms",()=>renderAll(whole.declarations,whole.order,whole.literals,whole.topAliases));
assert.strictEqual(rendered.errors.length,0);
// A lie near the end is still judged, even when the first projection page is open.
const anchor="VerifiedInDepartment<Emp12796, Finance>";assert(text.includes(anchor));
const lies=timed("deep_lie_ms",()=>judge("Company.swift",text.replace(anchor,"VerifiedInDepartment<Emp12796, Sales>"))).refusals;
assert(lies.some(r=>r.line>120000));
const worldCourt=require('../bin/world-court.js'), court=require('../bin/court-wasm/node/vi_court.js');
const ask=changed=>worldCourt.verdict(court,[],changed,[],parts,[],null,judge);
const clean=ask(texts);assert.equal(clean.verdict,'holds');assert.equal(clean.checked,owner.clean.premises);
for(const c of owner.cases) {
    assert.strictEqual(text.split(c.anchor).length-1,1,c.id);
    const refused=judge("Company.swift",text.replace(c.anchor,c.replacement)).refusals;
    assert.deepStrictEqual(refused.map(({line,premise})=>({line,premise})),c.canonical_refusals,c.id);
    const file=c.path.replace('Worlds/Playground/Scale/',''), changed={...texts,[file]:texts[file].replace(c.anchor,c.replacement)};
    const actual=ask(changed);assert.equal(actual.verdict,'refused');
    assert.deepStrictEqual(actual.refusals,c.refusals.map(r=>({address:r.file+':'+r.line,claim:r.premise})),c.id+' physical addresses');
}
assert(ui.includes("viewportMargin: 10, dragDrop: false"));
measurements.bytes=text.length;measurements.lines=lines.length;measurements.projection_pages=total;
measurements.first_html_bytes=first.length;measurements.last_html_bytes=last.length;
(async()=>{
    const record=JSON.parse(fs.readFileSync(path.join(root,"worlds.from"))), declaration=JSON.parse(fs.readFileSync(path.join(root,"playground/scale/world.json"))).drawing;
    const contract=JSON.parse(fs.readFileSync(path.join(__dirname,"../bin/.worlds/playground",record.showcase.revision,"showcase/Contracts/Drawing/v0.1/contract.json")));
    const {compare}=require("../bin/drawing-profile.js");
    assert.equal((await compare({contract},parts,rendered,declaration)).status,"not-compared");
    const changed=parts.map((p,i)=>({...p,text:p.text+(i===0?"\n// changed input":"")}));
    assert.equal((await compare({contract},changed,rendered,declaration)).status,"port-under-contract");
    console.log("PLAYGROUND SCALE GREEN: "+JSON.stringify(measurements));
})().catch(e=>{console.error(e);process.exitCode=1;});
