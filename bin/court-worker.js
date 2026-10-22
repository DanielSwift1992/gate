/* Heavy changed questions run off the UI thread. Unchanged questions reuse the
   owner's complete-input receipt before this worker is called. */
'use strict';
importScripts('court/vi_court.js','court/vi_court_bytes.js');
wasm_bindgen.initSync({module:Uint8Array.from(atob(VI_COURT_WASM_BASE64),c=>c.charCodeAt(0))});
self.onmessage=event=>{
    const {id,method,request}=event.data;
    try {
        if(!['judge','source_notation'].includes(method))throw Error('unsupported court transport method');
        self.postMessage({id,result:wasm_bindgen[method](request)});
    } catch(error) {self.postMessage({id,error:String(error.message||error)});}
};
