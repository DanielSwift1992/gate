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
 const scope=vm.createContext({theirsFiles:{[foreign]:origin},unavailableFiles:[],files:['Facts.swift',foreign],fileLoadGeneration:0,personalFile:null,badFiles:new Set(),seamRows:[],undeclaredFiles:[],active:'',viewingShelf:null,refLabel:null,undeclaredView:null,takenGroupState:new Map(),nameLabels:new Map(),readerDrafts:false,
 document:{getElementById:el,createElement:()=>new Element()},esc:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'),cm,window:{},history:{replaceState(){}},
 resetDrawing(){},scopesAt:{},projectionPage:0,setMode(m){scope.mode=m;},mode:'table',editor:{value:''},
 fetch:async()=>({ok:true,text:async()=>'# actual bytes\r\n🧭'}),judge:()=>({parsed:{declarations:new Map(),topAliases:new Map()}}),carriedFiles:new Set([foreign]),formsFiles:new Set(),layoutFile:'gate.manifest.swift',kitVocabulary:{},repaintNames(){},siblings:async()=>{},render(){},buildTables(){},bareForm:()=>'',refreshGit(){},navHere(){},recordJump(){}});
 for(const name of ['takenLabel','takenGroup','buildRail','loadFile','reading'])vm.runInContext(implementation(name),scope);
 await scope.loadFile(foreign);
 assert.equal(cm.options.readOnly,true);assert.equal(scope.viewingShelf,foreign);assert(scope.reading());assert.equal(scope.mode,'full');
 assert.equal(scope.editor.value,'# actual bytes\r\n🧭');assert(cm.cleared);assert(scope.refLabel.includes('&lt;owner&gt;@'+origin.revision+':notes.md'));assert(scope.refLabel.includes(origin.sha256));
 const descendants=e=>[e,...e.children.flatMap(descendants)];
 assert(!descendants(el('filelist')).some(e=>e.title?.includes('notes.md')));assert(descendants(el('taken-filelist')).some(e=>e.title?.includes('notes.md')));
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
 // Group by the declared origin, including unrelated names and interleaved pins.
 Object.assign(scope,{active:'Facts.swift',files:['Facts.swift',foreign,'unrelated.swift','second.md'],theirsFiles:{[foreign]:origin,'unrelated.swift':origin,'second.md':{...origin,revision:'c'.repeat(40)}}});
 scope.takenGroupState.clear();scope.buildRail();
 let groups=el('taken-filelist').children;assert.equal(groups.length,2);assert(!groups[0].open && !groups[1].open);
 assert(groups[0].children[0].textContent.endsWith(' · 2'));assert.equal(groups[0].children[0].title,'<owner>@'+origin.revision);
 groups[0].open=true;groups[0].ontoggle();scope.buildRail();assert(el('taken-filelist').children[0].open);
 // Git replies belong to the Mine file which requested them, even when delayed.
 vm.runInContext(implementation('refreshGit'),scope);
 let gitReply;scope.fetch=async()=>new Promise(resolve=>gitReply=resolve);
 const gitRequest=scope.refreshGit();scope.active=foreign;scope.viewingShelf=foreign;scope.fileLoadGeneration++;
 await scope.refreshGit();gitReply({json:async()=>({git:'untracked'})});await gitRequest;
 assert.equal(el('gitstate').textContent,'');assert.equal(el('gitstate').title,'');
 // The author's literal name is shown with an address; the court sentence stays intact.
 for(const name of ['collectLabels','refusalLabels','siblings'])vm.runInContext(implementation(name),scope);
 scope.active='Facts.swift';scope.viewingShelf=null;scope.lastParsed=null;
 scope.judge=require('../bin/judge.js').judge;
 scope.fetch=async()=>({ok:true,text:async()=> 'public enum Fingerprint {}\nextension Fingerprint { public static var typeName: String { "row at gate.manifest.swift:9 <old> -> <new>" } }\n'});
 scope.editor.value='public enum Own {}';scope.files=['Facts.swift','proof.swift',foreign];scope.formsFiles=new Set(['proof.swift']);scope.theirsFiles={'proof.swift':{kind:'FormsFile'},[foreign]:origin};
 await scope.siblings();let label=scope.refusalLabels('Fingerprint != Other');
 assert(label.includes('proof.swift:2') && label.includes('&lt;old&gt; -&gt; &lt;new&gt;'));assert.equal(scope.refusalLabels('FingerprintSuffix'), '');
 assert.equal(scope.refusalLabels('OtherScope.Fingerprint'), '');
 scope.collectLabels(scope.nameLabels,{literals:new Map([['Fingerprint',{value:'conflicting',line:1}]])},'another.swift');
 assert.equal(scope.refusalLabels('Fingerprint'), '');
 assert(/id="fname"[^>]*>Loading world/.test(ui));assert(!/files\[0\] \|\| "gate.swift"/.test(ui));
 console.log('CARRIED UI GREEN: real rail, loading, provenance escaping, failed input, read-only offers and no MINE names');
})().catch(e=>{console.error(e);process.exitCode=1;});
