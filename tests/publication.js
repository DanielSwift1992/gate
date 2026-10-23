'use strict';
const assert=require('assert'),fs=require('fs'),path=require('path'),vm=require('vm'),{webcrypto}=require('crypto');
const expected=process.argv[3]||'holds',file=process.argv[4]||'Facts.swift';
const site=process.argv[2],origin='http://fixture.test/book/';
const stored = new Map();
const storage = {getItem: key => stored.get(key) ?? null, setItem: (key, value) => stored.set(key, String(value)),
    removeItem: key => stored.delete(key)};
async function transport(broken, live = false, failStorage = false, options = {}) {
    const folder=options.site||site,route=options.route||'harbor/';
    const files=[];
    const real=async input=>{
        const u=new URL(String(input),origin),relative=decodeURIComponent(u.pathname.slice('/book/'.length));
        files.push(relative);
        if(relative===broken) return new Response('missing',{status:404});
        const name=path.join(folder,relative);
        return fs.existsSync(name)?new Response(fs.readFileSync(name)):new Response('missing',{status:404});
    };
    const plan=JSON.parse(fs.readFileSync(path.join(folder,'read-plan.json'),'utf8'));
    const html=fs.readFileSync(path.join(folder,route,'index.html'),'utf8');
    const loader=html.match(/<script[^>]*src="[^"]*assets\/publication\.js"[^>]*>/)[0];
    const attribute=name=>loader.match(new RegExp(name+'="([^"]*)"'))[1];
    const listeners={};
    const c={URL,Response,Uint8Array,TextEncoder,TextDecoder,WebAssembly,crypto:webcrypto,
        atob:s=>Buffer.from(s,'base64').toString('binary'),location:{href:origin+route,reload(){}},
        localStorage: failStorage ? {...storage, setItem(){throw Error('quota');}} : storage,
        document:{addEventListener:(name,handler)=>{listeners[name]=handler;},
            currentScript:{dataset:{replies:attribute('data-replies'),plan:attribute('data-plan'),
            draftPolicy:attribute('data-draft-policy'),live:String(live)}}},fetch:real,console};
    c.window=c;
    vm.createContext(c);
    // Load the delivered readers and ports in their declared order. Only
    // the DOM editor and the transport under test have separate hosts here.
    for(const tag of html.matchAll(/<script\b[^>]*\bsrc="([^"]+)"[^>]*>/g)) {
        const asset=new URL(tag[1],origin+route).pathname.slice('/book/'.length);
        if(['assets/codemirror.js','assets/publication.js'].includes(asset)) continue;
        assert(Object.hasOwn(plan.resources,asset),'undeclared script '+asset);
        vm.runInContext(fs.readFileSync(path.join(folder,asset),'utf8'),c);
    }
    vm.runInContext(fs.readFileSync(path.join(folder,'assets/publication.js'),'utf8'),c);
    return {fetch:c.window.fetch,plan,files,html,scope:c,listeners};
}
async function run(){
    const t=await transport();
    assert.equal((await (await t.fetch('/status')).json()).verdict,expected);
    const f=file,text=await(await t.fetch('/world?f='+encodeURIComponent(f))).text();
    assert.equal((await(await t.fetch('/verdict?f='+f,{method:'POST',body:text})).json()).verdict,expected);
    if(t.plan.draft_policy==='ReaderDraft') {
        assert.equal((await(await t.fetch('/files')).json()).save_policy,'reader-draft');
        assert(!JSON.stringify(await(await t.fetch('/status')).json()).includes('Read-only publication'));
        const files=await(await t.fetch('/files')).json();
        if(!files.capabilities.write.includes(f)) {
            assert.equal(files.capabilities.write.length,0,'unprepared Language cannot widen another file');
            assert((await(await t.fetch('/status')).json()).next.includes('no inputs available for browser drafts'),'N3: empty write must not promise reader edits');
            for(const changed of [text+'// comment\n',text.replace('import HarborShapes\n','').replaceAll('Token','Nowhere')]) {
                const posted=await t.fetch('/verdict?f='+f,{method:'POST',body:changed});
                assert.equal(posted.status,409);
                const answer=await posted.json();assert.notEqual(answer.verdict,'holds');
                assert(answer.unsupported.some(r=>r.address===f+':1'));
                const baseline=await(await t.fetch('/verdict?f='+f,{method:'POST',body:text})).json();
                assert.deepEqual(answer.refusals,baseline.refusals,'native refusals survive an unread edit');
                assert.equal((await t.fetch('/world?f='+f,{method:'PUT',body:changed})).status,409);
                assert.equal(await(await t.fetch('/world?f='+f)).text(),text);
                assert.equal(stored.size,0);
            }
        } else if(f!=='Facts.swift') {
            const changed=text+'// a prepared context is read again\n';
            const answer=await(await t.fetch('/verdict?f='+f,{method:'POST',body:changed})).json();
            assert.equal(answer.verdict,expected);assert(answer.court_readings.length);
            assert.equal((await t.fetch('/world?f='+f,{method:'PUT',body:changed})).status,200);
            const reopened=await transport();assert.equal(await(await reopened.fetch('/world?f='+f)).text(),changed);
            assert.equal((await(await reopened.fetch('/status')).json()).verdict,expected);
        } else {
        const red=text.replace('Pair<Coral, Coral>','Pair<Coral, Other>');
        assert.notEqual(red,text);
        assert.equal((await(await t.fetch('/verdict?f='+f,{method:'POST',body:red})).json()).verdict,'refused');
        const saved=await t.fetch('/world?f='+f,{method:'PUT',body:red});assert.equal(saved.status,200);
        const envelope=JSON.parse([...stored.values()][0]);
        assert.equal(envelope.text,red);assert.equal(envelope.verdict.verdict,'refused');
        assert.equal(envelope.base_inputs_digest,t.plan.inputs_digest);
        assert.equal(envelope.inputs_digest,envelope.verdict.inputs_digest);
        assert.match(envelope.inputs_digest,/^[0-9a-f]{64}$/);
        // The accepted 1b writer had a base digest but no base_length.
        const oldRecord={...envelope};delete oldRecord.base_length;
        stored.set((await(await t.fetch('/files')).json()).reader_draft_namespace+f,JSON.stringify(oldRecord));
        for(const live of [false,true]) {
            const reopened=await transport(null,live);
            assert.equal(await(await reopened.fetch('/world?f='+f)).text(),red);
            assert.equal((await(await reopened.fetch('/status')).json()).verdict,'refused');
            const status=await(await reopened.fetch('/gitstatus?f='+f)).json();
            assert.equal(status.git,'draft');assert.equal(status.verdict,'read again on open');
            assert.equal((await reopened.fetch('/world?f=Evidence.md',{method:'PUT',body:'changed'})).status,409);
            assert.equal((await reopened.fetch('/declare',{method:'PUT',body:'changed'})).status,409);
        }
        for(const route of ['', 'archive/start/']) {
            const alias=await transport(null,false,false,{route});
            assert.equal(await(await alias.fetch('/world?f='+f)).text(),red,'Entry and alias share the canonical draft');
        }
        const unprepared=await(await t.fetch('/verdict?f='+f,{method:'POST',body:'import UninvitedModule\n'+text})).json();
        assert.notEqual(unprepared.verdict,'holds');
        assert(unprepared.unsupported.some(r=>r.address===f+':1' && r.reason.includes('Language')));
        const count=text+'\npublic enum Asked: PredicateReading {\n public typealias Predicate = P\n public typealias Encoding = E\n public typealias Sigma = S\n}\n';
        const counted=await(await t.fetch('/verdict?f='+f,{method:'POST',body:count})).json();
        assert.notEqual(counted.verdict,'holds');
        assert(counted.unsupported.some(r=>r.address===f+':1'&&r.reason.includes('count')),'M6: count needs its own definition context');
        for(const broken of [text+'\npublic enum Broken: Choice {\n',text+'\npublic enum Coral: Choice {}\n']) {
            const posted=await t.fetch('/verdict?f='+f,{method:'POST',body:broken});assert.equal(posted.status,200);
            const answer=await posted.json();assert.notEqual(answer.verdict,'holds');
            assert(answer.unsupported.some(r=>r.address===f+':1'&&r.reason.includes('notation')));
            const saved=await t.fetch('/world?f='+f,{method:'PUT',body:broken});assert.equal(saved.status,200);
            for(const live of [false,true]) {
                const reopened=await transport(null,live);
                assert.equal(await(await reopened.fetch('/world?f='+f)).text(),broken);
                assert.notEqual((await(await reopened.fetch('/status')).json()).verdict,'holds');
            }
        }
        // An unlocated batch diagnostic must not be blamed on an unrelated
        // edited input. Use the actual owner reader on both source files.
        const sibling='Notes.swift', currentFiles=await(await t.fetch('/files')).json();
        if(currentFiles.capabilities.write.includes(sibling)) {
            const note=await(await t.fetch('/world?f='+sibling)).text();
            const changed=note+'// reader comment\n';
            const result=await(await t.fetch('/verdict?f='+sibling,{method:'POST',body:changed})).json();
            assert(result.unsupported.some(r=>r.address===f+':1'&&r.reason.includes('notation')));
            assert(!result.unsupported.some(r=>r.address===sibling+':1'&&r.reason.includes('notation')),'N3: the well-formed sibling is not the broken input');
            assert.equal((await t.fetch('/world?f='+sibling,{method:'PUT',body:changed})).status,200);
            stored.delete(currentFiles.reader_draft_namespace+sibling);
        }
        const full=await transport(null,false,true);
        assert.equal((await full.fetch('/world?f='+f,{method:'PUT',body:text})).status,507);
        assert.equal((await t.fetch('/world?f='+f,{method:'PUT',body:text})).status,200);
        assert.equal((await(await t.fetch('/status')).json()).verdict,'holds');
        const draftKey=[...stored.keys()][0],good=stored.get(draftKey),bad=JSON.parse(good);
        bad.base_inputs_digest='0'.repeat(64);bad.text='a draft of another source';stored.set(draftKey,JSON.stringify(bad));
        assert.equal(await(await(await transport()).fetch('/world?f='+f)).text(),text,'M8: wrong base digest cannot restore');
        stored.set(draftKey,good);
        if(process.argv[5]) {
            assert.equal((await t.fetch('/world?f='+f,{method:'PUT',body:red})).status,200);
            const next=await transport(null,false,false,{site:process.argv[5]});
            assert.notEqual(next.plan.plan_id,t.plan.plan_id);assert.notEqual(next.plan.inputs_digest,t.plan.inputs_digest);
            const fresh=await(await next.fetch('/world?f='+f)).text();assert.notEqual(fresh,red);
            assert.equal((await(await next.fetch('/status')).json()).verdict,'holds');
            assert.equal((await next.fetch('/world?f='+f,{method:'PUT',body:fresh+'// new draft\n'})).status,200);
            assert.equal(stored.size,2,'M13: republishing must not replace the prior plan key');
            assert.equal(await(await t.fetch('/world?f='+f)).text(),red);
        }
        assert(t.html.includes('id="reset-copy"'));
        let prevented=false;t.listeners.click({target:{closest:selector=>selector==='#reset-copy'},preventDefault(){prevented=true;}});
        assert(prevented);assert.equal(await(await t.fetch('/world?f='+f)).text(),text);
        }
    } else {
        assert.equal((await(await t.fetch('/verdict?f='+f,{method:'POST',body:text+'changed'})).json()).verdict,'unsupported');
        assert.equal((await t.fetch('/world?f='+f,{method:'PUT',body:text})).status,409);
    }
    assert.equal((await t.fetch('/world?f=gate.manifest.swift',{method:'PUT',body:'changed'})).status,409);
    const carried=JSON.parse(fs.readFileSync(path.join(site,'snapshots/harbor.json'),'utf8')).responses['GET /files'];
    for(const name of JSON.parse(carried.body).carried) {
        const denied=await t.fetch('/verdict?f='+encodeURIComponent(name),{method:'POST',body:'changed carried bytes'});
        assert.equal(denied.status,409,'M11: altered non-writable POST cannot borrow a delivered answer');
        assert.notEqual((await denied.json()).verdict,'holds');
    }
    if(t.plan.languages.Island?.resolved.active)
        assert.deepEqual(await(await t.fetch('/grammar-contexts')).json(),t.plan.languages.Island.resolved);
    const bytes=Object.keys(t.plan.resources).find(n=>n.startsWith('inputs/'));
    const lost=await transport(bytes),answer=await(await lost.fetch('/status')).json();
    assert.equal(answer.verdict,'refused');assert(answer.input_errors.length);
    const corrupt=path.join(site,bytes),old=fs.readFileSync(corrupt);fs.writeFileSync(corrupt,'corrupt');
    try{const bad=await transport();assert.equal((await(await bad.fetch('/status')).json()).verdict,'refused');}
    finally{fs.writeFileSync(corrupt,old);}
    const snap=path.join(site,'snapshots/harbor.json'),saved=fs.readFileSync(snap);
    const changed=JSON.parse(saved);changed.responses['GET /status'].body='{"verdict":"holds","forged":true}';fs.writeFileSync(snap,JSON.stringify(changed));
    try{const bad=await transport();assert.equal((await(await bad.fetch('/status')).json()).verdict,'refused');}
    finally{fs.writeFileSync(snap,saved);}
    // The artifact includes the actual browser court, not a placeholder asset.
    const w={TextDecoder,TextEncoder,WebAssembly,Uint8Array,console};vm.createContext(w);
    vm.runInContext(fs.readFileSync(path.join(site,'assets/vi_court.js'),'utf8'),w);
    vm.runInContext(fs.readFileSync(path.join(site,'assets/vi_court_bytes.js'),'utf8'),w);
    vm.runInContext('wasm_bindgen.initSync({module: Uint8Array.from(atob(VI_COURT_WASM_BASE64), c=>c.charCodeAt(0))})',Object.assign(w,{atob:s=>Buffer.from(s,'base64').toString('binary')}));
    console.log('PUBLICATION TRANSPORT ALL GREEN: mounted root, declared draft policy, addressed residues, delivery failures and wasm');
}
if(require.main===module)run().catch(e=>{console.error(e);process.exitCode=1;});
module.exports={transport,stored};
