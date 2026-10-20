// World text crosses the real UI builders, then an independent HTML parser.
// This is a DOM-fragment control; the separate live-browser review belongs to Claude.
const fs = require('fs'), path = require('path'), vm = require('vm'), cp = require('child_process');
const assert = require('assert/strict');
const root = path.resolve(__dirname, '..');
const ui = fs.readFileSync(path.join(root, 'web/ui.html'), 'utf8');
const {judge} = require(path.join(root, 'bin/judge.js'));
const renderer = require(path.join(root, 'bin/renderer.js'));
const payload = '<img src=x onerror="document.body.dataset.probe=1">';
const quoted = '<img src=x onerror=\'document.body.dataset.probe=1\'>';
const filename = 'world-' + payload + '.swift';
const pieces = [];
const fileAnswer = process.argv.includes('--file-list')
    ? JSON.parse(fs.readFileSync(process.argv[process.argv.indexOf('--file-list') + 1], 'utf8')) : null;
if (fileAnswer) assert(fileAnswer.undeclared.some(n => n.includes('<img')), 'the server exposes the hostile filename');
const railFiles = fileAnswer ? fileAnswer.files : [filename];
const railUndeclared = fileAnswer ? fileAnswer.undeclared : [];
const railNames = [...railFiles, ...railUndeclared].map(n => n.split('/').pop());
class Element {
    constructor(tag) { this.tag = tag; this.children = []; this.innerHTML = ''; this.textContent = ''; this.dataset = {}; }
    appendChild(e) { this.children.push(e); return e; }
    append(...es) { this.children.push(...es); }
    addEventListener() {}
}
const elements = new Map();
const document = {body: {dataset: {}}, createElement: tag => new Element(tag),
    getElementById: id => {if (!elements.has(id)) elements.set(id, new Element('div')); return elements.get(id);}};
const context = vm.createContext({document, console, Map, Set, Number, URL,
    active: filename, files: railFiles, personalFile: null, badFiles: new Set(),
    seamRows: [], undeclaredFiles: railUndeclared, viewingShelf: null, undeclaredView: null,
    navHere() {}, loadFile() {}, recordJump() {}, openUndeclared() {},
    unresolved: new Set(), bareSlots: [], lastRefusals: [], recordBoundaries: new WeakMap(),
    projectionPage: 0, projectionLines: 2000, mode: 'bare',
    cm: {lineCount: () => (context.source || '').split('\n').length},
    reading: () => true, locateSlot: () => null, holesOf: () => [], shownTerm: s => s,
    layoutOrActive: () => new Map(),
});
function fn(name) {
    const begin = ui.indexOf('function ' + name + '(');
    assert(begin >= 0, name + ' still has its real implementation');
    const end = ui.indexOf('\n}', begin);
    return ui.slice(begin, end + 2);
}
vm.runInContext(ui.slice(ui.indexOf('const esc ='), ui.indexOf('// Bare:', ui.indexOf('const esc ='))), context);
for (const name of ['nameTokens','attachNotes','freeComments','noteProse','recordEnd','projectionRange','projected','syncProjection','bareForm','buildRail'])
    vm.runInContext(fn(name), context);
let row = ui.slice(ui.indexOf('    const rowFor = (ref, cls) => {'), ui.indexOf('\n    for (const ref of broken)'));
if (process.argv.includes('--old-row-for')) {
    row = row.replace('esc(ref.file || active)', '(ref.file || active)').replace('esc(label)', 'label');
}
vm.runInContext(row + '\nglobalThis.rowProbe = rowFor;', context);
const claims = [
    {file: filename, line: 1, premise: payload},
    {file: filename, line: null, premise: 'unsupported " title=' + quoted},
];
if (process.argv.includes('--server-verdict')) {
    const answer = JSON.parse(fs.readFileSync(process.argv[process.argv.indexOf('--server-verdict') + 1], 'utf8'));
    assert(answer.refusals.some(r => (r.claim || '').includes('<img')), 'the real server quotes the hostile source');
    for (const r of answer.refusals) claims.push({file: filename, line: 1, premise: r.claim});
}
for (const claim of claims) {
    const node = context.rowProbe(claim, 'refusal');
    pieces.push({label: 'court and filename', html: node.innerHTML, expected: [claim.file, claim.premise]});
}
vm.runInContext('buildRail()', context);
let railIndex = 0;
for (const node of document.getElementById('filelist').children)
    if (node.innerHTML) pieces.push({label: 'file rail', html: node.innerHTML, expected: [railNames[railIndex++]]});
assert.equal(railIndex, railNames.length, 'every supplied file is shown');
const source = '/// ' + payload + '\npublic enum Hostile {}\n'
    + 'extension Hostile { public static var typeName: String { "' + quoted + '" } }\n'
    + '// ' + quoted + '\n// `' + payload + '`\n';
const parsed = judge(filename, source, {seeds: new Set(), generics: new Set()}).parsed;
context.parsed = parsed; context.source = source;
context.lastParsed = parsed;
assert([...parsed.literals.values()].some(l => l.value.includes('<img')), 'typeName is actually read');
pieces.push({label: 'Bare notes and typeName', html: vm.runInContext('bareForm(parsed, source)', context), expected: [payload, quoted]});
pieces.push({label: 'noteProse with formatting and hostile marks', html: vm.runInContext('noteProse(source, ["class", "known", "&lt;"])', context), expected: []});
context.quoted = '" onmouseover="document.body.dataset.probe=1';
pieces.push({label: 'attribute quotes', html: '<span title="' + vm.runInContext('escAttr(quoted)', context) + '">text</span>', expected: []});
// The renderer is asked the same hostile literals in text and attribute slots.
const graphic = `
public enum CaptionText {}
extension CaptionText { public static var typeName: String { "${quoted}" } }
public enum Label: SpanLabel {
 public typealias Y = Tally<U16>
 public typealias FillColor = TextPrimary
 public typealias Weight = WeightRegular
 public typealias Size = TextS
 public typealias Content = CaptionText
}
public enum DiagramText: GrownDiagram {
 public typealias Across = U128
 public typealias AriaLabel = CaptionText
 @StructureBuilder
 public static var body: some Structure & Divides {
  Fixed<U64, Label>.self
 }
}
`;
const read = judge('drawing.swift', graphic, renderer.kitVocabulary).parsed;
// Test serialization independently of the Swift literal decoder.
read.literals.get('CaptionText').value += '" onload="document.body.dataset.probe=1';
const drawn = renderer.renderAll(read.declarations, read.order, read.literals, read.topAliases);
assert.equal(drawn.errors.length, 0, drawn.errors.join('; '));
assert.equal(drawn.canvases.length, 1, 'the hostile drawing was actually rendered');
pieces.push({label: 'SVG text and attribute', html: drawn.canvases[0].svg, expected: [quoted]});
// Test the renderer's link policy on actual SpanLink output as well.
read.literals.get('CaptionText').value = 'javascript:document.body.dataset.probe=1';
read.declarations.get('DiagramText').entries[0].args[1] = 'SpanLink<CaptionText, Label>';
const links = renderer.renderAll(read.declarations, read.order, read.literals, read.topAliases);
assert.equal(links.canvases.length, 0, 'unsafe URLs refuse instead of changing the native href');
assert.deepEqual(links.refusals, [{name:'DiagramText',status:'refused',code:'unsupported',address:'drawing.swift#DiagramText'}]);
const parser = `
import json,sys
from html.parser import HTMLParser
class Tree(HTMLParser):
 def __init__(self): super().__init__(convert_charrefs=True); self.tags=[]; self.events=[]; self.data=[]; self.links=[]
 def handle_starttag(self,tag,attrs):
  self.tags.append(tag)
  for k,v in attrs:
   if k.lower().startswith('on'): self.events.append(v or '')
   if k.lower() in ('href','xlink:href'): self.links.append(v or '')
 def handle_data(self,data): self.data.append(data)
result=[]
for item in json.load(sys.stdin):
 t=Tree();t.feed(item['html']);result.append(dict(label=item['label'],tags=t.tags,events=t.events,text=''.join(t.data),links=t.links))
print(json.dumps(result))
`;
const proc = cp.spawnSync(process.env.PYTHON || 'python3', ['-c', parser], {input: JSON.stringify(pieces), encoding: 'utf8'});
assert.equal(proc.status, 0, proc.stderr);
const trees = JSON.parse(proc.stdout);
for (let i = 0; i < trees.length; i++) {
    const tree = trees[i], item = pieces[i];
    for (const event of tree.events) vm.runInContext(event, context);
    assert.equal(context.document.body.dataset.probe, undefined, tree.label + ': the event probe stays unset');
    assert(!tree.tags.some(t => ['img','script','iframe','object','embed','foreignobject'].includes(t)), tree.label + ': world text creates no elements');
    assert.equal(tree.events.length, 0, tree.label + ': no inline handlers');
    assert(tree.links.every(l => !/^\s*(?:javascript|data|vbscript):/i.test(l)), tree.label + ': no script URL');
    for (const expected of item.expected) assert(tree.text.includes(expected), tree.label + ': literal text remains readable');
}
console.log('BENCH SECURITY GREEN: ' + pieces.length + ' hostile fragments; no injected elements or running probe');
