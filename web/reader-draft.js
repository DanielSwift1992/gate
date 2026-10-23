/* A browser draft carries text and a reading; reopening always reads again.
   Storage permission does not grant a write to the source repository. */
(function (root) {
    'use strict';
    function namespace(publication, world, plan) {
        const ids = [publication, world, plan];
        if (!ids.every(id => typeof id === 'string' && id.length))
            throw Error('read-plan.json:1: reader drafts need Publication, world and plan identities');
        return 'gate.publication.draft.' + ids.map(encodeURIComponent).join('/') + '/';
    }
    async function inputsDigest(base, texts) {
        if (!root.crypto?.subtle)
            throw Error('saving a reader draft needs Web Crypto; use HTTPS or localhost; reading remains available');
        const ordered = Object.fromEntries(Object.keys(texts).sort().map(file => [file, texts[file]]));
        const bytes = new TextEncoder().encode(JSON.stringify({base_inputs_digest: base, texts: ordered}));
        const hash = await crypto.subtle.digest('SHA-256', bytes);
        return [...new Uint8Array(hash)].map(n => n.toString(16).padStart(2, '0')).join('');
    }
    function open(options) {
        const {storage, prefix, base, allowed, compact, inputsDigest: baseInputsDigest} = options;
        if (typeof prefix !== 'string' || !prefix || !/^[a-f0-9]{64}$/.test(baseInputsDigest))
            throw Error('read-plan.json:1: reader drafts need a namespace and a base inputs digest');
        const legacy = (options.legacy || []).filter(prior => prior
            && prior.baseInputsDigest === baseInputsDigest && typeof prior.prefix === 'string' && prior.prefix
            && ['raw', 'records'].includes(prior.format));
        function decoded(raw, file, prior = null) {
            // Only an explicitly bound raw protocol is text. Invalid JSON in
            // the current record protocol is damage, not a Swift source file.
            if (prior?.format === 'raw') return {text: raw, verdict: null};
            let row;
            try { row = JSON.parse(raw); } catch (_) { return null; }
            if (!row || (row.format !== 1 && row.format !== 2)) return null;
            if (row.base_inputs_digest !== baseInputsDigest
                && !(prior && row.base_inputs_digest === undefined)) return null;
            const original = base(file);
            if (row.base_length !== undefined && row.base_length !== original.length) return null;
            if (row.format === 1)
                return typeof row.text === 'string' ? {text: row.text, verdict: null} : null;
            if (!compact || !Array.isArray(row.splices)) return null;
            let text = original;
            for (const cut of row.splices) {
                if (!cut || !Number.isInteger(cut.from) || !Number.isInteger(cut.to)
                    || cut.from < 0 || cut.to < cut.from || cut.to > text.length
                    || typeof cut.insert !== 'string') return null;
                text = text.slice(0, cut.from) + cut.insert + text.slice(cut.to);
            }
            return {text, verdict: null, splices: row.splices};
        }
        function kept(file) {
            if (!allowed(file)) return null;
            try {
                const raw = storage.getItem(prefix + file);
                // A damaged current record never falls through to an old edit.
                if (raw !== null) return decoded(raw, file);
                for (const prior of legacy) {
                    const old = storage.getItem(prior.prefix + file);
                    if (old !== null) return decoded(old, file, prior);
                }
                return null;
            } catch (_) { return null; }
        }
        function record(file, text, verdict) {
            if (typeof text !== 'string') throw Error(file + ':1: a reader draft must be text');
            const original = base(file), metadata = {base_inputs_digest: baseInputsDigest,
                base_length: original.length, inputs_digest: verdict?.inputs_digest};
            if (!compact || original.length < 300000) return {format: 1, text, verdict, ...metadata};
            function splice(before, after) {
                let from = 0, tail = 0;
                while (from < before.length && from < after.length && before[from] === after[from]) from++;
                while (tail < before.length - from && tail < after.length - from
                    && before[before.length - 1 - tail] === after[after.length - 1 - tail]) tail++;
                return {from, to: before.length - tail, insert: after.slice(from, after.length - tail)};
            }
            const direct = [splice(original, text)], previous = kept(file);
            const chain = previous?.splices ? [...previous.splices, splice(previous.text, text)] : direct;
            return {format: 2, splices: JSON.stringify(chain).length < JSON.stringify(direct).length ? chain : direct,
                verdict, ...metadata};
        }
        return {kept, record, text(file) { return kept(file)?.text ?? base(file); },
            async save(file, text, verdict, texts = {[file]: text}) {
                if (!allowed(file)) throw Error(file + ':1: this plan does not grant a reader draft');
                const saved = {...verdict, inputs_digest: await inputsDigest(baseInputsDigest, texts)};
                storage.setItem(prefix + file, JSON.stringify(record(file, text, saved)));
                return saved;
            },
            reset(files) { for (const file of files) {
                storage.removeItem(prefix + file);
                for (const prior of legacy) storage.removeItem(prior.prefix + file);
            } }};
    }
    root.GateReaderDraft = Object.freeze({open, namespace, inputsDigest});
})(typeof window !== 'undefined' ? window : globalThis);
