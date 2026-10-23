'use strict';
const assert=require('assert'),fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const scope={crypto:crypto.webcrypto,TextEncoder,Uint8Array};vm.runInNewContext(fs.readFileSync((process.argv[2] || require('path').join(__dirname,'../web/reader-draft.js')),'utf8'),scope);
(async()=>{
const D=scope.GateReaderDraft, held=new Map(), hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const storage={getItem:k=>held.get(k)??null,setItem:(k,v)=>held.set(k,v),removeItem:k=>held.delete(k)};
const prefix=D.namespace('pub','world','plan'),file='Main.swift',base='// x\n'.repeat(70000),digest=hash(base);
const make=(b=base,extra={})=>D.open({storage,prefix,inputsDigest:hash(b),base:()=>b,allowed:f=>f===file,compact:true,...extra});
const fake={verdict:'holds',inputs_digest:'forged'}, original=make();
assert.notEqual(prefix,D.namespace('other','world','plan'));assert.notEqual(prefix,D.namespace('pub','other','plan'));assert.notEqual(prefix,D.namespace('pub','world','other'));
assert.notEqual(D.namespace('a/b','c','d'),D.namespace('a','b/c','d'));
assert.throws(()=>D.namespace('','world','plan'));
await original.save(file,base+'// one\n',fake);await original.save(file,base+'// one\n// two\n',fake);
assert.equal(JSON.parse(held.get(prefix+file)).format,2);assert.equal(make().text(file),base+'// one\n// two\n');
assert.equal(make().kept(file).verdict,null,'a saved answer must not be replayed');
// Each envelope format must discard its stored answer. A length check
// independently rejects a damaged envelope even with a matching digest.
for (const format of [1,2]) {
 const row={format,base_inputs_digest:digest,base_length:base.length,verdict:fake,
  ...(format===1?{text:base+'// draft\n'}:{splices:[{from:0,to:0,insert:'// draft\n'}]})};
 held.set(prefix+file,JSON.stringify(row));
 assert.equal(make().kept(file).verdict,null,'format '+format+' replayed a saved verdict');
 row.base_length++;
 held.set(prefix+file,JSON.stringify(row));
 assert.equal(make().text(file),base,'format '+format+' ignored base_length');
}
held.delete(prefix+file);
await original.save(file,base+'// foreign base control\n',fake);
assert.equal(make().text(file),base+'// foreign base control\n','the digest control needs a valid retained edit');
const changed=base.replaceAll('x','z');assert.equal(make(changed).text(file),changed,'same-length foreign base');
for(const raw of ['{"format":2,','{"format":17}', 'null','"raw source"','123','[]']){
 held.set(prefix+file,raw);assert.equal(make().text(file),base,'damaged envelope is not Swift');
}
for(const splices of ['bad',[{from:-1,to:0,insert:'x'}],[{from:1.5,to:2,insert:'x'}],
 [{from:3,to:2,insert:'x'}],[{from:0,to:base.length+1,insert:'x'}],
 [{from:0,to:base.length,insert:''},{from:1,to:1,insert:'x'}]]){
 held.set(prefix+file,JSON.stringify({format:2,base_inputs_digest:digest,splices}));assert.equal(make().text(file),base);
}
held.delete(prefix+file);const old='old-scoped.';held.set(old+file,JSON.stringify({format:2,splices:[{from:0,to:0,insert:'// old\n'}],verdict:fake}));
const prior={prefix:old,format:'records',baseInputsDigest:digest}, migrated=make(base,{legacy:[prior]});
const before=JSON.stringify([...held]);assert.equal(migrated.text(file),'// old\n'+base);assert.equal(migrated.kept(file).verdict,null);assert.equal(JSON.stringify([...held]),before,'GET migration wrote storage');
assert.equal(make(changed,{legacy:[prior]}).text(file),changed,'unbound legacy origin');
held.set(prefix+file,'{broken');assert.equal(migrated.text(file),base,'damage must not resurrect an older edit');held.delete(prefix+file);
held.set(old+file,'public enum Recovered {}');assert.equal(make(base,{legacy:[{...prior,format:'raw'}]}).text(file),'public enum Recovered {}');
assert.equal(migrated.text(file),base,'damaged record protocol became raw text');
held.set('gate.pages.'+file,'ambiguous unscoped text');assert.equal(make().text(file),base);
held.set(D.namespace('pub','world','other')+file,'other plan');migrated.reset([file]);assert.equal(held.get(D.namespace('pub','world','other')+file),'other plan');assert.equal(held.get('gate.pages.'+file),'ambiguous unscoped text');
await assert.rejects(()=>make().save('Owner.swift','bad',fake));await assert.rejects(()=>make().save(file,{},fake));
const snapshot=JSON.stringify([...held]);await assert.rejects(()=>make(base,{storage:{...storage,setItem(){throw Error('quota');}}}).save(file,'edit',fake));assert.equal(JSON.stringify([...held]),snapshot);
const a=await D.inputsDigest(digest,{[file]:base}),b=await D.inputsDigest(digest,{[file]:changed});assert.notEqual(a,b);assert.equal(await D.inputsDigest(digest,{B:'b',A:'a'}),await D.inputsDigest(digest,{A:'a',B:'b'}),'input order changes identity');if (!process.argv[2]) {
 const os=require('os'),path=require('path'),{spawnSync}=require('child_process');
 const source=fs.readFileSync(path.join(__dirname,'../web/reader-draft.js'),'utf8');
 const mutations=[
  ['format1-verdict','{text: row.text, verdict: null}','{text: row.text, verdict: row.verdict}','format 1 replayed'],
  ['format2-verdict','{text, verdict: null, splices: row.splices}','{text, verdict: row.verdict, splices: row.splices}','a saved answer must not be replayed'],
  ['base-length','if (row.base_length !== undefined && row.base_length !== original.length) return null;','','ignored base_length'],
  ['base-digest',`if (row.base_inputs_digest !== baseInputsDigest
                && !(prior && row.base_inputs_digest === undefined)) return null;`,'','same-length foreign base']];
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'gate-draft-mutations-'));
 try {
  for(const [name,before,after,diagnostic] of mutations) {
   assert(source.includes(before),name+' mutation has no target');
   const file=path.join(folder,name+'.js');fs.writeFileSync(file,source.replace(before,after));
   const result=spawnSync(process.execPath,[__filename,file],{encoding:'utf8'});
   assert.notEqual(result.status,0,name+' survived');
   assert(result.stderr.includes(diagnostic),name+' failed for a different reason: '+result.stderr);
  }
 } finally {fs.rmSync(folder,{recursive:true,force:true});}
 console.log('DRAFT MUTATIONS GREEN: format 1, format 2, base_length and base digest');
}
console.log('DRAFT CORE GREEN: namespace, base, recovery, malformed records, no stale verdict, quota and reset');})().catch(e=>{console.error(e);process.exitCode=1});
