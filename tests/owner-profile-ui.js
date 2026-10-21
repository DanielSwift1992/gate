// A stale published palette cannot borrow the live port or keep its old receipt.
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const profile=require('../bin/drawing-profile.js');
const ui=fs.readFileSync(require('path').join(__dirname,'../web/ui.html'),'utf8');
const source=ui.slice(ui.indexOf('let drawingProfileState ='),ui.indexOf('\nfunction drawable('));
(async()=>{
    const original='the published palette',changed='a reader changed the palette';
    let posts=0,compiles=0,allowed=false;
    const context={TextEncoder,console,GateDrawingProfile:{sha:profile.sha,compile:async()=>{compiles++;return {status:'ready'};}},
        document:{querySelector:()=>true,getElementById:()=>null},
        fetch:async(path,options)=>{
            if(options?.method==='POST')posts++;
            return {json:async()=>({port_allowed:allowed,palette_row:'Paint',inputs:{Paint:{path:'Paints.swift',sha256:await profile.sha(new TextEncoder().encode(original))}}})};
        }};
    vm.createContext(context);vm.runInContext(source,context);
    await context.loadDrawingProfile({path:'Paints.swift',text:original});
    assert.equal(vm.runInContext('drawingProfileState.status',context),'ready');
    await context.loadDrawingProfile({path:'Paints.swift',text:changed});
    const refused=vm.runInContext('drawingProfileState',context);
    assert.equal(refused.status,'unsupported');assert.match(refused.reason,/Paints.swift:1/);
    assert.equal(posts,0);assert.equal(compiles,1,'the stale published profile was recompiled');
    allowed=true;await context.loadDrawingProfile({path:'Paints.swift',text:changed});
    assert.equal(posts,1,'the live MINE overlay did not reach its own endpoint');
    console.log('PROFILE UI GREEN: stale publication stopped; only a live MINE palette asks the port');
})().catch(e=>{console.error(e);process.exit(1);});
