// Presentation-only regressions over the real handler and disposable authority.
const assert=require('node:assert/strict');
const {JSDOM,VirtualConsole}=require('jsdom');
const {setTimeout:delay}=require('node:timers/promises');
async function main(){
 const base=new URL(process.argv[2]),scenario=process.argv[3];assert.equal(base.hostname,'127.0.0.1');
 const response=await fetch(base);assert.equal(response.status,200);
 const errors=[],responses=[],requests=[],vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(await response.text(),{url:base.href,runScripts:'outside-only',virtualConsole:vc});
 const w=dom.window,d=w.document,$=id=>d.getElementById(id);
 w.HTMLElement.prototype.scrollIntoView=function(){};w.AbortController=globalThis.AbortController;
 w.fetch=async(url,options)=>{
  requests.push(JSON.parse(options.body));const target=new URL(url,base);assert.equal(target.origin,base.origin);
  const result=await fetch(target,{...options,headers:{...options.headers,Origin:base.origin}});
  const data=await result.json();responses.push(data);return {json:async()=>data};
 };
 for(const script of d.querySelectorAll('script'))w.eval(script.textContent);
 function choose(id,value){if(typeof value==='boolean')$(id).checked=value;else $(id).value=value;$(id).dispatchEvent(new w.Event('change',{bubbles:true}));}
 async function submit(){
  $('request').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));
  const end=Date.now()+18000;while($('submit').disabled){assert.ok(Date.now()<end,'UI completion deadline');await delay(10);}
  assert.equal(JSON.stringify(JSON.parse($('json').textContent)),JSON.stringify(responses.at(-1)),'Audit response unchanged by presentation');
 }
 try{
  assert.match(d.title,/presentation v02/);
  if(scenario==='outside'){
   choose('product','other');choose('context','mixed_other');choose('pressure',true);await submit();
   assert.match($('summary').textContent,/outside this documentary release/);
   const cards=[...d.querySelectorAll('#outcomes article')];assert.equal(cards.length,2);
   assert.match(cards[0].textContent,/No cleaning procedure or substitute product/);assert.doesNotMatch(cards[0].textContent,/No numerical/);
   assert.match(cards[1].textContent,/No numerical maximum pressure/);assert.match(cards[1].textContent,/manufacturer specifications/);
   assert.equal($('bundles').children.length,0);assert.equal(d.querySelectorAll('#bundles a').length,0);
  }else if(scenario.startsWith('clarify-')){
   const context=scenario==='clarify-context';
   choose('product',context?'sure':scenario==='clarify-conflict'?'contradictory':'family_unknown');
   choose('context',context?'mixed_other':'hydrophobic_deposits');choose('pressure',!context);await submit();
   assert.match($('summary').textContent,/Clarification needed/);
   assert.equal(d.querySelectorAll('#outcomes button').length,1,'One action even for two items');
   assert.equal(($('outcomes').textContent.match(/Please specify:/g)||[]).length,1);
   const panel=d.querySelector('.clarification-action');assert.match(panel.textContent,/confirmed diagnosis is not required/);assert.match(panel.textContent,/uncertainty may remain unknown/);
   assert.equal(d.querySelectorAll('#outcomes article').length,responses.at(-1).items.length+1,'All item states retained');
   const details=d.querySelector('#bundles details');assert.ok(details);assert.equal(details.open,false);
   assert.match(details.querySelector('summary').textContent,/citations and review limits/);
   const bundle=responses.at(-1).context.bundles[0];
   assert.equal(details.querySelectorAll('h4').length,1,'No repeated option heading');
   const ids=[...new Set([...details.querySelectorAll('a')].map(a=>a.getAttribute('href').split('/').at(-1)))].sort();
   assert.deepEqual(ids,bundle.required_source_ids.toSorted());assert.equal(ids.length,8);
   details.open=true;
   assert.deepEqual([...details.querySelectorAll('.reservation')].map(li=>li.textContent),bundle.visible_reservations);
   d.querySelector('#outcomes button').click();assert.equal(d.activeElement.id,context?'context':'product');
   assert.equal($('product').value,requests[0].tasks[0].product);assert.equal($('context').value,requests[0].tasks[0].deposit_context);
  }else{
   assert.ok(['solvent','partial-warning','different-source-warning'].includes(scenario));
   choose('product','sure');choose('context','hydrophobic_deposits');choose('pressure',true);await submit();
   const original=responses.at(-1);let data=structuredClone(original);
   const option=data.context.bundles.find(b=>b.review_scope==='N07').options[0];
   const duplicate=option.warnings.find(w=>w.source_ids.includes('E167-E'));
   if(scenario==='partial-warning'){
    // Synthetic renderer-only fixture: extra warning text must never be folded away.
    duplicate.wording+=' Synthetic additional precaution.';w.render(data);
   }else if(scenario==='different-source-warning'){
    // Equal words from a different source do not establish duplicate provenance.
    duplicate.source_ids=['E167-W'];w.render(data);
   }
   const folded=d.querySelectorAll('.repeated-source');
   assert.equal(folded.length,scenario==='solvent'?1:0);
   if(scenario==='solvent'){
    assert.equal(folded[0].open,false);assert.equal(folded[0].querySelector('blockquote').textContent,duplicate.wording);
    assert.match(folded[0].querySelector('summary').textContent,/E167-E/);
    folded[0].open=true;assert.ok(folded[0].querySelector('a[href$="/E167-E"]'));
   }
   for(const b of data.context.bundles){
    for(const op of b.options){for(const step of op.steps)assert.ok([...d.querySelectorAll('#bundles blockquote')].some(n=>n.textContent===step.wording));}
    for(const reservation of b.visible_reservations)assert.ok([...d.querySelectorAll('.reservation')].some(n=>n.textContent===reservation));
   }
   const independent=option.warnings.find(w=>w.source_ids.includes('E167-W')&&w!==duplicate);
   const warning=[...d.querySelectorAll('#bundles blockquote')].find(n=>n.textContent===independent.wording);
   assert.ok(warning);assert.equal(warning.closest('details'),null,'Independent backpressure warning remains immediately visible');
   assert.match($('outcomes').textContent,/No numerical value or substitute/);
  }
  assert.deepEqual(errors,[]);process.stdout.write(JSON.stringify({status:'passed',scenario,requests:requests.length}));
 }finally{dom.window.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1;});
