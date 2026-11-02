// Real shipped UI/JS against its loopback Registry API; DOM semantics, not pixel layout.
const assert = require('node:assert/strict');
const {JSDOM, VirtualConsole} = require('jsdom');
const {setTimeout: delay} = require('node:timers/promises');
async function main() {
 const base = new URL(process.argv[2]), scenario = process.argv[3] || 'baseline';
 assert.equal(base.hostname, '127.0.0.1');
 const response = await fetch(base, {signal:AbortSignal.timeout(8000)});
 assert.equal(response.status,200);
 const errors=[], requests=[];const console=new VirtualConsole();console.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(await response.text(),{url:base.href,runScripts:'outside-only',virtualConsole:console});
 const w=dom.window,d=w.document,$=id=>d.getElementById(id);
 w.HTMLElement.prototype.scrollIntoView=function(){};
 // Controlled clock: exercise the unchanged 15-second production deadline instantly.
 w.AbortController=globalThis.AbortController;
 const realTimeout=w.setTimeout.bind(w),realClear=w.clearTimeout.bind(w),deadlines=new Map();let timerId=0;
 w.setTimeout=(fn,ms,...args)=>{if(ms===15000){const id=--timerId;deadlines.set(id,()=>fn(...args));return id;}return realTimeout(fn,ms,...args);};
 w.clearTimeout=id=>{if(!deadlines.delete(id))realClear(id);};
 const fireDeadline=()=>{assert.equal(deadlines.size,1);const [id,fn]=[...deadlines][0];deadlines.delete(id);fn();};
 let gate,release,paused=false;
 w.fetch=async (url,options)=>{
  const target=new URL(url,base);assert.equal(target.origin,base.origin);assert.equal(target.pathname,'/api/reviewed/v1/evaluate');
  const body=JSON.parse(options.body);assert.deepEqual(Object.keys(body).sort(),['kind','language','request_id','tasks']);requests.push(body);
  assert.ok(options.signal,'The real UI must provide its own cancellation signal');
  if(scenario==='timeout'&&requests.length===2){paused=true;return new Promise(()=>{});}
  const result=await fetch(target,{...options,headers:{...options.headers,Origin:base.origin},signal:AbortSignal.any([options.signal,AbortSignal.timeout(8000)])});
  if((scenario==='late-fetch'||scenario==='late-body')&&requests.length===2){
   const data=await result.json();gate=new Promise(resolve=>release=resolve);paused=true;
   if(scenario==='late-fetch'){await gate;return {json:async()=>data};}
   return {json:async()=>{await gate;return data;}};
  }
  if(scenario==='stale'&&!paused){paused=true;gate=new Promise(resolve=>release=resolve);await gate;}
  return result;
 };
 for(const script of d.querySelectorAll('script'))w.eval(script.textContent);
 function choose(id,value){if(typeof value==='boolean')$(id).checked=value;else $(id).value=value;$(id).dispatchEvent(new w.Event('change',{bubbles:true}));}
 async function until(test){const end=Date.now()+12000;while(!test()){assert.ok(Date.now()<end,'DOM/API completion timeout: '+$('summary').textContent);await delay(10);}}
 async function submit(){ $('request').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));await until(()=>!$('submit').disabled); }
 try {
  assert.ok(d.body.textContent.includes('LOCAL REGISTRY MODE'));
  if(['timeout','late-fetch','late-body'].includes(scenario)){
   await submit();assert.ok($('bundles').children.length>0);
   $('request').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));await until(()=>paused);
   assert.equal($('bundles').children.length,0,'Old procedures clear immediately');
   assert.equal(d.querySelectorAll('#bundles a').length,0);
   fireDeadline();await until(()=>!$('submit').disabled);
   assert.match($('summary').textContent,/did not respond within 15 seconds/);
   assert.match($('summary').textContent,/Try again/);assert.equal(deadlines.size,0);
   choose('context','hydrophobic_deposits');choose('cleaning',false);choose('pressure',true);
   await submit();assert.match($('summary').textContent,/No supported answer/);
   const fresh=$('json').textContent;
   if(release){release();await delay(30);}
   assert.equal($('json').textContent,fresh,'Late reply must not replace the successful retry');
   assert.equal($('bundles').children.length,0);assert.equal($('submit').disabled,false);
  }else if(scenario==='stale'){
   $('request').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));await until(()=>paused);
   choose('product','family_unknown');release();await until(()=>!$('submit').disabled);
   assert.match($('summary').textContent,/Inputs changed/);assert.equal($('bundles').children.length,0);assert.equal($('stale').hidden,false);
  }else if(scenario==='unavailable'){
   await submit();assert.match($('summary').textContent,/Registry unavailable/);assert.match($('summary').textContent,/No preview fallback/);
   assert.equal($('bundles').children.length,0);assert.equal(d.querySelectorAll('#bundles a').length,0);
  }else if(scenario==='withdrawn'){
   await submit();assert.match($('summary').textContent,/Evidence held/);assert.equal($('bundles').children.length,0);
   const held=await fetch(new URL('/reviewed/v1/releases/release-v01/sources/E167-P',base));assert.match(await held.text(),/Source held/);
   choose('context','hydrophobic_deposits');await submit();assert.match($('summary').textContent,/Documented support/);
   assert.ok($('bundles').textContent.includes('Attached original precaution'));
   assert.ok(d.querySelector('a[href$="/E167-W"]'),'Independent solvent warning must remain');
  }else{
   assert.equal(scenario,'baseline');await submit();assert.match($('summary').textContent,/Documented support/);
   const link=d.querySelector('a[href$="/E167-P"]');assert.ok(link);
   const view=await fetch(new URL(link.getAttribute('href'),base));assert.equal(view.status,200);const page=await view.text();assert.match(page,/CURRENT WITHDRAWAL AUTHORITY CHECKED/);assert.ok(page.includes('<blockquote>'));
   choose('product','family_unknown');assert.equal($('stale').hidden,false);await submit();assert.match($('summary').textContent,/Clarification needed/);
   const edit=[...d.querySelectorAll('#outcomes button')][0];assert.ok(edit);edit.click();assert.equal(d.activeElement.id,'product');
   choose('product','mabselect');choose('context','hydrophobic_deposits');choose('cleaning',false);choose('pressure',true);await submit();assert.match($('summary').textContent,/No supported answer/);assert.match($('outcomes').textContent,/No numerical value or substitute/);
   choose('pressure',false);const previous=requests.length;await submit();assert.equal(requests.length,previous);assert.match($('summary').textContent,/at least one question/);assert.equal($('bundles').children.length,0);
  }
  assert.equal(deadlines.size,0,'No pending deadline after completion, cancellation or failure');
  assert.deepEqual(errors,[]);process.stdout.write(JSON.stringify({status:'passed',scenario,requests:requests.length}));
 }finally{dom.window.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
