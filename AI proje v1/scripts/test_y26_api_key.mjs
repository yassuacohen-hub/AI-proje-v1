#!/usr/bin/env node
// Y26 canli dogrulama: api-usage raporu + rotasyon + yeni key ile erisim.
import {readFileSync} from 'node:fs';
const B = 'http://localhost:8000';
const env = readFileSync('C:/Projeler/Huginn Data Insights/.env', 'utf8');
const DASH = (env.match(/DASH_API_KEY=(.+)/) || [])[1]?.trim();
const login = async (email, password) => (await (await fetch(B + '/api/buyer/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email, password})})).json());
const admin = (await login('admin@huginn.local', 'Admin2026!')).token;

// 1) api-usage raporu (baslangic)
let r = await fetch(B + '/api/admin/api-usage', {headers: {'Authorization': 'Bearer ' + admin}});
console.log('1-api-usage', r.status, JSON.stringify(await r.json()).slice(0, 120));

// 2) admin user_id + eski key
const me = await (await fetch(B + '/api/me?token=' + encodeURIComponent(admin))).json();
const prof = await (await fetch(B + '/api/buyer/profile?token=' + encodeURIComponent(admin))).json();
const eskiKey = prof.profil.api_key;

// 3) rotasyon
r = await fetch(B + '/api/admin/rotate-key', {method: 'POST', headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + admin}, body: JSON.stringify({user_id: me.user.user_id})});
const rkd = await r.json();
console.log('2-rotate-key', r.status, 'yeni=' + (rkd.api_key ? rkd.api_key.slice(0, 12) + '...' : '-'));

// 4) eski key artik 401 (public modda eski key red edilemez; sadece usage dogrulanir), yeni key 200
r = await fetch(B + '/api/kpi', {headers: {'X-API-Key': eskiKey}});
console.log('3-eski-key-kpi', r.status, '(public mod: 200 normal)');
r = await fetch(B + '/api/kpi', {headers: {'X-API-Key': rkd.api_key}});
console.log('4-yeni-key-kpi', r.status, '(200 beklenir)');

// 4b) rotasyon sonrasi DB'de eski key kalmamali
const profAfter = await (await fetch(B + '/api/buyer/profile?token=' + encodeURIComponent(admin))).json();
console.log('4b-db-eski-key-temizlendi', profAfter.profil.api_key !== eskiKey);

// 5) usage sayaci enterprise girisi yapti mi
r = await fetch(B + '/api/admin/api-usage', {headers: {'Authorization': 'Bearer ' + admin}});
const uad = await r.json();
console.log('5-api-usage-sonra', r.status, JSON.stringify(uad.items).slice(0, 160));
process.exit(0);