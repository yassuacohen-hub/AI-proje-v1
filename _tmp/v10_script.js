
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const ic=n=>`<svg class="ic"><use href="#i-${n}"/></svg>`;
const kabuk=$('#kabuk');
/* MENÜ VERİSİ: yan menü + bağlantı haritası buradan üretilir (tek kaynak) */
const MENU=[
 {g:'Genel',o:[
  {id:'ana',ad:'Genel Bakış',i:'home',t:'gercek',yol:'/panel',not:'Bu çizimin ana ekranı.'},
  {id:'firsat',ad:'Fırsatlar',i:'target',t:'cizilecek',say:5,yol:'/panel/firsatlar',not:'Çizilecek: 5 fırsat listesi + CSV dışa aktar (eski panelden).'},
  {id:'sirket',ad:'Şirket Kartı',i:'bld',t:'cizilecek',yol:'/panel/sirket',not:'Çizilecek: tek bakışta tüm puanlar (T0 §2.13).'},
  {id:'izlenen',ad:'İzlenen Firmalar',i:'star',t:'cizilecek',yol:'/panel/izlenen',not:'Eski panelde yıldızlı izleme listesi vardı; Next’te yok. Radar yuvasıyla (4/10) birleşir.'}]},
 {g:'Araçlar',o:[
  {id:'sektor',ad:'Sektör Radar',i:'trend',t:'gercek',yol:'/panel/sektor-radar',not:'Gerçek sayfa var.'},
  {id:'raporlab',ad:'Rapor Lab',i:'flask',t:'gercek',yol:'/panel/raporlab',not:'Gerçek sayfa var.'},
  {id:'radar',ad:'Radar',i:'radar',t:'beta',yol:'/panel/radar',not:'Sayfa yok; çizilecek, Beta.'},
  {id:'ubo',ad:'UBO Ağı',i:'net',t:'beta',yol:'/panel/ag',not:'Sayfa yok; Beta.'},
  {id:'dedektif',ad:'OSINT Dedektifi',i:'dedektif',t:'cizilecek',yol:'/panel/dedektif',not:'Butik hizmet: yalnız kayıt formu “Dosyanızı Açın” (D-397), kuyruklu. Plus 24 sa 750 kredi/37.500 ₺, Premium AMİRAL 48 sa 1.000 kredi/50.000 ₺ (+1 ücretsiz Mimir turu) — fiyatlar “katalog değeri”. Form sonrası: “Talebiniz alındı. Dosya numaranız kayda geçti — uzmanlarımız sizi arayacak.” Vaat satışa çıkana kadar yazılmaz; sayaç gerçek, eşik altı gizli (B25).'},
  {id:'api',ad:'API',i:'code',t:'beta',yol:'API sayfası (T0 §2.16)',not:'Geliştirici sayfası T0 §2.16’da tarif edildi; yok.'}]},
 {g:'Pazar',o:[
  {id:'esles',ad:'Eşleşme',i:'hand',t:'beta',yol:'/panel/eslesme',not:'AYRI SAYFA (gelişmiş senaryolar): yön tedarikçi/müşteri/rakip, kapsam komple zincir/aynı sektör, şehir/ölçek filtresi, kayıtlı senaryo, sonuç dışa aktar. Dashboard kartı + sağ üst ikon hızlı eşle (1 kredi). Eski FastAPI /api/match var; Next sayfası yok.'},
  {id:'satis',ad:'Satış Sinyali Radarı',i:'mega',t:'beta',yol:'/panel/satis-sinyali',not:'Eski kodda eşleşme yönü “müşteri”; ayrı sinyal beslemesi yok.'},
  {id:'alis',ad:'Alış Sinyali Radarı',i:'cart',t:'beta',yol:'/panel/alis-sinyali',not:'Eski kodda eşleşme yönü “tedarikçi”; ayrı sinyal beslemesi yok.'},
  {id:'pazar',ad:'Pazar Yeri',i:'store',t:'yakinda',yol:'/panel/pazar',not:'pazar_yeri.py yok; company_products 0 satır; faz-3 park.'},
  {id:'atil',ad:'Atıl Kapasite Radarı',i:'recycle',t:'yakinda',yol:'/panel/atil-kapasite',not:'company_capabilities 7.595 dolu ama ilan akışı yok; kancada 15 kredi planı.'}]},
 {g:'Hesap ve Destek',o:[
  {id:'isl',ad:'Benim İşletmem',i:'brief',t:'cizilecek',yol:'/panel/isletme',not:'4 sekme: Profil, İlanlarım (taslak→moderasyon→yayında; ilk ilana 3 kredi hediye, D-212), Fotoğraf ve Dosya (depolama ölçülmedi, Yakında), Vitrin önizleme (karşı müşteriye görünen sayfa; KVKK maskeli). Eski /api/buyer/profile (10 alan) yalnız Profil sekmesini besler.'},
  {id:'cuzdan',ad:'Paket ve Cüzdan',i:'wallet',t:'gercek',yol:'/panel/cuzdan',not:'Gerçek sayfa var.'},
  {id:'ayar',ad:'Ayarlar',i:'gear',t:'beta',yol:'/panel/ayarlar',not:'Sayfa yok; Beta. Bildirim tercihleri (e-posta/Telegram/webhook), dil, görünüm varsayılanları burada.'},
  {id:'ara',ad:'Aramalarım',i:'history',t:'cizilecek',yol:'/panel/aramalarim',not:'Eski panelde arama geçmişi vardı (search_events). Geri getirilecek: kayıtlı arama, tekrar çalıştır.'},
  {id:'disa',ad:'Dışa Aktar',i:'download',t:'cizilecek',yol:'/panel/disa-aktar',not:'Eski /api/companies/export (CSV) vardı. Kredi düşer; yetki scope.py paketine göre.'},
  {id:'fatura',ad:'Faturalar ve Ödemeler',i:'file',t:'cizilecek',yol:'/panel/faturalar',not:'Eski panelde ödeme geçmişi + kredi hareketleri (/api/buyer/ledger) + indirim kodu vardı. Paket ve Cüzdan sayfasına alt sekme olabilir.'},
  {id:'ekip',ad:'Ekip',i:'users',t:'beta',yol:'/panel/ekip',not:'Koltuk ve davet: /v1/ekip, /v1/ekip/davet, /v1/ekip/koltuk var; Next sayfası yok.'},
  {id:'anahtar',ad:'API Anahtarı ve Webhook',i:'key',t:'beta',yol:'/panel/api-anahtari',not:'Enterprise anahtar yenileme + webhook bildirimleri (eski panelde vardı). API sayfası T0 §2.16 ile birleşir.'},
  {id:'guv',ad:'Güvenlik',i:'shield',t:'cizilecek',yol:'/panel/guvenlik',not:'Giriş etkinliği (login_events), oturumlar, şifre değiştir (/api/buyer/change-password), MFA (şu an yalnız admin).'},
  {id:'destek',ad:'Destek',i:'headset',t:'cizilecek',yol:'/panel/destek',not:'Eski panelde destek talepleri vardı. Mimir yetmezse devir.'},
  {id:'yardim',ad:'Yardım',i:'help',t:'cizilecek',yol:'/panel/yardim',not:'Çizilecek.'}]}
];
const ROZ={gercek:['Gerçek','ok'],beta:['Beta','mor'],yakinda:['Yakında','warn'],cizilecek:['Çizilecek','warn']};
const YAZI={beta:'Beta sayfa: kod/tasarım tamam olmadan açılmaz. “Haber ver bana” ile kaydolunur.',yakinda:'Yakında: henüz yapılmadı. Haber ver bana ile bildirim iste.',cizilecek:'Bu sayfanın çizimi daha yapılmadı.',gercek:'Gerçek sayfa: üretimde var.'};
const TEK={};MENU.forEach(m=>m.o.forEach(x=>TEK[x.id]=x));
/* yan menü */
const yan=$('#yan');
yan.innerHTML=MENU.map(m=>`<div class="g"><button class="grup" aria-expanded="true"><span>${m.g}</span>${ic('chev')}</button><div class="g-ic">`+m.o.map(x=>`<a href="#" data-id="${x.id}" class="t-${x.t}${x.id==='ana'?' aktif':''}" title="${x.ad}${x.t==='beta'?' (Beta)':x.t==='yakinda'?' (Yakında)':''}">${ic(x.i)}<span class="etiket">${x.ad}</span>${x.say?`<span class="say">${x.say}</span>`:''}${x.t==='beta'?'<span class="beta">Beta</span>':x.t==='yakinda'?'<span class="yak">Yakında</span>':''}</a>`).join('')+`</div></div>`).join('')+
`<div class="yan-alt"><a href="#" data-id="isl" class="t-cizilecek" title="Benim İşletmem · %70 dolu"><span class="halka"></span><span class="etiket">İşletmem · %70 dolu</span></a><button id="dil-btn" title="Dil" aria-expanded="false">${ic('lang')}<span class="alt-yazi">Dil: Türkçe</span></button></div>`;
/* pencereler: hepsi aynı anchor */
const pops={'#uyari-btn':'#uyari-pop','#esles-btn':'#esles-pop','#mimir-btn':'#mimir-pop','#paket-btn':'#paket-pop','#avatar-btn':'#avatar-pop','#dil-btn':'#dil-pop','#ozel-btn':'#ozel-pop'};
function kapat(){$$('.pop').forEach(p=>p.classList.remove('acik'));Object.keys(pops).forEach(b=>$(b)?.setAttribute('aria-expanded','false'))}
Object.entries(pops).forEach(([b,p])=>{$(b).addEventListener('click',e=>{e.stopPropagation();const ac=$(p).classList.contains('acik');kapat();if(!ac){$(p).classList.add('acik');$(b).setAttribute('aria-expanded','true')}})});
document.addEventListener('click',e=>{if(!e.target.closest('.pop'))kapat()});
document.addEventListener('keydown',e=>{if(e.key==='Escape')kapat()});
$$('.pop [data-git]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();git(a.dataset.git)}));
$$('[data-dil]').forEach(b=>b.addEventListener('click',()=>{if(b.dataset.dil==='Türkçe')kapat()}));
$('#yukselt').addEventListener('click',()=>git('cuzdan'));
/* menü şekli */
const toggle=()=>{kabuk.classList.toggle('dar')};
$('#yan-toggle').addEventListener('click',toggle);$('#sekil-toggle').addEventListener('click',toggle);
$$('.grup').forEach(g=>g.addEventListener('click',()=>{if(kabuk.classList.contains('dar'))return;const gg=g.parentElement;gg.classList.toggle('kapali');g.setAttribute('aria-expanded',!gg.classList.contains('kapali'))}));
/* sayfa geçişi */
let aktifYer=null;
function git(id){
  const x=TEK[id]||{ad:id,t:'cizilecek',yol:'',not:''};
  $$('.yan a[data-id]').forEach(a=>a.classList.toggle('aktif',a.dataset.id===id));
  $('#yol-ad').textContent=x.ad;
  $('#s-isl').hidden=id!=='isl';
  if(id==='ana'){$('#s-ana').hidden=false;$('#s-yer').hidden=true;return}
  aktifYer=id;$('#s-ana').hidden=true;
  if(id==='isl'){$('#s-yer').hidden=true;kapat();return}
  $('#s-yer').hidden=false;
  $('#yer-ad').textContent=x.ad;
  const r=ROZ[x.t];$('#yer-rozet').innerHTML=`<span class="rozet ${r[1]}">${r[0]}</span>`;
  $('#yer-metin').textContent=`${YAZI[x.t]} ${x.not}`;
  $('#yer-yol2').textContent=x.yol;kapat();
}
$$('.yan a[data-id]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();git(a.dataset.id)}));
$$('[data-git]').forEach(b=>{if(!b.closest('.pop'))b.addEventListener('click',e=>{e.preventDefault();git(b.dataset.git)})});
$('#geri-ana').addEventListener('click',()=>git('ana'));
const haber=b=>b.addEventListener('click',()=>{b.textContent='Kaydedildi ✓ (örnek)';b.disabled=true});
haber($('#haber-ver'));haber($('#yer-haber'));
$$('.mini.kat').forEach(b=>b.addEventListener('click',()=>b.closest('.wg').classList.toggle('kapali')));
$('#tema-gece').addEventListener('click',()=>document.documentElement.dataset.tema='gece');
$('#tema-gunduz').addEventListener('click',()=>document.documentElement.dataset.tema='gunduz');
/* harita: şehir seç → yakınlaş (tüm sayılar ÖRNEK) */
const SEH={'Tüm şehirler':{x:150,y:80,z:1},'Ankara':{x:150,y:78,z:2.6},'İstanbul':{x:62,y:55,z:2.6},'İzmir':{x:38,y:92,z:2.6},'Bursa':{x:76,y:66,z:2.6},'Konya':{x:140,y:104,z:2.6}};
const KRIT={Durum:['Faaliyette','Yapım aşamasında','Planlanan / ilan edilecek'],Doluluk:['%0–50','%51–80','%81 ve üzeri'],'Sektör':['Metal / Makina','Gıda','Tekstil']};
const SAY={'Tüm şehirler':[[40,12,9],[20,18,23],[31,22,14]],Ankara:[[14,4,3],[6,8,7],[10,6,5]],'İstanbul':[[9,3,2],[5,4,9],[6,7,4]],'İzmir':[[7,2,2],[3,3,5],[5,4,2]],Bursa:[[5,2,1],[2,3,2],[4,3,2]],Konya:[[5,1,1],[4,0,2],[6,2,1]]};
let kr='Durum',sh='Tüm şehirler',z=1;
const sel=$('#sehir');sel.innerHTML=Object.keys(SEH).map(k=>`<option>${k}</option>`).join('');
$('#hr-nok').innerHTML=Object.entries(SEH).filter(([k])=>k!=='Tüm şehirler').map(([k,v])=>`<circle cx="${v.x}" cy="${v.y}" r="4" fill="var(--act)"/><text x="${v.x+6}" y="${v.y+3}" font-size="7" fill="var(--t2)" font-family="Inter">${k}</text>`).join('');
function haritaCiz(){
  const s=SEH[sh],k=Math.min(z,5),dx=150-s.x*k,dy=80-s.y*k;
  $('#hr').style.transform=`translate(${dx}px,${dy}px) scale(${k})`;$('#hr').style.transformOrigin='0 0';
  $('#h-baslik').textContent=sh==='Tüm şehirler'?'Tüm şehirler':sh+' · yeni / planlanan OSB';
  const v=SAY[sh]||SAY['Tüm şehirler'];
  $('#h-toplam').innerHTML=KRIT[kr].map((a,i)=>{const n=v[i][ ['Durum','Doluluk','Sektör'].indexOf(kr) ];return `<div class="satir"><div class="ad">${a}</div><b class="mono" style="color:var(--t1)">${n}</b></div>`}).join('');
}
sel.addEventListener('change',()=>{sh=sel.value;z=SEH[sh].z;haritaCiz()});
$('#z-art').addEventListener('click',()=>{z=Math.min(5,z+.6);haritaCiz()});
$('#z-az').addEventListener('click',()=>{z=Math.max(1,z-.6);haritaCiz()});
$$('#w-harita .seg button').forEach(b=>b.addEventListener('click',()=>{kr=b.dataset.k;$$('#w-harita .seg button').forEach(x=>x.setAttribute('aria-pressed',x===b));haritaCiz()}));
haritaCiz();
/* ===== V10 etkileşimler (tüm sayılar ÖRNEK) ===== */
const gunAd=k=>k===0?'bugün':k===1?'dün':new Date(Date.now()-k*864e5).toLocaleDateString('tr-TR',{day:'numeric',month:'short'});
/* düzen: KPI üstte / Fırsatlar üstte (hakem sorusu) */
$$('#duzen button').forEach(b=>b.addEventListener('click',()=>{$$('#duzen button').forEach(x=>x.setAttribute('aria-pressed',x===b));$('#s-ana .izgara').classList.toggle('firsat-ilk',b.dataset.d==='firsat')}));
$('#k-uyari').after($('#kpi-detay'));
/* fırsat grafiği: aralık, hover ipucu, tıkla → gün özeti, uyum süzgeci */
const FB=Array.from({length:30},(_,i)=>(i*5+2)%6+1);FB[28]=2;FB[29]=5;
function fgCiz(n){
  $('#fg').innerHTML='<span class="gtip" id="fg-tip"></span>'+FB.slice(-n).map((x,i)=>`<i tabindex="0" data-g="${n-1-i}" data-x="${x}" style="height:${x/6*100}%;animation-delay:${i*18}ms" aria-label="${gunAd(n-1-i)}: ${x} fırsat"></i>`).join('');
  $('#fg-et').innerHTML=`<span>${n-1} gün önce</span><span>bugün</span>`;
  $('#fg-detay').textContent='Çubuğa tıkla: o günün fırsat özeti burada açılır.';
}
$('#fg-aralik').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;$$('#fg-aralik button').forEach(x=>x.setAttribute('aria-pressed',x===b));fgCiz(+b.dataset.n)});
const fgEl=$('#fg');
const fgTip=e=>{const i=e.target.closest('i'),t=$('#fg-tip');if(!i){t.style.display='none';return}t.textContent=`${gunAd(+i.dataset.g)}: ${i.dataset.x} fırsat`;t.style.left=i.offsetLeft+i.offsetWidth/2+'px';t.style.display='block'};
fgEl.addEventListener('mouseover',fgTip);fgEl.addEventListener('focusin',fgTip);fgEl.addEventListener('mouseleave',()=>{$('#fg-tip').style.display='none'});
const fgSec=i=>{$$('#fg i').forEach(x=>x.classList.toggle('sec',x===i));const x=+i.dataset.x;$('#fg-detay').innerHTML=`<b>${gunAd(+i.dataset.g)}</b>: ${x} fırsat · ${Math.round(x*.4)} tanesi 80+ uyum <span class="ornek">Örnek</span> <button class="btn kucuk" onclick="git('firsat')">Bu günün listesi →</button>`};
fgEl.addEventListener('click',e=>{const i=e.target.closest('i');if(i)fgSec(i)});
fgEl.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){const i=e.target.closest('i');if(i){e.preventDefault();fgSec(i)}}});
fgCiz(14);
$('#fg-sz').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;$$('#fg-sz button').forEach(x=>x.setAttribute('aria-pressed',x===b));const u=+b.dataset.u;
  $$('#fg-liste .satir').forEach(r=>{const p=r.querySelector('.rozet'),s=p?+p.textContent.replace(/\D/g,''):-1;r.classList.toggle('gizli',u===0?false:u===80?s<80:!(s>=60&&s<80))})});
/* radar: nokta/satır → özet, süzgeç */
const RD={'BETA TEKSTİL':'Unvan değişti, 2 saat önce. Öneri: yeni unvanı Şirket Kartı’nda doğrula.','ACME MAKİNA':'Çelişki 2, 3 gündür açık. Öneri: Dedektife sor.','ÖZ-KAR GIDA':'Yeni tesis sinyali, bugün. Öneri: Fırsatlar’a bak.'};
function rdSec(f){$$('#w-radar .nok').forEach(n=>n.classList.toggle('sec',n.dataset.f===f));$('#radar-detay').innerHTML=`<b>${f}</b> · ${RD[f]||''} <span class="ornek">Örnek</span> <button class="btn kucuk" onclick="git('sirket')">Şirket Kartı →</button>`}
$$('#w-radar .nok').forEach(n=>n.addEventListener('click',()=>rdSec(n.dataset.f)));
$$('#w-radar .satir[data-t]').forEach(s=>{s.style.cursor='pointer';s.addEventListener('click',()=>rdSec(s.querySelector('b').textContent))});
$('#rd-sz').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;$$('#rd-sz button').forEach(x=>x.setAttribute('aria-pressed',x===b));const t=b.dataset.t;
  $$('#w-radar .satir[data-t]').forEach(r=>r.classList.toggle('gizli',t!=='tum'&&r.dataset.t!==t));
  $$('#w-radar .nok').forEach(n=>{n.style.opacity=t==='tum'||n.dataset.t===t?1:.2})});
/* KPI: tıkla → altında detay şeridi; tekrar tıkla kapanır */
const KD={
 kredi:{b:'Kalan Kredi',m:'Bu hafta 6 kredi harcandı (Rapor Lab 5, Eşleşme 1). Bu hızla yaklaşık 7 hafta yeter.',s:[1,0,2,0,1,2,0],g:['Paket ve Cüzdan','cuzdan']},
 radar:{b:'Radardaki Şirket',m:'10 yuvanın 4’ü dolu. 3 yeni sinyal, 1 riskli firma var.',s:[2,3,3,4,4,4,4],g:['İzlenen Firmalar','izlenen']},
 esles:{b:'Yeni Eşleşme',m:'Son 24 saatte 3 eşleşme; dün 2 idi. En yüksek puan 82.',s:[1,0,2,1,2,2,3],g:['Eşleşme','esles']},
 uyari:{b:'Kapanan Uyarı',m:'Bu ay 7 sinyal çözüldü, 1 tanesi açık.',s:[0,1,1,2,0,2,1],g:['Radar','radar']}
};
function kpiAc(k){
  const d=$('#kpi-detay'),acik=d.classList.contains('acik')&&d.dataset.k===k;
  $$('.kpi').forEach(x=>x.classList.toggle('sec',!acik&&x.dataset.kpi===k));
  d.classList.toggle('acik',!acik);d.dataset.k=k;
  if(acik)return;
  const o=KD[k],mx=Math.max(...o.s,1);
  $('#kpi-detay-ic').innerHTML=`<div style="display:flex;gap:18px;align-items:flex-end;flex-wrap:wrap;justify-content:space-between"><div style="flex:1;min-width:240px"><b style="color:var(--t1)">${o.b}</b> <span class="ornek">Örnek</span><p style="margin:4px 0 0">${o.m}</p></div><div style="width:220px"><small style="color:var(--t3)">Son 7 gün</small><div class="gcub" style="height:44px;margin:4px 0 0">${o.s.map(x=>`<i style="height:${Math.max(6,x/mx*100)}%"></i>`).join('')}</div></div><div style="display:flex;gap:8px"><button class="btn kucuk" onclick="git('${o.g[1]}')">${o.g[0]} →</button><button class="btn kucuk" onclick="kpiAc('${k}')">Kapat</button></div></div>`;
}
$$('.kpi').forEach(k=>{k.addEventListener('click',()=>kpiAc(k.dataset.kpi));k.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target===k){e.preventDefault();kpiAc(k.dataset.kpi)}})});
/* ⓘ: her karta "bu kart şu soruyu cevaplar" ipucu [soru, ne, nasıl] */
const BIL={
 'k-kredi':['Ne kadar hakkım kaldı?','Kalan kredi ve harcama hızı.','Karta tıkla: son 7 günlük harcama.'],
 'k-radar':['Kaç yuvam boş?','Radardaki firma sayısı ve boş yuva.','Karta tıkla: yuva durumu.'],
 'k-esles':['Yeni eşleşme geldi mi?','Son 24 saatteki eşleşme sayısı.','Karta tıkla: dünle karşılaştırma.'],
 'k-uyari':['Açık sorunum kaldı mı?','Bu ay çözülen ve açık kalan uyarılar.','Karta tıkla: 7 günlük seyir.'],
 'w-firsat':['Bugün kiminle iş konuşmalıyım?','Size uyan yeni firmalar, günlük sayı ve uyum puanı.','Çubuğa tıkla: o günün özeti. Süzgeçle uyumu seç. Kilitli satır 2 kredi.'],
 'w-radar':['İzlediğim firmalarda ne değişti?','İzlenen firmaların yeni sinyalleri ve riskleri.','Noktaya tıkla: firma özeti. “Riskli” süzgeci yalnız riskleri gösterir.'],
 'w-sirket':['Bu firmaya güvenebilir miyim?','Tek bakışta puanlar: kurumsallık, güvenilirlik, şeffaflık, risk.','Kartı aç: puanın kaynağı ve nedeni.'],
 'w-sinyal':['Son 24 saatte ne oldu?','Radardaki firmalardan gelen en yeni olaylar.','Çelişki görürsen “Dedektife sor”.'],
 'w-trend':['Pazar yükseliyor mu, düşüyor mu?','Sektör hareketi ve kendi ilgin yan yana.','Çiplere bak; “Bu ne demek?” ile açıklama iste.'],
 'w-harita':['Nerede yeni fırsat var?','Şehir bazında yeni ve planlanan OSB sayıları.','Şehir seç, yakınlaş; kriter: durum, doluluk, sektör.'],
 'w-satis':['Kim benden alabilir?','Satış sinyali veren firmalar.','Tümünü aç: 1 kredi.'],
 'w-alis':['Kimden alabilirim?','Alış sinyali veren firmalar.','Tümünü aç: 1 kredi.'],
 'w-dedektif':['Veri yetmiyorsa kim araştırır?','Uzman ekip dosya açar (butik hizmet).','“Dosyanızı Açın” formunu doldur.'],
 'w-esles':['Kimle iş yapmalıyım?','Sektör, konum, kalite ve kanıta göre puanlı eşleşme.','4 adım: ne arıyorsun, kimi, neye önem, eşle. 1 kredi.'],
 'w-islem':['Kredimi nereye harcadım?','Son harcamalarının kısa listesi.','Tam geçmiş Paket ve Cüzdan’da.']
};
Object.entries(BIL).forEach(([id,[q,ne,na]])=>{
  const el=$('#'+id),h=el.classList.contains('kpi')?$('.ust',el):$('.wg-bas h3',el);if(!h)return;
  h.insertAdjacentHTML('beforeend',`<button class="bilgi" type="button" aria-label="Bu kart ne işe yarar: ${q}"><svg class="ic"><use href="#i-info"/></svg><span class="tip" role="tooltip"><b>Bu kart şu soruyu cevaplar</b>“${q}”<br>${ne}<small>Nasıl kullanılır: ${na}</small></span></button>`);
  const b=h.lastElementChild;b.addEventListener('click',e=>e.stopPropagation());
  ['mouseenter','focus'].forEach(ev=>b.addEventListener(ev,()=>b.classList.toggle('sag',b.getBoundingClientRect().left>innerWidth/2)));
});
/* görünümü özelleştir: kart aç/kapa, tarayıcıda saklanır */
const OZ=[['k-kredi','Kalan Kredi'],['k-radar','Radardaki Şirket'],['k-esles','Yeni Eşleşme'],['k-uyari','Kapanan Uyarı'],['w-firsat','Fırsatlar'],['w-radar','Radarım'],['w-sirket','Şirket Kartı'],['w-sinyal','Son Sinyaller'],['w-trend','Trend'],['w-harita','Harita'],['w-satis','Satış Sinyali'],['w-alis','Alış Sinyali'],['w-dedektif','OSINT Dedektifi'],['w-esles','Akıllı Eşleşme'],['w-islem','Son İşlemler']];
const OZK='huginn_v10_gizli';let gz=[];try{gz=JSON.parse(localStorage.getItem(OZK)||'[]')}catch(e){}
const ozUygula=()=>{OZ.forEach(([id])=>$('#'+id).classList.toggle('gizli',gz.includes(id)));try{localStorage.setItem(OZK,JSON.stringify(gz))}catch(e){}};
const ozCiz=()=>{$('#oz-liste').innerHTML=OZ.map(([id,ad])=>`<div class="oz-satir"><span>${ad}</span><label class="anahtar"><input type="checkbox" data-id="${id}" aria-label="${ad} kartını göster"${gz.includes(id)?'':' checked'}><i></i></label></div>`).join('')};
$('#oz-liste').addEventListener('change',e=>{const c=e.target;gz=c.checked?gz.filter(x=>x!==c.dataset.id):[...gz,c.dataset.id];ozUygula()});
$('#oz-sifirla').addEventListener('click',()=>{gz=[];ozCiz();ozUygula()});
$('#oz-kapat').addEventListener('click',kapat);
ozCiz();ozUygula();
/* akıllı eşleşme: 4 adım, ağırlık kaydırıcıları, puan kırılımı (ÖRNEK) */
const EW={s:45,k:20,f:25,g:10},EN={s:'sektör',k:'konum',f:'kalite',g:'kanıt'},EK=['s','k','f','g'];
const EF=[['KAYA METAL SAN.',[100,80,72,30]],['DEMİR ÇELİK A.Ş.',[100,60,68,30]],['YILDIZ MAKİNA',[84,70,56,20]]];
const eAdim=a=>{$$('#e-adimlar .adim').forEach(x=>x.classList.toggle('aktif',x.dataset.a===String(a)));$$('.e-adim').forEach(x=>x.classList.toggle('gizli',x.dataset.a!==String(a)))};
$('#e-adimlar').addEventListener('click',e=>{const b=e.target.closest('.adim');if(b)eAdim(b.dataset.a)});
const eOzet=()=>{const t=EW.s+EW.k+EW.f+EW.g;$('#w-top').textContent=t;$('#e-ozet').textContent=`${$('#e-sektor').value.split(' (')[0]} · ${$('#e-yon').value} · ${$('#e-kap').value.toLowerCase()} · ağırlık ${EW.s}/${EW.k}/${EW.f}/${EW.g}`+(t===100?'':` (toplam ${t}, oranlanır)`)};
$$('input[data-w]').forEach(r=>r.addEventListener('input',()=>{EW[r.dataset.w]=+r.value;$('#w-'+r.dataset.w).textContent=r.value;eOzet()}));
['#e-sektor','#e-yon','#e-kap'].forEach(s=>$(s).addEventListener('change',eOzet));
$('#e-git').addEventListener('click',()=>{
  const t=EW.s+EW.k+EW.f+EW.g;if(!t){$('#e-sonuc').textContent='Tüm ağırlıklar 0: en az birine önem ver.';return}
  const R=EF.map(([ad,r])=>{const p=EK.map((k,i)=>EW[k]*r[i]/t);return [ad,Math.round(p.reduce((a,b)=>a+b,0)),p,r]}).sort((a,b)=>b[1]-a[1]);
  $('#e-sonuc').innerHTML=R.map(([ad,sk,p,r])=>`<div class="es-s" tabindex="0"><div><b>${ad}</b><div class="es-k gizli">${EK.map((k,i)=>`${EN[k]} ${r[i]}→${Math.round(p[i])}`).join(' + ')} = ${sk}</div></div><span class="rozet ${sk>75?'ok':'info'}">${sk}</span></div>`).join('')+`<small style="color:var(--t3)">${$('#e-sektor').value} · örnek sonuç · satıra tıkla: puan nasıl çıktı</small>`;
});
const esTog=e=>{const s=e.target.closest('.es-s');if(s)$('.es-k',s).classList.toggle('gizli')};
$('#e-sonuc').addEventListener('click',esTog);
$('#e-sonuc').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();esTog(e)}});
$('#e-kaydet').addEventListener('click',()=>{$('#w-esles .oneri').insertAdjacentHTML('beforeend',`<span>${$('#e-sektor').value.split(' (')[0]} ${$('#e-yon').value.toLowerCase()} · ${EW.s}/${EW.k}/${EW.f}/${EW.g}</span>`)});
/* benim işletmem: sekmeler, ilan türü, moderasyon, vitrin anahtarı */
$('#isl-sek').addEventListener('click',e=>{const b=e.target.closest('button[data-s]');if(!b)return;$$('#isl-sek button').forEach(x=>x.setAttribute('aria-selected',x===b));$$('#s-isl .sekme').forEach(s=>s.classList.toggle('acik',s.dataset.s===b.dataset.s))});
$$('#il-tur button').forEach(b=>b.addEventListener('click',()=>$$('#il-tur button').forEach(x=>x.setAttribute('aria-pressed',x===b))));
const ilg=$('#il-gonder');ilg.addEventListener('click',()=>{ilg.textContent='Moderasyona gönderildi ✓ (örnek)';ilg.disabled=true});
$('#vit-ac').addEventListener('change',e=>{$('#vit').style.opacity=e.target.checked?1:.35});
/* bağlantı haritası: menüden üretilir */
const D=(a,n,h,d,o)=>({a,n,h,d,o});
const ST={gercek:'Gerçek',beta:'Beta',yakinda:'Yakında',cizilecek:'Çizilecek',bu:'Bu sayfada'};
const ROW=[
 ['Üst çubuk',null],
 D('Menü düğmesi','İkon şeridi ⇄ geniş menü','Aynı sayfa','bu','tanımsız'),
 D('Logo','Genel Bakış’a döner','/panel','gercek','tanımsız'),
 D('Yol göstergesi','Üst sayfaya döner','Aktif sayfa','bu','tanımsız'),
 D('Arama kutusu','Yazarken öneri; Enter → Şirket Kartı','/panel/sirket','cizilecek','search.submit'),
 D('“/” kısayolu','Aramaya odaklanır','Aynı sayfa','bu','tanımsız'),
 D('Uyarı ikonu (ilk)','Uyarılar penceresi açılır','Pencere','bu','tanımsız'),
 D('Uyarı satırı','İlgili radar kaydına gider','/panel/radar','beta','alert.open'),
 D('Mimir ikonu','Mimir penceresi açılır','Pencere','bu','tanımsız'),
 D('Mimir → Tam ekran aç','Mimir sayfası','Mimir sayfası','cizilecek','tanımsız'),
 D('Paket rozeti','Paket penceresi açılır','Pencere','bu','tanımsız'),
 D('Yükselt ↑','Paket ve Cüzdan’a gider','/panel/cuzdan','gercek','upgrade.click'),
 D('Avatar','Profil penceresi açılır','Pencere','bu','tanımsız'),
 D('Profil → Hesap bilgilerim','Benim İşletmem','/panel/isletme','cizilecek','tanımsız'),
 D('Profil → Klavye kısayolları','Kısayol listesi','Pencere','cizilecek','tanımsız'),
 D('Profil → Çıkış','Oturum kapanır','/giris','cizilecek','auth.logout'),
 D('Dil ikonu (sol şerit)','Dil penceresi (şeridin sağına)','Pencere','bu','tanımsız'),
 D('Dil → English','Arayüz dili değişir','Tüm panel','cizilecek','locale.change'),
 ['Menü',null],
 ...MENU.flatMap(m=>m.o.map(x=>D(`${x.ad}${x.say?' ['+x.say+']':''}`,x.id==='ana'?'Genel Bakış gösterilir':(x.t==='gercek'?'Sayfa açılır':'Yer tutucu sayfa + “Haber ver bana”'),x.yol,x.t,x.t==='gercek'?'nav.open':'tanımsız'))),
 ['Genel Bakış kartları',null],
 D('Fırsatlar → satır','Şirket Kartı açılır','/panel/sirket','cizilecek','opportunity.open'),
 D('Fırsatlar → Kilidi aç','2 kredi düşer, satır açılır','Aynı kart','cizilecek','credit.spend'),
 D('Radarım → Aç','Radar sayfası','/panel/radar','beta','tanımsız'),
 D('Radarım → Firma ekle','Firma seçici','Pencere','cizilecek','radar.add'),
 D('Radarım → İzlenenler','İzlenen Firmalar sayfası','/panel/izlenen','cizilecek','tanımsız'),
 D('KPI Kalan Kredi','Paket ve Cüzdan','/panel/cuzdan','gercek','tanımsız'),
 D('Şirket Kartı → Kartı aç','Şirket Kartı sayfası','/panel/sirket','cizilecek','tanımsız'),
 D('Harita → Şehir kutusu','Seçilen şehre yakınlaşır, toplamlar yenilenir','Aynı kart','bu','map.city'),
 D('Harita → +/−','Yakınlaştırır / uzaklaştırır','Aynı kart','bu','tanımsız'),
 D('Harita → Kriter','Durum / Doluluk / Sektör toplamı','Aynı kart','bu','map.criteria'),
 D('Satış Sinyali → Tümünü aç','1 kredi, liste sayfası','/panel/satis-sinyali','beta','signal.open'),
 D('Alış Sinyali → Tümünü aç','1 kredi, liste sayfası','/panel/alis-sinyali','beta','signal.open'),
 D('Eşleşme → Eşle','1 kredi, örnek sonuç','Aynı kart','bu','match.run'),
 D('Eşleşme → Gelişmiş eşleşme →','Ayrı Eşleşme sayfası','/panel/eslesme','beta','match.advanced'),
 D('Eşleşme ikonu (sağ üst)','Hızlı eşleşme penceresi','Pencere','bu','tanımsız'),
 D('Eşleşme penceresi → Hızlı eşle','1 kredi, örnek sonuç','Pencere','bu','match.run'),
 ['OSINT Dedektifi (kanca seti)',null],
 D('Menü → OSINT Dedektifi','Dedektif sayfası + kayıt formu','/panel/dedektif','cizilecek','detective.open'),
 D('Dedektif kartı → Dosyanızı Açın','Kayıt formu; kuyruk bildirimi','/panel/dedektif','cizilecek','detective.form'),
 D('Şirket Kartı → Dedektife sor','Veri eksik firma için dosya açar','/panel/dedektif','cizilecek','detective.from_card'),
 D('Son Sinyaller → Çelişki → Dedektife sor','Çelişkili firma için dosya açar','/panel/dedektif','cizilecek','detective.from_signal'),
 D('Trend → “Bu ne demek?” bağlantısı','Çelişkili 2 firma için dosya açar','/panel/dedektif','cizilecek','detective.from_trend'),
 D('Mimir → Dedektife devret','Mimir cevabı yetmezse dosya açar','/panel/dedektif','cizilecek','detective.from_mimir'),
 D('Paket penceresi → Dedektif satırı','Premium/Plus bilgisi','/panel/dedektif','cizilecek','detective.from_pack'),
 ['Fırsat ve Trend altı',null],
 D('Fırsatlar → 7/14/30 gün seçici','Çubuk sayısı değişir','Aynı kart','bu','tanımsız'),
 D('Fırsatlar → çubuğa gel / tıkla','Gün sayısı ipucu; tıkla: alt şeritte detay + “Listeyi aç”','Aynı kart','bu','opportunity.day'),
 D('Fırsatlar → uyum dağılımı (tıkla)','Listeyi uyum bandına göre süzer','Aynı kart','bu','opportunity.filter'),
 ['V10 etkileşim katmanı',null],
 D('KPI kartı → tıkla','Kartın altında 7 günlük mini grafik + “Sayfayı aç”; tekrar tıkla kapanır','Aynı kart','bu','kpi.detail'),
 D('Düzen → KPI önce / Fırsat önce','KPI sırası değişir (hakeme sorulacak, K14)','Genel Bakış','bu','layout.order'),
 D('Her kartta ⓘ','Hover/odak: “Bu kart şu soruyu cevaplar” + ne + nasıl kullanılır','Aynı kart','bu','tanımsız'),
 D('Görünümü özelleştir','Kart aç/kapat; seçim yerelde saklanır; Sıfırla','Pencere','bu','prefs.layout'),
 D('Radar → nokta / satır tıkla','Sağ altta firma özeti; süzgeç çipi','Aynı kart','bu','radar.select'),
 D('Eşleşme → 4 adım','Ne arıyorsun → Yön/kapsam → Önem (ağırlık) → Sonuç + neden kırılımı','Aynı kart','bu','match.run'),
 D('Eşleşme → Senaryoyu kaydet','Öneri listesine eklenir (örnek)','Aynı kart','cizilecek','match.save'),
 ['Benim İşletmem (V10)',null],
 D('Sekmeler → Profil / İlanlarım / Fotoğraf ve Dosya / Vitrin','Sekme geçişi','/panel/isletme','cizilecek','tanımsız'),
 D('İlanlarım → Moderasyona gönder','Taslak → onay kuyruğu (örnek)','/panel/isletme','cizilecek','listing.submit'),
 D('Fotoğraf / Dosya → Yükle','Yakında: depolama ölçülmedi','/panel/isletme','yakinda','media.upload'),
 D('Vitrin → Herkese açık göster','Karşı müşteriye görünen sayfa aç/kapat (KVKK maskeli)','/panel/isletme','cizilecek','showcase.toggle'),
 D('Trend → 4 özet çip','Sayılar yükleme animasyonuyla sayar','Aynı kart','bu','tanımsız'),
 D('Yakında → Haber ver bana','İstek kaydedilir','Aynı kart','cizilecek','waitlist.join')
];
let n=0;$('#harita-tablo').insertAdjacentHTML('beforeend',ROW.map(r=>Array.isArray(r)?`<tr><td colspan="6" style="background:var(--raised);color:var(--t1)"><b>${r[0]}</b></td></tr>`:`<tr><td class="mono">${++n}</td><td><b>${r.a}</b></td><td>${r.n}</td><td class="mono">${r.h}</td><td><span class="rozet ${r.d==='gercek'?'ok':r.d==='beta'?'mor':r.d==='bu'?'info':'warn'}">${ST[r.d]}</span></td><td class="mono">${r.o}</td></tr>`).join(''));
/* tek seferlik yükleme animasyonu: sayılar 0'dan sayar (azaltılmış hareket ayarı varsa atlanır) */
(()=>{if(matchMedia('(prefers-reduced-motion:reduce)').matches)return;
  $$('[data-say]').forEach(el=>{const h=+el.dataset.say,ek=el.dataset.ek||'',t0=performance.now();
    (function adim(t){const p=Math.min(1,(t-t0)/900);el.textContent=Math.round(h*(1-Math.pow(1-p,3)))+ek;if(p<1)requestAnimationFrame(adim)})(t0)})})();
