// DocumentKit's executed answers, selected by the ONE showcase pin.
'use strict';
const fs = require('fs'), path = require('path'), assert = require('assert/strict'), crypto = require('crypto');
const {drawingParse} = require('../bin/judge.js'), {renderAll} = require('../bin/renderer.js');
const sc = path.join(process.argv[2], 'showcase'), contract = path.join(sc, 'Contracts/Drawing/v0.1');
const read = p => fs.readFileSync(p, 'utf8'), sha = s => crypto.createHash('sha256').update(s).digest('hex');
const manifest = JSON.parse(read(path.join(contract, 'manifest.json')));
const counts = {svg:0, refused:0, 'not-compared':0};
function draw(files) { const p = drawingParse(files); return renderAll(p.declarations, p.order, p.literals, p.topAliases); }
const profile = {contract:JSON.parse(read(path.join(contract, 'contract.json')))};
const comparison = require('../bin/drawing-profile.js');
(async () => {
for (const c of manifest.cases) {
    counts[c.status]++;
    if (c.status === 'not-compared') { assert(c.address && c.reason); continue; }
    const files = c.sources.map(file => ({file, text:read(path.join(sc, file))}));
    assert.equal(sha(files.map(f => f.text).join('\n')), c.inputSHA256, c.id + ' exact input');
    const r = draw(files);
    assert.equal((await comparison.compare(profile,files,r)).status,'compared',c.id+' shared comparison');
    assert.equal((await comparison.compare(profile,[...files,{file:'Extra.swift',text:'// extra input'}],r)).status,'port-under-contract');
    const edited=files.map((f,i)=>({...f,text:f.text+(i===0?'\n// edited':'')}));
    assert.equal((await comparison.compare(profile,edited,r)).status,'port-under-contract');
    const wrong=structuredClone(r);
    if(wrong.canvases.length)wrong.canvases[0].svg+=' ';else wrong.refusals[0].code='wrong';
    assert.equal((await comparison.compare(profile,files,wrong)).status,'not-compared');
    const art = r.canvases.find(x => x.name === c.root), refusal = r.refusals.find(x => x.name === c.root);
    if (c.status === 'svg') {
        assert(!refusal, c.id + ': ' + r.errors.join('; ')); assert(art, c.id);
        const expected = read(path.join(contract, c.output));
        assert.equal(sha(expected), c.svgSHA256, c.id + ' native output hash');
        assert.equal(art.svg, expected, c.id + ' native bytes (no normalization)');
    } else {
        assert(!art, c.id + ' refusal must produce no SVG');
        assert.deepEqual(refusal, {name:c.root,status:'refused',code:c.code,address:c.address}, c.id);
    }
}
assert.deepEqual(counts, {svg:17,refused:4,'not-compared':1});
// New names, executable overrides, unrecognized forms and escapes never gain
// semantics merely because a known demo once used a similar declaration.
const basic = read(path.join(contract, 'cases/half-even.swift'));
const artName = basic.replaceAll('FixtureArt', 'SomebodysArt');
assert.equal(draw([{file:'New.swift',text:artName}]).canvases[0].name, 'SomebodysArt');
for (const text of [
    basic.replace('Half<U2>', 'Mystery<U2>'),
    basic.replace('public typealias AriaLabel = FixtureTitle', 'public typealias AriaLabel = TermText<Undeclared>'),
    basic.replace('Half<U2>', 'Custom').concat('\npublic protocol Executable: Close {\n static var count: Int { get }\n}\npublic enum Custom: Executable {}\n'),
    basic.replace('public typealias Across = U64', 'public typealias Across = U64\n public typealias Backdrop = PageBackdrop'),
    basic.replace('public typealias Across = U64', 'public typealias Across = U64\n public typealias Backdrop = MadeUp'),
    basic.replace('Half<U2>', 'Custom').concat('\npublic enum Custom: Close { public static var count: Int { 50 } }\n'),
    basic.replace('Half<U2>', 'Custom').concat('\npublic enum Custom: Close {}\nextension Custom { public static var count: Int { 50 } }\n'),
    basic.replace('Half<U2>', 'Custom').concat('\nextension Custom { public static var count: Int { 50 } }\npublic enum Custom: Close {}\n'),
    basic.replace('Half<U2>', 'Half<U2, U4>'),
    basic.replace('Half<U2>', 'Cycle').concat('\npublic typealias Cycle = Cycle\n'),
    basic.replace('"Count"', '"\\(unknown)"'),
]) {
    const r = draw([{file:'Other.swift',text}]);
    assert.equal(r.canvases.length, 0);
    assert.deepEqual(r.refusals, [{name:'FixtureArt',status:'refused',code:'unsupported',address:'Other.swift#FixtureArt'}]);
}
console.log('DRAWING GREEN: 17 native SVG byte comparisons, 4 native refusals, 1 explicitly not-compared; independent caller and unsupported controls');

const parts=[{file:'Generated.swift',text:'generated input'}],empty={canvases:[],refusals:[]};
assert.equal((await comparison.compare({...profile,ownerInputsMatch:false},parts,empty)).status,'port-under-contract');
const current=await comparison.compare(profile,parts,empty);
const declared={case_id:'scale',source_digest:current.source_digest};
assert.equal((await comparison.compare(profile,parts,empty,declared)).status,'not-compared');
assert.equal((await comparison.compare(profile,[{file:'Generated.swift',text:'edited input'}],empty,declared)).status,'port-under-contract');
assert.equal((await comparison.compare(profile,parts,empty,{...declared,case_id:'unrecognized'})).status,'port-under-contract');
console.log('COMPARISON GREEN: exact input and output, added input, edit, differing output and bound owner remainder');
})().catch(e=>{console.error(e);process.exitCode=1;});
