// Huginn - Ticari Istihbarat Platformu - Dashboard JS
const API = window.location.origin;
console.log('[Huginn] app.js v3 yuklendi -', new Date().toLocaleTimeString('tr-TR'));
// API key: dashboard ?api_key=KEY ile acildiysa otomatik tasinir (Y6)
const API_KEY = new URLSearchParams(window.location.search).get('api_key') || localStorage.getItem('dash_api_key') || '';
if (!new URLSearchParams(window.location.search).has('api_key') && API_KEY) {
  // URL'de degilse localStorage'dan alindi
}
function apiUrl(path) {
  // API key'i query parametresi olarak ekle (rate limit + auth icin)
  const sep = path.includes('?') ? '&' : '?';
  return `${API}${path}${API_KEY ? sep + 'api_key=' + encodeURIComponent(API_KEY) : ''}`;
}
let allCompanies = [];
let qualityChart = null, coverageChart = null;
// Pagination state
let totalRecords = 0;
let currentPage = 1;
const pageSize = 200;
// Sort state
let sortKey = 'data_quality_score';
let sortDir = 'desc';
// Watchlist state (Y13) - localStorage kalici
let watchSet = new Set();
try { watchSet = new Set(JSON.parse(localStorage.getItem('huginn_watchlist') || '[]')); } catch(e){ watchSet = new Set(); }

function saveWatchStorage() { localStorage.setItem('huginn_watchlist', JSON.stringify(Array.from(watchSet))); }
function isWatched(c) { return watchSet.has(c.company_id || c.legal_name || ''); }
function toggleWatch(id, el) {
  id = id || '';
  if (!id) return;
  if (watchSet.has(id)) { watchSet.delete(id); if (el) el.querySelector('i').className = 'fas fa-star-o'; }
  else { watchSet.add(id); if (el) el.querySelector('i').className = 'fas fa-star'; }
  saveWatchStorage();
  renderWatchlist();
}
function renderWatchlist() {
  const wl = document.getElementById('watchlist');
  if (!wl) return;
  if (watchSet.size === 0) {
    wl.innerHTML = '<span class="watchlist-empty">Henüz firma izlenmiyor.<br>Satırdaki <i class="fas fa-star" style="color:var(--yellow)"></i> ikonuna tıklayın.</span>';
    return;
  }
  const items = Array.from(watchSet);
  wl.innerHTML = items.slice(0, 10).map(id => {
    const c = allCompanies.find(x => (x.company_id || x.legal_name) === id) || {};
    const name = (c.legal_name || id).toUpperCase();
    const nameS = name.length > 18 ? name.substring(0,17) + '…' : name;
    return `<div class="watchlist-item" onclick="selectCompany('${esc(id)}')" title="${esc(name)}">
      <span class="watchlist-name">${esc(nameS)}</span>
      <span class="watchlist-x" onclick="event.stopPropagation(); toggleWatch('${esc(id)}')">&times;</span>
    </div>`;
  }).join('') + (items.length > 10 ? `<div class="watchlist-more">+${items.length-10} daha</div>` : '');
}

document.addEventListener('DOMContentLoaded', () => { loadAll(); updateTimestamp(); setInterval(updateTimestamp, 60000); });

function showLoading() { document.getElementById('loading').classList.remove('hidden'); document.getElementById('content').classList.add('hidden'); }
function hideLoading() { document.getElementById('loading').classList.add('hidden'); document.getElementById('content').classList.remove('hidden'); }
function showError(msg) { const b=document.getElementById('error-banner'); b.classList.remove('hidden'); document.getElementById('error-text').textContent=msg; setTimeout(()=>b.classList.add('hidden'),5000); }
function updateTimestamp() { document.getElementById('last-update').textContent = 'Son guncelleme: ' + new Date().toLocaleTimeString('tr-TR'); }
function showView(v,el) { document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active')); if(el) el.classList.add('active'); }
function esc(s) { const d=document.createElement('div'); d.textContent=(s||'-').toString().replace(/[\r\n\t]+/g,' ').replace(/\s{2,}/g,' '); return d.innerHTML; }
function fmt(n) { return (n||0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }

async function loadAll() {
  showLoading();
  const results = await Promise.allSettled([loadKPI(), loadSources(), loadCompanies(), loadQualityTrend(), loadNACE()]);
  const errors = results.filter(r => r.status === 'rejected');
  if (errors.length > 0) console.error('Load errors:', errors.map(e => e.reason));
  hideLoading();
  renderWatchlist();
  restoreLastFilter();
}

async function loadKPI() {
  const r = await fetch(apiUrl('/api/kpi'));
  const d = await r.json();
  const total = d.total || 0;
  const cards = [
    {label:'Toplam Firma',value:fmt(d.total),icon:'fa-building',color:''},
    {label:'Kalite Skoru',value:(d.avg_score||0).toFixed(1)+'/100',icon:'fa-star',color:'green'},
    {label:'VKN Dolu',value:fmt(d.vkn_either),icon:'fa-id-card',color:'purple',sub:total?'%'+((d.vkn_either/total)*100).toFixed(1):''},
    {label:'Web Sitesi',value:fmt(d.web),icon:'fa-globe',color:'cyan',sub:total?'%'+((d.web/total)*100).toFixed(1):''},
    {label:'Telefon',value:fmt(d.tel),icon:'fa-phone',color:'orange',sub:total?'%'+((d.tel/total)*100).toFixed(1):''},
    {label:'E-posta',value:fmt(d.email),icon:'fa-envelope',color:'yellow',sub:total?'%'+((d.email/total)*100).toFixed(1):''},
    {label:'NACE Kodu',value:fmt(d.nace),icon:'fa-industry',color:'green',sub:total?'%'+((d.nace/total)*100).toFixed(1):''},
    {label:'Adres',value:fmt(d.adres),icon:'fa-map-marker-alt',color:'red',sub:total?'%'+((d.adres/total)*100).toFixed(1):''},
  ];
  document.getElementById('kpi-grid').innerHTML = cards.map(c=>`
    <div class="kpi-card ${c.color}">
      <div class="kpi-card-label"><i class="fas ${c.icon}"></i> ${c.label}</div>
      <div class="kpi-card-value">${c.value}</div>
      ${c.sub?`<div class="kpi-card-sub"><i class="fas fa-arrow-up"></i> ${c.sub}</div>`:''}
    </div>`).join('');
  const covLabels = ['Telefon','E-posta','Web','VKN','NACE','Adres'];
  const covData = [d.tel,d.email,d.web,d.vkn_either,d.nace,d.adres].map(v=>((v||0)/Math.max(total,1)*100).toFixed(1));
  const covColors = ['#3b82f6','#10b981','#06b6d4','#8b5cf6','#f59e0b','#ef4444'];
  if (coverageChart) coverageChart.destroy();
  coverageChart = new Chart(document.getElementById('coverageChart'),{type:'bar',data:{labels:covLabels,datasets:[{label:'Doluluk (%)',data:covData,backgroundColor:covColors,borderRadius:6}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,max:100,ticks:{color:'#64748b',font:{size:10}},grid:{color:'#1e2433'}},x:{ticks:{color:'#64748b',font:{size:10}},grid:{display:false}}}}});
}

let allSources = [];
let selectedSources = new Set();

async function loadSources() {
  const r = await fetch(apiUrl('/api/sources'));
  const d = await r.json();
  allSources = d;
  // Grid olustur
  const icons = {'ostim.org.tr':'fa-industry','aso.org.tr':'fa-building','ivedik.org.tr':'fa-city','baskent.org.tr':'fa-warehouse'};
  const typeLabels = {'osb':'OSB','chamber':'Oda','mersis':'MERSIS','gib':'GIB','web':'Web'};
  document.getElementById('sources-grid').innerHTML = d.map(s => `
    <div class="source-box" id="src-${s.source_name.replace(/\./g,'-')}" onclick="toggleSource('${s.source_name}')">
      <div class="source-box-icon"><i class="fas ${icons[s.source_name]||'fa-database'}"></i></div>
      <div class="source-box-name">${esc(s.source_name)}</div>
      <div class="source-box-type">${typeLabels[s.source_type]||s.source_type}</div>
      <div class="source-box-stats">
        <span>Kayıt: <span class="stat-value">${fmt(s.record_count)}</span></span>
        <span>${s.last_scrape ? new Date(s.last_scrape).toLocaleDateString('tr-TR') : '-'}</span>
      </div>
    </div>`).join('');
  // Hizli filtre dropdown'ini doldur
  const sourceFilter = document.getElementById('source-filter');
  if (sourceFilter) {
    sourceFilter.innerHTML = '<option value="">Tüm Kaynaklar</option>' + d.map(s => `<option value="${s.source_name}">${s.source_name} (${fmt(s.record_count)})</option>`).join('');
  }
}

function toggleSource(name) {
  const box = document.getElementById('src-' + name.replace(/\./g,'-'));
  if (selectedSources.has(name)) {
    selectedSources.delete(name);
    box.classList.remove('selected');
  } else {
    selectedSources.add(name);
    box.classList.add('selected');
  }
  applyQuickFilter();
}

function selectAllSources() {
  selectedSources = new Set(allSources.map(s => s.source_name));
  allSources.forEach(s => {
    const box = document.getElementById('src-' + s.source_name.replace(/\./g,'-'));
    if (box) box.classList.add('selected');
  });
  applyQuickFilter();
}

function clearSourceFilter() {
  selectedSources.clear();
  allSources.forEach(s => {
    const box = document.getElementById('src-' + s.source_name.replace(/\./g,'-'));
    if (box) box.classList.remove('selected');
  });
  const sf = document.getElementById('source-filter');
  if (sf) sf.value = '';
  applyQuickFilter();
}

function clearNACEFilter() {
  const nf = document.getElementById('nace-filter');
  if (nf) nf.value = '';
  currentNaceFilter = '';
  applyQuickFilter();
}

function updateScoreLabel() {
  const slider = document.getElementById('min-score-slider');
  const label = document.getElementById('score-label');
  if (slider && label) label.textContent = slider.value;
}

// Kayitli filtreler (Y13): son filtre localStorage'a kaydedilir, sayfa acilinca geri yuklenir
function saveLastFilter(search, nace, source, minScore) {
  try {
    localStorage.setItem('huginn_last_filter', JSON.stringify({search, nace, source, minScore, t: Date.now()}));
  } catch(e){}
}
function restoreLastFilter() {
  try {
    const raw = localStorage.getItem('huginn_last_filter');
    if (!raw) return;
    const f = JSON.parse(raw);
    const ageMin = (Date.now() - (f.t||0)) / 60000;
    if (ageMin > 60*12) return; // 12 saatten eski filtreyi yok say
    if (!f.search && !f.nace && !f.source && (f.minScore||0)<=0) return;
    // Filtreleri UI'a uygula
    const gs = document.getElementById('global-search');
    if (gs && f.search) gs.value = f.search;
    const nf = document.getElementById('nace-filter');
    if (nf && f.nace) nf.value = f.nace;
    const sf = document.getElementById('source-filter');
    if (sf && f.source) sf.value = f.source;
    const slider = document.getElementById('min-score-slider');
    if (slider && f.minScore) { slider.value = f.minScore; updateScoreLabel(); }
    currentNaceFilter = f.nace || '';
    currentSourceFilter = f.source || '';
    applyQuickFilter();
  } catch(e){}
}
function clearSavedFilter() {
  try { localStorage.removeItem('huginn_last_filter'); } catch(e){}
}

function applyQuickFilter() {
  currentPage = 1; // Yeni filtre -> ilk sayfa
  const search = document.getElementById('global-search').value.trim();
  const naceSelect = document.getElementById('nace-filter');
  const sourceSelect = document.getElementById('source-filter');
  const scoreSlider = document.getElementById('min-score-slider');
  const nace = naceSelect ? naceSelect.value : '';
  const source = sourceSelect ? sourceSelect.value : '';
  const minScore = scoreSlider ? parseInt(scoreSlider.value) : 0;
  // Coklu kaynak secimi varsa, ilk secileni API'ye gonder (API tek kaynak destekliyor)
  let activeSource = source;
  if (selectedSources.size > 0) {
    activeSource = Array.from(selectedSources).join(',');
  }
  currentNaceFilter = nace;
  currentSourceFilter = activeSource;
  // Son filtreyi kaydet (Y13 - kayitli filtreler)
  saveLastFilter(search, nace, activeSource, minScore);
  loadCompanies(search, minScore, 100, activeSource, nace);
}

function clearAllFilters() {
  currentPage = 1;
  clearSavedFilter();
  document.getElementById('global-search').value = '';
  const nf = document.getElementById('nace-filter');
  if (nf) nf.value = '';
  const sf = document.getElementById('source-filter');
  if (sf) sf.value = '';
  const slider = document.getElementById('min-score-slider');
  if (slider) { slider.value = 0; updateScoreLabel(); }
  selectedSources.clear();
  allSources.forEach(s => {
    const box = document.getElementById('src-' + s.source_name.replace(/\./g,'-'));
    if (box) box.classList.remove('selected');
  });
  currentNaceFilter = '';
  currentSourceFilter = '';
  loadCompanies('', 0, 100);
}

async function loadQualityTrend() {
  const r = await fetch(apiUrl('/api/quality-trend'));
  const d = await r.json();
  const labels = d.map(x=>x.bucket);
  const data = d.map(x=>x.cnt);
  const colors = d.map(x=>{if(x.bucket.startsWith('80'))return '#10b981';if(x.bucket.startsWith('60'))return '#3b82f6';if(x.bucket.startsWith('40'))return '#f59e0b';if(x.bucket.startsWith('20'))return '#f97316';return '#ef4444';});
  if (qualityChart) qualityChart.destroy();
  qualityChart = new Chart(document.getElementById('qualityChart'),{type:'doughnut',data:{labels,datasets:[{data,backgroundColor:colors,borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{color:'#64748b',font:{size:11},padding:8}}},cutout:'60%'}});
}

async function loadNACE() {
  const r = await fetch(apiUrl('/api/nace-distribution?limit=15'));
  const d = await r.json();
  const maxCnt = Math.max(...d.map(x=>x.cnt),1);
  document.getElementById('nace-list').innerHTML = d.map(x=>{
    const sector = getNaceSector(x.nace_code);
    const label = getNaceLabel(x.nace_code);
    return `<div class="nace-item" onclick="filterByNACE('${x.nace_code}')" style="cursor:pointer" title="${label}">
      <span class="nace-code">${esc(x.nace_code)}</span>
      <span class="nace-label">${esc(label)}</span>
      <span class="nace-count">${fmt(x.cnt)}</span>
    </div>
    <div class="nace-bar"><div class="nace-bar-fill" style="width:${(x.cnt/maxCnt)*100}%"></div></div>`;
  }).join('');
  // NACE dropdown'ini doldur
  const naceFilter = document.getElementById('nace-filter');
  if (naceFilter) {
    naceFilter.innerHTML = '<option value="">Tüm Sektörler</option>' + d.map(x => {
      const prefix = x.nace_code.substring(0,2);
      const sector = getNaceSector(x.nace_code);
      return `<option value="${prefix}">${sector} (${fmt(x.cnt)})</option>`;
    }).join('');
  }
}

function renderSkeleton() {
  // Y8: tablo yuklenirken iskelet satirlar goster
  let rows = '';
  for (let i=0; i<8; i++) {
    rows += '<tr class="skeleton-row">' + '<td><div class="skeleton"></div></td>'.repeat(8) + '</tr>';
  }
  const tb = document.getElementById('companies-tbody');
  if (tb) tb.innerHTML = rows;
}

async function loadCompanies(search='',minScore=0,maxScore=100,source='',nace='') {
  renderSkeleton();
  let url = `/api/companies?limit=${pageSize}&offset=${(currentPage-1)*pageSize}&min_score=${minScore}&max_score=${maxScore}`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  // ANA KURAL: Coklu kaynak icin sources= parametresi (virgulle ayrilmis liste)
  if (source) url += `&sources=${encodeURIComponent(source)}`;
  if (nace) url += `&nace=${encodeURIComponent(nace)}`;
  const r = await fetch(apiUrl(url));
  const d = await r.json();
  allCompanies = d.items || [];
  totalRecords = d.total || 0;
  renderTable(allCompanies);
  renderPagination();
  // Tablo sayacini guncelle
  const tableCount = document.getElementById('table-count');
  if (tableCount) tableCount.textContent = fmt(totalRecords);
  // Arama sonucu gostergesi
  const resultBar = document.getElementById('search-result');
  if (resultBar) {
    if (search || source || nace || minScore>0 || maxScore<100) {
      resultBar.classList.remove('hidden');
      document.getElementById('result-count').textContent = fmt(totalRecords);
      let filterParts = [];
      if (search) filterParts.push(`"${search}"`);
      if (nace) filterParts.push(`Sektör: ${getNaceSector(nace)} (${nace})`);
      if (source) filterParts.push(`Kaynak: ${source}`);
      if (minScore>0 || maxScore<100) filterParts.push(`Skor: ${minScore}-${maxScore}`);
      document.getElementById('result-filter').textContent = filterParts.join(' • ');
    } else {
      resultBar.classList.add('hidden');
    }
  }
  // Otomatik scroll firma tablosuna
  if (search || source || nace) {
    setTimeout(() => {
      const table = document.querySelector('.table-card');
      if (table) table.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 200);
  }
}

function renderTable(companies) {
  if (!companies || companies.length === 0) {
    document.getElementById('companies-tbody').innerHTML = '<tr><td colspan="8" style="text-align:center;padding:40px;color:var(--text-dim)"><i class="fas fa-search" style="font-size:24px;display:block;margin-bottom:8px"></i>Arama kriterlerine uygun firma bulunamadi</td></tr>';
    return;
  }
  // Client-side siralama uygula
  let rows = [...companies];
  if (sortKey) {
    rows.sort((a,b) => {
      let va = a[sortKey==='vkn' ? 'tax_number' : sortKey];
      let vb = b[sortKey==='vkn' ? 'tax_number' : sortKey];
      if (sortKey === 'data_quality_score') {
        va = Number(va||0); vb = Number(vb||0);
        return sortDir==='asc' ? va-vb : vb-va;
      }
      va = (va||'').toString().toUpperCase();
      vb = (vb||'').toString().toUpperCase();
      if (sortKey==='nace_code' && a.nace_code && b.nace_code) {
        return sortDir==='asc' ? va.localeCompare(vb) : vb.localeCompare(va);
      }
      return sortDir==='asc' ? va.localeCompare(vb) : vb.localeCompare(va);
    });
  }
  document.getElementById('companies-tbody').innerHTML = rows.map(c=>{
    const score = Number(c.data_quality_score||0);
    const cls = score>=80?'score-high':score>=60?'score-medium':score>=40?'score-low':'score-very-low';
    const naceLabel = c.nace_code ? getNaceSector(c.nace_code) : '-';
    // ANA KURAL: Firma adlari BUYUK HARFLE, ticaret adi ilk 2 hece
    const legalName = (c.legal_name||'-').toUpperCase();
    const tradeName = (c.trade_name||'-').toUpperCase();
    // Bos alan rozetleri (Y8): eksik veriler '-' yerine rozet gosterir
    const vknVal = c.tax_number||c.vergi_no||'';
    const webVal = c.website_domain||'';
    const phoneVal = c.primary_phone||'';
    const missVkn = vknVal ? esc(vknVal) : '<span class="missing-badge enrich" title="VKN eksik - zenginlestirme kuyruguna eklenebilir">VKN eksik ⚡</span>';
    const missWeb = webVal ? esc(webVal) : '<span class="missing-badge">web yok</span>';
    const missPhone = phoneVal ? esc(phoneVal) : '<span class="missing-badge">tel yok</span>';
    return `<tr onclick="selectCompany('${esc(c.company_id||c.legal_name)}')" tabindex="0" role="button">
      <td class="td-name">${esc(legalName)} ${isWatched(c) ? '<span class="watch-star">★</span>' : ''}</td>
      <td>${esc(tradeName)}</td>
      <td class="td-mono">${missWeb}</td>
      <td class="td-mono">${missPhone}</td>
      <td class="td-mono">${missVkn}</td>
      <td class="td-mono" title="${getNaceLabel(c.nace_code)}"><span class="nace-tag">${esc(c.nace_code||'-')}</span><br><span class="nace-sector">${esc(naceLabel)}</span></td>
      <td><span class="score-badge ${cls}">${score.toFixed(1)}</span></td>
      <td class="td-watch" onclick="event.stopPropagation(); toggleWatch('${esc(c.company_id||c.legal_name)}', this)"><i class="fas ${isWatched(c)?'fa-star':'fa-star-o'}"></i></td>
    </tr>`;
  }).join('');
}

function renderPagination() {
  const pager = document.getElementById('pagination');
  if (!pager) return;
  const totalPages = Math.max(1, Math.ceil(totalRecords / pageSize));
  if (currentPage > totalPages) { currentPage = totalPages; }
  if (totalPages <= 1) { pager.innerHTML = ''; return; }
  let html = '';
  // Onceki
  html += `<button class="page-btn" ${currentPage<=1?'disabled':''} onclick="goToPage(${currentPage-1})"><i class="fas fa-chevron-left"></i></button>`;
  // Sayfa numaralari (windowed: +/-2)
  const start = Math.max(1, currentPage-2);
  const end = Math.min(totalPages, currentPage+2);
  if (start > 1) html += `<span class="page-dots">…</span>`;
  for (let p=start; p<=end; p++) {
    html += `<button class="page-btn ${p===currentPage?'active':''}" onclick="goToPage(${p})">${p}</button>`;
  }
  if (end < totalPages) html += `<span class="page-dots">…</span>`;
  // Sonraki
  html += `<button class="page-btn" ${currentPage>=totalPages?'disabled':''} onclick="goToPage(${currentPage+1})"><i class="fas fa-chevron-right"></i></button>`;
  html += `<span class="page-info">${fmt(totalRecords)} kayıt · ${totalPages} sayfa</span>`;
  pager.innerHTML = html;
}

function goToPage(p) {
  const totalPages = Math.max(1, Math.ceil(totalRecords / pageSize));
  if (p < 1 || p > totalPages || p === currentPage) return;
  currentPage = p;
  // Aktif filtreleri koru
  applyQuickFilter();
}

function sortTable(key) {
  if (sortKey === key) {
    sortDir = sortDir === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey = key;
    sortDir = (key === 'data_quality_score') ? 'desc' : 'asc';
  }
  // Sort ikonlarini guncelle
  document.querySelectorAll('th.sortable').forEach(th => {
    th.querySelector('.sort-icon').textContent = '';
  });
  const th = document.querySelector(`th[data-sort="${key}"]`);
  if (th) th.querySelector('.sort-icon').textContent = sortDir === 'asc' ? ' ▲' : ' ▼';
  // Mevcut sayfayi yeniden render et
  renderTable(allCompanies);
}

// Tablo basligi tiklamalari (tek seferlik global listener)
document.addEventListener('click', (e) => {
  const th = e.target.closest('th.sortable');
  if (th && th.dataset.sort) {
    sortTable(th.dataset.sort);
  }
});

function selectCompany(id) {
  const c = allCompanies.find(x => (x.company_id||x.legal_name) === id);
  if (!c) return;
  document.querySelectorAll('tbody tr').forEach(r=>r.classList.remove('selected'));
  if (event && event.target) { const tr=event.target.closest('tr'); if(tr) tr.classList.add('selected'); }
  showDetail(c);
}

function showDetail(c) {
  const score = Number(c.data_quality_score||0);
  const cls = score>=80?'var(--green)':score>=60?'var(--accent)':score>=40?'var(--yellow)':'var(--red)';
  // ANA KURAL: Firma adlari BUYUK HARFLE
  const legalName = (c.legal_name||'-').toUpperCase();
  const tradeName = (c.trade_name||'').toUpperCase();
  document.getElementById('detail-empty').style.display='none';
  document.getElementById('detail-content').style.display='block';
  document.getElementById('detail-content').innerHTML = `
    <div class="detail-section">
      <div class="detail-company-name">${esc(legalName)}</div>
      <div class="detail-company-trade">${esc(tradeName)}</div>
      <div class="detail-score-ring">
        <div class="score-circle" style="border-color:${cls};color:${cls}">${score.toFixed(0)}</div>
        <div class="score-info">
          <div class="score-label">Kalite Skoru</div>
          <div class="score-value" style="color:${cls}">${score.toFixed(1)}/100</div>
        </div>
      </div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">Iletisim</div>
      <div class="detail-row"><span class="label">Telefon</span><span class="value mono">${esc(c.primary_phone||'-')}</span></div>
      <div class="detail-row"><span class="label">E-posta</span><span class="value mono">${esc(c.primary_email||'-')}</span></div>
      <div class="detail-row"><span class="label">Web Sitesi</span><span class="value mono">${esc(c.website_domain||'-')}</span></div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">Resmi Bilgiler</div>
      <div class="detail-row"><span class="label">VKN</span><span class="value mono">${esc(c.tax_number||'-')}</span></div>
      <div class="detail-row"><span class="label">Vergi No</span><span class="value mono">${esc(c.vergi_no||'-')}</span></div>
      <div class="detail-row"><span class="label">NACE Kodu</span><span class="value mono">${esc(c.nace_code||'-')}</span></div>
      <div class="detail-row"><span class="label">OSB Parsel</span><span class="value mono">${esc(c.osb_parsel||'-')}</span></div>
    </div>`;
}

function applyFilters() {
  applyQuickFilter();
}

function doSearch() { applyQuickFilter(); }
function filterBySource(s) { document.getElementById('global-search').value=''; currentSourceFilter=s; currentNaceFilter=''; loadCompanies('',0,100,s); }
function filterByNACE(n) {
  currentPage = 1;
  document.getElementById('global-search').value='';
  currentNaceFilter=n;
  currentSourceFilter='';
  const prefix = n.substring(0,2);
  // NACE dropdown'ini guncelle
  const nf = document.getElementById('nace-filter');
  if (nf) nf.value = prefix;
  loadCompanies('',0,100,'',prefix);
  // Scroll to table
  setTimeout(() => {
    const table = document.querySelector('.table-card');
    if (table) table.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 200);
}
function clearFilters() { clearAllFilters(); }

let currentSourceFilter = '';
let currentNaceFilter = '';

function exportCSV() {
  const search = document.getElementById('global-search').value.trim();
  const naceSelect = document.getElementById('nace-filter');
  const nace = naceSelect ? naceSelect.value : '';
  const sourceSelect = document.getElementById('source-filter');
  const source = sourceSelect ? sourceSelect.value : '';
  const slider = document.getElementById('min-score-slider');
  const minScore = slider ? parseInt(slider.value) : 0;
  // Coklu kaynak secimi kutucuklardan yapildiysa onu onceliklendir
  let activeSource = source;
  if (selectedSources.size > 0) activeSource = Array.from(selectedSources).join(',');
  let url = `/api/companies/export?min_score=${minScore}&max_score=100`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  if (activeSource) url += `&sources=${encodeURIComponent(activeSource)}`;
  if (nace) url += `&nace=${encodeURIComponent(nace)}`;
  window.open(apiUrl(url), '_blank');
}

// ── Y19: Akilli Eslestirme (match) Paneli ───────────────────────────────────

function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// NACE dropdown'ini doldur (ayni liste nace-filter'dan)
function populateMatchNace() {
  const src = document.getElementById('nace-filter');
  const dst = document.getElementById('match-nace');
  if (!src || !dst || dst.options.length > 1) return; // bir kez doldur
  Array.from(src.options).forEach(o => {
    const opt = document.createElement('option');
    opt.value = o.value;
    opt.textContent = o.textContent;
    dst.appendChild(opt);
  });
}

function matchBadge(iliski) {
  const map = {
    'ayni-sektor':    ['badge-ayni',   'Aynı Sektör'],
    'komple-sektor':  ['badge-komple', 'Komple Sektör'],
    'uzak-sektor':    ['badge-uzak',   'Uzak Sektör'],
  };
  const [cls, label] = map[iliski] || ['badge-uzak', iliski || '—'];
  return `<span class="match-badge ${cls}">${label}</span>`;
}

function matchScoreBar(puan) {
  const renk = puan >= 80 ? 'var(--green)' : puan >= 60 ? 'var(--accent)' : puan >= 40 ? '#f59e0b' : 'var(--red)';
  return `<div class="match-score-wrap">
    <div class="match-score-bar"><div class="match-score-fill" style="width:${Math.min(puan,100)}%;background:${renk}"></div></div>
    <span class="match-score-num" style="color:${renk}">${puan}</span>
  </div>`;
}

function matchKirilim(k) {
  if (!k) return '';
  const rows = [
    ['Sektör', k.sektor, 45], ['Konum', k.konum, 20],
    ['Kalite', k.kalite, 25], ['Kanıt', k.kanit, 10],
  ];
  return `<div class="match-kirilim">` + rows.map(([ad, v, max]) =>
    `<div class="mk" title="${ad}: ${v}/${max}"><span class="mk-label">${ad}</span>` +
    `<div class="mk-bar"><div class="mk-fill" style="width:${max ? Math.round(v / max * 100) : 0}%"></div></div>` +
    `<span class="mk-val">${v}</span></div>`).join('') + `</div>`;
}

async function runMatch() {
  const nace = document.getElementById('match-nace').value;
  const mode = document.getElementById('match-mode').value;
  const min = document.getElementById('match-min').value;
  const statusEl = document.getElementById('match-status');
  const resultsEl = document.getElementById('match-results');

  if (!nace) {
    statusEl.className = 'match-status warn';
    statusEl.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Önce alıcı sektörü seçin.';
    resultsEl.innerHTML = '';
    return;
  }

  statusEl.className = 'match-status info';
  statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Eşleştirme yapılıyor…';
  resultsEl.innerHTML = '';

  try {
    const r = await fetch(apiUrl(`/api/match?nace=${encodeURIComponent(nace)}&mode=${mode}&min_puan=${min}&limit=20`));
    if (!r.ok) throw new Error(`API ${r.status}`);
    const d = await r.json();

    statusEl.className = 'match-status ok';
    statusEl.innerHTML = `<i class="fas fa-check-circle"></i> <b>${d.toplam}</b> firma eşleştirildi — alıcı sektörü: <b>${esc(d.buyer.nace)}</b> (${mode === 'komple' ? 'tedarik zinciri dahil' : 'sadece aynı sektör'})`;

    if (!d.items.length) {
      resultsEl.innerHTML = '<div class="match-empty">Sonuç yok — Min Puan değerini düşürmeyi deneyin.</div>';
      return;
    }

    window._matchItems = d.items;
    resultsEl.innerHTML = `
      <div class="match-result-head">
        <span class="mr-col-name">Firma</span><span class="mr-col-nace">Sektör</span>
        <span class="mr-col-score">Puan</span><span class="mr-col-rel">İlişki</span>
      </div>` + d.items.map((i, idx) => `
      <div class="match-result-row" onclick="showDetail(window._matchItems[${idx}])">
        <div class="mr-name">
          <div class="mr-name-main">${esc(i.legal_name)}</div>
          <div class="mr-name-sub">${esc(i.trade_name)}${i.website_domain ? ' · ' + esc(i.website_domain) : ''}</div>
        </div>
        <div class="mr-nace">${esc(i.nace_code || '-')}</div>
        <div class="mr-score">${matchScoreBar(i.match.puan)}</div>
        <div class="mr-rel">${matchBadge(i.match.iliski)}${matchKirilim(i.match.kirilim)}</div>
      </div>`).join('');
  } catch (e) {
    statusEl.className = 'match-status err';
    statusEl.innerHTML = `<i class="fas fa-exclamation-circle"></i> Eşleştirme hatası: ${esc(e.message)}`;
  }
}

// showView'e match scroll entegrasyonu (mevcut fonksiyonu sarmala)
const _origShowView = showView;
showView = function (v, el) {
  _origShowView(v, el);
  if (v === 'match') {
    populateMatchNace();
    scrollToSection('match-section');
  }
};
