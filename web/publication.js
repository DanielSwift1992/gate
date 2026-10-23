/* The publication transports one native ReadPlan and its response bytes.
   DraftPolicy grants browser storage; the source repository stays read-only. */
(() => {
    'use strict';
    const script = document.currentScript;
    const real = window.fetch.bind(window);
    const snapshotsURL = new URL(script.dataset.replies, location.href);
    const root = new URL('../', snapshotsURL);
    const declaredPlan = script.dataset.plan;
    const live = script.dataset.live === 'true';
    let held, plan, snapshots, drafts, court, draftPrefix;
    const readings = new Map();
    window.GatePublication = Object.freeze({
        get readOnly() { return (plan?.draft_policy || script.dataset.draftPolicy) !== 'ReaderDraft'; },
        plan_id: declaredPlan
    });
    function failure(reason, address = 'read-plan.json:1') {
        return { verdict: 'refused', status: 'refused', address, reason,
            refusals: [{ address, claim: reason }], input_errors: [{ address, reason }] };
    }
    function response(body, status = 200, type = 'application/json; charset=utf-8') {
        return new Response(typeof body === 'string' ? body : JSON.stringify(body), { status, headers: { 'Content-Type': type } });
    }
    async function json(url) {
        const r = await real(url, { cache: 'no-store' });
        if (!r.ok) throw Error('Required publication input is unavailable: ' + new URL(url, location.href).pathname);
        return r.json();
    }
    async function read() {
        const [receivedPlan, snapshotReply] = await Promise.all([json(new URL('read-plan.json', root)), real(snapshotsURL, {cache:'no-store'})]);
        if (!snapshotReply.ok) throw Error('The publication responses are unavailable.');
        const snapshotText = await snapshotReply.text(), snapshot = JSON.parse(snapshotText), plan = receivedPlan;
        if (plan.plan_id !== declaredPlan || snapshot.plan_id !== declaredPlan)
            throw Error('The source plan changed. Reload this publication.');
        if (!globalThis.crypto?.subtle) throw Error('SHA-256 delivery checks need Web Crypto. Open this publication over HTTPS or localhost.');
        const responseHash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(snapshotText)))].map(n=>n.toString(16).padStart(2,'0')).join('');
        const responsePath = decodeURIComponent(snapshotsURL.pathname.slice(root.pathname.length));
        if (plan.response_sha256[responsePath] !== responseHash) throw Error('Publication responses differ from their SHA-256.');
        await Promise.all(Object.entries(plan.resources).map(async ([path, want]) => {
            const r = await real(new URL(path, root), { cache: 'no-store' });
            if (!r.ok) throw Error('Required publication input is unavailable: ' + path);
            const bytes = await r.arrayBuffer();
            const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(n => n.toString(16).padStart(2, '0')).join('');
            if (hash !== want) throw Error('Publication bytes differ from their SHA-256: ' + path);
        }));
        return {plan, snapshots: snapshot.responses};
    }
    function key(url, method) {
        const u = new URL(String(url), location.href);
        const path = u.pathname;
        if (['/world', '/verdict', '/gitstatus'].includes(path)) return method + ' ' + path + '?f=' + encodeURIComponent(u.searchParams.get('f') || '');
        if (path === '/language' && u.searchParams.has('f')) return method + ' /language?f=' + encodeURIComponent(u.searchParams.get('f'));
        if (path === '/shelf' && u.searchParams.has('m')) return method + ' /shelf?m=' + encodeURIComponent(u.searchParams.get('m'));
        return method + ' ' + path;
    }
    function item(path, method = 'GET') { return snapshots[key(path, method)]; }
    function object(path) { return JSON.parse(item(path)?.body || '{}'); }
    function source(file) { return item('/world?f=' + encodeURIComponent(file))?.body || ''; }
    function install(received) {
        if (plan === received.plan) return;
        plan = received.plan; snapshots = received.snapshots;
        const files = object('/files'), world = plan.worlds.find(w => 'snapshots/' + w.id + '.json'
            === decodeURIComponent(snapshotsURL.pathname.slice(root.pathname.length)));
        if (!world) throw Error('The snapshot has no declared world.');
        const writable = new Set(files.capabilities?.write || []);
        draftPrefix = GateReaderDraft.namespace(plan.publication.id, world.id, plan.plan_id);
        drafts = GateReaderDraft.open({storage: {
            getItem: key => localStorage.getItem(key), setItem: (key, value) => localStorage.setItem(key, value),
            removeItem: key => localStorage.removeItem(key)},
            prefix: draftPrefix,
            inputsDigest: plan.inputs_digest, compact: true, base: source,
            allowed: file => plan.draft_policy === 'ReaderDraft' && writable.has(file)});
    }
    function draftTexts(file, text) {
        const files = object('/files');
        return Object.fromEntries(files.files.filter(f => f !== files.layout && !files.carried.includes(f))
            .map(f => [f, f === file ? text : drafts.text(f)]));
    }
    async function reading(file, text) {
        const files = object('/files');
        if (file === files.layout || files.carried.includes(file))
            return JSON.parse(item('/verdict?f=' + encodeURIComponent(file), 'POST').body);
        const texts = draftTexts(file, text);
        const inputs = JSON.stringify(texts), previous = readings.get(file);
        if (previous?.inputs === inputs) return previous.answer;
        // The delivered answer belongs to these exact bytes. Edits, including
        // restored drafts, go through the existing ports and never inherit it.
        if (Object.entries(texts).every(([f, value]) => value === source(f)))
            return JSON.parse(item('/verdict?f=' + encodeURIComponent(file), 'POST').body);
        if (!court) {
            wasm_bindgen.initSync({module: Uint8Array.from(atob(VI_COURT_WASM_BASE64), c => c.charCodeAt(0))});
            court = wasm_bindgen;
        }
        const language = object('/grammar-contexts');
        const contextual = new Set((language.contexts || []).flatMap(c => c.court
            ? c.court.sources.filter(s => s.role === 'own').map(s => s.input) : []));
        const groups = files.worlds.map(group => group.filter(f => !contextual.has(f))).filter(group => group.length);
        const answer = GateWorldCourt.verdict(court, groups, texts, [], files.world_files.filter(f => !contextual.has(f)),
            files.carried, files.layout, judge, null, null, files.documents);
        const unprepared = Object.entries(texts).filter(([f, value]) => !contextual.has(f)
            && value !== source(f) && (files.forms.includes(f) || files.documents.includes(f)));
        if (unprepared.length) {
            function notationFor(parts) {
                const requested = parts.map(([name])=>name);
                const notation = JSON.parse(court.source_notation(JSON.stringify({
                    files:parts.map(([name, text])=>({name, text})), questions:requested})));
                const reported = notation.sources?.map(unit=>unit.input);
                if (notation.schema !== 'vi.court.notation/1' || !Array.isArray(notation.sources)
                    || !Array.isArray(notation.diagnostics) || !notation.diagnostics.every(d=>typeof d==='string')
                    || reported.some(f=>!requested.includes(f)) || new Set(reported).size!==reported.length
                    || (reported.length!==requested.length && !notation.diagnostics.length))
                    throw Error('The source notation reader did not return a complete reading.');
                return notation;
            }
            const batch = notationFor(unprepared), units = [], located = new Set();
            // The owner can return an unlocated batch diagnostic. Ask each
            // input separately before assigning it a source address.
            if (batch.diagnostics.length) {
                for (const part of unprepared) {
                    const single = notationFor([part]); units.push(...single.sources);
                    for (const diagnostic of single.diagnostics) {
                        located.add(diagnostic);
                        answer.unsupported.push({id:part[0], address:part[0]+':1', reason:'source notation: '+diagnostic});
                    }
                }
                for (const diagnostic of batch.diagnostics) if (!located.has(diagnostic))
                    answer.unsupported.push({id:'source-notation', address:'read-plan.json:1',
                        reason:'source notation batch: '+diagnostic});
            } else units.push(...batch.sources);
            for (const unit of units) {
                for (const imported of unit.imports) answer.unsupported.push({id:unit.input,
                    address:unit.input + ':' + imported.line, reason:'import ' + imported.module + ' needs a declared Language context'});
                for (const question of unit.questions) answer.unsupported.push({id:unit.input,
                    address:unit.input + ':1', reason:'count needs a declared definition context'});
            }
        }
        if (contextual.size) {
            const read = await GateCourtContexts.read(court, language, texts);
            answer.checked += read.checked;
            answer.refusals.push(...read.refusals); answer.unsupported.push(...read.unsupported);
            answer.unchecked = read.unchecked; answer.court_readings = read.court_readings;
        }
        answer.verdict = answer.refusals.length ? 'refused' : answer.unsupported.length
            ? (answer.checked ? 'partial' : 'unsupported') : (answer.checked ? 'holds' : 'empty');
        answer.compiler = 'page bodies have not been checked by Swift';
        answer.coverage_scope = 'declared relations; Swift bodies are unchecked';
        readings.set(file, {inputs, answer});
        return answer;
    }
    window.__resetWipe = () => { if (drafts) drafts.reset(object('/files').files); };
    window.__resetCopy = () => { window.__resetWipe(); location.reload(); };
    document.addEventListener('click', event => {
        if (!event.target.closest('#reset-copy')) return;
        event.preventDefault(); window.__resetCopy();
    });
    window.fetch = async (url, options = {}) => {
        const method = (options.method || 'GET').toUpperCase();
        const u = new URL(String(url), location.href);
        if (!['/files', '/world', '/verdict', '/gitstatus', '/status', '/shelf', '/version', '/language', '/attention', '/log', '/drawing-profile', '/grammar-contexts', '/value', '/declare'].includes(u.pathname))
            return real(url, options);
        try {
            if (!held || live) held = read();
            install(await held);
            const file = u.searchParams.get('f') || '', files = object('/files');
            const readerDraft = plan.draft_policy === 'ReaderDraft';
            if (method === 'PUT' && u.pathname === '/world' && readerDraft
                && files.capabilities.write.includes(file)) {
                const text = String(options.body || ''), answer = await reading(file, text);
                let saved;
                try { saved = await drafts.save(file, text, answer, draftTexts(file, text)); }
                catch (error) { return response(failure('Reader draft not saved: ' + error.message, file + ':1'), 507); }
                return response({saved: 'reader-draft', file, verdict: answer.verdict, inputs_digest: saved.inputs_digest});
            }
            if (method !== 'GET' && !(method === 'POST' && u.pathname === '/verdict'))
                return response({...failure('This plan grants no source write here. Change the source repository and publish again.',
                    (file || method + ' ' + u.pathname) + ':1'), code:'read-only-structure'}, 409);
            if (method === 'POST') {
                if (!item('/world' + u.search)) return response(failure('No declared input.', file + ':1'), 404);
                const text = String(options.body || '');
                if (text !== source(file) && (!readerDraft || !files.capabilities.write.includes(file))) {
                    const delivered = JSON.parse(item(url, method).body);
                    return response({...delivered, verdict:delivered.refusals?.length ? 'refused' : 'unsupported',
                        unsupported:[...(delivered.unsupported || []), {id:'read-only', address:file + ':1',
                            reason:'This edit has not been read: the plan grants reading here. Change the source repository and publish again.'}]}, 409);
                }
                if (!readerDraft) { const recorded = item(url, method); return response(recorded.body, 200, recorded.type); }
                return response(await reading(file, text));
            }
            if (u.pathname === '/files') return response({...files, reader_draft_namespace: readerDraft ? draftPrefix : null});
            if (readerDraft && u.pathname === '/world' && item('/world' + u.search))
                return response(drafts.text(file), 200, 'text/plain; charset=utf-8');
            if (u.pathname === '/gitstatus' && drafts.kept(file))
                return response({file, git:'draft', verdict:'read again on open'});
            if (readerDraft && u.pathname === '/status') {
                const shown = files.files.find(f => f !== files.layout && !files.carried.includes(f));
                return response(await reading(shown, drafts.text(shown)));
            }
            const found = item(url, method);
            if (found && u.pathname === '/drawing-profile') {
                const drawing = JSON.parse(found.body);
                if (drawing.asset_urls) drawing.asset_urls = Object.fromEntries(Object.entries(drawing.asset_urls)
                    .map(([hash, path]) => [hash, new URL(path, root).href]));
                return response(drawing, 200, found.type);
            }
            return found ? response(found.body, 200, found.type) : response(failure('This request has no declared publication reader.'), 404);
        } catch (error) { return response(failure(error.message), 409); }
    };
})();
