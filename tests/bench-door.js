'use strict';
// The real door, loader and Table builder, with replies held until asserted.
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const ui=fs.readFileSync(__dirname+'/../web/ui.html','utf8');
const judge=require('../bin/judge.js').judge;
const fn=name=>{let at=ui.indexOf('function '+name+'(');assert(at>=0,name);at=ui.lastIndexOf('\n',at)+1;return ui.slice(at,ui.indexOf('\n}',at)+2);};
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.style={};this.classList={add(){}};this.textContent='';}
 set innerHTML(value){this.html=value;this.children=[];} get innerHTML(){return this.html||'';}
 append(...children){this.children.push(...children);} appendChild(child){this.append(child);}
}
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};};
async function checkDoor(opening) {
 const ids=new Map(),el=id=>{if(!ids.has(id))ids.set(id,new Element('div'));return ids.get(id);};
 const source='public enum One: Record {\n public typealias State = Open\n}\npublic enum Two: Record {\n public typealias State = Held\n}\npublic enum Three: Record {\n public typealias State = Rejected\n}\n';
 const body=deferred(),neighbors=deferred(),verdict=deferred(),readingNeighbors=deferred();
 const context=vm.createContext({Map,Set,files:['Records.swift','Evidence.swift'],active:'',formsFiles:new Set(['Records.swift']),carriedFiles:new Set(),theirsFiles:{},nameLabels:new Map(),lastParsed:null,lastRefusals:[],tableSort:null,
  layoutFile:'gate.manifest.swift',viewingShelf:null,refLabel:null,undeclaredView:null,fileLoadGeneration:0,scopesAt:{},projectionPage:0,takenGroupState:new Map(),kitVocabulary:{},
  document:{getElementById:el,createElement:t=>new Element(t),querySelectorAll:()=>[]},window:{},history:{replaceState(){}},editor:{value:''},
  cm:{setOption(){},clearHistory(){},getValue:()=>context.editor.value,refresh(){}},judge,
  resetDrawing(){},refreshGit(){},repaintNames(){},buildRail(){},siblings:async()=>{readingNeighbors.resolve();await neighbors.promise;},
  render:async()=>{await verdict.promise;},fetch:async()=>{await body.promise;return {ok:true,text:async()=>source};},
  mode:'bare',syncProjection(){},drawCanvases(){},bareForm:()=>'',shelfInputs:{},seams:[],openSeam:null,localNames:new Set(),declFile:new Map(),overridden:{},
  projected:()=>true,attachNotes:()=>new Map(),noteProse:x=>x,shownTerm:x=>x,countTerm:()=>null,esc:x=>String(x),reading:()=>false});
 for(const name of ['activeDecls','tableGroups','ledgerGroups','collectLabels','statedLabels','tableTerm','buildTables','setMode','loadFile'])vm.runInContext(fn(name),context);
 // Execute the actual boot's selected-view sequence, not a second click.
 const begin=ui.indexOf('        setMode(opensAs[first] || mode);');
 const alternate=ui.indexOf('        setMode(theirsFiles[first]?.kind');
 const start=begin>=0?begin:alternate;assert(start>=0,'door view sequence exists');
 const end=ui.indexOf('        if (first === askedFile',start);
 context.opening=opening;
 const door=vm.runInContext('(async()=>{const first="Records.swift",askedView="table",opensAs={"Records.swift":opening};'+ui.slice(start,end)+'})()',context);
 const before=el('table-host').innerHTML;
 body.resolve();await readingNeighbors.promise;
 const text=element=>element.textContent+' '+element.innerHTML+' '+element.children.map(text).join(' ');
 assert.equal(context.mode,'table','URL selects Table before waiting for neighboring files');
 assert(!before.includes('no relations'),'a missing parse is still loading, not an empty world');
 assert(text(el('table-host')).includes('Record · 3 rows'),'first source reply projects rows before neighbors/verdict, without a click');
 for(const name of ['One','Two','Three'])assert(text(el('table-host')).includes(name),name);
 neighbors.resolve();verdict.resolve();await door;
 assert(text(el('table-host')).includes('Record · 3 rows'));
}
(async()=>{
 for (const opening of ['bare','table']) await checkDoor(opening);
 console.log('BENCH DOOR GREEN: requested Table projects the loaded source while neighboring input and verdict replies are delayed');
})().catch(e=>{console.error(e);process.exitCode=1;});
