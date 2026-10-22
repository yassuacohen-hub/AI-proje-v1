
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
  {id:'isl',ad:'Benim İşletmem',i:'brief',t:'cizilecek',yol:'/panel/isletme',not:'Eski /api/buyer/profile (10 alan, tamlama %) var; Next sayfası yok.'},
  {id:'cuzdan',ad:'Paket ve Cüzdan',i:'wallet',t:'gercek',yol:'/panel/cuzdan',not:'Gerçek sayfa var.'},
  {id:'ayar',ad:'Ayarlar',i:'gear',t:'beta',yol:'/panel/ayarlar',not:'Sayfa yok; Beta.'},
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
const pops={'#uyari-btn':'#uyari-pop','#esles-btn':'#esles-pop','#mimir-btn':'#mimir-pop','#paket-btn':'#paket-pop','#avatar-btn':'#avatar-pop','#dil-btn':'#dil-pop'};
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
  if(id==='ana'){$('#s-ana').hidden=false;$('#s-yer').hidden=true;return}
  aktifYer=id;$('#s-ana').hidden=true;$('#s-yer').hidden=false;
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
$$('.seg button').forEach(b=>b.addEventListener('click',()=>{kr=b.dataset.k;$$('.seg button').forEach(x=>x.setAttribute('aria-pressed',x===b));haritaCiz()}));
haritaCiz();
/* eşleşme: örnek sonuç */
$('#e-git').addEventListener('click',()=>{
  const s=$('#e-sektor').value;
  $('#e-sonuc').innerHTML=[['KAYA METAL SAN.',82,'45+16+18+3'],['DEMİR ÇELİK A.Ş.',77,'45+12+17+3'],['YILDIZ MAKİNA',68,'38+14+14+2']].map(r=>`<div class="satir"><div class="ad"><b>${r[0]}</b><small class="mono">sektör+konum+kalite+kanıt = ${r[2]}</small></div><span class="rozet ${r[1]>75?'ok':'info'}">${r[1]}</span></div>`).join('')+`<small style="color:var(--t3)">${s} · örnek sonuç</small>`;
});
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
 D('Fırsatlar → 14 gün çubuk grafiği','Gün üstüne gelince sayı (örnek)','Aynı kart','bu','tanımsız'),
 D('Fırsatlar → uyum dağılımı','Yüksek/orta/düşük uyum payı (örnek)','Aynı kart','bu','tanımsız'),
 D('Trend → 4 özet çip','Sayılar yükleme animasyonuyla sayar','Aynı kart','bu','tanımsız'),
 D('Yakında → Haber ver bana','İstek kaydedilir','Aynı kart','cizilecek','waitlist.join')
];
let n=0;$('#harita-tablo').insertAdjacentHTML('beforeend',ROW.map(r=>Array.isArray(r)?`<tr><td colspan="6" style="background:var(--raised);color:var(--t1)"><b>${r[0]}</b></td></tr>`:`<tr><td class="mono">${++n}</td><td><b>${r.a}</b></td><td>${r.n}</td><td class="mono">${r.h}</td><td><span class="rozet ${r.d==='gercek'?'ok':r.d==='beta'?'mor':r.d==='bu'?'info':'warn'}">${ST[r.d]}</span></td><td class="mono">${r.o}</td></tr>`).join(''));
/* tek seferlik yükleme animasyonu: sayılar 0'dan sayar (azaltılmış hareket ayarı varsa atlanır) */
(()=>{if(matchMedia('(prefers-reduced-motion:reduce)').matches)return;
  $$('[data-say]').forEach(el=>{const h=+el.dataset.say,ek=el.dataset.ek||'',t0=performance.now();
    (function adim(t){const p=Math.min(1,(t-t0)/900);el.textContent=Math.round(h*(1-Math.pow(1-p,3)))+ek;if(p<1)requestAnimationFrame(adim)})(t0)})})();
