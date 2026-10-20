// Read the pinned catalog through the published fetch path and the bench's own views.
"use strict";
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const {open}=require('./published-bench.js'),{judge}=require('../bin/judge.js'),{kitVocabulary}=require('../bin/renderer.js');
const {fixedImports,pageGuards}=require('../bin/playground-guards.js');
const ui=fs.readFileSync(path.join(__dirname,'../web/ui.html'),'utf8');
function implementation(name){const at=ui.indexOf('function '+name+'('),end=ui.indexOf('\n}',at);assert(at>=0&&end>at,name);return (ui.slice(at-6,at)==='async '?'async ':'')+ui.slice(at,end+2);}
class Element{
 constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.style={};this.classList={add(){},remove(){}};}
 append(...xs){this.children.push(...xs);} appendChild(x){this.children.push(x);} setAttribute(k,v){this.attrs[k]=v;}
}
const escape=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
module.exports=async function(root){
 const storage={getItem(){return null;},setItem(){throw Error('reference wrote a draft');},removeItem(){}};
 const tabs=JSON.parse(fs.readFileSync(path.join(root,'playground/tabs.json')));
 assert.equal(tabs.length,12);
 for(const id of tabs.map(t=>t.id)){
  const page=open(root,id,storage),shelf=await(await page.fetch('/shelf')).json();
  assert.equal(shelf.modules.filter(m=>m==='Site/Manifest').length,1);
  const input=shelf.inputs['Site/Manifest'];
  const text=await(await page.fetch('/shelf?m=Site%2FManifest')).text();
  assert.equal(require('crypto').createHash('sha256').update(text).digest('hex'),input.sha256);
  const files=await(await page.fetch('/files')).json();
  if(id==='site')assert(!files.files.includes('Manifest.swift'));
  const parsed=judge('Site/Manifest.swift',text,kitVocabulary).parsed;
  const doors=tabs.map(t=>[t.record,t.id]).concat(tabs.filter(t=>!t.generated).map(t=>[t.reads,t.id]));
  assert.deepEqual(Object.entries(input.destinations),doors);
  assert.equal(input.destinations.CompanyWorld,'company');assert.equal(input.destinations.ScaleTab,'scale');
  const pane=new Element('div'),fname=new Element('div'),host=new Element('div');let readonly=false,selected='bare',shown='',revealed=0,moved;
  const ctx=vm.createContext({Map,Set,console,judge,location:{pathname:'/gate/playground/'+id+'/',assign:url=>moved=url},
   fetch:page.fetch,shelfInputs:shelf.inputs,viewingShelf:null,active:'Palette.swift',refLabel:null,undeclaredView:null,mode:'bare',opensAs:{},
   document:{getElementById:n=>n==='table-host'?host:n==='shelf-host'?pane:fname,createElement:tag=>new Element(tag)},
   cm:{setValue:t=>shown=t,setOption:(k,v)=>{if(k==='readOnly')readonly=v;},getValue:()=>text,lineCount:()=>text.split('\n').length},
   buildRail(){},render(){},setMode:m=>selected=m,say(){},reveal:()=>revealed++,navHere:()=>({}),declFile:new Map(),
   esc:escape,escAttr:escape,lastParsed:parsed,lastRefusals:[],localNames:new Set(),layoutDecls:new Map(),unresolved:new Set(),
   syncProjection(){},projectionRange:()=>({from:0,to:Infinity}),projected:()=>true,attachNotes:()=>new Map(),freeComments:()=>[],
   recordEnd:()=>Infinity,holesOf:()=>[],locateSlot:()=>null,noteProse:escape,shownTerm:x=>x,tableSort:null,seams:[],
   files:files.files,SHELF_SORTS:['a-domain','the-tool','the-bench','the-reader'],SHELF_MEANS:{}});
  ctx.formsFiles=new Set(files.forms);ctx.worldAliases=new Map();ctx.FORM_ROWS={gate:{}};ctx.buildScopes=()=>{};
  ctx.vocabulary={};ctx.conformers={};ctx.axisOf={};ctx.protoAxes={};ctx.shelfDecls=new Map();
  vm.runInContext(implementation('loadVocabulary'),ctx);await vm.runInContext('loadVocabulary()',ctx);
  assert(!ctx.vocabulary.ReadMeTab,'a catalog is not a language grant');
  for(const n of ['reading','layoutOrActive','nameTokens','activeDecls','tableGroups','ledgerGroups','bareForm','buildTables','shelfRank','buildShelf','openShelf','jumpTo'])vm.runInContext(implementation(n),ctx);
  await vm.runInContext('buildShelf()',ctx);
  const reference=pane.children.find(e=>(e.innerHTML||'').includes('Site/Manifest.swift'));assert(reference,'ordinary shelf file row');
  await reference.onclick();assert(readonly);assert.equal(shown,text);assert.equal(selected,'bare');
  ctx.mode='table';await reference.onclick();assert.equal(selected,'table');
  assert(ctx.refLabel.includes(input.revision));
  const bare=vm.runInContext('bareForm(lastParsed,cm.getValue())',ctx);
  for(const [name] of doors)assert(bare.includes('data-jump="'+name+'"'),name+' in Bare');
  assert(!bare.includes('data-add-')&&!bare.includes('data-cut='));
  vm.runInContext('buildTables()',ctx);
  const walk=e=>[e,...e.children.flatMap(walk)],nodes=walk(host);
  assert(!nodes.some(e=>e.className==='add caption'),'read-only Table offers no add row');
  for(const pathname of ['/gate/playground/','/gate/playground/index.html','/gate/playground/'+id+'/','/gate/playground/'+id+'/index.html']){
   ctx.location.pathname=pathname;
   for(const [name,id] of doors){
    moved=null;const cell=nodes.find(e=>e.className==='fact cell-name'&&e.textContent===name);assert(cell,name+' in Table');
    await cell.onclick();assert.equal(moved,(/\/playground\/(?:index\.html)?$/.test(pathname)?'':'../')+id+'/');
   }
  }
  assert.equal(revealed,0,'catalog names take their world, never an unrelated declaration line');
  moved=null;await vm.runInContext('jumpTo("ReadMeFileWord")',ctx);assert.equal(revealed,1);assert.equal(moved,null,'a catalog word opens its own declaration');
  ctx.viewingShelf=null;ctx.layoutDecls.set('ReadMeTab',{line:9});await vm.runInContext('jumpTo("ReadMeTab")',ctx);assert.equal(revealed,2);assert.equal(moved,null,'names in MINE still open their own lines');
 }
 // The underline and guard consume the SAME list, including changes to that list.
 let line='';const ctx=vm.createContext({fixedImports,cm:{getLine:()=>line},noteStartAt:()=>-1,formsFiles:new Set(),active:'Pages.swift',
  scopesAt:()=>[],placeAt:()=>({host:null,inBody:false}),LINE_OPENERS:{top:new Set(['enum'])},LINE_MODS:{top:new Set()},LINE_CONTINUERS:new Set()});
 vm.runInContext(implementation('ungrantedOpenerAt'),ctx);
 const parsed=judge('Pages.swift','',kitVocabulary).parsed;
 for(const source of [...fixedImports,'import NotInThePackage']){line=source;const allowed=!pageGuards(parsed,[source],new Set()).length;assert.equal(vm.runInContext('ungrantedOpenerAt(0)',ctx)===null,allowed);}
 fixedImports.push('import CatalogProbe');line='import CatalogProbe';assert.equal(vm.runInContext('ungrantedOpenerAt(0)',ctx),null);assert.deepEqual(pageGuards(parsed,[line],new Set()),[]);fixedImports.pop();
 const native=vm.createContext({cm:{getLine:()=>fixedImports[0]},noteStartAt:()=>-1,formsFiles:new Set(),active:'world.swift',scopesAt:()=>[],placeAt:()=>({host:null,inBody:false}),LINE_OPENERS:{top:new Set(['enum'])},LINE_MODS:{top:new Set()},LINE_CONTINUERS:new Set()});
 vm.runInContext(implementation('ungrantedOpenerAt'),native);assert(vm.runInContext('ungrantedOpenerAt(0)',native),'native grammar is not widened');
 console.log('CATALOG GREEN: 12 read-only inputs, actual Bare/Table names, 1104 doors, shared import grants');
};
