/* Transport controls: edits rebuild questions, receipts bind every byte, and a
   grammar refusal cannot be hidden by a body's unchecked status. Semantic
   answers themselves are compared by the pinned Court contract battery. */
'use strict';
const assert=require('assert');
const {canonical,sha,requests,read}=require('../bin/court-contexts.js');
(async()=>{
    const source={input:'Page.swift',source:'Page.swift',role:'own',sha256:await sha('before'),module:'Page',namespace:'Page',imports:[],at:{imports:[]}};
    const contextText=canonical({schema:'vi.court.context/2',sources:[source]});
    const base={arguments:['where','Page.swift','--context','.gate/court/Language.json','--report','--document','Page.swift'],files:[{name:'Page.swift',text:'before'},{name:'.gate/court/Language.json',text:contextText}],reader:{revision:'r'},scope:[{path:'Page.swift',scope:'DemoScope'}]};
    const context={language:'Language',court:{sources:[source]},inputs:[{path:'Page.swift',scope:'DemoScope'}],imports:['Harbor'],requests:[base],receipts:[]};
    let calls=0,selectors=[{predicate:'P',encoding:'E',sigma:'False'}];
    const court={source_notation:async raw=>{
        calls++;const input=JSON.parse(raw);assert.deepStrictEqual(input.questions,['Page.swift']);
        return canonical({schema:'vi.court.notation/1',diagnostics:[],sources:await Promise.all(input.files.map(async f=>({input:f.name,sha256:await sha(f.text),imports:[],questions:selectors})))});
    }};
    const grammar={findings:()=>[]};
    let result=await requests(court,context,{'Page.swift':'after'}, {},grammar);
    assert.equal(calls,1);assert.equal(result.requests.length,2);
    assert.deepStrictEqual(result.requests[1].arguments.slice(-6),['--predicate','P','--encoding','E','--sigma','False']);
    assert.equal(result.requests[1].files[0].text,'after');
    assert.notEqual(await sha(canonical(result.requests[0])),await sha(canonical(base)));
    context.requests=result.requests;selectors=[];
    result=await requests(court,context,{'Page.swift':'removed'}, {},grammar);
    assert.equal(result.requests.length,1);assert.equal(result.requests[0].arguments[0],'where');
    const before=calls;
    result=await requests(court,context,{'Page.swift':'euro'}, {},{findings:()=>[{line:3,atom:'Char8364Atom',scope:'DemoScope',context:'Exempt'}]});
    assert.equal(calls,before);assert.equal(result.requests.length,0);assert.equal(result.refusals[0].address,'Page.swift:3');
    context.requests=[base];
    function answer(request){return Promise.all(request.files.map(async f=>({path:f.name,sha256:await sha(f.text)}))).then(inputs=>({exit:2,stderr:'',stdout:canonical({schema:'vi.court.sources/1',question:'where',inputs:inputs.sort((a,b)=>a.path.localeCompare(b.path,'en')),outcome:'empty',results:[{path:'Page.swift',source:'Page.swift',outcome:'empty',equalities:0,memberships:0,readings:0,unchecked:['Page.swift:2'],diagnostics:[]}],diagnostics:[]})+'\n'}));}
    let judged=0;
    court.judge=async raw=>{judged++;return JSON.stringify(await answer(JSON.parse(raw)));};
    context.receipts=[{schema:'gate.court.receipt/1',origin:{revision:'owner-pin'},request_sha256:await sha(canonical(base)),response:await answer(base)}];
    let readout=await read(court,{contexts:[context]},{});
    assert.equal(judged,0);assert.equal(readout.unsupported.length,0);assert.equal(readout.unchecked.length,1);
    const oldRefusal={address:'Other.swift:3',claim:'grammar: Char8364Atom is not granted DemoScope/Exempt'};
    readout=await read(court,{contexts:[context],refusals:[oldRefusal],unsupported:[{address:'.gate/forms-definitions.json:4',reason:'missing pin'}]},{});
    assert.deepStrictEqual(readout.refusals,[oldRefusal]);assert.equal(readout.unsupported.length,1);
    // A receipt is not cached as a freshly computed owner answer.
    context.receipts=[];readout=await read(court,{contexts:[context]},{});
    assert.equal(judged,1);assert.equal(readout.unsupported.length,0);
    const receipt={schema:'gate.court.receipt/1',origin:{revision:'owner-pin'},request_sha256:await sha(canonical(base)),response:await answer(base)};
    const forged=JSON.parse(receipt.response.stdout);forged.inputs[0].sha256='0'.repeat(64);receipt.response.stdout=canonical(forged)+'\n';
    context.receipts=[receipt];readout=await read(court,{contexts:[context]},{});
    assert.equal(readout.unsupported.length,1);assert.match(readout.unsupported[0].reason,/input hashes/);
    for (const mutation of [
        response => { response.exit=false; },
        response => { const report=JSON.parse(response.stdout); report.unread=true; response.stdout=canonical(report)+'\n'; },
        response => { const report=JSON.parse(response.stdout); report.results[0].unread=true; response.stdout=canonical(report)+'\n'; },
        response => { const report=JSON.parse(response.stdout); report.results[0].unchecked=[false]; response.stdout=canonical(report)+'\n'; },
        response => { const report=JSON.parse(response.stdout); report.results[0].readings=true; response.stdout=canonical(report)+'\n'; },
        response => { const report=JSON.parse(response.stdout); report.results[0].readings=Number.MAX_SAFE_INTEGER+1; response.stdout=canonical(report)+'\n'; },
        response => { const report=JSON.parse(response.stdout); report.results[0].readings=Number.MAX_SAFE_INTEGER; report.results[0].memberships=1; response.stdout=canonical(report)+'\n'; }
    ]) {
        const response=await answer(base);mutation(response);
        await assert.rejects(()=>require('../bin/court-contexts.js').bound(base,response));
    }
    // Execute the delivered worker body with the delivered web wasm bytes.
    // The file-page Blob uses this same glue/bytes/body without importScripts.
    const fs=require('fs'),path=require('path'),{Worker}=require('worker_threads'),{once}=require('events');
    const root=path.join(__dirname,'../bin');
    const handler=fs.readFileSync(path.join(root,'court-worker.js'),'utf8').replace("importScripts('court/vi_court.js','court/vi_court_bytes.js');",'');
    assert(!handler.includes('importScripts('));
    const program="const {parentPort}=require('worker_threads');global.self=global;self.postMessage=data=>parentPort.postMessage(data);\n"
        +fs.readFileSync(path.join(root,'court-wasm/web/vi_court.js'),'utf8')+'\n'
        +fs.readFileSync(path.join(root,'court-wasm/web/vi_court_bytes.js'),'utf8')+'\n'+handler
        +"\nparentPort.on('message',data=>self.onmessage({data}));";
    const worker=new Worker(program,{eval:true});
    try {
        let sequence=0;
        async function call(method,request) { const pending=once(worker,'message'),id=++sequence;
            worker.postMessage({id,method,request:JSON.stringify(request)});const [response]=await pending;
            assert.equal(response.id,id);return response; }
        const notation=await call('source_notation',{files:[{name:'New.swift',text:'public enum NewReading: PredicateReading {\n public typealias Predicate = P\n public typealias Encoding = E\n public typealias Sigma = S\n}\n'}],questions:['New.swift']});
        assert(!notation.error,notation.error);assert.deepEqual(JSON.parse(notation.result).sources[0].questions,[{predicate:'P',encoding:'E',sigma:'S'}]);
        const judgement=await call('judge',{arguments:['where','New.swift'],files:[{name:'New.swift',text:'public protocol Law {\n associatedtype Value\n}\npublic protocol Required: Law\nwhere Value == A {}\npublic enum A {}\npublic enum B {}\npublic enum FalseClaim: Required {\n public typealias Value = B\n}\npublic typealias Use = FalseClaim\n'}]});
        assert(!judgement.error,judgement.error);assert.equal(JSON.parse(judgement.result).exit,1);
        const unsupported=await call('invent',{});assert.match(unsupported.error,/unsupported court transport method/);
    } finally { await worker.terminate(); }
    console.log('PASS: context edits and complete-input receipts retire stale green; the delivered worker reads notation and refuses a false claim');
})().catch(e=>{console.error(e);process.exit(1);});
