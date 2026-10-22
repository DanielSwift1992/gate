/* vi-grammar-policy/1, carried from the pinned owner's GrammarPolicy.swift.
   Grants come only from the compiler-exported policy. This port declares an
   unsupported identifier outside its compared ASCII identifier subset. */
'use strict';
(function(root) {
function findings(source,scope,policy) {
    const fallback=policy.atoms.find(a=>a.name===policy.defaultAtom);
    if(policy.format!=='vi-grammar-policy/1'||!policy.scopes.includes(scope)||!fallback)throw Error('unsupported grammar policy or scope '+scope);
    if(typeof Intl?.Segmenter!=='function')throw Error('grammar needs Character boundaries');
    const characters=text=>[...new Intl.Segmenter('und',{granularity:'grapheme'}).segment(text)].map(s=>s.segment);
    const chars=characters(source);let i=0,line=1;
    const byName=new Map(policy.atoms.map(a=>[a.name,a]));
    const words=new Map(policy.atoms.filter(a=>a.word).map(a=>[a.spelling,a]));
    const punctuation=policy.atoms.filter(a=>!a.word&&a.spelling).map(a=>({...a,chars:characters(a.spelling)})).sort((a,b)=>b.chars.length-a.chars.length||(a.name<b.name?-1:a.name>b.name?1:0));
    const glyphs=new Map(punctuation.filter(a=>a.chars.length===1).map(a=>[a.spelling,a]));
    const identifier=c=>{
        if(/^[A-Za-z0-9_]$/.test(c))return true;
        if(/[\p{L}\p{N}\p{Alphabetic}]/u.test(c))throw Error('grammar Character identifier at line '+line+' is outside this port’s compared subset');
        return false;
    };
    const starts=a=>a.length&&a.every((c,n)=>chars[i+n]===c);
    function advance(n){while(n--&&i<chars.length){if(chars[i]==='\n')line++;i++;}}
    function next(){
        const at=line;if(i>=chars.length)return [null,'Char0Atom',at];
        if(identifier(chars[i])){
            const from=i;while(i<chars.length&&identifier(chars[i]))advance(1);
            const atom=words.get(chars.slice(from,i).join(''))||fallback;return [atom,atom.name,at];
        }
        for(const atom of punctuation)if(starts(atom.chars)){advance(atom.chars.length);return [atom,atom.name,at];}
        const unknown='Char'+chars[i].codePointAt(0)+'Atom';advance(1);return [null,unknown,at];
    }
    function foreignHere(){for(const atom of punctuation)if(atom.foreign&&starts(atom.chars)){advance(atom.chars.length);return atom;}return null;}
    function balanced(opener){
        let depth=0;
        while(i<chars.length){
            const foreign=foreignHere();if(foreign){span(foreign);continue;}
            const atom=glyphs.get(chars[i]);
            if(atom?.opening&&atom.name===opener.name){depth++;advance(1);continue;}
            if(atom?.closes===opener.name){depth--;advance(1);if(depth===0)return;continue;}
            advance(1);
        }
    }
    function span(atom){
        const closer=byName.get(atom.foreign);if(!closer)return;
        const end=characters(closer.spelling);
        while(i<chars.length){
            if(starts(end)){advance(end.length);return;}
            if(glyphs.get(chars[i])?.escapes){advance(1);if(i>=chars.length)return;const opener=glyphs.get(chars[i]);if(opener?.opening)balanced(opener);else advance(1);continue;}
            advance(1);
        }
    }
    const frames=[{opener:'',context:'Plain',pending:[]}],bad=[];
    let last=fallback,head=true,lineHead=true,exempt=false;
    function finish(frame){
        for(const p of frame.pending)if(frame.context!=='Exempt'&&!p.grants.includes(scope+'/'+frame.context))bad.push({line:p.line,atom:p.atom,scope,context:frame.context});
        if(frame.context==='Exempt')for(const p of frame.pending)if(!byName.has(p.atom)&&!Object.hasOwn(policy.pairs,p.atom)&&!p.atom.startsWith('Midline<'))bad.push({line:p.line,atom:p.atom,scope,context:frame.context});
    }
    const emit=(atom,grants,line)=>frames[frames.length-1].pending.push({atom,grants,line});
    while(i<chars.length){
        const [atom,name,at]=next();if(!atom){emit(name,[],at);last=null;continue;}
        if(atom.declaration)head=true;if(atom.exempt)exempt=true;
        if(atom.foreign){span(atom);emit(name,atom.grants,at);last=atom;if(byName.get(atom.foreign)?.spelling==='\n')lineHead=true;continue;}
        if(atom.medium){if(atom.spelling==='\n')lineHead=true;continue;}
        const headsLine=lineHead;if(!atom.modifier)lineHead=false;
        if(atom.opening){
            if(atom.pairs){frames.push({opener:name,context:exempt?'Exempt':((last?.builder||!head)?'Builder':'Plain'),pending:[]});head=false;exempt=false;}
            else emit(name,atom.grants,at);
            last=atom;continue;
        }
        if(atom.closes&&frames.length>1&&frames[frames.length-1].opener===atom.closes){finish(frames.pop());head=false;exempt=false;last=atom;continue;}
        if(atom.line&&!headsLine){emit('Midline<'+name+'>',[],at);last=atom;continue;}
        if(atom.pair){let [other,otherName]=next();while(other?.medium&&i<chars.length)[other,otherName]=next();lineHead=false;const pairName='Declares<'+name+', '+otherName+'>';emit(pairName,policy.pairs[pairName]||[],at);last=other;continue;}
        emit(name,atom.grants,at);last=atom;
    }
    while(frames.length>1)frames[frames.length-2].pending.push(...frames.pop().pending);
    finish(frames[0]);return bad.sort((a,b)=>a.line-b.line);
}
const api={findings};if(typeof module!=='undefined')module.exports=api;root.GateGrammarPolicy=api;
})(typeof globalThis!=='undefined'?globalThis:this);
