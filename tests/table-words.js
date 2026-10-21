'use strict';
// Execute Table's shipped builders with parsed atoms, not a second renderer.
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const ui=fs.readFileSync(__dirname+'/../web/ui.html','utf8'),judge=require('../bin/judge.js').judge;
const fn=n=>{const at=ui.indexOf('function '+n+'(');assert(at>=0,n);return ui.slice(at,ui.indexOf('\n}',at)+2);};
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.style={};this.classList={add(){}};this.textContent='';}
 set textContent(v){this.text=v;this.children=[];}get textContent(){return this.text+this.children.map(e=>e.textContent).join('');}
 set innerHTML(v){this.html=v;this.children=[];}get innerHTML(){return this.html||'';}
 append(...a){this.children.push(...a);}appendChild(a){this.append(a);}
 getBoundingClientRect(){return {};}
}
const source=`public protocol Record { associatedtype Next }
public enum One: Record { public typealias Next = Advance }
public enum Two: Record { public typealias Next = Advance }
extension One { public static var typeName: String { "First record" } }
public typealias Choice = Advance
`;
const parsed=s=>judge('Records.swift',s,{seeds:new Set(),generics:new Set()}).parsed;
const host=new Element('div'),c=vm.createContext({nameLabels:new Map(),lastParsed:parsed(source),active:'Records.swift',
 document:{getElementById:()=>host,createElement:t=>new Element(t)},syncProjection(){},lastRefusals:[],tableSort:null,
 viewingShelf:null,shelfInputs:{},seams:[],openSeam:null,localNames:new Set(),declFile:new Map(),overridden:{},
 projected:()=>true,attachNotes:()=>new Map(),noteProse:x=>x,shownTerm:x=>x,countTerm:()=>null,esc:x=>x,
 reading:()=>true,cm:{getValue:()=>source},ledgerGroups:()=>[]});
for(const n of ['activeDecls','tableGroups','collectLabels','statedLabels','tableTerm','buildTables'])vm.runInContext(fn(n),c);
const walk=e=>[e,...e.children.flatMap(walk)];
const text=()=>walk(host).map(e=>e.textContent).join(' ');
const neighbor=parsed('public enum Advance {}\nextension Advance { public static var typeName: String { "Read <next> & decide" } }');
c.collectLabels(c.nameLabels,neighbor,'Other.swift');c.buildTables();
assert(text().includes('First record'));assert(text().includes('Read <next> & decide'));
const words=walk(host).filter(e=>e.tag==='small');assert(words.length>=4,'row name, two axes and file-scope value show words');
assert(words.some(e=>e.title.startsWith('stated name at Records.swift:')));
assert(words.some(e=>e.title==='stated name at Other.swift:2'));
assert(words.every(e=>!e.innerHTML),'literal punctuation stays text');
c.reading=()=>false;c.axesOfHost=()=>({Next:'Step'});c.fillersFor=()=>['Advance'];
c.compEl={dataset:{}};c.drawCompletion=()=>{};c.offerIndex=(items,current)=>{c.chosenAtom=current;return 0;};
c.buildTables();
const slot=walk(host).find(e=>e.tag==='td'&&e.textContent.startsWith('Advance')&&e.onclick);
assert(slot.textContent.includes('Read <next>'),'the clicked cell includes a caption');
slot.onclick();assert.equal(c.chosenAtom,'Advance','completion selects the atom, independently of its caption');
c.collectLabels(c.nameLabels,parsed('extension Advance { public static var typeName: String { "Different" } }'),'Conflict.swift');
c.buildTables();assert(!text().includes('Read <next>')&&!text().includes('Different'),'ambiguous spellings are omitted');
c.lastParsed=parsed(source.replace('"First record"','makeWords()'));c.buildTables();
assert(!text().includes('First record'),'nonliteral typeName is not an explanation');
assert(text().includes('One')&&text().includes('Advance'),'atom names survive missing words');
c.shownTerm=term=>term==='One'?'1':term;c.buildTables();
assert(walk(host).some(e=>e.tag==='td'&&e.className.includes('cell-name')&&e.textContent==='One'),
 'the name column keeps the spelling of a countable atom');
console.log('TABLE WORDS GREEN: local and neighboring words, attribution, literal safety, ambiguity and unsupported spelling');
