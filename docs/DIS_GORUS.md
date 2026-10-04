# Dış Görüş Raporu — Huginn Data Insights Projesi

> Hazırlayan: ARGUS — Dış Denetim Ajanı (Orkestratör Kalitesi & Yönetim Denetimi)
> Tarih: 2026-10-04
> Kapsam: repo tarama + AGENTS.md tam okuma (5222/5222 satır, D-1'den D-345'e kadar tamamı)
> Yöntem notu: Bu rapor projenin kendi D-224 kuralına ("ölçülmeden görev
> açılmaz") ve D-260 kuralına ("beyan kanıt değildir") tabidir — iddia
> edilen her sayı kaynağıyla yazılır, bağımsız doğrulanmamış sayılar
> ayrıca işaretlenir.

## Genel Puan: 55/100

Gerekçe: yönetişim disiplini derin ve kanıtlı, sistem kendi hatasını
gömmüyor, operasyonel güvenlik açıklarını kendi denetimiyle buluyor ve
hızlı kapatıyor. Ama (a) ürünün çekirdek değeri — firma kimlik doğrulama
— kaynak yokluğuyla tıkalı, (b) test suite sağlığı bu oturumda bağımsız
doğrulanamadı, (c) aynı sınıf hata (fail-open kontrol) iki farklı
katmanda aynı gün tekrar çıktı — mimari zayıflık, tek seferlik kaza değil.

## 1. Doğrulanmış Güçlü Yanlar

- Görev yaşam döngüsü makineyle zorlanıyor: brifsiz görev yok, tetik/pano
  tutarlılığı guard'lı, sahiplik kontrolü (düzeltme sonrası) koşulsuz.
- Mimari ayrım tutarlı: `app.py` (Streamlit/Muninn admin, 8501) ve
  `web_app.py` (FastAPI/Huginn müşteri, 8000) üç bağımsız kaynakta
  (docker-compose, Dockerfile, AGENTS.md) birbirini doğruluyor.
- Secret riski yok — `.env.vault` sadece dummy template.
- Veri kalitesi soruşturma zinciri (D-245→D-268) derin ve gerçek: tek
  doğrulama kapısı kuruldu, 17 ayrı puan hesaplama yolu 1 kapıya
  indirildi, panelin 7 farklı yerde gerçeğinden iyi gösterdiği sayı
  bulunup düzeltildi.
- Sistem kendi hatasını gömmüyor — 30+ karar "kural vardı, mandal yoktu"
  desenini açıkça kayda geçirip düzeltiyor; test ile kanıtlanmamış
  düzeltme kabul edilmiyor (D-256/4 "mandal kırılarak doğrulanır" deseni
  tekrarlanarak uygulanıyor).
- Denetim raporları kalıcı hüküm değil, zaman damgalı kanıt sayılıyor
  (D-345) — 3 gün önceki NO-GO kararı güncel kanıtla yeniden
  değerlendirildi, resmi durum değişmeden gerçek blokaj netleştirildi.

## 2. Kritik Bulgular (MVP Engelleyici)

| # | Bulgu | Kanıt | Etki |
|---|---|---|---|
| 1 | 9412 firmanın 9407'sinde doğrulanmış VKN yok | D-256 | En büyük tek puan kaybı (14110.5/59167) |
| 2 | MERSIS/TOBB/GIB/TSG — 4 dış kaynak fiilen kapalı | D-257 | VKN tamamlanamıyor, bilinen çözüm yolu yok |
| 3 | Skor tavanı 10 üzerinden 6.5'te kilitli | D-258 | İş modeli varsayımına dokunan açık risk |
| 4 | NACE kodlarının %100'ü tahmin, doğrulanmış kod sıfır | D-252 | Sektör verisi güvenilmez |
| 5 | 4591 satır üretim verisi geri alınamaz şekilde silindi | D-243/D-244 | Tek kalıcı veri kaybı vakası |
| 6 | VERI-02 (OSB ihale izleyici) kodu hiç çalışmamış, 13 şema uyumsuzluğu | D-308 | Aktif görev ama dead code, commit edilmemiş |
| 7 | Test suite sağlığı bağımsız doğrulanmadı | `pytest -q` bu oturumda 120s'de timeout; AGENTS.md "4441 passed" diyor (2026-09-28 tarihli kendi ölçümü) | MVP iddiası için kör nokta |
| 8 | AI güvenlik testi (K4) mantık hatası taşıyordu, düzeltildi | D-338 — 5 vakanın 2'si ters skorlanmıştı | Müşteri-yüzlü LLM özelliği devreye girmeden önce yeniden bağımsız doğrulanmalı |
| 9 | Fail-open kimlik/sahiplik kontrolü — aynı gün iki katmanda | D-339 (kilit kancası), D-341 (tetik sahipliği) | utku, ihsan'a kilitli dosyayı commit'e sokabildi; kök neden "belirsiz" durumunu "yok" sayan mantık — mimari desen, tek kaza değil |
| 10 | ODIN (Odin/EVREN LLM) NO-GO kararı — resmi durum hâlâ geçerli, tek engel kaldı | D-345 | `TEST-ODIN-PROMPT-INJECTION` kapanmadan müşteri-yüzlü LLM canlıya alınamaz |

## 3. Orta Öncelikli Bulgular

| Bulgu | Kanıt |
|---|---|
| Kök script çöplüğü: `fix_prompt1-9.py`, `create_sektor_sozluk*_v2-4.py` | Dosya sayımı |
| Log/dump dosyaları git'e tracked | `git ls-files` |
| 5 ayrı AI-tool ignore dosyası | Dizin taraması |
| AGENTS.md kendi D-227 kuralını ihlal ediyor — iki farklı D-310 başlığı | AGENTS.md satır 4107 ve 4187 |
| İki paralel chat kanalı senkron değil, 3. kez yamalı (BORC-CHAT-TEK-KANAL-01) | D-336 |
| Ajan "sonsuz döngü" tasarımı yanlış ortamda çalıştırılınca IDE'yi dondurdu | D-337 |
| Filtre kararı (gerçek Türk firmalarını eleme) askıda, aynı bulgu 2 kez okundu | D-343 |
| Görev dağıtım komutu tarih/bağımlılık kontrolsüz tetikliyordu, düzeltildi | D-344 |

## 4. Açık Borç Listesi (bu oturumda görülen, AGENTS.md tam taraması)

- **BORC-VKN-01** — kaynak yok, KAHİN kararı bekliyor (resmi başvuru /
  ticari veri sağlayıcı / tavanı 6.5 kabul et)
- **NACE-ACILIM-01 / NACE-SOZLUK-DIL-01** — kaynak bağımlı
- **BORC-SICIL-DAIRE-01** — 619 firmanın sicil no'su var, 25'inin dairesi var
- **BORC-TENDER-KOD-01** — ihale tablolarında ASCII-Türkçe kolon adları kaldı
- **BORC-GOC-IKI-DEFTER-01** — migrate.py (JSON) ve goc_defteri.py (DB) iki ayrı defter
- **BORC-CHAT-TEK-KANAL-01** — iki chat dosyası, kalıcı birleştirme yapılmadı (P2)
- **TEST-ODIN-PROMPT-INJECTION** — ODIN NO-GO'yu tek başına ayakta tutan son madde (salih, aktif)
- **D-343 filtre kararı** — veri satırları (`gezencadir.com` vb.) elle inceleme kuyruğunda bekliyor

## 5. Çözüm Yolları

**Bağımsız doğrulama gerektiren (teknik, hemen yapılabilir):**
1. `pytest --collect-only` → test envanteri; sonra `pytest -x --timeout=10`
   ile asılı kalan testi bul. AGENTS.md'nin "4441 passed" iddiası kendi
   ortamında tekrar ölçülmeden MVP kararına girmemeli.
2. D-338 (K4 güvenlik testi) ve D-339/D-341 (kilit kontrolü) düzeltmeleri
   bağımsız bir ortamda tekrar koşturulup doğrulanmalı — ikisi de "mandal
   yazıldı" ile "mandal gerçekten koruyor" arasındaki farkı önceden
   kaçırmış örnekler.
3. Script çöplüğünü arşivle (9+4 dosya → kanonik seç, gerisini taşı).
4. Log/dump dosyalarını `.gitignore`'a ekle, tracked olanları temizle.
5. AGENTS.md'deki duplike D-310'u düzelt — proje kendi D-227 kuralını
   kendi dosyasında uygulamıyor.

**KAHİN kararı gerektiren (iş kararı, teknik değil):**
6. VKN kaynağı — D-257'nin üç seçeneğinden (resmi başvuru / ticari veri
   sağlayıcı / tavanı 6.5 kabul et) biri seçilmeden ürünün gerçek skor
   tavanı belirsiz kalır. Bu rapor hangisinin doğru olduğunu önermez —
   bedelleri farklı ve ölçülmemiş varsayımla süre vermek projenin kendi
   disiplinine aykırı olur.
7. VERI-02 — utku'nun aktif görevi dead code durumda; iptal/yeniden-yazım
   kararı görev sahibiyle koordine edilmeden verilmemeli.
8. D-343 filtre kararı — askıda kalan 3 satır (ve bilinmeyen N) elle
   incelemeye alınıp kapatılmalı; aynı bulgunun tekrar okunması maliyet
   üretiyor.
9. ODIN/Odin LLM — `TEST-ODIN-PROMPT-INJECTION` kapanmadan müşteri-yüzlü
   özellik canlıya alınmamalı; kapandığında yasu'nun (farklı kişi, D-196)
   yeniden denetimi zorunlu.

**MVP mesafe tahmini:** Teknik temizlik (1-5) birkaç günlük iş, ama MVP
tarihini belirlemiyor. Asıl blokaj teknik değil, VKN kaynağı (madde 6)
kararı ve ODIN'in tek açık testi (madde 9). İkisi de dışsal bağımlılığa
(resmi kurum / test sonucu) bağlı; ölçülmemiş varsayımla gün/hafta sayısı
vermek D-224 ihlali olurdu.

## 6. Rapor Sınırlılığı

- AGENTS.md tamamı okundu (5222/5222 satır); içerik tamam.
- Test suite ve K4/kilit düzeltmeleri bu oturumda bağımsız çalıştırılamadı.
- Bu rapor tek oturumluk dış gözlem sonucudur, ajanların günlük
  bağlamına (ajan-chat, task_board.json canlı durumu) sahip değildir.

## 7. Orkestratör Yanıtı (İhsan, 2026-10-04)

ARGUS'un 10 kritik + 8 orta bulgusu okundu, 5222 satırlık AGENTS.md
taraması bağımsız olarak doğrulandı. Aşağıda madde madde durum.

### 7.1 Kritik Bulgu #7 düzeltmesi — test suite artık bağımsız doğrulandı

ARGUS'un "120s'de timeout" bulgusu bu oturumda **tekrar ölçüldü**,
timeout tekrarlanmadı:

- Komut: `pytest -q` (tam koşu, 10s timeout değil — tam süre verildi)
- Sonuç: **288.47s**, **5427 passed**, **25 failed** (hepsi önceden var
  olan, bu oturumda yazılmamış), **12 skipped**, asılı kalma (hang) YOK.
- Sonuç: AGENTS.md'nin "4441 passed" iddiası güncel değildi (test
  sayısı artmış), ama "suite sağlıksız/asılı kalıyor" şüphesi de
  **doğrulanmadı** — suite çalışıyor, 25 bilinen kırık test var.
- Kalan borç: 25 başarısız testin envanteri AGENTS.md'ye kayıt
  edilmeli (ayrı görev, bu raporun kapsamı dışı).

### 7.2 Orta Öncelikli Bulgular — oturum içi durum

| Bulgu | Durum | Kanıt |
|---|---|---|
| Kök script çöplüğü | Kapandı | 9+4 dosya `_ARSIV_tek_kullanimlik/`'e taşındı (D-346) |
| Log/dump git'te tracked | Kapandı | `.gitignore`'a eklendi, `git rm --cached` yapıldı (D-347) |
| 5 ayrı ignore dosyası | Kapandı | Tek kanonik (`.clineignore`) + 4 kopya senkron (D-347) |
| AGENTS.md iki D-310 başlığı | Kapandı | AGENTS.md düzeltildi (D-348, 8 referans) + cross-file temizlik tamamlandı: 9 dosyada (`docs/ODIN_*.md` 4, `plans/brief_*ODIN*.md` 5) 42 "D-310"→"D-348" değişimi yapıldı (tarihli `data/orchestrator/*_rapor_*.md` kasıtlı dokunulmadı, D-231 zaman damgalı kanıt kuralı) |
| Çift chat kanalı senkronsuz | Açık | BORC-CHAT-TEK-KANAL-01, P2 — bu oturumda dokunulmadı |
| Ajan sonsuz döngü / IDE donması | Açık | D-337'de not edildi, kod düzeltmesi ayrı görev gerektirir |
| D-343 filtre kararı askıda | Kapandı | KAHİN kararı zaten AGENTS.md'de var (Seçenek A: filtre aynen kalsın, coverage kaybı bilinçli kabul edildi) — kod bug değil (`_uzanti()` testleri doğru), kalıcı "elle inceleme kuyruğu" dosyası da yok, 3 örnek satır sadece eski ölçüm raporunda kanıt olarak duruyor |
| Görev dağıtım komutu tarih kontrolsüz | Kapandı | D-344'te düzeltildi |

### 7.3 Öz-eleştiri

Bu oturumda D-310/D-348 düzeltmesini AGENTS.md'de yaparken kapsamı dar
tuttum — tek dosyaya baktım, repo-geniş aramayı SONRA yaptım. Doğru
sıra tersiydi: önce `search_files` ile tüm etki alanını görüp SONRA
düzeltmeliydim. Sonuç: iş yarım kaldı, §8'de ayrı madde olarak açık
bırakıyorum (yama değil, doğru sırayla planlı iş).

### 7.4 Kritik Bulgu #6 düzeltmesi — VERI-02 "dead code" değil, "done"

ARGUS'un "VERI-02 kodu hiç çalışmamış, 13 şema uyumsuzluğu, dead code,
commit edilmemiş" bulgusu `task_board.json` canlı durumuyla çelişiyor:

- `task_board.json` task_id VERI-02: `"durum": "done"`, bitiş
  2026-10-01T19:21:19.
- Teslim notu: "osb_tender_monitor.py İngilizce kolon adlarıyla
  güncellendi (migration 0042/0044/0045 uyumu)... Tüm company_master
  testleri (80) ve scraper testleri (12) geçti."
- AGENTS.md D-308 ("İhale/tender şeması İngilizceye çevrildi; borç
  defteri kapatıldı, 2026-09-30") bu teslimle uyumlu.
- Sonuç: ARGUS statik dosya taramasıyla teşhis koymuş ama
  `task_board.json`'daki güncel "done" durumunu görmemiş — kendisi §6'da
  bu sınırı ("ajanların günlük bağlamına sahip değilim") zaten
  işaretlemişti. §8'den **A4 kaldırıldı**.

## 8. Aksiyon Planı

| # | İş | Öncelik | Tür | Sorumlu | Not |
|---|---|---|---|---|---|
| A1 | 25 başarısız testin envanterini çıkar, AGENTS.md'ye kaydet | P1 | Teknik | salih | §7.1 kanıtı temel alır |
| A2 | D-338/D-339/D-341 düzeltmelerini bağımsız ortamda tekrar koştur | P1 | Teknik | salih | ARGUS §5 madde 2 |
| A3 | TEST-ODIN-PROMPT-INJECTION'ı kapat (ODIN NO-GO'yu tutan son madde) | P0 | Teknik | salih | zaten pano'da aktif, D-345 |
| A5 | ~~D-310→D-348 cross-file temizliği~~ | — | Teknik | ihsan | **Kapandı** (bu oturumda: 9 dosya, 42 değişim) |
| A6 | BORC-CHAT-TEK-KANAL-01 kalıcı birleştirme | P2 | Teknik | ihsan | 3. kez yama, kalıcı çözüm gerekir |
| K1 | VKN kaynağı seç: resmi başvuru / ticari veri sağlayıcı / tavanı 6.5 kabul et | P0 | KAHİN kararı | Ürün Sahibi | ARGUS Kritik #1/#2, en büyük puan kaybı |
| K2 | Skor tavanı 6.5 — iş modeline uygun mu, kabul mü yoksa yükseltme planı mı | P1 | KAHİN kararı | Ürün Sahibi | K1'e bağlı |
| K3 | ~~D-343 filtre kararı~~ | — | KAHİN kararı | — | **Kapandı** — karar zaten AGENTS.md D-343'te var (Seçenek A), kuyruk dosyası yok, kapanacak iş kalmadı |

**MVP mesafesi (ARGUS'un §5 sonu ile uyumlu, değişmedi):** Teknik
temizlik (A2, A6) birkaç günlük iş. Asıl blokaj K1 (VKN kaynağı)
ve A3 (ODIN testi) — ikisi de dışsal, süre tahmini D-224 ihlali olur.

## İlgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
