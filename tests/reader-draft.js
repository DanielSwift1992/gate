// One browser draft policy, independent of how a world was selected.
'use strict';
const assert = require('assert'), fs = require('fs'), vm = require('vm');
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
function open(context, kept, base = original, policy) {
    const files = {files:[file, taken], layout, forms:[], worlds:[[file]], save_policy:policy,
        theirs:{[taken]:{address:layout + ':7', kind:'CarriedFile'}}};
    const snap = {'/files':JSON.stringify(files), '/version':'{}'};
    for (const f of [file, taken, layout]) {
        snap['/world?f=' + f] = f === file ? base : 'owner source';
        snap['/verdict?f=' + f] = '{}';
    }
    const refusal = {address:file + ':2', claim:'a controlled refusal'};
    const scope = vm.createContext({Response, Uint8Array, atob, localStorage:kept,
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
        __STORAGE__:'draft.', __FORMS__:files.forms, __WORLDS__:files.worlds,
        __LAYOUT__:layout, __ALL__:[file, taken, layout],
        __COURT_WORKER_GLUE__:'', __COURT_WORKER_HANDLER__:''}))
        program = program.split(key).join(JSON.stringify(value));
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
        assert.strictEqual((await (await page.fetch('/gitstatus?f='+file)).json()).git, 'draft');
        page.readerDrafts = false;
        await page.tick(true); assert.strictEqual(writes, 1, 'native on-holds was weakened');
        // Rejudge the new bytes rather than retaining the saved red receipt.
        assert((await page.fetch('/world?f='+file,{method:'PUT',body:original})).ok);
        assert.strictEqual(JSON.parse(held.getItem('draft.'+file)).verdict.verdict, 'holds');
        assert.strictEqual((await page.fetch('/world?f='+taken,{method:'PUT',body:red})).status,409);
        assert.strictEqual((await page.fetch('/world?f='+layout,{method:'PUT',body:red})).status,409);
        // Existing raw and format 1 records survive a reopen in either carrier.
        held.setItem('draft.'+file, red);
        assert.strictEqual(await read(open(context, held), '/world?f='+file), red);
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
            assert.strictEqual(await read(open(context,held),'/world?f='+file),oldText);
            assert((await page.fetch('/world?f='+file,{method:'PUT',body:red})).ok);
            assert.strictEqual(held.getItem(oldKey),oldText);
            assert.strictEqual(JSON.parse(held.getItem('draft.'+file)).text,red);
            assert.strictEqual(await read(open(context,held),'/world?f='+file),red);
            page.__resetWipe();
            assert.strictEqual(held.getItem(oldKey),null);
            assert.strictEqual(await read(open(context,held),'/world?f='+file),original);
        }

        // A pinned world can use compact edits. An ordinary snapshot has no
        // base identity yet, so a republished page must keep the complete draft.
        const base = '// padding\n'.repeat(60000), big = open(context, held, base);
        const first = base.slice(0,100)+'// refused reading\n'+base.slice(100);
        const second = first+'// end\n';
        assert((await big.fetch('/world?f='+file,{method:'PUT',body:first})).ok);
        assert((await big.fetch('/world?f='+file,{method:'PUT',body:second})).ok);
        const compact = JSON.parse(held.getItem('draft.'+file));
        assert.strictEqual(compact.verdict.verdict,'refused');
        assert.strictEqual(await read(open(context, held, base), '/world?f='+file), second);
        if (!context) {
            const changedBases = [['short', 'public enum NewSource {}\n'],
                ['equal-length', base.replaceAll('padding', 'changed')]];
            for (const [kind, replacement] of changedBases) {
                assert.strictEqual(await read(open(null, held, replacement), '/world?f='+file), second,
                    'republished ' + kind + ' base must preserve the complete reader text');
            }
            assert.strictEqual(compact.format, 1);
            assert.strictEqual(compact.text, second);
            // Previously produced, unbound format 2 is inapplicable here.
            // Never expose its JSON envelope or splice it into a new source.
            held.setItem('draft.'+file, JSON.stringify({format:2,
                splices:[{from:100,to:100,insert:'// old edit\n'}],verdict:compact.verdict}));
            for (const replacement of [base, 'short', base.replaceAll('padding', 'changed')])
                assert.strictEqual(await read(open(null, held, replacement), '/world?f='+file), replacement);
        } else {
            assert.strictEqual(compact.format, 2);
            assert(held.getItem('draft.'+file).length < 2000);
        }
        for (const splices of ['broken', [{from:-1,to:0,insert:'bad'}],
            [{from:0,to:base.length+1,insert:'bad'}]]) {
            held.setItem('draft.'+file, JSON.stringify({format:2,splices}));
            assert.strictEqual(await read(open(context, held, base), '/world?f='+file), base,
                'an inapplicable format 2 must return source, never its JSON envelope');
        }
        // A storage failure must not acknowledge a draft it did not keep.
        const denied = {getItem(){return null;},setItem(){throw Error('quota');}};
        assert.strictEqual((await open(context, denied).fetch('/world?f='+file,{method:'PUT',body:red})).status,507);
    }
    console.log('READER DRAFT GREEN: both carriers keep red receipts; ordinary drafts survive republishing; pinned edits stay compact; native on-holds');
})().catch(e=>{console.error(e);process.exitCode=1;});
