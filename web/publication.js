/* The publication transports one native ReadPlan and its response bytes.
   This delivery grants reading. It grants no edits or old browser drafts. */
(() => {
    'use strict';
    const script = document.currentScript;
    const real = window.fetch.bind(window);
    const snapshotsURL = new URL(script.dataset.replies, location.href);
    const root = new URL('../', snapshotsURL);
    const declaredPlan = script.dataset.plan;
    const live = script.dataset.live === 'true';
    window.GatePublication = Object.freeze({ readOnly: true, plan_id: declaredPlan });
    let held;
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
        const [plan, snapshotReply] = await Promise.all([json(new URL('read-plan.json', root)), real(snapshotsURL, {cache:'no-store'})]);
        if (!snapshotReply.ok) throw Error('The publication responses are unavailable.');
        const snapshotText = await snapshotReply.text(), snapshot = JSON.parse(snapshotText);
        if (plan.plan_id !== declaredPlan || snapshot.plan_id !== declaredPlan)
            throw Error('The source plan changed. Reload this read-only publication.');
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
        return snapshot.responses;
    }
    function key(url, method) {
        const u = new URL(String(url), location.href);
        const path = u.pathname;
        if (['/world', '/verdict', '/gitstatus'].includes(path)) return method + ' ' + path + '?f=' + encodeURIComponent(u.searchParams.get('f') || '');
        if (path === '/language' && u.searchParams.has('f')) return method + ' /language?f=' + encodeURIComponent(u.searchParams.get('f'));
        if (path === '/shelf' && u.searchParams.has('m')) return method + ' /shelf?m=' + encodeURIComponent(u.searchParams.get('m'));
        return method + ' ' + path;
    }
    window.fetch = async (url, options = {}) => {
        const method = (options.method || 'GET').toUpperCase();
        // Browser requests for installed assets remain ordinary HTTP requests.
        const u = new URL(String(url), location.href);
        if (!['/files', '/world', '/verdict', '/gitstatus', '/status', '/shelf', '/version', '/language', '/attention', '/log', '/drawing-profile', '/value', '/declare'].includes(u.pathname))
            return real(url, options);
        if (method !== 'GET' && !(method === 'POST' && u.pathname === '/verdict'))
            return response({ ...failure('Read-only publication. Change the source repository and publish again.'), code: 'read-only-structure' }, 409);
        try {
            if (!held || live) held = read();
            const snapshots = await held;
            if (method === 'POST') {
                const source = snapshots[key('/world' + u.search, 'GET')];
                if (!source || String(options.body || '') !== source.body)
                    return response({ verdict: 'unsupported', unsupported: [{ id: 'read-only', address: (u.searchParams.get('f') || 'world') + ':1', reason: 'This plan grants reading. Reopen the source repository to change it.' }], refusals: [] }, 409);
            }
            const item = snapshots[key(url, method)];
            return item ? response(item.body, 200, item.type) : response(failure('This request has no declared publication reader.'), 404);
        } catch (e) {
            return response(failure(e.message), 409);
        }
    };
})();
