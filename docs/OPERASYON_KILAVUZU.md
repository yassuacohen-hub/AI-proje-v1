# OPERASYON KILAVUZU — Ürün Sahibi El Kitabı

> ⚠️ **Kurtarma notu (D-223 — 2026-09-27):** Bu dosya 2026-09-21 tarihinde yazıldı, D-187 sırasında yedeğe alındı ve canlı ağaçta kayboldu. Buraya geri alındı. İçindeki `worktree klasoru/` yolları `Huginn Data Insights/` olarak düzeltildi (13 adet). Satır sayıları ve ölçümler 2026-09-21 tarihlidir, güncel değildir — güncelleme ayrı görevdir.


> **Hedef kitle:** Türkçe konuşan, teknik olmayan ürün sahibi (KAHİN)  
> **Amaç:** Huginn Data Projesi Obsidian vault'unu, çoklu ajan (İHSAN, UTKU, SALİH, YASU) sistemini anlamak ve yönetmek.  
> **Son güncelleme:** 2026-09-21  
> **Hazırlayan:** İHSAN (Orkestratör)

---

## 1. VAULT YAPISI — Ortak Hafıza Ağacı

### 1.1 Vault nedir?

**Vault** = ajanlara ait paylaşılan not deposu (Obsidian formatında). 407 markdown dosyası + 49 dizin. Ajan brifler, raporlar, kararlar, görev bilgileri burada tutulur. **Tek kaynak odağı (SSOT)** = dijital bellektir.

### 1.2 Ana dizin yapısı

```
Huginn Data Insights/
├── AGENTS.md                    # ← Çoklu ajan kuralları (DEMİR KURAL)
├── PLAN_gorev_panosu.md         # ← Görev yönetim planı
├── VAULT_HARITA.md              # ← 407 nod rehberi (otomatik üretim)
├── ANA_KURALLAR.md              # ← Sistem kuralları
├── CHANGELOG.md                 # ← Tüm değişikliklerin tarihi
│
├── data/
│   └── orchestrator/            # ← MERKEZ: görev panosu + raporlar
│       ├── task_board.json      # ← Ana görev veritabanı (ajan kurgusu)
│       ├── decision_log.jsonl   # ← Karar defteri (D-XX numaralı)
│       ├── triggers/            # ← Ajan posta kutuları
│       │   ├── ihsan.jsonl
│       │   ├── utku.jsonl
│       │   ├── salih.jsonl
│       │   └── yasu.jsonl
│       └── *_rapor_*.md         # ← Görev raporları
│
├── docs/
│   ├── AJAN_DETAY.md            # ← Ajan işleri detaylı (§ bölümler)
│   ├── GOREV_PANOSU_KULLANIM_KILAVUZU.md
│   ├── teknik_sozluk.md
│   ├── ajanlar/                 # ← Her ajan için persona dosyası
│   │   ├── ihsan.md
│   │   ├── utku.md
│   │   ├── salih.md
│   │   └── yasu.md
│   └── brand/                   # ← Marka SSOT (Huginn 🦅 / Muninn 🛡️ / Odin ⚡)
│
└── scripts/                     # ← Operasyon scriptleri
    ├── gorev_kutusu.py          # ← Ajan posta kutusu + onay CLI
    ├── karar_yaz.py             # ← Kararı yazıyor (D-XX)
    ├── vault_saglik.py          # ← Vault sağlık kontrolü
    ├── oto_nobetci.py           # ← Otomatik onay/teslim
    └── [100+ ingest/scrape/maintenance scriptleri]
```

### 1.3 Hub notlar = merkez başlıklar

Her dizinin "merkez not"ü başlığını taşır:
- `data/orchestrator/` → **Görev defteri, kararlar, raporlar**
- `docs/` → **Kurallar, kişi bilgileri, dokümantasyon**
- `docs/ajanlar/` → **İHSAN, UTKU, SALİH, YASU kişileri**

**VAULT_HARITA.md**, 407 nodu bu merkez notlar altında gruplandırır. Yeni döküman yazarken:
1. Doğru dizine koy
2. Başlığını VAULT_HARITA.md'ye ekle (`[[klasor/dosya|alias]]` formatında)

### 1.4 Görev panosu nerede?

İki yerde aynı bilgi:
- **JSON (makine):** `data/orchestrator/task_board.json` — tek doğruluk kaynağı
- **Markdown (insan):** `data/orchestrator/gorev_panosu.md` — otomatik üretilir, elle düzenleme **YASAK**

Pano statüsü: `plan` → `aktif` → `teslim` → `review` → `done` → arşiv

---

## 2. SÖZLÜK — Proje Terimleri (50+ madde)

### 2.1 Ajanlar ve Roller

| Ajan | Araç | Rol | Görevler |
|------|------|-----|---------|
| **İHSAN** | roo (Claude Code) | Orkestratör | Görev dağıtımı, onay, commit, karar kaydı, koordinasyon. Son söz İHSAN'da. |
| **UTKU** | kilo (Cursor) | Üretim/Hacim | Kod yazma, refactoring, test, CI/CD. Kilitli dosyalarda çalışır. |
| **SALİH** | continue (Continue IDE) | Test Danışman | Mekanik görevler: test planlama, benchmark, bilgi tabanı, uyum denetimi. Rapor yazımı → YASU'ya gider. |
| **YASU** | cline (Cline) | Denetim/Review | Kod inceleme, güvenlik, mimari uyum, doküman doğrulama. |

**Eski → Yeni ad geçişi (D-60):**
- `roo` / `orkestrator` → **İHSAN**
- `kilo` → **UTKU**
- `merve` / `continue` → **SALİH**
- `cline` / `yasin` → **YASU**
- `copilot` → **Kaldırıldı** (dış gözlemci)

### 2.2 Görev Yaşam Döngüsü

| Durum | Anlamı | Ajan Görevi |
|-------|--------|-------------|
| **plan** | Planlandı, henüz başlanmadı | Bekliyor |
| **aktif** | Ajan tarafından alındı | Kilitler verildi, çalışıyor |
| **teslim** | Ajan işi bitirdi | İHSAN incelemeye alıyor |
| **review** | İHSAN/YASU incelemede | Bulgular yazılabilir |
| **done** | Onaylandı | Kilitler bırakıldı, zincir devam |
| **iptal_stale** | Bayat/çalışılmayan | Bakım ile temizlenir |

### 2.3 Görev Başlığı Standardı (D-57)

**Kalıp:** `[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)`

Örnek: `[UI] Ayarlar sayfasını yaz → admin_kullanici_ayarlari.py (2s)`

| Unsur | Seçenekler | Örnek |
|-------|-----------|-------|
| ALAN (7 kanonik) | `UI` · `API` · `VERI` · `TEST` · `DOC` · `ALTYAPI` · `ORKESTRA` | `UI` |
| FİİL (8 kanonik) | `yaz` · `düzelt` · `taşı` · `sil` · `denetle` · `ölç` · `belgele` · `araştır` | `yaz` |
| ÇIKTI | Tek dosya/komut | `admin_kullanici_ayarlari.py` |
| SÜRE | Tahmini saat (`30d`, `1s`, `2s`, `4s`) | `2s` |

**Kural:** Başlık bu kalıba uymuyorsa ajan almaz, orkestratöre geri sorar.

### 2.4 Dosya Yolları ve Kısaltmalar

| Yol | Anlamı |
|-----|--------|
| `data/orchestrator/` | Görev, karar, rapor merkezi |
| `data/orchestrator/task_board.json` | Ana görev veritabanı (ajan kurgusu) |
| `data/orchestrator/decision_log.jsonl` | Karar defteri — D-XX satır satır |
| `data/orchestrator/triggers/{ajan}.jsonl` | Ajan posta kutusu (bekleyen/alınan görevler) |
| `data/orchestrator/handoff.jsonl` | Teslim kayıtları — kimin ne zaman ne teslim etti |
| `scripts/gorev_kutusu.py` | Ajan posta kutusu + İHSAN onay komutları |
| `scripts/oto_nobetci.py` | Otomatik onay/teslim (P2 ve altı) |
| `scripts/karar_yaz.py` | Karar defterine D-XX yaz |
| `scripts/vault_saglik.py` | Vault sağlık raporu ve harita üretimi |
| `scripts/kodlama_denetim.py` | BOM/NUL/mojibake/sozdizimi kontrolü |

### 2.5 Teknik Terimler ve Kısaltmalar

| Terim | Anlamı |
|-------|--------|
| **Vault** | Obsidian not deposu = ortak ajan hafızası |
| **Wikilink** | Obsidian iç link formatı: `[[dosya]]` veya `[[dosya\|alias]]` |
| **Hub not** | Dizin merkez dosyası — tüm içeriğe giriş |
| **Kırık link** | Hedefi olmayan referans (`[[00-Home]]` ama dosya yok) |
| **Orphan** | Hiç referans almayan dosya (bağlı değil) |
| **İkiz dosya** | Aynı isimde iki dosya (path farklı) |
| **SSOT** | Single Source of Truth — tek doğruluk kaynağı |
| **Worktree** | Git worktree — paralel çalışma branşı |
| **Submodule** | Git alt-modülü (`src/company_master/` vb.) |
| **D-XX** | Karar kaydı numarası (`D-174`, `D-60` vb.) |
| **BOM** | Byte Order Mark — UTF-8 dosyalarda yasak |
| **Mojibake** | Karakter kodlama bozulması (Türkçe karakterler çöplenmiş) |
| **NUL** | Null byte — dosya içinde yasak |
| **P0/P1/P2/P3** | Öncelik seviyeleri (P0=kritik blokaj, P1=yüksek, P2=orta, P3=düşük) |
| **AST** | Abstract Syntax Tree — kod analiz yapısı |
| **Handoff** | Teslim kaydı — ajan işi bitirip teslim etti |
| **Lock/Kilit** | Dosya kilidi — başka ajan değiştirmek yasak |
| **Trigger** | Ajan tetik kuyruğu (posta kutusu) |
| **Monkeypatch** | Pytest fixture — kodu test için değiştirir |
| **Rate-limit** | API istek sınırı |
| **SSE** | Server-Sent Events — canlı veri akışı |
| **DLQ** | Dead Letter Queue — işlenemeyen mesajlar |
| **Tenant** | Çoklu müşteri sisteminde bir müşteri/kurum |
| **Churn** | Müşteri kaybı oranı |
| **MRR/ARR** | Aylık/Yıllık Tekrar Eden Gelir |

### 2.6 Marka Kimliği (3 Ayak)

| Marka | Port | Veritabanı | Önek | Anlamı |
|-------|------|-----------|------|--------|
| **Huginn** 🦅 | 8000 | `huginn_` | `huginn_` | Müşteri tarafı API |
| **Muninn** 🛡️ | 8501 | `muninn_` | `muninn_` | İç ekip/admin paneli |
| **Odin** ⚡ | — | `odin_` | `odin_` | Çekirdek/kütüphane |

**Yasak yazımlar:** Huggin, Hugginn, Hugin, Munin, Muginn, Munnin, Odinn, Odın.

### 2.7 Karar Terimleri

| Terim | Anlamı |
|-------|--------|
| **D-XX** | Karar kaydı (örn. D-174 = VAULT sağlık, D-60 = ajan adı geçişi) |
| **Karar defteri** | `data/orchestrator/decision_log.jsonl` — her satır bir D-XX |
| **Status** | `plan`, `in_progress`, `implemented`, `rejected` |
| **Related decisions** | Bağlantılı eski kararlar |

---

## 3. GÖREV YÖNETİMİ — İş Akışı ve Senkronizasyon

### 3.1 Görev Panosu Nasıl Çalışır?

```
Merkez veri tabanı
        ↓
  task_board.json (48 görev, JSON formatı)
        ↓
    ↓       ↓       ↓
 triggers/  |  gorev_panosu.md  |  AGENT_SYNC.md
ihsan.jsonl |  (markdown insan  |  (ajan koordine
utku.jsonl  |   okuması)        |   ediyor)
salih.jsonl |                   |
yasu.jsonl  |                   |
```

**Akış:**
1. **İHSAN** yeni görev ekler → `task_board.json` güncellenir
2. **Makine** otomatik üretir: `gorev_panosu.md` (markdown tablosu) + ajan posta kutuları (`triggers/`)
3. **Ajan** posta kutusunda brifini okur → `gorev_kutusu.py al` çağırır
4. **Ajan** işini bitirip `gorev_kutusu.py teslim` çağırır
5. **İHSAN** inceleyip `gorev_kutusu.py onayla` çağırır
6. **Makine** tarafı zincir devam eder (sonraki bağlı görev tetiklenir)

### 3.2 Görev Panosu Nasıl Okunur?

Pano: `data/orchestrator/gorev_panosu.md` (Obsidian'da aç veya metin editörde oku)

**Tablo sütunları:**
- `ID` — Görev numarası (örn. `UI-01`, `VERI-12`)
- `Başlık` — 4 parçalı başlık (ALAN + FİİL + NESNE + ÇIKTI)
- `Ajan` — Kim yapıyor? (İHSAN, UTKU, SALİH, YASU)
- `Durum` — `plan` / `aktif` / `teslim` / `review` / `done`
- `Öncelik` — P0 (kritik), P1 (yüksek), P2 (orta), P3 (düşük)
- `Başlama` — Ajan işi aldığı tarih
- `Bitirme` — Ajan teslim ettiği tarih
- `Not` — İnsan notları (hata, bulgular vb.)

**Renk kodlaması (Obsidian markdown):**
- 🔴 **Kırmızı** (P0) — Acil blokaj görevleri
- 🟡 **Sarı** (P1) — Yüksek öncelik
- 🟢 **Yeşil** (P2/P3) — Normal iş

### 3.3 Karar Defteri Nasıl Okunur?

Dosya: `data/orchestrator/decision_log.jsonl`

**Her satır bir karar (JSONL formatı):**
```json
{
  "id": "D-174",
  "timestamp": "2026-09-21T08:17:14Z",
  "title": "VAULT-XREF-DÜZELT + DUBLO-BIRLES: canonical ağaç + ignore filter + sağlık script",
  "status": "implemented",
  "context": "Vault bütünlüğü ve ajan hafızası sağlığı için temel infrastruktur",
  "decision": "Huginn Data Insights/ canonical seçildi. vault_saglik.py yazıldı.",
  "details": { ... },
  "implemented_by": "İHSAN",
  "related_decisions": ["D-173", "D-175"]
}
```

**Nasıl aranır:**
1. Metin editörde açısından `D-` ara (örn. `D-60` ajan ad geçişi)
2. Veya Python: `python -c "import json; lines=open('data/orchestrator/decision_log.jsonl').readlines(); d=[json.loads(l) for l in lines]; print([x for x in d if x['id']=='D-174'][0])"`

### 3.4 Görev Ekle / Güncelle (İHSAN İçin)

**Yeni görev ekle:**
```bash
python scripts/gorev_kutusu.py ekle \
  --id UI-27 \
  --baslik "[UI] Arama kutusunu yaz -> search_module.py (2s)" \
  --ajan utku \
  --oncelik P1 \
  --dosyalar "src/ui/search_module.py,src/ui/search_styles.css"
```

**Görev durumunu güncelle:**
```bash
python scripts/gorev_kutusu.py guncelle --id UI-27 --durum aktif --not "UTKU başladı"
```

**Görev teslim al (Ajan):**
```bash
python scripts/gorev_kutusu.py al --id UI-27
# Kilitler alınır, rapor şablonu açılır
```

**Görev teslim et (Ajan):**
```bash
python scripts/gorev_kutusu.py teslim --id UI-27 --notlar "İşin özeti ve bulgular"
# status → review (İHSAN incelemesi bekler)
```

**Görev onayla (İHSAN):**
```bash
python scripts/gorev_kutusu.py onayla --id UI-27
# status → done, kilitler bırakıldı, zincir tetiklendi
```

### 3.5 Senkron Akışı — Worktree ↔ Merkez

Worktree ve merkez proje arasında **iki yönlü senkron:**

**Worktree → Merkez (İHSAN işleri teslim eder):**
1. İHSAN `Huginn Data Insights/` içinde değişiklik yaptı
2. `git worktree` branch'i commit/push
3. Merkez (`Huginn Data Insights/`) pull alır
4. Artefaktlar (`gorev_panosu.md`, `AGENT_SYNC.md`, raporlar) senkron kalır

**Kontrol komutları:**
```bash
# Senkron durumunu kontrol et
python scripts/senkron_fark.py

# Merkezi yenile
python scripts/senkron_append.py --mod merkez
```

---

## 4. RAPORA OKUMA AKIŞI — Görevden Rapor'a

### 4.1 Rapor Dosya Adı Şeması

```
<GÖREV_ID>_<TİP>_<TARİH>_<AJAN>.md
```

Örnek:
- `UI-27_rapor_2026-09-21_uretim.md` — UTKU'nun UI-27 teslim raporu
- `VERI-12_bulgular_2026-09-18_denetim.md` — YASU'nun bulgular raporu
- `ORKESTRA-01_karar_2026-09-21_orkestrator.md` — İHSAN'ın karar kaydı

### 4.2 Rapor Türleri

| Tür | İçeriği | Kimin Yazması |
|-----|---------|--------------|
| `_rapor_` | Görev tamamlandı, tam özet + çıktılar + test sonuçları | Ajan (UTKU/YASU) |
| `_bulgular_` | Görevde bulunmuş ek hata/risk — kapsam dışı bulgular | Ajan (YASU/SALİH) |
| `_brif_` | Görev başlangıcında yapılacaklar listesi | İHSAN |
| `_karar_` | Kurumsal karar / politika / strateji | İHSAN |

### 4.3 Rapor Nerede Bulunur?

Hepsi `data/orchestrator/` klasörüne yazılır:

```bash
# UTKU'nun teslim raporlarını listele
ls data/orchestrator/*_rapor_*_uretim.md

# YASU'nun bulgularını listele
ls data/orchestrator/*_bulgular_*_denetim.md

# Tüm D-XX kararlarını listele
grep '"id": "D-' data/orchestrator/decision_log.jsonl
```

### 4.4 Rapor İçerik Yapısı (Standart)

Tüm raporlar şu başlıkları taşır:

```markdown
# <GÖREV_ID> — <Başlık>

> Ajan: <AJAN_ADI>  
> Tarih: <TARİH>  
> Durum: <done | blocked | paused>

## Özet
[1-2 cümle — iş ne yapıldı]

## Çıktılar
- Dosya 1: `src/path/file.py`
- Dosya 2: `tests/test_file.py`

## Test Sonuçları
- Tam test: ✅ 3567 passed, 0 failed
- Regresyon: ✅ Önceki testler yine yeşil

## Bulgular
[Ek hata, risk, öneriler — kapsam dışı ama raporla]

## Not
[İHSAN'a özel mesaj]
```

### 4.5 Tarih + Konu + Ajan Örüntüsü

Rapor adı okunurken sıra:
1. **TARİH** — ne zaman yapılmış? (`2026-09-21`)
2. **GÖREV_ID** — hangi iş? (`UI-27`)
3. **AJAN** — kim yaptı? (`uretim` = UTKU)

Örnek: `UI-27_rapor_2026-09-21_uretim.md`
- Tarih: 21 Eylül 2026
- Görev: UI-27 (arama kutusu)
- Ajan: UTKU

---

## 5. SAĞLIK KONTROLÜ — Vault'u İyileştir

### 5.1 Sağlık Kontrolü Nedir?

Vault (407 nod, 49 dizin) zaman içinde **kırılabilir:**
- ❌ **Kırık link:** Referans hedefi yok (`[[00-Home]]` dosya yok)
- ❌ **İkiz dosya:** Aynı isimde iki dosya (isim çakışması)
- ❌ **Orphan:** Hiç referans almayan dosya (ulaşılamaz)

**vault_saglik.py** tek geçişte hepsini tespit eder.

### 5.2 Sağlık Kontrolü Nasıl Çalışır?

Script: `Huginn Data Insights/scripts/vault_saglik.py`

**Çalıştır:**
```bash
cd "worktree klasoru"
python scripts/vault_saglik.py --rapor
```

**Çıktı:**
- **Rapor JSON:** `data/orchestrator/VAULT-SAGLIK-01_rapor_2026-09-21_orkestrator.json`
- **Harita:** `Huginn Data Insights/VAULT_HARITA.md` (407 nod, 49 dizin)

### 5.3 Rapor İçeriği

**VAULT-SAGLIK-01_rapor_*.json:**

```json
{
  "metadata": {
    "olusturulma": "2026-09-21T08:17:14Z",
    "vault_root": "C:\\Huginn Data Projesi\\worktree klasoru"
  },
  "istatistik": {
    "toplam_dosya": 408,
    "krik_link_sayisi": 46,      ← Kırık linkler
    "ikiz_grup_sayisi": 7,       ← İkiz dosya grupları
    "ikiz_dosya_toplam": 21,     ← Toplam çakışan dosya
    "orphan_sayisi": 3           ← Yetim dosyalar
  },
  "krik_link": [
    {
      "kaynak_dosya": "CLAUDE.md",
      "hedef": "00-Home",          ← Aranan dosya yok
      "neden": "hedef_yok",
      "risk": "high"
    }
  ],
  "ikiz_grup": {
    "gorev_panosu.md": ["data/orchestrator/gorev_panosu.md", "AGENT_SYNC/gorev_panosu.md"]
  },
  "orphan": [
    {
      "dosya": "old_config.md",    ← Hiç referans almıyor
      "boyut": 1024
    }
  ]
}
```

### 5.4 Çıktı Nasıl Yorumlanır?

| Metrik | Durum | Aksyon |
|--------|-------|--------|
| `krik_link_sayisi: 0` | ✅ İyi | Hiç kırık link yok, devam et |
| `krik_link_sayisi: 1-10` | 🟡 Uyarı | Kırık linkleri ella düzelt: `[[00-Home]]` referansını sil veya hedef dosyayı oluştur |
| `krik_link_sayisi: 50+` | 🔴 Kritik | Vault'ta yapısal sorun var. İHSAN'a rapor gönder |
| `ikiz_dosya_toplam: 3+` | 🔴 Kritik | İkiz dosyaları birleştir (D-174'e bak) |
| `orphan_sayisi: 0` | ✅ İyi | Tüm dosyalar bağlı |
| `orphan_sayisi: 5+` | 🟡 Uyarı | Orphan dosyaları arşivle veya VAULT_HARITA'ya bağla |

### 5.5 VAULT_HARITA.md Nasıl Kullanılır?

`Huginn Data Insights/VAULT_HARITA.md` — **407 nod + 49 dizin merkezi**

**Yapı:**
```markdown
# VAULT_HARITA

> Otomatik üretim: `python scripts/vault_saglik.py --harita`  
> Son güncelleme: 2026-09-21  
> Kapsam: 407 nod

## OSINT kümesi (62)
[[docs/v10_OSINT_YETENEK_KATALOGU|hub]], [[docs/OSINT_SCRAPER_MOTORU|scraper]], ...

## data/orchestrator (155)
[[data/orchestrator/task_board|pano]], [[data/orchestrator/VAULT-SAGLIK-01_rapor|saglik]], ...

## docs (43)
[[docs/AJAN_DETAY|ajan]], [[docs/AGENTS|rules]], ...
```

**Nasıl kullanılır:**
1. Obsidian'da aç
2. `Ctrl+F` ara (örn. "görev panosu" → [[data/orchestrator/gorev_panosu|...]])
3. Tıkla → dosya açılır
4. Tüm nod ağını görürsün

### 5.6 Düzeltme Komutları

**Kırık linkleri liste:**
```bash
python scripts/vault_saglik.py --rapor
# JSON'da krik_link bölümü kontrol et
```

**VAULT_HARITA'yı yenile:**
```bash
python scripts/vault_saglik.py --harita
# VAULT_HARITA.md yeniden yazılır (407 nod otomatik)
```

**Orphan dosyaları listele:**
```bash
python scripts/vault_saglik.py --rapor | grep -A 50 '"orphan"'
# İlk 50 yetim dosya görünür
```

**Örnekler — el ile düzeltme:**

Kırık link `[[00-Home]]` bulunduysa:
1. Kırık linki içeren dosya bul: (rapordan: CLAUDE.md)
2. Dosyayı aç: `Huginn Data Insights/CLAUDE.md`
3. `[[00-Home]]` referansını sil VEYA `docs/00-Home.md` dosyası oluştur
4. Tekrar `python scripts/vault_saglik.py --rapor` çalıştır → 0 olmalı

---

## ÖZET — Hızlı Referans

### Günlük İşler

**Sabah — Görevleri kontrol et:**
```bash
python scripts/gorev_kutusu.py bak        # Posta kutusu durumunu gör
python scripts/gorev_kutusu.py liste      # Tüm görevler
cat data/orchestrator/gorev_panosu.md     # Pano (markdown)
```

**Gün içinde — Raporları kontrol et:**
```bash
ls -lt data/orchestrator/*_rapor*.md | head -10    # Son raporlar
grep '"id": "D-' data/orchestrator/decision_log.jsonl | tail -5  # Son kararlar
```

**Haftada bir — Vault sağlığını kontrol et:**
```bash
python scripts/vault_saglik.py --rapor
# Kırık link sayısı 0 olmalı
# Orphan sayısı < 5 olmalı
```

### Ajan Iletişim

| Durum | Yapılacak | Komut |
|-------|-----------|-------|
| Görev yeni | Posta kutusuna gönder | `gorev_kutusu.py ekle` |
| Ajan aldı | Kilitler verildi | `gorev_kutusu.py al` |
| Ajan teslim | Rapor çıktı | `gorev_kutusu.py teslim` |
| İHSAN onayladı | Zincir devam | `gorev_kutusu.py onayla` |

### Kararlar

Tüm stratejik kararlar `data/orchestrator/decision_log.jsonl` → D-XX

**Son karar örnek:**
- D-174: VAULT sağlık script ve harita
- D-60: Ajan ad geçişi (roo→İHSAN vb.)
- D-57: Görev başlığı standardı

---

## İLETİŞİM KURALLAR

### KAHİN (Ürün Sahibi) — İHSAN (Orkestratör)

- **Rapor:** Haftalık özet + renkli tablolar (🔴 kritik, 🟡 uyarı, 🟢 iyi)
- **Dil:** Basit Türkçe, teknik terimler parantezde
- **Dosya referansı:** Tam yol + satır numarası
- **Karar:** `KAHİN kararı` yazılır (D-XX'e bağlı)

### Ajanlar Arası

- **Koordinasyon:** `AGENT_SYNC.md` okuyun
- **Çakışma:** Kilitli dosya → başka ajan değiştirmek yasak
- **Sorular:** İHSAN'a tetik bırakın (posta kutusu)

---

## 6. ABRAKADABRA RİTÜELİ — Orkestratör Devir Teslimi

### 6.1 Nedir?

**abrakadabra** = sizin (KAHİN) elinizde olan **güvenlik parolası**. Orkestratörlüğü bir ajandan diğerine devretmek için kullanılır.

Neden gerekli? Çünkü orkestratör = görev dağıtan, onaylayan, commit atan ajan. Bu yetki kimseye kendiliğinden geçmemeli. Sadece siz verebilirsiniz.

**Basit benzetme:** Şirkette müdürlük koltuğu. Koltuğa kimse kendi oturamaz — patron (siz) anahtarı verir.

### 6.2 İki mekanizma — ikisi de doğru, farklı işler

Sistemde abrakadabra iki ayrı yerde geçer. **Çakışma yok**, biri diğerini tamamlar:

| Mekanizma | Dosya | Ne yapar? | Ne zaman kullanılır? |
|-----------|-------|-----------|---------------------|
| **Anahtarlı devralma** (D-58) | `scripts/gorev_at.py abrakadabra` | Gizli anahtarı doğrular, `orchestrator.json` dosyasını günceller. Anahtar asla ekrana basılmaz. | Ajan kendisi devralmak istediğinde — anahtarı bilmeli. |
| **Ritüel rotasyon** | `scripts/orkestrator_rotasyon.py` | Sabit `abrakadabra` sözcüğüyle devri karar defterine + CHANGELOG'a yazar. | Siz "artık YASU orkestratör" dediğinizde. |

Birincisi **kapı** (kim geçebilir), ikincisi **kayıt defteri** (kim ne zaman geçti). Sistem güvenliği ikisinin birlikte çalışmasıyla sağlanır.

### 6.3 Nasıl kullanılır? (sizin komutlarınız)

**Kim şu an orkestratör?**
```
python scripts/orkestrator_rotasyon.py --kim
```

**Devri yapın (örnek: YASU'ya geçiş):**
```
python scripts/orkestrator_rotasyon.py yasu --kelime abrakadabra --gerekce "İHSAN yoğun, YASU devralıyor"
```

Sonuç: karar defterine kayıt düşer, CHANGELOG'a not yazılır. Geri alınabilir — aynı komutla eski ajana dönersiniz.

### 6.4 Anahtar kuralları (D-73 / D-74)

Güvenlik açısından üç kural kesindir:

1. **Anahtar sahibi yalnız aktif orkestratördür.** SALİH, UTKU, YASU anahtarı isteyemez, saklayamaz.
2. **Anahtar tek seferliktir.** Devir sonrası yenilenir (rotasyon protokolü).
3. **Anahtar asla loglanmaz.** Sistem sadece `sha256` parmak izini tutar — anahtarın kendisi hiçbir dosyada yazılı kalmaz.

Anahtar nerede durur? `ABRAKADABRA_KEY` ortam değişkeni veya `data/orchestrator/abrakadabra.key` dosyası. İkisi de `.gitignore` altında — git'e karışmaz.

### 6.5 MIMIR: Seviye 0 (Asistan) ve Seviye 1 (Orkestratör)

Sohbet ekranında (MIMIR) `abrakadabra` sözcüğü geçer — ama **aynı hiyerarşinin parçası**, ayrı değil. MIMIR iki seviyeli bir ajandır:

| Seviye | Tetikleyici | İşlem | Sonuç |
|--------|-------------|--------|-------|
| **Seviye 0** (Öntanımlı) | Hiçbir | Pano okur, raporla sunar | 🔒 Asistan |
| **Seviye 1** | PO "abrakadabra, artık orkestratör sensin" | Key ister, doğrular, `.env` döner | 🔓 Orkestratör |

**Ayrıntı:**
- MIMIR Seviye 0'da `abrakadabra` sohbette sorulursa, UI password field açar (`st.text_input(type="password")`).
- PO `.env`'deki `ABRAKADABRA_KEY` değerini yapıştırır.
- Sistem doğrular (`hmac.compare_digest`), sonra yeni anahtar üretir ve `.env` atomik yeniden yazılır.
- `orchestrator.json` → `kime: mimir` ; İhsan Seviye 0'a düşer.
- Session state temizlenir; sohbet history'ye hiçbir key **asla girmedi**.
- MIMIR UI rozeti 🔒 → 🔓 değişir.

Tek sözcük (`abrakadabra`), iki **seviye**: MIMIR ayrı bir hiyerarşi kurmaz; aynı orkestratör koltuğuna geçici olarak oturur. D-182 kararı (2026-09-21).

---

## Dosya Listesi

**Bu kılavuzda referans verilen ana dosyalar:**

- ✅ `Huginn Data Insights/AGENTS.md` — Çekirdek kurallar
- ✅ `data/orchestrator/task_board.json` — Görev veritabanı
- ✅ `data/orchestrator/decision_log.jsonl` — Karar defteri
- ✅ `data/orchestrator/gorev_panosu.md` — Pano (markdown)
- ✅ `Huginn Data Insights/VAULT_HARITA.md` — 407 nod rehberi
- ✅ `Huginn Data Insights/scripts/vault_saglik.py` — Sağlık kontrolü
- ✅ `Huginn Data Insights/scripts/gorev_kutusu.py` — Posta kutusu CLI
- ✅ `Huginn Data Insights/scripts/orkestrator_rotasyon.py` — Abrakadabra ritüeli (orkestratör devri)
- ✅ `Huginn Data Insights/scripts/gorev_at.py` — Görev atama + anahtarlı devralma (D-58)
- ✅ `docs/AJAN_DETAY.md` — Ajan işleri detaylı
- ✅ `docs/ajanlar/*.md` — Her ajan kişi dosyası

---

**Son güncelleme:** 2026-09-21 · İHSAN (Orkestratör)

---
