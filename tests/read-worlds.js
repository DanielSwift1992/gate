'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const source=fs.readFileSync(__dirname+'/../web/ui.html','utf8');
const start=source.indexOf('async function readWorlds(');
const code=source.slice(start,source.indexOf('\n}',start)+2);
(async()=>{
 let requests=0,body='verified first',refused=false;
 const context=vm.createContext({batchReadings:true,fetch:async(url,options)=>{
  requests++;assert.equal(url,'/world');const names=JSON.parse(options.body);
  return {ok:true,json:async()=>Object.fromEntries(names.map(n=>[n,{status:refused?409:200,text:body}]))};
 }});
 vm.runInContext(code,context);
 const first=await context.readWorlds(['Forms.swift','Now.swift']);
 assert.equal(requests,1);assert.equal(first.get('Now.swift').text,'verified first');
 // Startup can consume its operation's owned text more than once.
 assert.equal(first.get('Now.swift').text,'verified first');assert.equal(requests,1);
 body='addressed refusal';refused=true;
 const second=await context.readWorlds(['Forms.swift','Now.swift']);
 assert.equal(requests,2);assert(!second.get('Now.swift').ok);assert.equal(second.get('Now.swift').text,body);
 context.batchReadings=false;context.fetch=async url=>({ok:true,status:200,text:async()=>url});
 const legacy=await context.readWorlds(['a b.swift']);assert.equal(legacy.get('a b.swift').text,'/world?f=a%20b.swift');
 context.batchReadings=true;context.fetch=async()=>({ok:true,json:async()=>({})});
 await assert.rejects(context.readWorlds(['absent']),/Missing reading/);
 console.log('WORLD READINGS GREEN: one batch per operation, owned texts, fresh refusal and static fallback');
})().catch(e=>{console.error(e);process.exitCode=1;});
