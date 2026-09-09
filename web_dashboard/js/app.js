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
function watchKeyOf(c) { return c.company_id || c.legal_name || ''; }
function isWatched(c) { return watchSet.has(watchKeyOf(c)); }
function toggleWatch(id, el) {
  id = id || '';
  if (!id) return;
  if (watchSet.has(id)) { watchSet.delete(id); if (el) el.className = 'watch-star-btn'; }
  else { watchSet.add(id); if (el) el.className = 'watch-star-btn on'; }
  saveWatchStorage();
  renderWatchlist();
}
function toggleWatchByCompany(companyId, legalName, el) {
  const key = companyId || legalName;
  toggleWatch(key, el);
}
function renderWatchlist() {
  const wl = document.getElementById('watchlist');
  if (!wl) return;
  if (watchSet.size === 0) {
    wl.innerHTML = '<span class="watchlist-empty">Henüz firma izlenmiyor.<br>Tablodaki <i class="fas fa-star" style="color:var(--yellow)"></i> düğmesiyle veya detay panelinden <b>İzlemeye Al</b> ile ekleyin. İzlediğiniz firmalar burada kalıcı olarak listelenir — satış takibi için hızlı erişim.</span>';
    return;
  }
  const items = Array.from(watchSet);
  wl.innerHTML = items.slice(0, 10).map(id => {
    const c = allCompanies.find(x => (x.company_id || x.legal_name) === id);
    const name = (c ? (c.legal_name || id) : id).toUpperCase();
    const nameS = name.length > 18 ? name.substring(0,17) + '…' : name;
    const score = c ? Math.round(Number(c.data_quality_score||0)) : null;
    const scoreTag = score !== null ? ` <span class="watchlist-score">${score}</span>` : '';
    return `<div class="watchlist-item" onclick="selectCompany('${esc(id)}')" title="${esc(name)}">
      <span class="watchlist-name">${esc(nameS)}</span>${scoreTag}
      <span class="watchlist-x" onclick="event.stopPropagation(); toggleWatch('${esc(id)}')">&times;</span>
    </div>`;
  }).join('') + (items.length > 10 ? `<div class="watchlist-more">+${items.length-10} daha</div>` : '');
}

document.addEventListener('DOMContentLoaded', () => { loadAll(); updateTimestamp(); setInterval(updateTimestamp, 60000);
  if (localStorage.getItem('huginn_info_collapsed') === '1') toggleInfoCenter();
});

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
  populateMatchNace(); // match dropdown sayfa acilisinda dolsun
  loadTasks();
}

function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }); }

// ── Y22: Gorev Tahtasi (bagimsiz admin overlay: gorevler + uye onay paneli) ──

function openTasks() {
  let ov = document.getElementById('tasks-overlay');
  if (!ov) {
    ov = document.createElement('div');
    ov.id = 'tasks-overlay';
    ov.style.cssText = 'position:fixed;inset:0;background:rgba(5,7,12,.92);z-index:9998;overflow-y:auto;padding:28px 20px';
    ov.innerHTML = `
      <div style="max-width:980px;margin:0 auto">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <h2 style="margin:0;font-size:20px"><i class="fas fa-tasks" style="color:var(--accent)"></i> Görev Tahtası
            <span style="font-size:12px;color:var(--text-dim);margin-left:8px">iç ajan görevleri · üye onay paneli</span></h2>
          <button onclick="closeTasks()" style="background:var(--panel-bg);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:8px 14px;cursor:pointer;font-size:13px">✕ Kapat</button>
        </div>
        <div id="tasks-admin-panel" class="chart-card" style="padding:4px 0 12px;margin-bottom:14px;display:none">
          <div class="chart-card-header"><div class="chart-card-title"><i class="fas fa-user-check"></i> Üye Onay Paneli</div>
            <div class="chart-card-actions"><button class="chart-btn" onclick="loadTasks()"><i class="fas fa-sync-alt"></i> Yenile</button></div></div>
          <div id="admin-pending-body" style="padding:0 16px 16px"></div>
        </div>
        <div class="chart-card" style="padding:4px 0 12px">
          <div id="tasks-summary" class="match-agg" style="margin:10px 16px"></div>
          <div id="tasks-body" class="match-results"></div>
        </div>
      </div>`;
    document.body.appendChild(ov);
    ov.addEventListener('click', e => { if (e.target === ov) closeTasks(); });
  }
  ov.style.display = 'block';
  document.body.style.overflow = 'hidden';
  loadTasks();
}

function closeTasks() {
  const ov = document.getElementById('tasks-overlay');
  if (ov) ov.style.display = 'none';
  document.body.style.overflow = '';
}

function _isTaskAdmin(cb) {
  const tok = getMemberToken();
  if (!tok) { cb(false, null); return; }
  fetch(apiUrl('/api/me?token=' + encodeURIComponent(tok)))
    .then(r => (r.ok ? r.json() : Promise.reject()))
    .then(d => cb((d.user || {}).role === 'admin', d.user || {}))
    .catch(() => cb(false, null));
}

async function loadTasks() {
  const summaryEl = document.getElementById('tasks-summary');
  const bodyEl = document.getElementById('tasks-body');
  if (!summaryEl || !bodyEl) return;
  _isTaskAdmin(async (isAdmin) => {
    const adminPanel = document.getElementById('tasks-admin-panel');
    adminPanel.style.display = isAdmin ? 'block' : 'none';
    if (isAdmin) loadAdminPending();
    try {
      const r = await fetch(apiUrl('/api/tasks'));
      if (!r.ok) throw new Error(`API ${r.status}`);
      const d = await r.json();
      const gorevler = Array.isArray(d) ? d : (d.gorevler || d.items || []);
      const say = g => gorevler.filter(x => x.durum === g).length;
      summaryEl.className = 'match-agg';
      summaryEl.innerHTML = `
        <div class="agg-chip">Toplam Görev<b>${gorevler.length}</b></div>
        <div class="agg-chip">Tamamlanan<b style="color:var(--green)">${say('done') + say('tamamlandi')}</b></div>
        <div class="agg-chip">Plan / Bekleyen<b style="color:#fbbf24">${say('plan')}</b></div>
        <div class="agg-chip">Aktif<b style="color:var(--accent)">${say('aktif')}</b></div>
        <div class="agg-chip">Engelli<b style="color:var(--red)">${say('blocked')}</b></div>`;
      const sirali = gorevler.filter(g => ['plan', 'aktif', 'blocked'].includes(g.durum)).slice(0, 12);
      const sonTam = gorevler.filter(g => ['done', 'tamamlandi'].includes(g.durum)).slice(-4);
      const durumRenk = { plan: '#fbbf24', aktif: 'var(--accent)', blocked: 'var(--red)', done: 'var(--green)', tamamlandi: 'var(--green)' };
      bodyEl.innerHTML = `
        <div class="match-result-head">
          <span class="mr-col-name">Görev</span><span class="mr-col-nace">Sahip</span>
          <span class="mr-col-score">Durum</span><span class="mr-col-rel">Not</span>
        </div>` +
        (sirali.map(g => `
        <div class="match-result-row" style="cursor:default">
          <div class="mr-name"><div class="mr-name-main">${esc(g.baslik || g.ad || g.id || '-')}</div></div>
          <div class="mr-nace">${esc(g.sahip || '-')}</div>
          <div class="mr-score"><span class="match-badge" style="background:rgba(255,255,255,.06);color:${durumRenk[g.durum] || 'inherit'};border:1px solid ${durumRenk[g.durum] || 'inherit'}">${esc(g.durum)}</span></div>
          <div class="mr-rel" style="font-size:11px;color:var(--text-dim)">${esc((g.not || '').substring(0, 90))}${(g.not || '').length > 90 ? '…' : ''}</div>
        </div>`).join('') || '') +
        `<div class="match-empty" style="border-style:solid;margin-top:10px">
          <i class="fas fa-check-circle" style="color:var(--green)"></i> Bekleyen görevlerin hepsi ajanda. Son tamamlananlar:
          ${sonTam.map(g => esc((g.baslik || g.id) + '')).join(' · ')}
        </div>`;
    } catch (e) {
      bodyEl.innerHTML = `<div class="match-empty"><i class="fas fa-exclamation-circle"></i> Görev tahtası yüklenemedi: ${esc(e.message)}</div>`;
    }
  });
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
  renderSources();
  // Hizli filtre dropdown'ini doldur
  const sourceFilter = document.getElementById('source-filter');
  if (sourceFilter) {
    sourceFilter.innerHTML = '<option value="">Tüm Kaynaklar</option>' + d.map(s => `<option value="${s.source_name}">${s.source_name} (${fmt(s.record_count)})</option>`).join('');
  }
}

let showAllSources = false;
function renderSources() {
  const list = showAllSources ? allSources : allSources.slice(0, 8);
  const icons = {'ostim.org.tr':'fa-industry','aso.org.tr':'fa-building','ivedik.org.tr':'fa-city','baskent.org.tr':'fa-warehouse'};
  const typeLabels = {'osb':'OSB','chamber':'Oda','mersis':'MERSIS','gib':'GIB','web':'Web'};
  document.getElementById('sources-grid').innerHTML = list.map(s => `
    <div class="source-box${selectedSources.has(s.source_name)?' selected':''}" id="src-${s.source_name.replace(/\./g,'-')}" onclick="toggleSource('${s.source_name}')">
      <div class="source-box-icon"><i class="fas ${icons[s.source_name]||'fa-database'}"></i></div>
      <div class="source-box-name">${esc(s.source_name)}</div>
      <div class="source-box-type">${typeLabels[s.source_type]||s.source_type}</div>
      <div class="source-box-stats">
        <span>Kayıt: <span class="stat-value">${fmt(s.record_count)}</span></span>
        <span>${s.last_scrape ? new Date(s.last_scrape).toLocaleDateString('tr-TR') : '-'}</span>
      </div>
    </div>`).join('');
  updateListToggle('sources-toggle','sources-toggle-label',allSources.length,showAllSources);
}

function toggleSourcesList() { showAllSources = !showAllSources; renderSources(); }

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

let allNace = [], showAllNace = false;
async function loadNACE() {
  const r = await fetch(apiUrl('/api/nace-distribution?limit=100'));
  const d = await r.json();
  allNace = d;
  renderNaceList();
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

function renderNaceList() {
  const list = showAllNace ? allNace : allNace.slice(0, 8);
  const maxCnt = Math.max(...list.map(x=>x.cnt), 1);
  document.getElementById('nace-list').innerHTML = list.map(x=>{
    const label = getNaceLabel(x.nace_code);
    return `<div class="nace-item" onclick="filterByNACE('${x.nace_code}')" style="cursor:pointer" title="${label}">
      <span class="nace-code">${esc(x.nace_code)}</span>
      <span class="nace-label">${esc(label)}</span>
      <span class="nace-count">${fmt(x.cnt)}</span>
      <div class="nace-bar"><div class="nace-bar-fill" style="width:${(x.cnt/maxCnt)*100}%"></div></div>
    </div>`;
  }).join('');
  updateListToggle('nace-toggle','nace-toggle-label',allNace.length,showAllNace);
}

function toggleNaceList() { showAllNace = !showAllNace; renderNaceList(); }

function updateListToggle(btnId, labelId, total, isOpen) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  const VISIBLE = 8;
  if (total > VISIBLE) {
    btn.classList.remove('hidden');
    document.getElementById(labelId).textContent = isOpen ? 'Daha az göster' : `Tümünü göster (${total})`;
    btn.classList.toggle('open', isOpen);
  } else {
    btn.classList.add('hidden');
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
    const watchKey = esc(c.company_id||c.legal_name||'');
    const watched = isWatched(c);
    return `<tr onclick="selectCompany('${watchKey}')" tabindex="0" role="button">
      <td class="td-name"><button class="watch-star-btn${watched?' on':''}" title="${watched?'İzlemeden çıkar':'İzlemeye al'}" onclick="event.stopPropagation(); toggleWatch('${watchKey}', this)"><i class="${watched?'fas':'far'} fa-star"></i></button> ${esc(legalName)}</td>
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

// Responsive navigation and company-detail drawers.
let drawerReturnFocus = null;
function closeMobileMenu() {
  document.body.classList.remove('menu-open');
  document.getElementById('menu-toggle')?.setAttribute('aria-expanded', 'false');
}
function closeDetailPanel() {
  document.body.classList.remove('detail-open');
  document.querySelector('.detail-panel')?.classList.remove('is-open');
  if (drawerReturnFocus?.isConnected) drawerReturnFocus.focus({preventScroll:true});
  drawerReturnFocus = null;
}
function openDetailPanel() {
  closeMobileMenu();
  const panel = document.querySelector('.detail-panel');
  if (!panel) return;
  panel.scrollTop = 0;
  panel.classList.add('is-open');
  if (window.matchMedia('(max-width:1150px)').matches) {
    if (!document.body.classList.contains('detail-open')) drawerReturnFocus = document.activeElement;
    document.body.classList.add('detail-open');
    document.getElementById('detail-close')?.focus({preventScroll:true});
  }
}
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('menu-toggle')?.addEventListener('click', () => {
    closeDetailPanel();
    const open = document.body.classList.toggle('menu-open');
    document.getElementById('menu-toggle').setAttribute('aria-expanded', String(open));
    if (open) document.getElementById('menu-close')?.focus();
  });
  document.getElementById('mobile-backdrop')?.addEventListener('click', () => {
    closeDetailPanel();
    closeMobileMenu();
  });
  document.querySelector('.sidebar')?.addEventListener('click', e => {
    if (e.target.closest('.nav-item')) closeMobileMenu();
  });
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    const menuOpen = document.body.classList.contains('menu-open');
    closeDetailPanel();
    closeMobileMenu();
    if (menuOpen) document.getElementById('menu-toggle')?.focus();
  }
  const drawer = document.body.classList.contains('detail-open') ? document.querySelector('.detail-panel')
    : document.body.classList.contains('menu-open') ? document.querySelector('.sidebar') : null;
  if (e.key === 'Tab' && drawer) {
    const items = [...drawer.querySelectorAll('button:not(:disabled),a[href],[tabindex="0"]')].filter(el => el.getClientRects().length);
    const first = items[0], last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
  }
  const nav = e.target.closest('.nav-item[role="button"]');
  if (nav && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); nav.click(); }
});
window.addEventListener('resize', () => {
  if (window.innerWidth > 760) closeMobileMenu();
  if (window.innerWidth > 1150) closeDetailPanel();
});

function selectCompany(id) {
  const c = allCompanies.find(x => (x.company_id||x.legal_name) === id);
  if (!c) return;
  document.querySelectorAll('tbody tr').forEach(r=>r.classList.remove('selected'));
  if (event && event.target) { const tr=event.target.closest('tr'); if(tr) tr.classList.add('selected'); }
  showDetail(c);
}

function showDetail(c) {
  openDetailPanel();
  const score = Number(c.data_quality_score||0);
  const cls = score>=80?'var(--green)':score>=60?'var(--accent)':score>=40?'var(--yellow)':'var(--red)';
  // ANA KURAL: Firma adlari BUYUK HARFLE
  const legalName = (c.legal_name||'-').toUpperCase();
  const tradeName = (c.trade_name||'').toUpperCase();
  window._detailCompany = c; // butonlar icin aktif firma saklanir
  const inWatch = watchSet.has(watchKeyOf(c));
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
    </div>
    <div class="detail-actions">
      <button class="d-btn primary tip tip-left" data-tip="Bu firmanın sektörüne en uygun firmaları eşleştirme panelinde açar." onclick="matchFor(window._detailCompany)"${c.nace_code ? '' : ' disabled'}><i class="fas fa-handshake"></i> Kimler Uygun?</button>
      <button class="d-btn tip tip-left" data-tip="Bu firmayı izleme listenize ekler/kaldırır (tarayıcınızda kalıcı)." onclick="toggleWatchDetail()"><i class="fas fa-star"></i> ${inWatch ? 'İzlemeden Çıkar' : 'İzlemeye Al'}</button>
      <button class="d-btn tip tip-left" data-tip="Görünen telefon numarasını panoya kopyalar." onclick="copyField('primary_phone','Telefon')"${c.primary_phone ? '' : ' disabled'}><i class="fas fa-phone"></i> Telefon Kopyala</button>
      <button class="d-btn tip tip-left" data-tip="Görünen e-posta adresini panoya kopyalar." onclick="copyField('primary_email','E-posta')"${c.primary_email ? '' : ' disabled'}><i class="fas fa-envelope"></i> E-posta Kopyala</button>
    </div>`;
}

function matchFor(c) {
  if (!c || !c.nace_code) { toast('Bu firmanın NACE kodu yok — eşleştirme yapılamaz.'); return; }
  closeDetailPanel();
  scrollToSection('match-section');
  const sel = document.getElementById('match-nace');
  const grup = (c.nace_code || '').split('.')[0];
  const opt = Array.from(sel.options).find(o => o.value === grup || o.value === c.nace_code);
  if (opt) sel.value = opt.value;
  else {
    const o = document.createElement('option');
    o.value = grup; o.textContent = grup;
    sel.appendChild(o); sel.value = grup;
  }
  runMatchFor(c.company_id);
}

async function runMatchFor(buyerId) {
  const statusEl = document.getElementById('match-status');
  const resultsEl = document.getElementById('match-results');
  const aggEl = document.getElementById('match-agg');
  const mode = document.getElementById('match-mode').value;
  const min = document.getElementById('match-min').value;
  statusEl.className = 'match-status info';
  statusEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Firma profiline göre eşleştiriliyor…';
  aggEl.classList.add('hidden');
  resultsEl.innerHTML = '';
  try {
    const r = await fetch(apiUrl(`/api/match?buyer_id=${encodeURIComponent(buyerId)}&mode=${mode}&min_puan=${min}&limit=20`));
    if (!r.ok) throw new Error(`API ${r.status}`);
    const d = await r.json();
    renderMatchResults(d, mode);
    toast(`Eşleştirme tamam: ${d.toplam} firma`);
  } catch (e) {
    statusEl.className = 'match-status err';
    statusEl.innerHTML = `<i class="fas fa-exclamation-circle"></i> Hata: ${esc(e.message)}`;
  }
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
    renderMatchResults(d, mode);
    toast(`Eşleştirme tamam: ${d.toplam} firma`);
  } catch (e) {
    statusEl.className = 'match-status err';
    statusEl.innerHTML = `<i class="fas fa-exclamation-circle"></i> Eşleştirme hatası: ${esc(e.message)}`;
  }
}

function renderMatchResults(d, mode) {
  const statusEl = document.getElementById('match-status');
  const aggEl = document.getElementById('match-agg');
  const resultsEl = document.getElementById('match-results');
  statusEl.className = 'match-status ok';
  statusEl.innerHTML = `<i class="fas fa-check-circle"></i> <b>${d.toplam}</b> firma eşleştirildi — alıcı: <b>${esc(d.buyer.adi || d.buyer.nace)}</b> · ${esc(d.buyer.nace)} (${mode === 'komple' ? 'tedarik zinciri dahil' : 'sadece aynı sektör'})`;

  const items = d.items || [];
  if (items.length) {
    const ort = (items.reduce((s, i) => s + i.match.puan, 0) / items.length).toFixed(1);
    const dag = {};
    items.forEach(i => { dag[i.match.iliski] = (dag[i.match.iliski] || 0) + 1; });
    const dagStr = Object.entries(dag).map(([k, v]) => `${k}: ${v}`).join(' · ');
    aggEl.className = 'match-agg';
    aggEl.innerHTML = `
      <div class="agg-chip">Toplam<b>${d.toplam}</b></div>
      <div class="agg-chip">Gösterilen<b>${items.length}</b></div>
      <div class="agg-chip">Ortalama Puan<b>${ort}</b></div>
      <div class="agg-chip">İlişki<b style="font-size:11px">${dagStr}</b></div>
      <div class="agg-chip" style="display:flex;align-items:center">
        <button class="d-btn tip tip-left" data-tip="Görünen eşleştirme sonucunu CSV olarak indirir." style="min-width:auto;width:100%" onclick="exportMatchCSV()"><i class="fas fa-download"></i> CSV</button>
      </div>`;
  } else {
    aggEl.classList.add('hidden');
  }

  if (!items.length) {
    resultsEl.innerHTML = '<div class="match-empty">Sonuç yok — Min Puan değerini düşürmeyi deneyin.</div>';
    return;
  }

  window._matchItems = items;
  resultsEl.innerHTML = `
    <div class="match-result-head">
      <span class="mr-col-name">Firma</span><span class="mr-col-nace">Sektör</span>
      <span class="mr-col-score">Puan</span><span class="mr-col-rel">İlişki</span>
    </div>` + items.map((i, idx) => `
    <div class="match-result-row" onclick="showDetail(window._matchItems[${idx}])">
      <div class="mr-name">
        <div class="mr-name-main">${esc(i.legal_name)} <span class="mr-watch ${watchSet.has(i.company_id) ? 'on' : ''}" title="İzleme listesi" onclick="event.stopPropagation(); toggleWatch('${i.company_id}'); this.classList.toggle('on')"><i class="fas fa-star"></i></span></div>
        <div class="mr-name-sub">${esc(i.trade_name)}${i.website_domain ? ' · ' + esc(i.website_domain) : ''}</div>
      </div>
      <div class="mr-nace">${esc(i.nace_code || '-')}</div>
      <div class="mr-score">${matchScoreBar(i.match.puan)}</div>
      <div class="mr-rel">${matchBadge(i.match.iliski)}${matchKirilim(i.match.kirilim)}</div>
    </div>`).join('');
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

function exportMatchCSV() {
  const items = window._matchItems || [];
  if (!items.length) { toast('Dışa aktarılacak sonuç yok.'); return; }
  const head = 'firma,ticaret_adi,nace,puan,iliski,sektor,konum,kalite,kanit,web';
  const rows = items.map(i =>
    `"${(i.legal_name || '').replace(/"/g, '""')}","${(i.trade_name || '').replace(/"/g, '""')}",${i.nace_code || ''},${i.match.puan},${i.match.iliski},${i.match.kirilim.sektor},${i.match.kirilim.konum},${i.match.kirilim.kalite},${i.match.kirilim.kanit},"${i.website_domain || ''}"`
  );
  const blob = new Blob(['\ufeff' + head + '\n' + rows.join('\n')], { type: 'text/csv;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `eslestirme_${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);
  toast(`${items.length} satır CSV indirildi`);
}

function toast(msg) {
  let el = document.getElementById('toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove('show'), 2200);
}

function copyField(field, label) {
  const c = window._detailCompany;
  if (!c || !c[field]) { toast(`${label} bilgisi yok.`); return; }
  navigator.clipboard.writeText(c[field]).then(
    () => toast(`${label} kopyalandı ✓`),
    () => toast('Kopyalama başarısız.')
  );
}

function toggleWatchDetail() {
  const c = window._detailCompany;
  if (!c) return;
  toggleWatch(watchKeyOf(c));
  showDetail(c); // buton etiketini yenile
  toast(isWatched(c) ? 'İzleme listesine eklendi' : 'İzleme listesinden çıkarıldı');
}

// Ctrl+K: arama kutusuna odak (global arama kisayolu)
function toggleInfoCenter() {
  const cards = document.getElementById('info-cards');
  const btn = document.getElementById('info-toggle');
  const collapsed = cards.classList.toggle('collapsed');
  btn.classList.toggle('collapsed', collapsed);
  btn.setAttribute('aria-expanded', String(!collapsed));
  localStorage.setItem('huginn_info_collapsed', collapsed ? '1' : '0');
}
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
    e.preventDefault();
    const s = document.getElementById('global-search');
    if (s) { s.focus(); s.select(); }
  }
});

// ── Monetizasyon: Uyelik modal + kredi gostergesi ──────────────────────────

function getMemberToken() { return localStorage.getItem('huginn_member_token') || ''; }
function setMemberToken(t) {
  if (t) localStorage.setItem('huginn_member_token', t);
  else localStorage.removeItem('huginn_member_token');
  refreshCreditBadge();
}

function refreshCreditBadge() {
  const tok = getMemberToken();
  let el = document.getElementById('credit-badge');
  if (!el) return;
  if (!tok) { el.innerHTML = ''; return; }
  fetch(apiUrl('/api/me?token=' + encodeURIComponent(tok)))
    .then(r => (r.ok ? r.json() : Promise.reject()))
    .then(d => {
      const u = d.user || {};
      if (u.status !== 'onayli') { el.innerHTML = ''; return; }
      el.innerHTML = `<i class="fas fa-coins" style="color:#fbbf24"></i> ${u.credit_balance < 0 ? 'Sınırsız' : u.credit_balance + ' kredi'}
        <span style="color:var(--text-dim);font-size:10px;margin-left:4px">${esc(u.company_name || u.email)}</span>`;
    })
    .catch(() => { el.innerHTML = ''; });
}

function openMembership() {
  let m = document.getElementById('membership-modal');
  if (!m) { buildMembershipModal(); m = document.getElementById('membership-modal'); }
  m.style.display = 'flex';
}

function closeMembership() {
  const m = document.getElementById('membership-modal');
  if (m) m.style.display = 'none';
}

function buildMembershipModal() {
  const wrap = document.createElement('div');
  wrap.id = 'membership-modal';
  wrap.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:10000;display:flex;align-items:center;justify-content:center';
  wrap.innerHTML = `
    <div style="background:var(--panel-bg,#141824);border:1px solid var(--border);border-radius:14px;padding:24px;width:min(560px,92vw);max-height:88vh;overflow-y:auto">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <h3 style="margin:0;font-size:16px"><i class="fas fa-user-plus"></i> Firmanızı Tanıtın — Üyelik Başvurusu</h3>
        <button onclick="closeMembership()" style="background:none;border:none;color:var(--text-dim);font-size:18px;cursor:pointer">✕</button>
      </div>
      <div id="memb-msg" class="match-status hidden" style="margin-bottom:10px"></div>
      <div class="quick-filter-item"><label>Kurumsal E-posta *</label>
        <input id="memb-email" class="filter-select" style="width:100%" placeholder="ad@sirketiniz.com.tr">
        <small style="color:var(--text-dim);font-size:10.5px">Gmail/Hotmail kabul edilmez — sirket e-postasi gereklidir.</small></div>
      <div class="quick-filter-item"><label>Firma Adı *</label>
        <input id="memb-company" class="filter-select" style="width:100%" placeholder="Şirket unvanınız"></div>
      <div class="quick-filter-item"><label>NACE Kodunuz (örn. 29.32)</label>
        <input id="memb-nace" class="filter-select" style="width:100%" placeholder="29.32"></div>
      <div class="quick-filter-item"><label>Ne üretiyor / satıyorsunuz?</label>
        <input id="memb-products" class="filter-select" style="width:100%" placeholder="Örn: fren sistemi yedek parçaları, pres döküm..."></div>
      <div class="quick-filter-item"><label>Kime satmak / nereden tedarik etmek istiyorsunuz? (NACE ana gruplar, virgülle)</label>
        <input id="memb-target" class="filter-select" style="width:100%" placeholder="Örn: 45,46,28"></div>
      <div class="quick-filter-item"><label>Amacınız</label>
        <select id="memb-goal" class="filter-select" style="width:100%">
          <option value="tumu">Hepsi</option><option value="musteri">Müşteri bulmak</option>
          <option value="tedarikci">Tedarikçi bulmak</option><option value="ortagi">İş ortağı</option>
        </select></div>
      <div class="quick-filter-item"><label>Web siteniz</label>
        <input id="memb-web" class="filter-select" style="width:100%" placeholder="sirketiniz.com.tr"></div>
      <label style="display:flex;gap:8px;align-items:flex-start;font-size:11.5px;color:var(--text-dim);margin:10px 0">
        <input type="checkbox" id="memb-kvkk"> KVKK aydınlatma metnini okudum; firma ve iletişim verilerimin
        eşleştirme amacıyla işlenmesine onay veriyorum. (İletişim bilgileri ekranda maskelenir.)
      </label>
      <div style="display:flex;gap:10px;margin-top:8px">
        <button class="d-btn primary" onclick="submitMembership()" style="flex:2"><i class="fas fa-paper-plane"></i> Başvuruyu Gönder</button>
        <button class="d-btn" onclick="closeMembership()" style="flex:1">Vazgeç</button>
      </div>
      <hr style="border-color:var(--border);margin:16px 0 10px">
      <div style="font-size:12px"><b>Üye girişi:</b></div>
      <div style="display:flex;gap:8px;margin-top:6px">
        <input id="memb-login-email" class="filter-select" style="flex:1" placeholder="Kayıtlı kurumsal e-postanız">
        <button class="d-btn" style="flex:0" onclick="memberLogin()">Giriş</button>
      </div>
    </div>`;
  document.body.appendChild(wrap);
  wrap.addEventListener('click', e => { if (e.target === wrap) closeMembership(); });
}

function submitMembership() {
  const body = {
    email: document.getElementById('memb-email').value.trim(),
    company_name: document.getElementById('memb-company').value.trim(),
    nace_code: document.getElementById('memb-nace').value.trim(),
    products_desc: document.getElementById('memb-products').value.trim(),
    target_nace: document.getElementById('memb-target').value.trim(),
    goal: document.getElementById('memb-goal').value,
    website: document.getElementById('memb-web').value.trim(),
    kvkk_consent: document.getElementById('memb-kvkk').checked,
  };
  const msg = document.getElementById('memb-msg');
  fetch(apiUrl('/api/buyer/register'), {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(async r => {
    const d = await r.json().catch(() => ({}));
    if (r.ok) {
      msg.className = 'match-status ok';
      msg.innerHTML = `<i class="fas fa-check-circle"></i> ${esc(d.message || 'Kaydınız alındı.')}`;
    } else {
      msg.className = 'match-status err';
      msg.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${esc(d.detail || 'Hata ' + r.status)}`;
    }
  }).catch(e => {
    msg.className = 'match-status err';
    msg.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${esc(e.message)}`;
  });
}

function memberLogin() {
  const email = document.getElementById('memb-login-email').value.trim();
  fetch(apiUrl('/api/buyer/login'), {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  }).then(async r => {
    const d = await r.json().catch(() => ({}));
    if (r.ok) {
      setMemberToken(d.token);
      closeMembership();
      toast(`Hoş geldiniz — ${d.user.credit_balance < 0 ? 'sınırsız' : d.user.credit_balance + ' kredi'}`);
    } else {
      toast(d.detail || 'Giriş başarısız');
    }
  }).catch(e => toast(e.message));
}

// sayfa acilisinda kredi gostergesi (topbar'a eklenir)
document.addEventListener('DOMContentLoaded', () => {
  const badge = document.createElement('div');
  badge.id = 'credit-badge';
  badge.style.cssText = 'font-size:12px;font-weight:600;color:var(--text)';
  const actions = document.querySelector('.topbar-actions');
  if (actions) actions.prepend(badge);
  refreshCreditBadge();
  // #tasks hash ile acilirsa yonetici panelini otomatik ac (test/debug)
  if (location.hash === '#tasks') openTasks();
});

// ── Admin: uye onay paneli (Gorev Tahtasi overlay icinde) ──────────────────

async function loadAdminPending() {
  const el = document.getElementById('admin-pending-body');
  const tok = getMemberToken();
  try {
    const r = await fetch(apiUrl('/api/admin/pending'), {
      headers: { 'Authorization': 'Bearer ' + tok },
    });
    if (!r.ok) throw new Error(`API ${r.status}`);
    const d = await r.json();
    const bek = d.bekleyen || [];
    window._adminIds = {}; // email -> user_id (credit pack yukleme icin)
    (d.onayli_son || []).forEach(u => {
      if (u.user_id) window._adminIds[u.email] = u.user_id;
    });
el.innerHTML = bek.length ? `
      <div class="match-result-head"><span class="mr-col-name">Bekleyen Üye</span>
        <span class="mr-col-nace">NACE / Amaç</span><span class="mr-col-score">Tier Seç</span><span class="mr-col-rel">İşlem</span></div>` +
      bek.map(b => `
      <div class="match-result-row" style="cursor:default;align-items:start">
        <div class="mr-name">
          <div class="mr-name-main">${esc(b.company_name)}</div>
          <div class="mr-name-sub">${esc(b.email)}${b.website ? " · " + esc(b.website) : ""}</div>
          <div class="mr-name-sub">${esc(b.products_desc || "")}</div>
        </div>
        <div class="mr-nace">${esc(b.nace_code || "-")}<br><small style="color:var(--text-dim)">${esc(b.goal || "")}</small></div>
        <div class="mr-score">
          <select id="tier-${b.user_id}" class="filter-select" style="width:100%">
            <option value="terminal">Terminal (100 kredi)</option>
            <option value="strategic">Strategic (500 kredi)</option>
            <option value="enterprise">Enterprise (Sınırsız+API)</option>
          </select>
        </div>
        <div class="mr-rel" style="display:flex;flex-direction:column;gap:6px">
          <button class="d-btn primary" style="min-width:auto" onclick="adminApprove('${b.user_id}')"><i class="fas fa-check"></i> Onayla</button>
          <button class="d-btn" style="min-width:auto;border-color:rgba(239,68,68,.4);color:#f87171" onclick="adminReject('${b.user_id}')"><i class="fas fa-times"></i> Reddet</button>
        </div>
      </div>`).join("") : `<div class="match-empty"><i class="fas fa-check-circle" style="color:var(--green)"></i> Onay bekleyen üye yok.</div>`;
    const son = d.onayli_son || [];
    if (son.length) {
      el.innerHTML += `<div class="detail-section" style="margin-top:12px">
        <div class="detail-section-title">Onaylı Üyeler (son 10) — Credit Pack Yükle</div>` +
        son.map(u => `
        <div class="detail-row" style="gap:8px">
          <span class="label" style="min-width:200px">${esc(u.company_name)}<br><small style="color:var(--text-dim)">${esc(u.email)}</small></span>
          <span class="value mono" style="min-width:80px">${u.credit_balance < 0 ? 'Sınırsız' : u.credit_balance + ' kredi'}</span>
          <input id="credit-${String(u.email).replace(/[^a-z0-9]/gi, '')}" type="number" min="1" value="50" style="width:70px;background:var(--panel-bg);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:4px 8px;font-size:12px">
          <button class="d-btn" style="min-width:auto" onclick="adminLoadCredit('${esc(u.email)}')">Kredi Yükle</button>
        </div>`).join('') + '</div>';
    }
  } catch (e) {
    el.innerHTML = `<div class="match-empty"><i class="fas fa-exclamation-circle"></i> ${esc(e.message)}</div>`;
  }
}

async function adminApprove(userId) {
  const tier = document.getElementById('tier-' + userId).value;
  const tok = getMemberToken();
  const r = await fetch(apiUrl('/api/admin/approve'), {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok },
    body: JSON.stringify({ user_id: userId, tier }),
  });
  const d = await r.json().catch(() => ({}));
  if (r.ok) {
    toast(`Onaylandı — ${d.tier} tier, ${d.credit_balance < 0 ? 'sınırsız' : d.credit_balance + ' kredi'} yüklendi`);
    loadAdminPending();
  } else toast(d.detail || 'Onaylama başarısız');
}

async function adminReject(userId) {
  const tok = getMemberToken();
  const r = await fetch(apiUrl('/api/admin/approve'), {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok },
    body: JSON.stringify({ user_id: userId, reject: true, note: 'Yonetici reddi' }),
  });
  if (r.ok) { toast('Üyelik reddedildi'); loadAdminPending(); } else toast('İşlem başarısız');
}

async function adminLoadCredit(email) {
  const inp = document.getElementById('credit-' + email.replace(/[^a-z0-9]/gi, ''));
  const amount = parseInt(inp ? inp.value : '50') || 50;
  const tok = getMemberToken();
  const uid = (window._adminIds || {})[email];
  if (!uid) { toast('Kullanıcı kimliği bulunamadı — sayfayı yenileyin.'); return; }
  const r = await fetch(apiUrl('/api/admin/credit'), {
    method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok },
    body: JSON.stringify({ user_id: uid, amount }),
  });
  if (r.ok) { toast(`${amount} kredi yüklendi`); loadAdminPending(); } else toast('Yükleme başarısız');
}

// ── Y22: Isletmem sayfasi (bagimsiz tam ekran overlay: profil + kredi + paket) ──

function openIsletmem() {
  let ov = document.getElementById('isletmem-overlay');
  if (!ov) {
    ov = document.createElement('div');
    ov.id = 'isletmem-overlay';
    ov.style.cssText = 'position:fixed;inset:0;background:rgba(5,7,12,.92);z-index:9998;overflow-y:auto;padding:28px 20px';
    ov.innerHTML = `
      <div style="max-width:980px;margin:0 auto">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <h2 style="margin:0;font-size:20px"><i class="fas fa-briefcase" style="color:var(--accent)"></i> İşletmem
            <span style="font-size:12px;color:var(--text-dim);margin-left:8px">profil · kredi · paket yönetimi</span></h2>
          <button onclick="closeIsletmem()" style="background:var(--panel-bg);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:8px 14px;cursor:pointer;font-size:13px">✕ Kapat</button>
        </div>
        <div class="chart-card" style="padding:4px 0 12px">
          <p class="sources-hint" style="padding:8px 16px 0"><i class="fas fa-info-circle"></i> Profiliniz ne kadar doluysa eşleştirme o kadar isabetli olur. Krediniz her "Eşleştir" ve kontak görüntülemesinde azalır.</p>
          <div id="isletmem-body" style="padding:0 16px 16px"></div>
        </div>
      </div>`;
    document.body.appendChild(ov);
    ov.addEventListener('click', e => { if (e.target === ov) closeIsletmem(); });
  }
  ov.style.display = 'block';
  document.body.style.overflow = 'hidden';
  loadIsletmem();
}

function closeIsletmem() {
  const ov = document.getElementById('isletmem-overlay');
  if (ov) ov.style.display = 'none';
  document.body.style.overflow = '';
}

function loadIsletmem() {
  const tok = getMemberToken();
  const el = document.getElementById('isletmem-body');
  if (!el) return;
  if (!tok) {
    el.innerHTML = `
      <div class="match-empty">
        <div style="font-size:15px;margin-bottom:8px"><i class="fas fa-briefcase"></i> İşletmenizi sisteme tanıtın</div>
        <div style="max-width:520px;margin:0 auto 14px">Üye olduğunuzda firmalarınız kişiselleştirilmiş eşleştirmeler, kredili kontak erişimi ve paket yönetimi açılır. Kurumsal e-posta ile kayıt ücretsizdir; üyelik onayı sonrası krediniz yüklenir.</div>
        <button class="d-btn primary" style="min-width:220px" onclick="openMembership()"><i class="fas fa-user-plus"></i> Kayıt Ol / Giriş Yap</button>
      </div>`;
    return;
  }
  fetch(apiUrl('/api/buyer/profile?token=' + encodeURIComponent(tok)))
    .then(async r => {
      const d = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(d.detail || r.status);
      renderIsletmem(d);
    })
    .catch(e => {
      if (String(e.message).includes('oturum gecersiz')) {
        setMemberToken('');
        loadIsletmem();
        return;
      }
      el.innerHTML = `<div class="match-empty"><i class="fas fa-exclamation-circle"></i> Yüklenemedi: ${esc(e.message)}</div>`;
    });
}

function renderIsletmem(d) {
  const el = document.getElementById('isletmem-body');
  const p = d.profil || {};
  const tam = p.profil_tamlama || 0;
  const tamRenk = tam >= 80 ? 'var(--green)' : tam >= 50 ? '#fbbf24' : 'var(--red)';
  const onayli = p.status === 'onayli';
  const krediTxt = p.credit_balance < 0 ? 'Sınırsız' : `${p.credit_balance} kredi`;

  el.innerHTML = `
    <div class="match-agg" style="margin:0 0 12px">
      <div class="agg-chip">Durum<b>${esc(p.status || '-')}</b></div>
      <div class="agg-chip">Paket / Tier<b>${esc(p.tier || '-')}</b></div>
      <div class="agg-chip">Kredi Bakiyesi<b style="color:${p.credit_balance < 0 ? 'var(--green)' : 'var(--accent)'}">${krediTxt}</b></div>
      <div class="agg-chip" style="min-width:180px">Profil Tamamlanma<b style="color:${tamRenk}">%${tam}</b>
        <div class="mk-bar" style="margin-top:4px"><div class="mk-fill" style="width:${tam}%;background:${tamRenk}"></div></div></div>
      ${onayli ? `<div class="agg-chip"><button class="d-btn tip tip-left" data-tip="Credit Pack: krediniz bittiğinde 750 TRY / 50 kredi ile devam edebilirsiniz. Talebiniz yönetici onayıyla yüklenir." style="min-width:auto;width:100%" onclick="requestCreditPack()"><i class="fas fa-shopping-cart"></i> Kredi Yükle</button></div>` : ''}
    </div>
    ${!onayli ? `<div class="match-status info" style="margin:0 0 12px"><i class="fas fa-hourglass-half"></i> Üyelik onayınız bekleniyor — profilinizi şimdiden doldurun, onayla birlikte eşleştirmeler kişiselleşir.</div>` : ''}
    <div class="match-result-head"><span class="mr-col-name">Firma Profili</span><span class="mr-col-nace">Departman / Rol</span><span class="mr-col-score">Eşleştirme Amacı</span><span class="mr-col-rel">İletişim & Web</span></div>
    <div class="match-result-row" style="cursor:default;align-items:start">
      <div class="mr-name">
        <div class="quick-filter-item" style="width:100%"><label>Firma Adı</label><input id="is-company" class="filter-select" style="width:100%" value="${esc(p.company_name || '')}"></div>
        <div class="quick-filter-item" style="width:100%;margin-top:6px"><label>NACE Kodu</label><input id="is-nace" class="filter-select" style="width:100%" value="${esc(p.nace_code || '')}" placeholder="29.32"></div>
        <div class="quick-filter-item" style="width:100%;margin-top:6px"><label>Ne üretiyor / satıyorsunuz?</label><input id="is-products" class="filter-select" style="width:100%" value="${esc(p.products_desc || '')}" placeholder="fren sistemi yedek parçaları, pres döküm..."></div>
        <div class="quick-filter-item" style="width:100%;margin-top:6px"><label>Hedef Sektörler (NACE ana grup, virgülle)</label><input id="is-target" class="filter-select" style="width:100%" value="${esc(p.target_nace || '')}" placeholder="45,46,28"></div>
      </div>
      <div class="mr-nace">
        <div class="quick-filter-item" style="width:100%"><label>Departman / Rolünüz</label><input id="is-department" class="filter-select" style="width:100%" value="${esc(p.department || '')}" placeholder="Satış, Üretim, Satın Alma..."></div>
        <small style="color:var(--text-dim);font-size:10.5px;margin-top:4px;display:block">Departman bilgisi önerileri kişiselleştirmek için kullanılır.</small>
      </div>
      <div class="mr-score">
        <div class="quick-filter-item" style="width:100%"><label>Eşleştirme Amacı</label>
          <select id="is-goal" class="filter-select" style="width:100%">
            <option value="tumu"${p.goal === 'tumu' ? ' selected' : ''}>Hepsi</option>
            <option value="musteri"${p.goal === 'musteri' ? ' selected' : ''}>Müşteri bulmak</option>
            <option value="tedarikci"${p.goal === 'tedarikci' ? ' selected' : ''}>Tedarikçi bulmak</option>
            <option value="ortagi"${p.goal === 'ortagi' ? ' selected' : ''}>İş ortağı</option>
          </select></div>
        <small style="color:var(--text-dim);font-size:10.5px;display:block;margin-top:4px">Amaç, eşleştirme yönünü belirler (müşteri/tedarikçi).</small>
      </div>
      <div class="mr-rel">
        <div class="quick-filter-item" style="width:100%"><label>Yetkili Adı</label><input id="is-contact" class="filter-select" style="width:100%" value="${esc(p.contact_name || '')}"></div>
        <div class="quick-filter-item" style="width:100%;margin-top:6px"><label>Web Site</label><input id="is-web" class="filter-select" style="width:100%" value="${esc(p.website || '')}"></div>
      </div>
    </div>
    <div style="display:flex;gap:10px;margin:12px 0">
      <button class="d-btn primary" style="flex:2" onclick="saveIsletmemProfile()"><i class="fas fa-save"></i> Profili Kaydet</button>
      <button class="d-btn" style="flex:1" onclick="loadIsletmem()">Sıfırla</button>
    </div>
    <div class="detail-section" style="margin-top:8px">
      <div class="detail-section-title">Kredi Hareketleri (son 12)</div>
      ${(d.ledger || []).map(l => `
        <div class="detail-row"><span class="label">${esc(l.created_at ? String(l.created_at).substring(0, 16).replace('T', ' ') : '')}</span>
        <span class="value mono" style="color:${l.delta > 0 ? 'var(--green)' : 'var(--red)'}">${l.delta > 0 ? '+' : ''}${l.delta}</span>
        <span class="value" style="color:var(--text-dim);font-size:11px">${esc(l.reason)} → bakiye ${l.balance_after}</span></div>`).join('') ||
        '<div class="detail-row"><span class="label">Henüz hareket yok</span></div>'}
    </div>
    ${p.tier === 'enterprise' && p.api_key ? `
    <div class="detail-section">
      <div class="detail-section-title">Enterprise API Key</div>
      <div class="detail-row"><span class="label">API Key</span><span class="value mono">${esc((p.api_key || '').substring(0, 12))}…</span>
      <button class="d-btn" style="min-width:auto;flex:0" onclick="copyField('${p.api_key}','API Key')"><i class="fas fa-copy"></i></button></div>
    </div>` : ''}`;
}

function saveIsletmemProfile() {
  const tok = getMemberToken();
  if (!tok) { toast('Önce giriş yapın.'); return; }
  const body = {
    company_name: document.getElementById('is-company').value,
    nace_code: document.getElementById('is-nace').value,
    products_desc: document.getElementById('is-products').value,
    target_nace: document.getElementById('is-target').value,
    department: document.getElementById('is-department').value,
    goal: document.getElementById('is-goal').value,
    contact_name: document.getElementById('is-contact').value,
    website: document.getElementById('is-web').value,
  };
  fetch(apiUrl('/api/buyer/profile?token=' + encodeURIComponent(tok)), {
    method: 'PUT', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(async r => {
    const d = await r.json().catch(() => ({}));
    if (r.ok) {
      toast(`Profil kaydedildi — tamamlanma %${d.profil_tamlama}`);
      refreshCreditBadge();
      loadIsletmem();
    } else { toast(d.detail || 'Kaydetme başarısız'); }
  }).catch(e => toast(e.message));
}

function requestCreditPack() {
  toast('Credit Pack talebiniz alındı — yönetici onayıyla krediniz yüklenecek (750 TRY / 50 kredi).');
}
