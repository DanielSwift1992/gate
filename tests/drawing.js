// DocumentKit's executed answers, selected by the ONE showcase pin.
'use strict';
const fs = require('fs'), path = require('path'), assert = require('assert/strict'), crypto = require('crypto');
const {drawingParse} = require('../bin/judge.js'), {renderAll} = require('../bin/renderer.js');
const sc = path.join(process.argv[2], 'showcase'), contract = path.join(sc, 'Contracts/Drawing/v0.1');
const read = p => fs.readFileSync(p, 'utf8'), sha = s => crypto.createHash('sha256').update(s).digest('hex');
const manifest = JSON.parse(read(path.join(contract, 'manifest.json')));
const counts = {svg:0, refused:0, 'not-compared':0};
function draw(files) { const p = drawingParse(files); return renderAll(p.declarations, p.order, p.literals, p.topAliases); }
for (const c of manifest.cases) {
    counts[c.status]++;
    if (c.status === 'not-compared') { assert(c.address && c.reason); continue; }
    const files = c.sources.map(file => ({file, text:read(path.join(sc, file))}));
    assert.equal(sha(files.map(f => f.text).join('\n')), c.inputSHA256, c.id + ' exact input');
    const r = draw(files), art = r.canvases.find(x => x.name === c.root), refusal = r.refusals.find(x => x.name === c.root);
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
assert.deepEqual(counts, {svg:16,refused:4,'not-compared':1});
// New names, executable overrides, unrecognized forms and escapes never gain
// semantics merely because a known demo once used a similar declaration.
const basic = read(path.join(contract, 'cases/half-even.swift'));
const artName = basic.replaceAll('FixtureArt', 'SomebodysArt');
assert.equal(draw([{file:'New.swift',text:artName}]).canvases[0].name, 'SomebodysArt');
for (const text of [
    basic.replace('Half<U2>', 'Mystery<U2>'),
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
console.log('DRAWING GREEN: 16 native SVG byte comparisons, 4 native refusals, 1 explicitly not-compared; independent caller and unsupported controls');
