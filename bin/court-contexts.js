/* Transport of the owner's per-source Court response. Parsing and judgement
   stay in the same wasm owner port, including imports after a source edit. */
'use strict';
(function(root) {
    const crypto = root.crypto || (typeof require === 'function' ? require('crypto').webcrypto : null);
    const canonical = value => JSON.stringify(order(value));
    function order(value) {
        if (Array.isArray(value)) return value.map(order);
        if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(k=>[k,order(value[k])]));
        return value;
    }
    async function sha(text) {
        if (!crypto?.subtle) throw Error('SHA-256 is unavailable');
        return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))].map(x=>x.toString(16).padStart(2,'0')).join('');
    }
    async function bound(request, answer) {
        if (answer.stderr !== '' || !Number.isInteger(answer.exit)) throw Error('court response has no canonical streams');
        const report = JSON.parse(answer.stdout), question = request.arguments[0];
        const keys=(value,wanted)=>value && typeof value==='object' && !Array.isArray(value)
            && canonical(Object.keys(value).sort())===canonical(wanted.sort());
        const strings=value=>Array.isArray(value)&&value.every(v=>typeof v==='string');
        if(!keys(report,['schema','question','inputs','outcome','results','diagnostics']))throw Error('invalid source report fields');
        if (report.schema !== 'vi.court.sources/1' || report.question !== question) throw Error('court response has another question');
        const wanted = await Promise.all(request.files.map(async f=>({path:f.name,sha256:await sha(f.text)})));
        wanted.sort((a,b)=>a.path<b.path?-1:a.path>b.path?1:0);
        if (canonical(report.inputs)!==canonical(wanted)) throw Error('court input hashes differ from the complete request');
        const contextFile=request.arguments[request.arguments.indexOf('--context')+1];
        const context=JSON.parse(request.files.find(f=>f.name===contextFile).text);
        const selected=context.sources.filter(s=>question==='count'||s.role==='own');
        const states=['holds','empty','refused','not-established','unsupported'];
        if(!states.includes(report.outcome)||!Array.isArray(report.results)||!strings(report.diagnostics))throw Error('invalid source coverage');
        const exit=report.outcome==='holds'?0:['refused','not-established'].includes(report.outcome)?1:2;
        if(answer.exit!==exit)throw Error('court outcome and exit differ');
        if(report.results.length===0&&report.diagnostics.length) {
            if(report.outcome!=='unsupported')throw Error('an admission error cannot hold');
            return report;
        }
        const paths=selected.map(s=>s.input).sort();
        if(canonical(report.results.map(r=>r.path))!==canonical(paths))throw Error('court omitted or repeated a source');
        let total=0;
        for(const r of report.results) {
            if(!keys(r,['path','source','outcome','equalities','memberships','readings','unchecked','diagnostics'])
                ||r.source!==selected.find(s=>s.input===r.path).source||!states.includes(r.outcome)||!strings(r.unchecked)||!strings(r.diagnostics))throw Error('invalid source result');
            const values=[r.equalities,r.memberships,r.readings];
            if(values.some(n=>!Number.isSafeInteger(n)||n<0))throw Error('invalid checked count');
            const n=values.reduce((a,b)=>a+b,0);total+=n;
            if(!Number.isSafeInteger(n)||!Number.isSafeInteger(total))throw Error('checked count is outside the portable integer range');
            if((r.outcome==='holds'&&n===0)||(r.outcome==='empty'&&n!==0))throw Error('zero checked cannot hold');
            if(['refused','not-established','unsupported'].includes(r.outcome)&&!r.diagnostics.length)throw Error('negative result has no addressed reason');
        }
        const aggregate=['unsupported','refused','not-established','holds'].find(s=>report.results.some(r=>r.outcome===s))||'empty';
        if(aggregate!==report.outcome||report.diagnostics.length)throw Error('court aggregate differs from its source results');
        return report;
    }
    // A changed source is read once by the owner port. Both imports and the
    // question selectors are replaced from these bytes, never from the old plan.
    async function requests(court, context, texts, policy, grammar) {
        const originals=context.requests||[];
        if(!originals.length)return {requests:[],refusals:[]};
        const base=JSON.parse(JSON.stringify(originals[0]));
        const contextFile=base.arguments[base.arguments.indexOf('--context')+1];
        const input=base.files.find(f=>f.name===contextFile),declared=JSON.parse(input.text);
        const sources=base.files.filter(f=>f!==input),changed=[];
        for(const file of sources)if(Object.hasOwn(texts,file.name)&&file.text!==texts[file.name]) {
            file.text=texts[file.name];changed.push(file);
        }
        if(!changed.length)return {requests:originals,refusals:[]};
        if(!policy||!grammar)throw Error('the declared grammar policy is unavailable');
        const refusals=[];
        for(const file of changed) {
            const unit=context.inputs.find(u=>u.path===file.name);
            if(!unit)throw Error('changed input has no declared scope: '+file.name);
            for(const found of grammar.findings(file.text,unit.scope,policy))
                refusals.push({address:file.name+':'+found.line,claim:'grammar: '+found.atom+' is not granted '+found.scope+'/'+found.context});
        }
        if(refusals.length)return {requests:[],refusals};
        const own=declared.sources.filter(s=>s.role==='own').map(s=>s.input);
        const notation=JSON.parse(await court.source_notation(JSON.stringify({files:sources,questions:own})));
        if(notation.schema!=='vi.court.notation/1'||!Array.isArray(notation.diagnostics)||notation.diagnostics.length)
            throw Error((notation.diagnostics||['cannot read notation']).join('; '));
        if(canonical(notation.sources.map(s=>s.input).sort())!==canonical(sources.map(s=>s.name).sort()))throw Error('notation omitted or repeated a source');
        for(const source of declared.sources) {
            const file=sources.find(f=>f.name===source.input),read=notation.sources.find(s=>s.input===source.input);
            source.sha256=await sha(file.text);
            if(read.sha256!==source.sha256)throw Error('notation input hash differs');
            if(!Array.isArray(read.imports)||!Array.isArray(read.questions))throw Error('notation has no imports or question selectors');
            for(const item of read.imports)if(!context.imports.includes(item.module))throw Error(source.source+':'+item.line+': import '+item.module+' is not declared by Language');
            source.imports=read.imports.map(i=>i.module);
            source.at.imports=read.imports.map(i=>source.source+':'+i.line);
        }
        input.text=canonical(declared);
        const args=base.arguments.slice();
        for(const flag of ['--predicate','--encoding','--sigma']) {
            const index=args.indexOf(flag);if(index>=0)args.splice(index,2);
        }
        const fresh=[];
        if(own.length)fresh.push({...base,arguments:['where',...args.slice(1)]});
        const seen=new Set();
        // Match the owner's order: input order, then declaration order within
        // that input. Every question still reads all original named sources.
        for(const unit of context.inputs) {
            if(!own.includes(unit.path))continue;
            for(const q of notation.sources.find(s=>s.input===unit.path).questions) {
                if(['predicate','encoding','sigma'].some(k=>typeof q[k]!=='string'||!q[k]))throw Error('invalid count question selector');
                const key=canonical(q);if(seen.has(key))continue;seen.add(key);
                fresh.push({...base,arguments:['count',...args.slice(1),'--predicate',q.predicate,'--encoding',q.encoding,'--sigma',q.sigma]});
            }
        }
        return {requests:fresh,refusals};
    }
    const cache=new Map();
    async function read(court, plan, texts) {
        const reports=[],refusals=[],unsupported=[],unchecked=[];
        let checked=0;
        const changed=new Set();
        for(const context of plan.contexts||[])for(const request of context.requests||[])
            for(const file of request.files)if(Object.hasOwn(texts,file.name)&&texts[file.name]!==file.text)changed.add(file.name);
        // Only a re-read of this source can retire its previous refusal.
        // Record/pin/scope errors and errors of unchanged inputs survive edits
        // elsewhere, even when Court excludes a document's executable body.
        const stillApplies=row=>![...changed].some(path=>row.address?.startsWith(path+':'));
        refusals.push(...(plan.refusals||[]).filter(stillApplies));
        unsupported.push(...(plan.unsupported||[]).filter(stillApplies));
        const grammar = root.GateGrammarPolicy || (typeof require === 'function' ? require('./grammar-policy.js') : null);
        let policy,policyError;
        try {
            if (plan.policy) {
                if (await sha(plan.policy) !== plan.policy_sha256) throw Error('grammar policy hash differs');
                policy=JSON.parse(plan.policy);
            }
        } catch(error) {policyError=error;}
        for(const context of plan.contexts||[]) {
            if(!context.court)continue;
            const at=(context.inputs[0]?.path||'gate.manifest.swift')+':1';
            try {
                if(policyError)throw policyError;
                const prepared=await requests(court,context,texts,policy,grammar);
                refusals.push(...prepared.refusals);
                for(const request of prepared.requests) {
                    const hash=await sha(canonical(request));
                    const receipt=(context.receipts||[]).find(r=>r.request_sha256===hash);
                    let promise;
                    if(receipt) {
                        if(receipt.schema!=='gate.court.receipt/1'||!receipt.origin)throw Error('court receipt has no pinned origin');
                        promise=bound(request,receipt.response);
                    } else {
                        promise=cache.get(hash);
                        if(!promise) {
                            promise=Promise.resolve(court.judge(JSON.stringify({arguments:request.arguments,files:request.files}))).then(raw=>bound(request,JSON.parse(raw)));
                            cache.set(hash,promise);
                        }
                    }
                    const report=await promise;reports.push(report);
                    for(const reason of report.diagnostics)unsupported.push({id:context.language,address:at,reason});
                    for(const row of report.results) {
                        checked+=row.equalities+row.memberships+row.readings;
                        for(const address of row.unchecked)if(!unchecked.some(r=>r.address===address))unchecked.push({address,reason:'excluded from the court reading'});
                        for(const reason of row.diagnostics) {
                            if(row.outcome==='unsupported')unsupported.push({id:row.path,address:row.path+':1',reason});
                            else if(['refused','not-established'].includes(row.outcome))refusals.push({address:row.path+':1',claim:reason});
                        }
                    }
                }
            } catch(error) {unsupported.push({id:context.language,address:at,reason:error.message});}
        }
        return {checked,refusals,unsupported,unchecked,court_readings:reports};
    }
    const api={canonical,sha,bound,requests,read};
    if(typeof module!=='undefined')module.exports=api;
    root.GateCourtContexts=api;
})(typeof globalThis!=='undefined'?globalThis:this);
