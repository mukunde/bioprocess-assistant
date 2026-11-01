// Execute the shipped page, its handlers and renderer against the real local API.
// jsdom supplies DOM semantics, not browser layout; CUA verifies visual behavior.
const assert = require('node:assert/strict');
const { JSDOM, VirtualConsole } = require('jsdom');
const { setTimeout: delay } = require('node:timers/promises');
const tick = () => delay(10); // Yield without spinning while the HTTP/DOM event completes.

async function main() {
  const base = new URL(process.argv[2]);
  const mutation = process.argv[3] || 'none';
  assert.equal(base.protocol, 'http:');
  assert.equal(base.hostname, '127.0.0.1');
  process.stderr.write('[MC12] ' + mutation + ': loading application\n');
  const response = await fetch(base, { signal: AbortSignal.timeout(8000), headers: { Connection: 'close' } });
  assert.equal(response.status, 200);
  let html = await response.text();
  if (mutation === 'missing-entry') {
    html = html.replace(/<option value="mabselect">MabSelect · cleaning guidance<\/option>/, '');
  } else if (mutation === 'wrong-payload') {
    html = html.replace("product:$('mab-product').value", "product:'sure'");
  } else if (mutation === 'missing-stale') {
    html = html.replace("$('request').addEventListener('change',markStale);", '');
  } else if (mutation === 'missing-warning') {
    html = html.replace('for(const id of option.quote_ids)', "for(const id of option.quote_ids.filter(id=>id!=='E167-W'))");
  } else if (mutation === 'broken-source-link') {
    html = html.replaceAll("a.href='#source-'+id", "a.href='#broken-'+id");
  } else {
    assert.equal(mutation, 'none');
  }
  const errors = [], requests = [], outcomes = [];
  const console = new VirtualConsole();
  console.on('jsdomError', e => errors.push(e.message));
  const dom = new JSDOM(html, { url: base.href + '#mabselect-controls', runScripts: 'outside-only', virtualConsole: console });
  const w = dom.window, d = w.document;
  // Layout-only operation absent from jsdom; selection/focus/hash/events are real DOM.
  w.HTMLElement.prototype.scrollIntoView = function () {};
  w.fetch = async (url, options) => {
    const destination = new URL(url, base);
    assert.equal(destination.origin, base.origin, 'No external requests');
    assert.equal(destination.pathname, '/evaluate');
    assert.equal(options.method, 'POST');
    const payload = JSON.parse(options.body);
    requests.push(payload);
    process.stderr.write('[MC12] ' + mutation + ': request ' + requests.length + ' dispatched\n');
    const res = await fetch(destination, { ...options, signal: AbortSignal.timeout(8000), headers: { ...options.headers, Origin: base.origin, Connection: 'close' } });
    return { ok: res.ok, status: res.status, json: async () => {
      const data = await res.json(); outcomes.push(data); process.stderr.write('[MC12] ' + mutation + ': request ' + requests.length + ' completed\n'); return data;
    }};
  };
  const $ = id => {const node=d.getElementById(id);assert.ok(node, 'Missing element: '+id);return node;};
  assert.ok([...$('mode').options].some(o => o.value === 'mabselect'), 'Missing MabSelect entry');
  for (const script of d.querySelectorAll('script')) {
    assert.ok(!script.src, 'Only local inline application code is evaluated');
    w.eval(script.textContent);
  }
  const seen=[];
  function select(id, value) {
    const control=$(id);control.value=value;
    assert.equal(control.value,value,'Missing selectable value '+value);
    control.dispatchEvent(new w.Event('change',{bubbles:true}));
  }
  async function submit() {
    const before=requests.length;
    $('submit').click();
    const deadline=Date.now()+10000;
    while ($('submit').disabled) {assert.ok(Date.now()<deadline,'Submission timed out');await tick();}
    assert.equal($('error').textContent,'','UI request failed');
    assert.equal(requests.length,before+1,'Form must submit exactly once');
    return outcomes.at(-1);
  }
  async function untilHash(expected) {
    const deadline=Date.now()+3000;
    while(w.location.hash!==expected) {assert.ok(Date.now()<deadline,'Anchor navigation timed out: '+expected);await tick();}
  }
  const cards=()=>[...$('outcome').querySelectorAll('article')];
  const text=()=>$('outcome').textContent;
  try {
    assert.equal($('mode').value,'mabselect');
    assert.equal($('mabselect-controls').style.display,'block');
    select('mab-product','family_unknown');select('mab-context','precipitated_substances');
    await submit();assert.equal(cards().length,0);assert.match(text(),/confirm the exact product label/);
    assert.deepEqual(requests.at(-1),{mode:'mabselect',product:'family_unknown',deposit_context:'precipitated_substances'});
    $('outcome').querySelector('button').click();assert.equal(d.activeElement.id,'mab-product');
    seen.push('family clarification and focus');

    select('mab-product','mabselect');await submit();
    assert.deepEqual(requests.at(-1),{mode:'mabselect',product:'mabselect',deposit_context:'precipitated_substances'});
    assert.equal(cards().length,1);assert.equal(cards()[0].querySelectorAll('li').length,4);
    assert.match(text(),/Contact time: at least 10 min/);assert.match(text(),/pH 7.0 to 8.0/);
    seen.push('plain product, four alternatives, complete following wash');

    select('mab-product','sure');assert.equal($('stale').hidden,false,'Changed product must mark results stale');
    await submit();assert.equal($('stale').hidden,true);
    assert.equal(cards().length,2);assert.match(text(),/not consecutive treatments/);
    assert.match(cards()[0].textContent,/four separate alternatives/);
    assert.match(cards()[1].textContent,/SuRe \/ SuRe LX only/);
    assert.match(cards()[1].textContent,/3 column volumes/);assert.match(cards()[1].textContent,/10 to 15 min/);
    seen.push('stale result and separate restricted block');

    select('mab-product','sure_lx');select('mab-context','hydrophobic_deposits');await submit();
    assert.equal(cards().length,2);assert.match(text(),/ethanol OR 2-propanol/);
    assert.match(cards()[0].textContent,/0.1% is an example/);
    assert.match(cards()[1].textContent,/Increasing gradients address air bubbles; lower flow addresses increased backpressure/);
    assert.match(cards()[1].textContent,/Washing with 70% ethanol and 30% 2-propanol will increase backpressure/);
    assert.match(cards()[1].textContent,/3 to 4 column volumes/);
    assert.doesNotMatch(cards()[1].textContent,/stand for 12 h/);
    const citation=[...cards()[1].querySelectorAll('a')].find(a=>a.textContent==='E167-W');
    assert.ok(citation);assert.equal(citation.hash,'#source-E167-W');
    citation.click();await untilHash('#source-E167-W');assert.equal(w.location.hash,'#source-E167-W');
    assert.match($('source-E167-W').textContent,/MabSelect media/);
    assert.match($('source-E167-W').textContent,/Use a lower flow rate/);
    $('source-E167-W').querySelector('a').click();await untilHash('#results-panel');assert.equal(w.location.hash,'#results-panel');
    seen.push('detergent/solvent alternatives, warnings and source navigation');

    select('mab-context','mixed_other');await submit();assert.equal(cards().length,0);
    $('outcome').querySelector('button').click();assert.equal(d.activeElement.id,'mab-context');
    assert.equal($('mab-product').value,'sure_lx');
    seen.push('mixed context retains product and clarifies');

    select('mode','guided');await submit();
    assert.equal(requests.at(-1).mode,'guided');assert.equal(requests.at(-1).column,'1');
    assert.equal(requests.at(-1).operations[0],'washing_flow');
    assert.match($('runtime-badge').textContent,/FROZEN v03/);
    assert.equal($('sources').querySelectorAll('article').length,5);
    assert.match(text(),/All identified requests have documented support/);
    seen.push('return to frozen guided route');

    select('mode','troubleshooting');select('trouble-product','protein_a');select('deposit-context','hydrophobic_deposits');await submit();
    assert.equal(requests.at(-1).mode,'troubleshooting');assert.equal(cards().length,2);
    assert.match(cards()[1].textContent,/stand for 12 h/);
    assert.match(text(),/These are alternative routes, not consecutive mandatory treatments/);
    seen.push('return to original Protein A/G route');
    assert.deepEqual(errors,[]);
    process.stdout.write(JSON.stringify({status:'passed',cases:seen,requests:requests.length,mutation})+'\n');
  } finally { w.close(); }
}
main().catch(error=>{process.stderr.write(String(error.stack||error)+'\n');process.exitCode=1;});
