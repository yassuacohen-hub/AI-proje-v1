// Debug: renderIsletmem tip hatasini canli yakalar (CDP 9334).
import assert from 'node:assert/strict';
const tabs = await (await fetch('http://127.0.0.1:9334/json')).json();
const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const pend = new Map();
ws.addEventListener('message', ({ data }) => { const m = JSON.parse(data); if (pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); } });
const send = (method, params = {}) => new Promise(res => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expr) => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result?.value;
await send('Page.enable');
await send('Page.navigate', { url: 'http://127.0.0.1:8000/static/index.html' });
for (let i = 0; i < 40; i++) {
  const ok = await ev('typeof allCompanies!=="undefined"&&allCompanies.length>0&&!document.getElementById("content").classList.contains("hidden")');
  if (ok) break;
  await new Promise(r => setTimeout(r, 500));
}
const e1 = await ev('(function(){try{renderIsletmemTabs({email:"a@b.c"});return "OK";}catch(e){return e.message;}})()');
console.log('renderIsletmemTabs:', e1);
const login = await (await fetch('http://127.0.0.1:8000/api/buyer/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: 'admin@huginn.local' }) })).json();
const tok = login.token;
const e2 = await ev(`(function(){try{localStorage.setItem("huginn_member_token", ${JSON.stringify(tok)}); openIsletmem(); return "OK";}catch(e){return e.message + " @ " + (e.stack||"").split("\\n").slice(0,3).join(" << ");}})()`);
console.log('openIsletmem:', e2);
await new Promise(r => setTimeout(r, 2500));
const prof = await (await fetch('http://127.0.0.1:8000/api/buyer/profile?token=' + encodeURIComponent(tok))).json();
const e3 = await ev(`(function () {
  try {
    renderIsletmem(${JSON.stringify(prof)});
    const src = renderIsletmem.toString();
    const tipIdx = src.indexOf('tip(');
    return 'render OK | tip@' + tipIdx + ' | tabsCall=' + src.includes('renderIsletmemTabs');
  } catch (e) { return 'ERR ' + e.message + ' @ ' + (e.stack || '').split('\\n').slice(0, 3).join(' << '); }
})()`);
console.log('isletmem-body:', e3);
const e4 = await ev('(function(){try{switchIsletmemTab("info");return "OK";}catch(e){return e.message;}})()');
console.log('switchTab info:', e4);
const e5 = await ev('(function(){try{switchIsletmemTab("account");return "OK";}catch(e){return e.message;}})()');
console.log('switchTab account:', e5);
process.exit(0);