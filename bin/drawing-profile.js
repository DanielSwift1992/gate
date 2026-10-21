// Carry the owner's resolved profile. Only a live MINE palette uses the port.
// Its colour expressions belong to the installed DocumentKit port.
(function (host) {
"use strict";
const node = typeof module !== 'undefined';
const webcrypto = node ? require('node:crypto').webcrypto : crypto;
const kit = node ? require('./renderer.js') : {parseType,textOf,makeEnvironment,kitVocabulary};
const read = node ? require('./judge.js').judge : judge;
class ProfileError extends Error {
    constructor(address, message, status='refused') {super(address+': '+message);this.address=address;this.status=status;}
}
const bytes = text => new TextEncoder().encode(text);
async function sha(data) {return [...new Uint8Array(await webcrypto.subtle.digest('SHA-256',data))].map(n=>n.toString(16).padStart(2,'0')).join('');}
function fontTable(data, expected, address) {
    const v=new DataView(data.buffer,data.byteOffset,data.byteLength),u16=p=>v.getUint16(p),u32=p=>v.getUint32(p);
    const tables={};for(let i=0;i<u16(4);i++){const at=12+16*i;tables[new TextDecoder().decode(data.slice(at,at+4))]=u32(at+8);}
    if(u16(tables.head+18)!==expected.units||u16(tables['OS/2']+88)!==expected.cap)throw new ProfileError(address,'font header differs from its metrics');
    const cmap=tables.cmap;let full;
    for(let i=0;i<u16(cmap+2);i++){const at=cmap+u32(cmap+8+8*i);if(u16(at)===12)full=at;}
    if(full===undefined)throw new ProfileError(address,'font cmap is not supported','unsupported');
    const groups=[];for(let i=0;i<u32(full+12);i++){const at=full+16+12*i;groups.push([u32(at),u32(at+4),u32(at+8)]);}
    const widths=tables.hmtx,num=u16(tables.hhea+34);
    for(const [cp,advance] of expected.advances){const g=groups.find(([a,b])=>a<=cp&&cp<=b);if(!g||u16(widths+4*Math.min(g[2]+cp-g[0],num-1))!==advance)throw new ProfileError(address,'glyph '+cp+' differs from its declared advance');}
    const fvar=tables.fvar;let weight=String(u16(tables['OS/2']+4));
    if(fvar!==undefined)for(let i=0;i<u16(fvar+8);i++){
        const at=fvar+u16(fvar+4)+i*u16(fvar+10);
        if(new TextDecoder().decode(data.slice(at,at+4))==='wght')weight=v.getInt32(at+4)/65536+' '+v.getInt32(at+12)/65536;
    }
    return {weight};
}
function parsed(file) {
    // This is the shared source parser's literal door, including multiline trivia.
    return read(file.path,file.text.replace(/(typeName:\s*String\s*\{)\s*("[^"\n]*")\s*\}/g,'$1 $2 }'),kit.kitVocabulary).parsed;
}
async function compile(plan, getBytes, assetURL) {
    if(plan.status==='none')return {status:'none',reason:'Drawing without a profile',css:'',assets:[]};
    if(plan.status==='refused')throw new ProfileError(plan.address,plan.reason);
    if(plan.status==='unsupported')throw new ProfileError(plan.address,plan.reason,'unsupported');
    if(plan.status==='resolved') {
        const result=plan.resolved,at=plan.profile.path+':1';
        if(!result)throw new ProfileError(at,'owner profile delivery is missing');
        const delivered=new Map();
        for(const item of result.assets||[]) {
            const data=await getBytes(item.sha256);
            if(await sha(data)!==item.sha256)throw new ProfileError(at,'owner profile resource delivery differs: '+item.name);
            delivered.set(item.sha256,data);
        }
        const cssBytes=delivered.get(plan.css_sha256);
        if(!cssBytes)throw new ProfileError(at,'owner CSS delivery is missing');
        const css=new TextDecoder().decode(cssBytes);
        // Transport only: an inline live sheet needs a server URL; a published
        // link retains the relative URL in the owner's checked CSS bytes.
        return {...result,css:css.replaceAll('../'+result.font.sha256+'/font.ttf',assetURL(result.font.sha256,'font.ttf'))};
    }
    if(plan.status!=='declared'||!plan.profile||!plan.reader)throw new ProfileError('drawing-profile:1','cannot read the drawing input plan','unsupported');
    const support = node ? require('./drawing-fonts.json') : await (await fetch('drawing-fonts.json')).json();
    if(await sha(bytes(plan.reader.source))!==plan.reader.sha256)throw new ProfileError('drawing-profile:1','reader bytes differ from their snapshot');
    const origin=plan.profile.path, p=parsed(plan.profile);
    for(const file of [plan.profile,...Object.values(plan.inputs)])if(file.text!==undefined&&await sha(bytes(file.text))!==file.sha256)throw new ProfileError(file.path+':1','input bytes differ from the resolved snapshot');
    const records=[...p.declarations.values()].filter(d=>d.conformances.includes('DrawingProfile'));
    if(records.length!==1)throw new ProfileError(origin+':1','one DrawingProfile is required');
    const d=records[0],address=origin+':'+d.line;
    const fail=(message,status='refused',at=address)=>{throw new ProfileError(at,message,status);};
    function shape(record, keys, file) {
        const at=file.path+':'+(record?.line||1);
        if(!record||record.aliases.size!==keys.length||keys.some(k=>!record.aliases.has(k)))fail('unknown or missing profile field','refused',at);
        const body=file.text.match(new RegExp('public enum '+record.name+'\\b[^\\n]*\\{([\\s\\S]*?)\\n\\}'))?.[1]||'';
        const cleanBody=body.replace(/\/\*[\s\S]*?\*\/|\/\/[^\n]*/g,'');
        const fields=[...cleanBody.matchAll(/\btypealias\s+(\w+)\s*=/g)].map(m=>m[1]);
        if(fields.length!==new Set(fields).size)fail('duplicate profile field','refused',at);
    }
    shape(d,['Reader','Contract','Palette','Bindings','Font','Metrics','License','Legible'],plan.profile);
    function axis(record,key){const a=record?.aliases.get(key);if(!a)fail('missing '+key);return a.target;}
    function word(name,source=p){const w=source.literals.get(name)?.value;if(w===undefined)fail('unresolved word '+name);return w;}
    function input(name){const f=plan.inputs[name];if(!f)fail('missing input row '+name);return f;}
    const list=text=>{if(!/^\([^()]*\)$/.test(text))fail('a reference list must be a finite tuple');return text.slice(1,-1).split(',').map(s=>s.trim()).filter(Boolean);};
    if(word(axis(d,'Reader'))!=='gate/documentkit-drawing')fail('this drawing reader is not installed','unsupported');
    const contractName=axis(d,'Contract');
    let contract=null, contractPin=null;
    if(p.literals.get(contractName)?.value!=='') {
        const file=input(contractName);
        try { contract=JSON.parse(file.text); } catch { fail('invalid Drawing contract','refused',file.path+':1'); }
        if(!contract||typeof contract!=='object'||Array.isArray(contract))fail('Drawing contract input must be a record','refused',file.path+':1');
        if(contract.format==='drawing/1') {
        if(!Array.isArray(contract.cases)||!contract.owner?.files)fail('incomplete Drawing contract','refused',file.path+':1');
        const ids=new Set();
        for(const c of contract.cases) {
            if(typeof c.id!=='string'||!c.id||ids.has(c.id)||!['svg','refused','not-compared'].includes(c.status)||!c.root||!c.address)fail('invalid Drawing case','refused',file.path+':1');
            ids.add(c.id);
            if(c.status==='not-compared') { if(!c.reason)fail('Drawing remainder has no reason'); continue; }
            if(!/^[a-f0-9]{64}$/.test(c.inputSHA256)||!Array.isArray(c.sources)||!Array.isArray(c.sourceSHA256)||c.sourceSHA256.length!==c.sources.length||c.sourceSHA256.some(h=>!/^[a-f0-9]{64}$/.test(h)))fail('Drawing input hashes are missing');
            if(c.status==='svg'&&(typeof c.svg!=='string'||await sha(bytes(c.svg))!==c.svgSHA256))fail('Drawing output bytes differ','refused',file.path+':1');
        }
        }
        const provenance=(plan.record?.files||[]).find(row=>row.row===contractName);
        contractPin={sha256:file.sha256,...(provenance?{repository:provenance.repository,revision:provenance.revision,source_path:provenance.source_path}:{path:file.path,source:file.source})};
        if(plan.accepted_contract?.sha256!==file.sha256){contract=null;contractPin=null;}
    }
    const palette=input(axis(d,'Palette')), pp=parsed(palette), env=kit.makeEnvironment(pp.declarations,pp.literals,pp.topAliases);
    const colour=term=>{const value=kit.textOf(env,kit.parseType(term));if(!/^color\(xyz-d65 [\d.]+ [\d.]+ [\d.]+\)$/.test(value))fail('unsupported colour '+term,'unsupported');return value;};
    const count=term=>{const n=Number(kit.textOf(env,kit.parseType('Tally<'+term+'>')));if(!Number.isSafeInteger(n)||n<0)fail('unsupported luminance '+term,'unsupported');return n;};
    const parsedInputs=new Map([[axis(d,'Palette'),pp]]);
    const ownerReference=ref=>{const pair=word(ref).split('::');if(pair.length!==2)fail('reference is not qualified by an input row');const file=input(pair[0]);if(!parsedInputs.has(pair[0]))parsedInputs.set(pair[0],parsed(file));return {row:pair[0],name:pair[1],file,parsed:parsedInputs.get(pair[0])};};
    const bindings=[],names=new Map();
    for(const ref of list(axis(d,'Bindings'))){
        const owner=ownerReference(ref),{name,file,parsed:bp}=owner;
        const b=bp.declarations.get(name), at=file.path+':'+(b?.line||1);
        if(!b?.conformances.includes('DrawingBinding'))fail('unresolved DrawingBinding '+name,'refused',at);
        shape(b,['Role','Theme','Colour','Luminance'],file);
        const role=word(axis(b,'Role'),bp),theme=word(axis(b,'Theme'),bp),term=axis(b,'Colour');
        if(!/^[a-z][a-z0-9-]*$/.test(role)||!['light','dark'].includes(theme))fail('invalid role or theme','refused',at);
        const y=bp.declarations.get(axis(b,'Luminance'));
        shape(y,['Value','Colour','Projection'],file);
        if(!y?.conformances.includes('DrawingLuminance')||axis(y,'Colour')!==term)fail('luminance does not name this colour','refused',at);
        const value=axis(y,'Value'),css=colour(term);
        const projection=kit.parseType(axis(y,'Projection'));
        if(projection.head!=='XYZRatioWrite'||projection.args.length!==4||projection.args[0].head!=='Never'||projection.args[1].head!==value||projection.args[2].head!=='Never')fail('projection does not bind its declared luminance','refused',at);
        const projected=colour(axis(y,'Projection'));
        if(projected.split(' ')[2]!==css.split(' ')[2])fail('luminance and printed Y disagree','refused',at);
        const key=theme+'/'+role;if(names.has(key))fail('duplicate binding '+key,'refused',at);
        const row={name,id:owner.row+'::'+name,role,theme,term,value,css,address:at};names.set(key,row);bindings.push(row);
    }
    const required=[...new Set([...plan.reader.source.matchAll(/var\(--vi-([a-z-]+),/g)].map(m=>m[1]))];
    for(const role of required)for(const theme of ['light','dark'])if(!names.has(theme+'/'+role))fail('missing '+theme+' binding for '+role);
    const byName=new Map(bindings.map(b=>[b.id,b])),witnesses=[];
    for(const ref of list(axis(d,'Legible'))){
        const owner=ownerReference(ref),{name,file,parsed:wp}=owner;
        const w=wp.declarations.get(name),at=file.path+':'+(w?.line||1);
        if(!w?.conformances.includes('DrawingLegible'))fail('unresolved DrawingLegible '+name,'refused',at);
        shape(w,['Theme','Foreground','Background','Witness'],file);
        const theme=word(axis(w,'Theme'),wp),fg=byName.get(owner.row+'::'+axis(w,'Foreground')),bg=byName.get(owner.row+'::'+axis(w,'Background'));
        const reference=word(axis(w,'Witness'),wp).split('::');
        if(reference.length!==2||reference[0]!==axis(d,'Palette'))fail('witness is not qualified by the declared palette','refused',at);
        const witness=reference[1];
        const a=pp.topAliases.get(witness),term=a&&kit.parseType(a.target);
        if(!fg||!bg||fg.theme!==theme||bg.theme!==theme||term?.head!=='Legible'||term.args.length!==3)fail('witness has no matching endpoints','refused',at);
        const ends=term.args.slice(0,2).map(t=>t.head);
        if(!((ends[0]===fg.value&&ends[1]===bg.value)||(ends[1]===fg.value&&ends[0]===bg.value)))fail('witness endpoints do not match the declared bindings','refused',at);
        witnesses.push({id:witness,address:palette.path+':'+a.line,foreground:fg.name,background:bg.name,theme});
    }
    const judgement=palette.count||{};
    if(judgement.source_sha256!==palette.sha256||!judgement.text?.includes('source-bound readings checked')||judgement.text.includes('✗'))fail('the palette count court did not confirm these inputs','refused',palette.path+':1');
    const checked=Number(judgement.text.match(/(\d+) source-bound readings checked/)?.[1]);
    const requested=new Set([...pp.topAliases].filter(([,a])=>kit.parseType(a.target).head==='Legible').map(([name])=>name));
    const delivered=new Set(witnesses.map(w=>w.id));
    if(checked<requested.size||requested.size!==delivered.size||[...requested].some(id=>!delivered.has(id)))fail('Legible coverage differs from the count reading','refused',palette.path+':1');
    if(env.errors.length)fail(env.errors.join('; '),'unsupported');
    const font=p.declarations.get(axis(d,'Font')),metrics=p.declarations.get(axis(d,'Metrics'));
    if(!font?.conformances.includes('DrawingFont')||!metrics?.conformances.includes('DrawingMetrics')||axis(metrics,'Font')!==font.name)fail('font and metrics do not name the same face');
    shape(font,['Asset','Family','Face'],plan.profile);
    shape(metrics,['Input','Profile','Font','SourceFontSHA256','UnitsPerEm','CapHeight','Advances','MissingGlyph'],plan.profile);
    const asset=input(axis(font,'Asset')),mf=input(axis(metrics,'Input')),license=input(axis(d,'License')),mp=parsed(mf);
    const family=word(axis(font,'Family')),face=word(axis(font,'Face'));
    // Family is the owner's label. Registration uses the content hash, so a
    // different label never selects a different table or overwrites a bench font.
    if(word(axis(metrics,'SourceFontSHA256'))!==asset.sha256)fail('font bytes differ from SourceFontSHA256','refused',asset.path+':1');
    if(face!=='default'||word(axis(metrics,'Profile'))!==support.profile||!support.fonts.includes(asset.sha256))fail('font/face is outside the installed metric profile','unsupported',asset.path+':1');
    const units=Number(word(axis(metrics,'UnitsPerEm'),mp)),cap=Number(word(axis(metrics,'CapHeight'),mp)),advances=word(axis(metrics,'Advances'),mp),missing=word(axis(metrics,'MissingGlyph'));
    if(units!==Number(plan.reader.source.match(/const fontUnitsPerEm = (\d+)/)?.[1])||cap!==Number(plan.reader.source.match(/const fontCapHeight = (\d+)/)?.[1])||advances!==plan.reader.source.match(/const fontAdvances = new Map\("([^"]+)"/)?.[1]||missing!=='advance-of-U+006D')fail('metrics differ from the installed drawing reader','unsupported',mf.path+':1');
    const fontBytes=await getBytes(asset.sha256);
    if(await sha(fontBytes)!==asset.sha256)fail('font delivery hash differs','refused',asset.path+':1');
    let faceInfo;
    try{faceInfo=fontTable(fontBytes,{units,cap,advances:advances.split(/\s+/).map(s=>s.split(':').map(Number))},asset.path+':1');}catch(e){if(e instanceof ProfileError)throw e;fail('cannot read the declared font tables','unsupported',asset.path+':1');}
    if(!license.text?.trim())fail('font license is missing','refused',license.path+':1');
    // A world's family label must not register over a bench interface family.
    const cssFamily='gate-drawing-'+asset.sha256;
    const css=['light','dark'].map(theme=>(theme==='light'?':root':':root[data-theme="dark"]')+'{'+bindings.filter(b=>b.theme===theme).map(b=>'--vi-'+b.role+':'+b.css+';').join('')+'}').join('\n')+'\n'
        +'@font-face{font-family:'+JSON.stringify(cssFamily)+';src:url("'+assetURL(asset.sha256,'font.ttf')+'") format("truetype");font-weight:'+faceInfo.weight+';font-style:normal;font-display:block;}\n'
        +'svg[data-vi-canvas]{font-family:'+JSON.stringify(cssFamily)+';font-optical-sizing:none;font-kerning:none;font-variant-ligatures:none;}\n';
    const ownerInputsMatch=!!contract?.profile
        && contract.profile.profileSHA256===plan.profile.sha256
        && JSON.stringify([...contract.profile.inputSHA256].sort())===JSON.stringify(Object.entries(plan.inputs).filter(([name])=>name!==contractName).map(([,file])=>file.sha256).sort());
    const inputSHA256=await sha(bytes(JSON.stringify({profile:plan.profile.sha256,reader:plan.reader.sha256,inputs:Object.keys(plan.inputs).sort().map(name=>[name,plan.inputs[name].sha256])})));
    if(plan.accepted_contract?.sha256!==contractPin?.sha256){contract=null;contractPin=null;}
    return {inputSHA256,ownerInputsMatch:!!contract&&ownerInputsMatch,status:contract?'ready':'not-compared',reason:contract?'Drawing contract is installed':'The owner Drawing contract is not declared or has not been accepted',contract,contract_pin:contractPin,port_under_contract:!!contract&&plan.accepted_contract.port_sha256===plan.reader.sha256,origin:'port',owner_receipt:plan.owner_receipt||null,css,bindings,witnesses,reader:{id:'gate/documentkit-drawing',sha256:plan.reader.sha256},font:{sha256:asset.sha256,family,cssFamily,face,units,cap,metrics_sha256:mf.sha256,missingGlyph:missing},assets:[{sha256:asset.sha256,name:'font.ttf'},{sha256:license.sha256,name:'license.txt'}],profile_sha256:plan.profile.sha256,source:{record_sha256:plan.record_sha256,inputs:plan.record?.files||[]}};
}
// One comparison for live and static readings. File labels do not grant parity:
// every semantic source byte and every actual result must match the owner.
async function compare(profile, parts, drawn, declaration=null) {
    const hashes=await Promise.all(parts.map(p=>sha(bytes(p.text))));
    const sourceDigest=await sha(bytes(JSON.stringify([...hashes].sort())));
    const digest=await sha(bytes(JSON.stringify({sources:sourceDigest,profile:profile?.inputSHA256||null})));
    const contract=profile?.contract;
    const base={status:'port-under-contract',inputs_digest:digest,source_digest:sourceDigest,contract_pin:profile?.contract_pin||null,case_count:contract?.cases.length||0,profile_origin:profile?.origin||'none',owner_receipt:profile?.owner_receipt||null};
    if(!contract)return {...base,status:'not-compared',reason:profile?.reason||'The owner Drawing contract is not declared'};
    if(profile.port_under_contract===false)return {...base,status:'not-compared',case_count:0,reason:'The installed drawing port has not passed this owner contract'};
    if(profile.ownerInputsMatch===false)return {...base,reason:'The drawing profile inputs differ from the owner case environment'};
    const stated=contract.cases.find(c=>c.id===declaration?.case_id&&c.status==='not-compared');
    if(stated&&declaration.source_digest===sourceDigest)return {...base,status:'not-compared',case_id:stated.id,address:stated.address,reason:stated.reason};
    const matches=[];
    for(const c of contract.cases) {
        if(c.status==='not-compared'||c.sourceSHA256.length!==hashes.length)continue;
        const unused=hashes.map((hash,i)=>({hash,i})), ordered=[];
        for(const h of c.sourceSHA256) { const at=unused.findIndex(x=>x.hash===h);if(at<0)break;ordered.push(parts[unused.splice(at,1)[0].i]); }
        if(unused.length||await sha(bytes(ordered.map(p=>p.text).join('\n')))!==c.inputSHA256)continue;
        const art=drawn.canvases.find(a=>a.name===c.root), refusal=drawn.refusals.find(a=>a.name===c.root);
        const ownerFile=c.address.split('#')[0],index=c.sources.indexOf(ownerFile);
        const address=index<0?c.address:ordered[index].file+'#'+c.root;
        const equal=c.status==='svg'?art?.svg===c.svg&&!refusal:!art&&refusal?.status==='refused'&&refusal.code===c.code&&refusal.address===address;
        if(!equal)return {...base,status:'not-compared',case_id:c.id,address:c.address,reason:'The port output differs from the owner Drawing case'};
        matches.push(c.id);
    }
    if(matches.length&&matches.length===drawn.canvases.length+drawn.refusals.length)return {...base,status:'compared',case_id:matches.join(', ')};
    return {...base,reason:'This input has not been read by the owner'};
}
function caption(comparison) {
    return comparison.status+(comparison.case_id?' · '+comparison.case_id:'')+(comparison.reason?' · '+(comparison.address?comparison.address+': ':'')+comparison.reason:'')+(comparison.profile_origin==='port'?' · palette: browser port; owner receipt stale':'');
}
const api={compile,compare,caption,ProfileError,sha};
if(node){module.exports=api;if(require.main===module){let s='';process.stdin.setEncoding('utf8');process.stdin.on('data',b=>s+=b);process.stdin.on('end',async()=>{try{const plan=JSON.parse(s),base=process.argv[2];const result=await compile(plan,async h=>base==='--assets'?new Uint8Array(require('fs').readFileSync(require('path').join(process.argv[3],h,(plan.resolved?.assets||[]).find(a=>a.sha256===h)?.name||'font.ttf'))):new Uint8Array(await(await fetch(base+'/drawing-assets/'+h)).arrayBuffer()),(h,n)=>'../'+h+'/'+n);console.log(JSON.stringify(result));}catch(e){console.error(JSON.stringify({status:e.status||'refused',address:e.address||'drawing-profile:1',message:e.message}));process.exitCode=1;}});}}
else host.GateDrawingProfile=api;
})(globalThis);
