'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const ui=fs.readFileSync(__dirname+'/../web/ui.html','utf8');
function implementation(name){let at=ui.indexOf('function '+name+'(');assert(at>=0,name);at=ui.lastIndexOf('\n',at)+1;return ui.slice(at,ui.indexOf('\n}',at)+2);}
class Element {
 constructor(){this.children=[];this.style={};this._html='';}
 set innerHTML(value){this._html=value;this.children=[];}
 get innerHTML(){return this._html;}
 appendChild(child){this.children.push(child);}
}
(async()=>{
 const ids=new Map(),el=id=>{if(!ids.has(id))ids.set(id,new Element());return ids.get(id);};
 const foreign='material/source.md',origin={kind:'CarriedFile',address:'gate.manifest.swift:12',verified:true,repository:'<owner>',revision:'a'.repeat(40),source_path:'notes.md',sha256:'b'.repeat(64)};
 const cm={options:{},setOption(k,v){this.options[k]=v;},clearHistory(){this.cleared=true;}};
 const scope=vm.createContext({theirsFiles:{[foreign]:origin},unavailableFiles:[],files:['Facts.swift',foreign],fileLoadGeneration:0,personalFile:null,badFiles:new Set(),seamRows:[],undeclaredFiles:[],active:'',viewingShelf:null,refLabel:null,undeclaredView:null,
 document:{getElementById:el,createElement:()=>new Element()},esc:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'),cm,window:{},history:{replaceState(){}},
 resetDrawing(){},scopesAt:{},projectionPage:0,setMode(m){scope.mode=m;},mode:'table',editor:{value:''},
 fetch:async()=>({ok:true,text:async()=>'# actual bytes\r\n🧭'}),judge:()=>({parsed:{declarations:new Map(),topAliases:new Map()}}),carriedFiles:new Set([foreign]),formsFiles:new Set(),layoutFile:'gate.manifest.swift',kitVocabulary:{},repaintNames(){},siblings:async()=>{},render(){},refreshGit(){},navHere(){},recordJump(){}});
 for(const name of ['takenLabel','buildRail','loadFile','reading'])vm.runInContext(implementation(name),scope);
 await scope.loadFile(foreign);
 assert.equal(cm.options.readOnly,true);assert.equal(scope.viewingShelf,foreign);assert(scope.reading());assert.equal(scope.mode,'full');
 assert.equal(scope.editor.value,'# actual bytes\r\n🧭');assert(cm.cleared);assert(scope.refLabel.includes('&lt;owner&gt;@'+origin.revision+':notes.md'));assert(scope.refLabel.includes(origin.sha256));
 assert(!el('filelist').children.some(e=>e.title?.includes('notes.md')));assert(el('taken-filelist').children.some(e=>e.title?.includes('notes.md')));
 scope.mode='table';await scope.loadFile('Facts.swift');assert.equal(scope.mode,'table');assert.equal(cm.options.readOnly,false);assert(!scope.reading());assert.equal(scope.refLabel,null);
 scope.fetch=async()=>({ok:false,text:async()=>JSON.stringify({address:'.gate/forms-definitions.json:9',reason:'pin unavailable'})});
 await scope.loadFile(foreign);assert(cm.options.readOnly && scope.reading());assert(scope.refLabel.includes('.gate/forms-definitions.json:9 · refused · pin unavailable'));
 // The actual name painter must not recolour a taken declaration as MINE.
 Object.assign(scope,{siblingNames:new Set(['Own']),layoutDecls:new Map(),axisOf:{},protoAxes:{},vocabulary:{},language:{names:{}},paintedKey:''});
 vm.runInContext(implementation('namesOf'),scope);vm.runInContext(implementation('repaintNames'),scope);
 scope.repaintNames({declarations:new Map([['Foreign',{params:[]}]]),topAliases:new Map()},[]);
 assert(!scope.localNames.has('Foreign') && scope.localNames.has('Own'));
 // A delayed taken response cannot overwrite the later MINE buffer.
 let release;
 scope.fetch=async url=>url.includes(encodeURIComponent(foreign))
     ? new Promise(resolve=>release=()=>resolve({ok:true,text:async()=>'OLD TAKEN BYTES'}))
     : {ok:true,text:async()=>'CURRENT MINE'};
 const earlier=scope.loadFile(foreign);
 assert(cm.options.readOnly && scope.reading());assert.equal(scope.editor.value,'');
 await scope.loadFile('Facts.swift');
 release();await earlier;
 assert.equal(scope.editor.value,'CURRENT MINE');assert(!cm.options.readOnly && !scope.reading());
 console.log('CARRIED UI GREEN: real rail, loading, provenance escaping, failed input, read-only offers and no MINE names');
})().catch(e=>{console.error(e);process.exitCode=1;});
