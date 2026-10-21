"use strict";
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert/strict');
const ui = fs.readFileSync(path.join(__dirname, '../web/ui.html'), 'utf8');
const start = ui.indexOf('function readingChip('), end = ui.indexOf('\n}', start);
assert(start >= 0 && end > start);
const chip = answer => {
    const ctx = vm.createContext({r: answer, broken: answer.refusals || [], escAttr: String});
    vm.runInContext(ui.slice(start, end + 2), ctx);
    return vm.runInContext('readingChip(r, broken)', ctx);
};
const [empty, held, refused] = JSON.parse(fs.readFileSync(0, 'utf8'));
assert.equal(empty.verdict, 'empty');
assert(chip(empty).includes('empty · no declared applications'));
assert(!chip(empty).includes('chip ok'));
assert(chip(held).includes('>holds</span>'));
assert(chip(refused).includes('chip bad'));
assert(!chip({...empty, refusals: refused.refusals}).includes('no declared applications'));
// The static bench uses the same wasm where court through this adapter.
const world = require('../bin/world-court.js'), court = require('../bin/court-wasm/node/vi_court.js');
const base = 'public protocol Choice {}\npublic protocol Paired {}\npublic enum Coral: Choice {}\npublic enum Pair<L: Choice, R: Choice> {}\nextension Pair: Paired where L == R {}\n';
for (const [text, expected] of [[base, 'empty'], [base + 'public typealias Same = Pair<Coral, Coral>\n', 'holds']]) {
    const result = world.verdict(court, [['Claims.swift']], {'Claims.swift': text}, [], [], [], null);
    assert.equal(result.verdict, expected);
    if (expected === 'empty') { assert.equal(result.reason, empty.reason); assert(!chip(result).includes('chip ok')); }
}
