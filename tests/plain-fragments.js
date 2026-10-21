'use strict';
const assert = require('assert/strict');
const {verdict} = require('../bin/world-court.js');
const {judge} = require('../bin/judge.js');
const {kitVocabulary} = require('../bin/renderer.js');
const source = `public enum Alice: Employee {
    public typealias Rank = Lead
    public typealias Home = Finance
}
public enum MustHold: Team {
    @StructureBuilder
    public static var body: some Structure {
        VerifiedInDepartment<Alice, Sales>.self;
    }
}
// the company below
`;
const ask = text => verdict(null, [], {'Company.swift': text}, [], ['Company.swift'], [], null,
    (file, stream) => judge(file, stream, kitVocabulary));
const refused = ask(source);
assert.equal(refused.verdict, 'refused');
assert.deepEqual(refused.refusals.map(r => r.address), ['Company.swift:8']);
assert.equal(ask(source.replace('Alice, Sales', 'Alice, Finance')).verdict, 'holds');
console.log('BROWSER WHOLE FILE GREEN: a false requirement before the former delimiter retains its address');
