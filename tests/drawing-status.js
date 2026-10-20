// Exercise the same comparison consumer on the actual published input bytes.
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {drawingParse}=require('../bin/judge.js'),{renderAll}=require('../bin/renderer.js');
const profile=require('../bin/drawing-profile.js'),site=process.argv[2];
(async()=>{
    const results=[];
    for(const name of fs.readdirSync(path.join(site,'playground'))) {
        const dir=path.join(site,'playground',name),snapshot=path.join(dir,'snapshots.json');
        if(!fs.existsSync(snapshot))continue;
        const snap=JSON.parse(fs.readFileSync(snapshot)),world=JSON.parse(fs.readFileSync(path.join(dir,'world.json')));
        const plan=JSON.parse(snap['/drawing-profile']);
        const state=await profile.compile(plan,async hash=>new Uint8Array(fs.readFileSync(path.join(site,'assets/drawing',hash,'font.ttf'))),(h,n)=>h+'/'+n);
        const files=JSON.parse(snap['/files']).files;
        const parts=files.map(file=>({file,text:snap['/world?f='+file]}));
        const parsed=drawingParse(parts),drawn=renderAll(parsed.declarations,parsed.order,parsed.literals,parsed.topAliases);
        const declared=state.contract.cases.find(c=>c.id===world.drawing.case_id);
        if(!declared)continue;
        const actual=await profile.compare(state,parts,drawn,world.drawing);
        if(declared.status==='not-compared') {
            assert.equal(actual.status,'not-compared',name+': '+JSON.stringify(actual));
        } else {
            // /files also carries the manifest and the personal bench record.
            // Their presence must not silently inherit a native source hash.
            const hashes=await Promise.all(parts.map(p=>profile.sha(new TextEncoder().encode(p.text))));
            const ownerParts=declared.sourceSHA256.map(h=>parts[hashes.indexOf(h)]);
            assert(ownerParts.every(Boolean),name+': all owner source bytes are present');
            assert.equal(drawn.canvases.find(c=>c.name===declared.root)?.svg,declared.svg,name+': actual published SVG equals native bytes');
            assert.equal((await profile.compare(state,ownerParts,drawn)).status,'compared',name+': exact owner input and actual output');
            assert(parts.length>ownerParts.length,name+': publication includes additional product records');
            assert.equal(actual.status,'port-under-contract',name+': extra inputs do not gain exact-case evidence');
        }
        const edited=parts.map((p,i)=>({...p,text:p.text+(i===0?'\n// browser edit':'')}));
        assert.equal((await profile.compare(state,edited,drawn,world.drawing)).status,'port-under-contract',name+' edit');
        results.push({world:name,status:actual.status,case_id:actual.case_id,inputs_digest:actual.inputs_digest});
    }
    assert.equal(results.filter(r=>r.status==='port-under-contract').length,9);
    assert.equal(results.filter(r=>r.status==='not-compared').length,1);
    console.log(JSON.stringify(results,null,2));
    console.log('DRAWING STATUS GREEN: 9 published SVGs equal native bytes; exact owner inputs compare; additional product records remain port-under-contract; bound At scale remainder; edits lose exact comparison');
})().catch(e=>{console.error(e);process.exitCode=1;});
