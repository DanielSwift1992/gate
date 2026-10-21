'use strict';
const assert=require('assert/strict'),{verdict,documentDeclarations}=require('../bin/world-court.js');
const court=require('../bin/court-wasm/node/vi_court.js');
const claim=`public protocol Pair { associatedtype Left; associatedtype Right }
public protocol Same: Pair where Left == Right {}
public enum Coral {}
public enum Stone {}
public enum Claim: Same {
    public typealias Left = Coral
    public typealias Right = Coral
}
`;
const body=`public enum Page {
    public static var body: some Structure {
        /* a comment with a closing brace } /* nested */ */
        "braces { } are text"
        MissingDrawing<Stone>.self
    }
}
`;
function ask(text,document=true){return verdict(court,[['Page.swift']],{'Page.swift':text},[],[],[],null,()=>({refusals:[]}),null,[],null,document?['Page.swift']:[]);}
const source=claim+body, projected=documentDeclarations(source);
assert.equal(source.split('\n').length,projected.split('\n').length);
assert(!projected.includes('MissingDrawing<Stone>'));
assert(projected.includes('typealias Right = Coral'));
assert.equal(ask(source).verdict,'holds');
assert.equal(ask(source.replace('Right = Coral','Right = Stone')).verdict,'refused');
assert.equal(ask(source.replace('public enum Page','@Unknown public enum Page')).verdict,'unsupported');
assert.equal(ask(body).verdict,'empty');
assert.notEqual(ask(source,false).verdict,'holds');
assert.equal(documentDeclarations(source.replaceAll('\n','\r\n')),projected);
const quoted='public enum Word {\n    public static var typeName: String {\n        """\n        public static var body: some Structure {\n        }\n        """\n    }\n}\n';
assert.equal(documentDeclarations(quoted),quoted);
assert.throws(()=>documentDeclarations(body.replace('    }','    } public enum Hidden {}')),/separate body closing line/);
const marked=source+'// gate-unsupported: Owed | remains a requirement\npublic typealias Owed = Coral\n';
assert.equal(ask(marked).verdict,'partial');
assert(ask(marked).unsupported.some(r=>r.id==='Owed'));
assert.equal(ask(marked.replace('public typealias Owed = Coral','')).verdict,'refused');
const second=verdict(court,[['Claims.swift','Canvas.swift']],{'Claims.swift':claim,'Canvas.swift':body.replace('public enum Page','@Unknown public enum Page')},[],[],[],null,()=>({refusals:[]}),null,[],null,['Claims.swift','Canvas.swift']);
assert.equal(second.verdict,'unsupported');
assert(second.unsupported.some(r=>r.address==='Canvas.swift:1'),JSON.stringify(second));
console.log('DOCUMENT READER GREEN: declaration equality, false equality, unread attribute, empty, original line addresses, body boundary, strings/comments, CRLF and retained requirements');
