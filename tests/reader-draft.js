// One browser draft policy, independent of how a world was selected.
'use strict';
const assert = require('assert'), fs = require('fs'), vm = require('vm'), crypto = require('crypto');
const source = JSON.parse(fs.readFileSync(0, 'utf8'));
function implementation(name) {
    const start = source.ui.search(new RegExp('(?:async )?function ' + name + '\\('));
    assert(start >= 0, name);
    return source.ui.slice(start, source.ui.indexOf('\n}', start) + 2);
}
function storage() {
    const held = Object.create(null);
    Object.defineProperties(held, {
        getItem: {value: key => held[key] ?? null},
        setItem: {value: (key, text) => { held[key] = String(text); }},
        removeItem: {value: key => { delete held[key]; }}
    });
    return held;
}
const layout = 'gate.manifest.swift', file = 'Facts.swift', taken = 'Owner.swift';
const original = 'public enum Owner {}\n', red = original + '// refused reading\n';
function open(context, kept, base = original, policy, noCrypto = false) {
    const files = {files:[file, taken], layout, forms:[], worlds:[[file]], save_policy:policy,
        theirs:{[taken]:{address:layout + ':7', kind:'CarriedFile'}}};
    const snap = {'/files':JSON.stringify(files), '/version':'{}'};
    for (const f of [file, taken, layout]) {
        snap['/world?f=' + f] = f === file ? base : 'owner source';
        snap['/verdict?f=' + f] = '{}';
    }
    const refusal = {address:file + ':2', claim:'a controlled refusal'};
    const scope = vm.createContext({Response, Uint8Array, atob, TextEncoder, crypto:noCrypto ? undefined : crypto.webcrypto, localStorage:kept,
        wasm_bindgen:{initSync(){}}, VI_COURT_WASM_BASE64:'', kitVocabulary:{}, lint(){}, pageGuards(){},
        // The court is controlled here; these probes judge draft transport,
        // not Swift relations. Finished worlds also run playground-storage.js.
        judge(f, text) { return {refusals:text.includes('refused reading')
            ? [{line:2, premise:refusal.claim}] : []}; },
        GateWorldCourt:{verdict(court, groups, texts) { return {
            verdict:texts[file].includes('refused reading') ? 'refused' : 'holds',
            refusals:texts[file].includes('refused reading') ? [refusal] : []}; }},
        fetch:async()=>{throw Error('unexpected network');},
        document:{addEventListener(){}}, location:{}});
    scope.window = scope;
    let program = source.shim.replace(/^<script[^>]*>.*<\/script>\s*$/gm, '')
        .replace(/^<\/?script>\s*$/gm, '');
    for (const [key, value] of Object.entries({__SNAP__:snap, __CONTEXT__:context,
        __STORAGE__:'draft.', __INPUTS_DIGEST__:crypto.createHash('sha256').update(base).digest('hex'),
        __LEGACY_DRAFTS__:context ? [{prefix:'gate.pages.'+context.pin+'.'+context.world+'.',format:'records',baseInputsDigest:crypto.createHash('sha256').update(base).digest('hex')}] : [],
        __PREFERENCE_KEYS__:[], __FORMS__:files.forms, __WORLDS__:files.worlds,
        __LAYOUT__:layout, __ALL__:[file, taken, layout],
        __COURT_WORKER_GLUE__:'', __COURT_WORKER_HANDLER__:''}))
        program = program.split(key).join(JSON.stringify(value));
    vm.runInContext(source.store, scope);
    vm.runInContext(program, scope);
    return scope;
}
async function read(page, route) { return (await page.fetch(route)).text(); }
(async () => {
    for (const context of [null, {pin:'pinned', world:'island', definitions:[], carried:[], guard_names:[]}]) {
        const held = storage(), page = open(context, held);
        assert.strictEqual((await (await page.fetch('/files')).json()).save_policy, 'reader-draft');
        // The actual UI tick must write a red browser draft, while the native
        // repository policy still withholds that same red file.
        let writes = 0;
        const fetch = page.fetch;
        page.fetch = (...args) => { if (args[1]?.method === 'PUT') writes++; return fetch(...args); };
        Object.assign(page, {active:file, editor:{value:red}, readerDrafts:true, lastRefusals:[],
            layoutFile:layout, paintUngranted(){}, refreshGit(){}, esc:String,
            document:{getElementById(){return {}; }}, render:async()=>{
                const answer = await (await page.fetch('/verdict?f='+file,{method:'POST',body:page.editor.value})).json();
                assert.strictEqual(answer.verdict, 'refused');
                page.lastRefusals = answer.refusals.map(r=>({file:r.address.split(':')[0]}));
            }});
        for (const name of ['showWriteRefusal','tick']) vm.runInContext(implementation(name), page);
        await page.tick(true);
        assert.strictEqual(writes, 1);
        const row = JSON.parse(held.getItem('draft.'+file));
        assert.strictEqual(row.format, 1); assert.strictEqual(row.text, red);
        assert.strictEqual(row.verdict.verdict, 'refused');
        assert.strictEqual(await read(open(context, held), '/world?f='+file), red);
        for (const current of [page,open(context,held)]) {
            const status=await(await current.fetch('/gitstatus?f='+file)).json();
            assert.strictEqual(status.git,'draft');
            assert.strictEqual(status.verdict,'read again on open','format 1 must name the rereading');
        }
        // The legacy reader works without Web Crypto. Only storage needs it.
        const noCrypto=open(context,held,original,undefined,true), beforeCrypto=JSON.stringify(held);
        assert.strictEqual(await read(noCrypto,'/world?f='+file),red);
        assert.strictEqual((await(await noCrypto.fetch('/verdict?f='+file,{method:'POST',body:red})).json()).verdict,'refused');
        const notSaved=await noCrypto.fetch('/world?f='+file,{method:'PUT',body:original});
        assert.strictEqual(notSaved.status,507);
        const missingCrypto=await notSaved.json();
        assert.strictEqual(missingCrypto.verdict,'refused');
        assert.strictEqual(missingCrypto.address,file+':1');
        assert(missingCrypto.reason.startsWith('reader draft not saved: '));
        assert(missingCrypto.reason.includes('Web Crypto') && missingCrypto.reason.includes('HTTPS'));
        assert(!missingCrypto.reason.includes('storage unavailable'));
        assert.strictEqual(JSON.stringify(held),beforeCrypto);
        assert.strictEqual((await(await noCrypto.fetch('/verdict?f='+file,{method:'POST',body:original})).json()).verdict,'holds');
        page.readerDrafts = false;
        await page.tick(true); assert.strictEqual(writes, 1, 'native on-holds was weakened');
        // Rejudge the new bytes rather than retaining the saved red receipt.
        assert((await page.fetch('/world?f='+file,{method:'PUT',body:original})).ok);
        assert.strictEqual(JSON.parse(held.getItem('draft.'+file)).verdict.verdict, 'holds');
        assert.strictEqual((await page.fetch('/world?f='+taken,{method:'PUT',body:red})).status,409);
        assert.strictEqual((await page.fetch('/world?f='+layout,{method:'PUT',body:red})).status,409);
        // The current namespace is a record protocol; raw/corrupted bytes are not source.
        held.setItem('draft.'+file, red);
        assert.strictEqual(await read(open(context, held), '/world?f='+file), original);
        held.setItem('draft.'+file, JSON.stringify(row));
        assert.strictEqual(await read(open(context, held), '/world?f='+file), red);
        // An explicit ReadOnly plan must not acquire the legacy default grant,
        // read a retained draft, or answer a changed reading as if permitted.
        const readOnly = open(context, held, original, 'read-only'), retained = JSON.stringify(held);
        assert.strictEqual((await (await readOnly.fetch('/files')).json()).save_policy, 'read-only');
        assert.strictEqual(await read(readOnly, '/world?f='+file), original);
        for (const [route,method] of [['/world?f='+file,'PUT'],['/verdict?f='+file,'POST']]) {
            const r = await readOnly.fetch(route,{method,body:red});
            assert.strictEqual(r.status,409);
            const refusal = await r.json(); assert(refusal.address && refusal.reason);
        }
        assert.strictEqual(JSON.stringify(held),retained);
        page.__resetWipe(); assert.strictEqual(held.getItem('draft.'+file), null);
        if (!context) {
            // A pre-upgrade tab must still see raw Swift at its old key. A JSON
            // looking legacy edit is text too, not our new record envelope.
            const oldKey = 'gate.pages.'+file, oldText = '{"format":1,"text":"legacy source"}';
            held.setItem(oldKey,oldText);
            assert.strictEqual(await read(open(context,held),'/world?f='+file),original);
            assert((await page.fetch('/world?f='+file,{method:'PUT',body:red})).ok);
            assert.strictEqual(held.getItem(oldKey),oldText);
            assert.strictEqual(JSON.parse(held.getItem('draft.'+file)).text,red);
            assert.strictEqual(await read(open(context,held),'/world?f='+file),red);
            page.__resetWipe();
            assert.strictEqual(held.getItem(oldKey),oldText,'an unidentified older copy must be preserved');
            assert.strictEqual(await read(open(context,held),'/world?f='+file),original);
        }

        // Both carriers bind compact edits to the actual base, not its length.
        const base = '// padding\n'.repeat(60000), big = open(context, held, base);
        const first = base.slice(0,100)+'// refused reading\n'+base.slice(100);
        const second = first+'// end\n';
        assert((await big.fetch('/world?f='+file,{method:'PUT',body:first})).ok);
        assert((await big.fetch('/world?f='+file,{method:'PUT',body:second})).ok);
        const compact = JSON.parse(held.getItem('draft.'+file));
        assert.strictEqual(compact.verdict.verdict,'refused');
        assert.strictEqual(await read(open(context, held, base), '/world?f='+file), second);
        const changedBases = [['short', 'public enum NewSource {}\n'],
            ['equal-length', base.replaceAll('padding', 'changed')]];
        for (const [kind, replacement] of changedBases) {
            assert.strictEqual(await read(open(context, held, replacement), '/world?f='+file), replacement,
                'republished ' + kind + ' base must ignore a draft of other bytes');
        }
        assert.strictEqual(compact.format, 2);
        assert(held.getItem('draft.'+file).length < 2000);
        assert.strictEqual((await (await open(context,held,base).fetch('/gitstatus?f='+file)).json()).verdict,'read again on open');
        for (const raw of ['{"format":2,', '{"format":77}', 'null']) {
            held.setItem('draft.'+file,raw);
            assert.strictEqual(await read(open(context,held,base),'/world?f='+file),base);
        }
        if (context) {
            held.removeItem('draft.'+file);
            const oldKey='gate.pages.'+context.pin+'.'+context.world+'.'+file;
            held.setItem(oldKey,JSON.stringify({format:2,splices:[{from:0,to:0,insert:'// recovered\n'}],verdict:{verdict:'holds'}}));
            assert.strictEqual(await read(open(context,held,base),'/world?f='+file),'// recovered\n'+base);
            assert.strictEqual((await(await open(context,held,base).fetch('/gitstatus?f='+file)).json()).verdict,'read again on open');
            open(context,held,base).__resetWipe();assert.strictEqual(held.getItem(oldKey),null);
        }
        for (const splices of ['broken', [{from:-1,to:0,insert:'bad'}],
            [{from:0,to:base.length+1,insert:'bad'}]]) {
            held.setItem('draft.'+file, JSON.stringify({format:2,splices,base_inputs_digest:crypto.createHash('sha256').update(base).digest('hex')}));
            assert.strictEqual(await read(open(context, held, base), '/world?f='+file), base,
                'an inapplicable format 2 must return source, never its JSON envelope');
        }
        // A storage failure must not acknowledge a draft it did not keep.
        const denied = {getItem(){return null;},setItem(){throw Error('quota');}};
        assert.strictEqual((await open(context, denied).fetch('/world?f='+file,{method:'PUT',body:red})).status,507);
    }
    const badge={};
    const ui=vm.createContext({active:file,fileLoadGeneration:1,theirsFiles:{},readerDrafts:true,
        reading:()=>false,fetch:async()=>({json:async()=>({git:'draft',verdict:'read again on open'})}),
        document:{getElementById:()=>badge},window:{}});
    vm.runInContext(implementation('refreshGit'),ui);await ui.refreshGit();
    assert.strictEqual(badge.textContent,'draft saved · read again on open');
    console.log('READER DRAFT GREEN: both carriers bind drafts to their base, recover scoped records, ignore damage and saved verdicts; read without crypto; native on-holds');
})().catch(e=>{console.error(e);process.exitCode=1;});
