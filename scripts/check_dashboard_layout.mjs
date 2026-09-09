// Run with Node 22+ and an isolated Edge/Chrome on --remote-debugging-port=9334.
// Read-only live dashboard regression: no registration, credits, or DB writes.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const tabs = await (await fetch('http://127.0.0.1:9334/json')).json();
const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(resolve => ws.addEventListener('open', resolve, {once:true}));
let seq = 0;
const pending = new Map(), errors = [];
ws.addEventListener('message', ({data}) => {
  const m = JSON.parse(data);
  if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.text + ': ' + (m.params.exceptionDetails.exception?.description || ''));
  if (pending.has(m.id)) {
    const {resolve,reject,timer} = pending.get(m.id);
    clearTimeout(timer); pending.delete(m.id);
    m.error ? reject(new Error(JSON.stringify(m.error))) : resolve(m.result);
  }
});
function send(method, params = {}) {
  const id = ++seq;
  return new Promise((resolve,reject) => {
    const timer = setTimeout(() => { pending.delete(id); reject(new Error('CDP timeout: ' + method)); }, 20000);
    pending.set(id, {resolve,reject,timer}); ws.send(JSON.stringify({id,method,params}));
  });
}
async function evaluate(expression) {
  const r = await send('Runtime.evaluate', {expression,returnByValue:true,awaitPromise:true});
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
  return r.result.value;
}
const pause = ms => new Promise(r => setTimeout(r,ms));
process.on('exit', () => {});
try {
  await send('Runtime.enable'); await send('Page.enable');
  await send('Page.navigate', {url:'http://127.0.0.1:8000/static/index.html'});
  let loaded = false;
  for (let i=0;i<60;i++) {
    try {
      if (await evaluate('typeof allCompanies !== "undefined" && allCompanies.length > 0 && !document.getElementById("content").classList.contains("hidden")')) { loaded = true; break; }
    } catch(e) { /* sayfa yukleniyor */ }
    await pause(500);
  }
  if (!loaded) {
    const diag = await evaluate('({url: location.href, hasAll: typeof allCompanies !== "undefined", n: typeof allCompanies !== "undefined" ? allCompanies.length : -1, contentHidden: document.getElementById("content")?.classList.contains("hidden"), err: document.getElementById("error-text")?.textContent})');
    console.log('DIAG:', JSON.stringify(diag));
  }
  assert.ok(loaded, 'Dashboard must load');
  // ── Watchlist toggle canary (bug fix dogrulamasi) ──
  // Deterministik: izleme listesini temizle, sayfayi yeniden yukle, sonra toggle davranisini dogrula
  await evaluate('localStorage.removeItem("huginn_watchlist")');
  await send('Page.navigate', {url:'http://127.0.0.1:8000/static/index.html'});
  for (let i=0;i<60;i++) {
    try { if (await evaluate('typeof allCompanies !== "undefined" && allCompanies.length > 0 && !document.getElementById("content").classList.contains("hidden")')) break; } catch(e) {}
    await pause(500);
  }
  const watchTest = await evaluate(`(async () => {
    const c = allCompanies.find(x => x.nace_code);
    if (!c) return {ok:false, reason:'firma yok'};
    // detay panelini ac
    showDetail(c);
    await new Promise(r=>setTimeout(r,300));
    const btnLabelBefore = document.querySelector('.detail-actions .d-btn:nth-child(2)')?.textContent.trim() || '?';
    // toggleWatchDetail cagir (butonun yaptigi sey)
    toggleWatchDetail();
    await new Promise(r=>setTimeout(r,300));
    const toastText = document.getElementById('toast')?.textContent || '';
    const added = watchSet.has(watchKeyOf(c));
    const btnLabelAfter = document.querySelector('.detail-actions .d-btn:nth-child(2)')?.textContent.trim() || '?';
    const listCount = watchSet.size;
    // geri al (temiz cikis)
    toggleWatchDetail();
    await new Promise(r=>setTimeout(r,200));
    const removed = !watchSet.has(watchKeyOf(c));
    return {ok:true, btnLabelBefore, toastText, added, btnLabelAfter, listCount, removed, watchKeyOfName: typeof watchKeyOf};
  })()`);
  assert.ok(watchTest.ok !== false, 'Watch test calismadi: ' + JSON.stringify(watchTest));
  assert.ok(/eklendi/.test(watchTest.toastText), 'Toast ekleme demeli: ' + watchTest.toastText);
  assert.ok(watchTest.added === true, 'toggle sonrasi watchSet icinde olmali');
  assert.ok(/İzlemeden Çıkar/.test(watchTest.btnLabelAfter), 'Buton etiketi Izlemeden Cikar olmali: ' + watchTest.btnLabelAfter);
  assert.ok(watchTest.removed === true, 'Ikinci toggle ile listeden cikmali');
  console.log('PASS watchlist-toggle:', JSON.stringify(watchTest));
  assert.ok(await evaluate('allCompanies.length > 0'), 'Live companies must load');
  for (const width of [1600,1366,1150,1024,768,760,390,320]) {
    await send('Emulation.setDeviceMetricsOverride', {width,height:900,deviceScaleFactor:1,mobile:false});
    await pause(300);
    await evaluate('closeDetailPanel(); closeMobileMenu(); document.querySelector(".content-scroll").scrollTop=0');
    const layout = await evaluate(`(() => {
      const box=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height}};
      const sc=document.querySelector('.content-scroll');
      return {vw:innerWidth,doc:document.documentElement.scrollWidth,main:box('.main'),header:box('.topbar'),search:box('.topbar-search'),actions:box('.topbar-actions'),brand:box('.topbar-brand'),detail:box('.detail-panel'),contentWidth:sc.clientWidth,contentScrollWidth:sc.scrollWidth,offenders:[...sc.querySelectorAll('*')].filter(el=>el.scrollWidth>sc.clientWidth+5 && !el.closest('.table-wrapper') && !['TABLE','THEAD','TBODY','TR','TD','TH'].includes(el.tagName)).map(el=>el.tagName+'.'+el.className).slice(0,6)};
    })()`);
    assert.ok(layout.doc <= width, `Document overflow ${width}: ${JSON.stringify(layout)}`);
    assert.deepEqual(layout.offenders, [], `Content overflow ${width}: ${JSON.stringify(layout)}`);
    assert.ok(layout.main.y >= layout.header.bottom-1, `Header overlaps main ${width}`);
    assert.ok(layout.actions.right <= width && layout.brand.right <= layout.actions.x+1, `Topbar overlap ${width}`);
    if(width>760) assert.ok(layout.search.right <= layout.actions.x+1, `Search overlaps actions ${width}`);
    if(width>1150) assert.ok(layout.detail.width>0 && layout.detail.x>=layout.main.right-1 && layout.detail.right<=width, 'Desktop detail visible on right');
    await evaluate('document.querySelector(".content-scroll").scrollTop=300');
    assert.equal(await evaluate('document.querySelector(".topbar").getBoundingClientRect().y'),layout.header.y,'Header stays fixed');
    await evaluate('document.querySelector("#companies-tbody tr td").click()');
    await pause(450); /* drawer transform transition .28s */
    const dbg = await evaluate(`(() => {const e=document.querySelector('.detail-panel'),r=e.getBoundingClientRect();return {w:r.width,x:r.x,right:r.right,vw:innerWidth,name:document.querySelector('.detail-company-name').textContent.length,cls:e.className,bodyCls:document.body.className,computed:getComputedStyle(e).visibility+'|'+getComputedStyle(e).position}})()`);
    assert.ok(dbg.w>0 && dbg.right<=dbg.vw && dbg.x>=0 && dbg.name>0, `Detail open ${width}: ${JSON.stringify(dbg)}`);
    if ([1600,390].includes(width)) {
      const shot = await send('Page.captureScreenshot', {format:'png'});
      await writeFile(new URL(`../logs/layout-${width}.png`,import.meta.url),Buffer.from(shot.data,'base64'));
    }
    await evaluate('closeDetailPanel()');
    await pause(450);
    if(width<=1150) assert.ok(await evaluate(`(() => {const e=document.querySelector('.detail-panel');return getComputedStyle(e).visibility==='hidden' && !document.body.classList.contains('detail-open') && e.getBoundingClientRect().x>=innerWidth-1})()`),'Detail closes');
    if(width<=760) {
      await evaluate('document.getElementById("menu-toggle").click()');
      assert.ok(await evaluate('document.querySelector(".sidebar").getBoundingClientRect().width>0'),'Menu opens');
      await evaluate('document.getElementById("mobile-backdrop").click()');
      await pause(450);
      assert.ok(await evaluate(`(() => {const e=document.querySelector('.sidebar');return getComputedStyle(e).visibility!=='visible' || e.getBoundingClientRect().right<=0})()`),'Menu closes');
    }
    console.log(`PASS ${width}px: no overflow/overlap; scroll isolated; detail and navigation OK`);
  }
  assert.deepEqual(errors, [], 'No runtime exceptions');
  console.log('PASS browser runtime exceptions: 0');
} finally { ws.close(); }
