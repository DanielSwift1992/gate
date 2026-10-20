'use strict';
const assert=require('assert'),fs=require('fs'),path=require('path'),vm=require('vm'),{webcrypto}=require('crypto');
const site=process.argv[2],origin='http://fixture.test/book/';
const source=fs.readFileSync(path.join(site,'assets/publication.js'),'utf8');
async function transport(broken) {
    const files=[];
    const real=async input=>{
        const u=new URL(String(input),origin),relative=decodeURIComponent(u.pathname.slice('/book/'.length));
        files.push(relative);
        if(relative===broken) return new Response('missing',{status:404});
        const name=path.join(site,relative);
        return fs.existsSync(name)?new Response(fs.readFileSync(name)):new Response('missing',{status:404});
    };
    const plan=JSON.parse(fs.readFileSync(path.join(site,'read-plan.json'),'utf8'));
    const c={URL,Response,Uint8Array,TextEncoder,crypto:webcrypto,location:{href:origin+'harbor/'},
        document:{currentScript:{dataset:{replies:'../snapshots/harbor.json',plan:plan.plan_id}}},window:{fetch:real},console};
    vm.createContext(c);vm.runInContext(source,c);
    return {fetch:c.window.fetch,plan,files};
}
(async()=>{
    const t=await transport();
    assert.equal((await (await t.fetch('/status')).json()).verdict,'holds');
    const f='Facts.swift',text=await(await t.fetch('/world?f='+encodeURIComponent(f))).text();
    assert.equal((await(await t.fetch('/verdict?f='+f,{method:'POST',body:text})).json()).verdict,'holds');
    assert.equal((await(await t.fetch('/verdict?f='+f,{method:'POST',body:text+'changed'})).json()).verdict,'unsupported');
    assert.equal((await t.fetch('/world?f=gate.manifest.swift',{method:'PUT',body:'changed'})).status,409);
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
    console.log('PUBLICATION TRANSPORT ALL GREEN: mounted root, read-only API, delivery failures and wasm');
})().catch(e=>{console.error(e);process.exitCode=1;});
