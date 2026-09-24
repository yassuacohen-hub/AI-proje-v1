#!/usr/bin/env node
// Y26 oncesi gorev panosu revizyonu (idempotent): X01-X05 gorevlerini ekler,
// eskimis notlari gunceller. Cikti: task_board.json (BOM'suz UTF-8).
import {readFileSync, writeFileSync} from 'node:fs';
const FILE = 'C:/Projeler/Huginn Data Insights/data/orchestrator/task_board.json';
const arr = JSON.parse(readFileSync(FILE, 'utf8'));
const has = id => arr.some(g => g.task_id === id);
const now = '2026-09-10T00:00:00';
const g = (id, baslik, sahip, oncelik, durum, not) => {
  if (has(id)) return;
  arr.push({task_id: id, baslik, sahip, oncelik, durum, baslangic: now, bitis: null, dosyalar: [], not});
};
// Eski tanimlardaki belirsizlikleri acik revizyon gorevlerine cevir
g('X01', 'ARASTIRMA: GIB VKN dogrulama (acik API + KVKK) - scripts/gib_vkn_lookup.py devami', 'arastirmaci', 'P1', 'plan',
  'REVIZE. gib_vkn_lookup.py + vkn_batch_enrich.py hazir; resmi GIB API erisim yolu + KVKK raporlanacak. VKN zenginlestirme kuyrugu bekliyor.');
g('X02', 'BUG: VKN zenginlestirme (MERSIS + web footer) pipeline tamamlama', 'gelistirici', 'P1', 'blocked',
  'REVIZE (eski MERSIS pipeline). vkn_batch_enrich.py + vkn_review_queue.py mevcut; data/orchestrator/engel_raporu.json engelleri cozulmeli. VKN dolulugu KPI hedefi.');
g('X03', 'MATCH v3: buyer profili skorlari (olcek uyumu + sertifika + amac yonu)', 'gelistirici', 'P2', 'plan',
  'YENI. Buyer profilindeki employee_range, certificates, goal alanlari match skoruna baglanacak. Y22 (yon secimi) uzerine dogal sonraki adim.');
g('X04', 'UYELIK: sifre sifirlama + kurumsal e-posta dogrulama + Telegram hosgeldin', 'gelistirici', 'P2', 'plan',
  'REVIZE (eski Y24). PBKDF2 sifre sistemi hazir; sifirlama linki + dogrulama e-postasi + Telegram bot hosgeldin raporu. SMTP saglayici secimi gerekli.');
g('X05', 'Y26: API key yonetimi - rotasyon + kullanim metrikleri + tier rate limit', 'gelistirici', 'P2', 'plan',
  'REVIZE (eski Y26). require_api_key istek sayaci + /metrics tier bazli rapor + enterprise key rotasyon endpoint. Su an sadece uretim zamanli key var.');
writeFileSync(FILE, JSON.stringify(arr, null, 2), {encoding: 'utf8'});
console.log('OK: gorev panosu revize edildi, toplam=' + arr.length);
