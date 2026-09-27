# Kilo Brief — MRK-03 · MRK-04 · FIX-NOB-01

> **ARŞİV — tamamlandı.** Bu brif tarihsel kayıttır; içeriği güncel iş emri değildir.
> Güncel marka kiti konumu: `docs/brand/` (bkz. `docs/brand/README.md`, D-44/D-45).
> Güncel marka revizyon zinciri: `docs/plans/MARKA-REVIZE-01_brief.md`.

> **Hazırlayan:** roo (orkestratör) · **Tarih:** 2026-09-14
> **Amaç:** Belge/kural katmanı işlerini roo'dan ayırıp paralelleştirmek.
> **Çakışma garantisi:** Bu üç görevin dosya kümesi, roo'nun aktif çalıştığı
> `src/company_master/i18n/` ve `web_dashboard/` alanlarıyla **kesişmez**.

---

## 0. Ortak bağlam (önce bunu oku, başka dosya açma)

**Marka/port eşlemesi (SSOT — tartışmaya kapalı):**

| Port | Teknoloji | Marka | Rol |
|---|---|---|---|
| 8000 | HTML/CSS/JS | **HUGINN** 🦅 | Müşteri yüzeyi — "Ne oluyor?" |
| 8501 | Streamlit | **MUNINN** 🛡️ | İç ekip yüzeyi — "Ne oldu, neden?" |
| — | `src/company_master/*` | **ODIN** ⚡ | Çekirdek (görünmez) |

**"Tarihsel Çatı Adı" kuralı:** `huginn` adı **veritabanı adı, repo adı,
`HuginnMCPServer`, `admin@huginn.local`** gibi teknik kimliklerde **hiç
değişmez**. Sıfır migration. Marka adları yalnızca **kullanıcıya görünen
metinlerde** ve **yeni yazılan kodun adlandırmasında** kullanılır.

**Katman ayrımı (marka dili kuralı):**

| Katman | İçerik | Dil |
|---|---|---|
| `veri` | Sayı, hata kodu, para, tarih, tablo başlığı, menü etiketi, yasal uyarı | ❄️ Kuru, **mitolojisiz** |
| `cerceve` | Sayfa başlığı, boş durum, ipucu, yükleme, başarı mesajı | 🦅 Mitolojik, anlatısal |

**Demir kural:** Müşterinin karar verdiği hiçbir rakam veya hata mesajı
mitolojik dile bürünmez.

---

## 1. MRK-03 — Marka konumlandırma belgesini projeye taşı

### Kaynak
`C:\Huginn Data Projesi\proje_kapsam_ve_konumlandirma.md` (112 satır,
çalışma alanının **bir üst dizininde**, repo dışında).

### Yapılacaklar

1. **Taşı (kopyala + kaynağı sil = "kesip yapıştır"):**
   `AI proje v1/V10/00_ana_belgeler/03_marka_konumlandirma_ve_kapsam.md`
2. **Ayna oluştur:** `docs/MARKA_KONUMLANDIRMA.md`
   Ayna dosyanın başına şu not düşülür:
   ```markdown
   > Bu dosya `AI proje v1/V10/00_ana_belgeler/03_marka_konumlandirma_ve_kapsam.md`
   > dosyasının kod tarafı aynasıdır. **Kaynak orasıdır**; değişiklik önce
   > vault'ta yapılır, sonra buraya yansıtılır.
   ```
3. **Obsidian frontmatter ekle** (vault kopyasına):
   ```yaml
   ---
   tags: [marka, konumlandirma, huginn, muninn, odin, v10]
   olusturma: 2026-09-14
   durum: aktif
   kaynak: proje_kapsam_ve_konumlandirma.md
   ---
   ```
4. **Çapraz wikilink kur:**
   - `AI proje v1/V10/00-Home.md` → "Ana bölümler" listesine ekle:
     `- Marka konumlandırma — [[03_marka_konumlandirma_ve_kapsam]] · Huginn/Muninn/Odin kimliği, sloganlar, görsel kimlik`
   - Yeni belgenin sonuna "İlgili" bölümü:
     `[[14_urun_yuzeyleri_sitemap]]`, `[[01_versiyon_9_baglam_dokumani]]`, `[[00-Home]]`
5. **MRK-03c — yazım hatası:** `AI proje v1/V10/00-Home.md` satır ~19'da
   `[[02_hugins_master_kaynak_dokumani]]` yazıyor. Doğrusu **`huginn`**.
   ⚠️ Önce hedef dosyanın gerçek adını `dir /b` ile doğrula; wikilink hedefi
   yoksa **dosya adını değil, linki** gerçek dosya adına uydur.

### Kabul kriteri
- [ ] Kaynak dosya repo dışında **kalmadı** (taşındı)
- [ ] Vault + `docs/` iki kopya da UTF-8, Türkçe karakterler bozulmamış
- [ ] `00-Home.md`'deki "hugins" yazımı düzeldi ve link gerçek dosyaya gidiyor
- [ ] Frontmatter + çapraz linkler eklendi

### Kilitlenecek dosyalar
```
AI proje v1/V10/00_ana_belgeler/03_marka_konumlandirma_ve_kapsam.md
docs/MARKA_KONUMLANDIRMA.md
AI proje v1/V10/00-Home.md
```

---

## 2. MRK-04 — Marka terminolojisini kural dosyalarına işle

### Hedef dosyalar
`ANA_KURALLAR.md`, `AGENTS.md`, `.roorules`, `.clinerules`

Her dördüne **aynı içerikli** yeni bir bölüm eklenir (dosya diline uygun
başlık seviyesiyle). `.roorules` / `.clinerules` için kısa özet yeterlidir;
tam metin `ANA_KURALLAR.md`'ye gider.

### Eklenecek bölüm — kopyala/uyarla

```markdown
## Marka Adları ve Dil Sözleşmesi (MRK-04)

### Sözlük

| Marka | Emoji | Kapsam | Teknik önek |
|---|---|---|---|
| **Huginn** | 🦅 | Müşteri yüzeyi (8000) — canlı izleme, "Ne oluyor?" | `huginn_` |
| **Muninn** | 🛡️ | İç ekip yüzeyi (8501) — hafıza, denetim, "Ne oldu, neden?" | `muninn_` |
| **Odin** | ⚡ | Çekirdek/altyapı (görünmez) — karar, yetki, köprü | `odin_` |

### Yazım kuralları (ZORUNLU)

- `Huginn`, `Muninn`, `Odin` **çevrilmez, kısaltılmaz, ekle bölünmez**.
- **Yasak yazımlar:** `Muginn`, `Hugin`, `Munin`, `Hugginn`, `Odın`.
- Türkçe ek alırken kesme işareti: `Huginn'in`, `Muninn'e`, `Odin'in`.
- Dil paketi anahtarları `{marka}_{alan}_{durum}` biçiminde, **en az 3 parça**:
  `huginn_akis_bos` ✅ · `huginn_bos` ❌
- Kod içi teknik önek küçük harf: `huginn_`, `muninn_`, `odin_`.

### "Tarihsel Çatı Adı" kuralı

`huginn` adı **veritabanı adı, repo adı, `HuginnMCPServer`,
`admin@huginn.local`** gibi teknik kimliklerde **hiç değişmez**.
Marka ayrımı yalnızca kullanıcıya görünen metinde ve yeni kod
adlandırmasında geçerlidir. **Sıfır migration.**

### Güvenlik supabı — mitolojik dil yasağı

Aşağıdaki metinlerde mitolojik dil **kesinlikle kullanılmaz**:

- Hata mesajları ve hata kodları
- Para, fatura, fiyat, kota bilgisi
- Yetki reddi ve güvenlik uyarıları
- Yasal / KVKK / sözleşme metinleri
- Tablo başlıkları, metrik değerleri, menü etiketleri

**Yasaklı sözcükler (`veri` katmanında):**
`Huginn, Muninn, Odin, Bifröst, diyar, kuzgun, taht, mühür, Valhalla, Asgard`

❌ "Bifröst çöktü, kuzgunlar geri dönemiyor."
✅ "Bağlantı kesildi (503). Yeniden deneniyor."

### Paket → kuzgun mantıksal haritası (fiziksel taşıma YOK)

| Kod dizini | Kuzgun | Gerekçe |
|---|---|---|
| `web_dashboard/` (8000 statik) | 🦅 Huginn | Müşteri yüzeyi |
| `web_dashboard/tabs/admin_*` | 🛡️ Muninn | İç ekip ekranları |
| `src/company_master/engine/`, `intelligence/`, `vector/` | ⚡ Odin | Karar çekirdeği |
| `src/company_master/db/`, `schema/`, `etl/` | 🛡️ Muninn | Hafıza/arşiv |
| `src/company_master/api/`, `gateway/`, `queue/` | 🦅 Huginn | Canlı akış |
| `src/company_master/auth/`, `logging/`, `orchestrator/` | ⚡ Odin | Yetki ve yönetim |

⚠️ Bu tablo **mantıksal**tır. Hiçbir dizin yeniden adlandırılmaz veya
taşınmaz; import yolları değişmez.
```

### Kabul kriteri
- [ ] Dört dosyada da bölüm mevcut ve birbirleriyle çelişmiyor
- [ ] Mevcut kurallar **silinmedi**, yalnızca yeni bölüm eklendi
- [ ] Tüm dosyalar UTF-8, Türkçe karakterler sağlam
- [ ] `.roorules` / `.clinerules` içinde özet + `ANA_KURALLAR.md`'ye referans var

### Kilitlenecek dosyalar
```
ANA_KURALLAR.md
AGENTS.md
.roorules
.clinerules
```

---

## 3. FIX-NOB-01 — `gorev_nobetci.py durum` kodlama hatası

### Belirti
```
python scripts/gorev_nobetci.py durum
→ UnicodeDecodeError: 'charmap' codec can't decode byte ... (cp1254)
```

### Kök neden
`cmd_durum()` (satır ~96-109) log/JSON dosyalarını **encoding belirtmeden**
açıyor; Windows varsayılanı `cp1254` olduğu için UTF-8 Türkçe karakterlerde
çöküyor.

### Yapılacak
1. `scripts/gorev_nobetci.py` içindeki **tüm** `open(...)` çağrılarına
   `encoding="utf-8"` ekle (yazma dahil).
2. Bozuk baytlara karşı `errors="replace"` ile okuma toleransı ekle
   (dosya bozuksa komut çökmemeli, uyarı yazmalı).
3. Konsol çıktısı için gerekiyorsa dosya başına:
   ```python
   sys.stdout.reconfigure(encoding="utf-8", errors="replace")
   ```
4. Doğrula: `python scripts/gorev_nobetci.py durum` hatasız çalışmalı.

### Kabul kriteri
- [ ] `durum` komutu hatasız çalışıyor
- [ ] Türkçe karakterler konsolda bozulmadan görünüyor
- [ ] Diğer alt komutlar (`nobet`, `kur`, `kaldir`) bozulmadı

### Kilitlenecek dosyalar
```
scripts/gorev_nobetci.py
```

---

## 4. Teslim protokolü (ZORUNLU)

Her görev bitince ayrı ayrı:

```bat
python scripts/gorev_kutusu.py teslim --ajan kilo --task-id <ID> --ozet "..."
```

- `done` durumunu **kendin yazma** — teslim → onay kapısından geçer.
- Kilitler yalnızca onayda düşer.
- Takıldığın noktada `durum="blocked"` + not yaz, tahmin yürütme.

## 5. Sınırlar (dokunma)

| Alan | Neden |
|---|---|
| `src/company_master/i18n/**` | roo aktif yazıyor (MRK-02) |
| `web_dashboard/tabs/**` | U-09/U-03 sırası bekliyor |
| `app.py` | Navigasyon revizyonu roo'da |
| `scripts/i18n_ses_uret.py` | roo'nun üreticisi |
| `.env*` | Her zaman yasak |
