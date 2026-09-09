# Code Review: ostim_scraper.py ve ingest_ostim_detail.py

**Tarih:** 2026-09-03  
**Ajan:** Cursor Grok  
**Kapsam:**
- `src/company_master/etl/scrapers/ostim_scraper.py`
- `scripts/ingest_ostim_detail.py`

---

## 1. Ozet

| Kategori | Bulgu |
|----------|-------|
| Guvenlik | 3 (orta) |
| Performans | 4 (2 orta, 2 dusuk) |
| Code Smell | 6 (orta) |
| Hata Yonetimi | 4 |
| Stil / UTF-8 | 2 |

---

## 2. Guvenlik Bulgulari

### G1 [ORTA] User-Agent bolu bilgi ifsa riski
- **Konum:** `ostim_scraper.py:54`
- **Sorun:** `USER_AGENT = "AnkaraB2B-Bot/1.0 (research@example.com)"` gercek bir e-posta adresi iceriyor; bu adres scraping operasyonunda loglanirsa hedef site veya 3. sahislara ifsa olur.
- **Oneri:** `USER_AGENT` degerini ortam degiskeninden oku (`os.getenv("SCRAPER_USER_AGENT", "AnkaraB2B-Bot/1.0")`); gercek e-posta yerine `https://proje.example/contact` gibi sahibi kontrol edilen bir URL kullan.

### G2 [ORTA] robots.txt kontrolu vardir ama istege bagli
- **Konum:** `ostim_scraper.py:356-362`
- **Sorun:** `fetch_robots()` hatasi durumunda `disallow = set()` doner; bu sessizce `is_path_allowed()` her zaman True dondurur. KVKK ve robots.txt uyumlulugu icin riskli.
- **Oneri:** Robots alinamadiysa en azindan log seviyesini ERROR yap ve bir flag ile operatore bildir. Islem Secim Modu icin `scraping_permission_router.py` ile entegre et.

### G3 [ORTA] SQL Injection riski yok ama dinamik sorgu dikkat
- **Konum:** `ingest_ostim_detail.py:65`
- **Sorun:** `text("... WHERE LOWER(TRIM(legal_name)) = LOWER(:n) ...")` parametrik, ancak `conn.execute(text(...))` icinde string interpolation olmadigindan emin ol. Bireysel alanlarda (`phone`, `email`) liste ilk elemanini almak da None donusu icin test edilmeli.
- **Oneri:** Mevcut haliyle guvenli. Liste bos ise `[None]` fallback yerine `if not lst else lst[0]` semantigi ile yaz; coverage testi ekle.

---

## 3. Performans Bulgulari

### P1 [ORTA] HTTP isteklerinde retry/backoff yok
- **Konum:** `ostim_scraper.py:289-296`
- **Sorun:** Detay sayfasi cekilirken `requests.get` basarisiz olursa tek seferde hata loglanip `{}` donulur. Transient hatalarda (5xx, timeout) tum firma atlanir.
- **Oneri:** `urllib3.util.retry.Retry` ile `Retry(total=3, backoff_factor=1, status_forcelist=[500,502,503,504])` tanimla ve `requests.Session()` uzerinden baglantiyi yeniden kullan.

### P2 [ORTA] Detay cekimi sirali ve yavas
- **Konum:** `ostim_scraper.py:331-349`
- **Sorun:** Her firma icin tek tek `time.sleep(RATE_LIMIT_SECONDS)` (3s) uygulanir. ~1500 firma icin sadece detay cekimi ~75 dakika surer.
- **Oneri:** `concurrent.futures.ThreadPoolExecutor(max_workers=3)` ile paralel detay cekimi (ornek: `max_workers=2-3` politika kuralidir). Sirayi garanti etmek icin `slug` vektorunu batch'lere bol, siraya saygi goster.

### P3 [DUSUK] Bellek kullanimi sirali iterator
- **Konum:** `ostim_scraper.py:368-389`
- **Sorun:** `scrape_tum_osb` sektorler uzerinde sirali calisir; her sayfayi tek tek acar. Cok sayida sektor varsa, yavaslamaya ek olarak log bufferi buyur.
- **Oneri:** Ileride iyilestirme: sektorleri async worker'lara dagit. Mevcut haliyle kabul edilebilir.

### P4 [DUSUK] Dosya yazma buffering
- **Konum:** `ostim_scraper.py:368-382`
- **Sorun:** `with open(output_path, "w", ...)` satir satir yazma; I/O buffering varsayilan; eger Crash olursa veriler kaybolabilir.
**Oneri:** `buffering=8192` veya `io.TextIOWrapper` ile explicit flush periyodu.

---

## 4. Code Smell Bulgulari

### S1 [ORTA] Buyuk fonksiyon: `scrape_tum_osb`
- **Konum:** `ostim_scraper.py:352-389`
- **Sorun:** ~40 satirlik tek fonksiyon icinde: robots cekme, sektor listeleme, sayfalama, yazma, loglama. SRP ihlali.
- **Oneri:** Asagidaki yardimcilari cikar:
  - `_check_scraping_allowed() -> bool`
  - `_iter_sektor_pages(sektor_url) -> Iterator[OstimFirma]`
  - `_iter_all_pages(sektorler, detay_al) -> Iterator[OstimFirma]`
  - `scrape_tum_osb` yalnizca orkestrasyon yapsin.

### S2 [ORTA] Magic string/constant dagilimi
- **Konum:** `ostim_scraper.py:24-56`, `ingest_ostim_detail.py:21-22`
- **Sorun:** `LOG_DIR`, `LOG_PATH`, `LOG_DIR`, `LOG_PATH`, regex patternleri farkli modullerde tekrarlaniyor. VKN_PATTERN her iki dosyada da var, parsel patterni her iki dosyada var. DRY ihlali.
- **Oneri:** Ortak sabitleri `src/company_master/etl/scrapers/constants.py` altinda topla (`VKN_PATTERN`, `PARSEL_PATTERN`, `LOG_DIR`).

### S3 [ORTA] `try/except` ile sessiz swallow
- **Konum:** `ingest_ostim_detail.py:99-100`
```python
try: conn.rollback()
except: pass
```
- **Sorun:** AGENTS.md "hatalari sessizce yutma" kuralini ihlal ediyor.
- **Oneri:** `except Exception as rb_exc: log.exception("rollback failed: %s", rb_exc)` ile en az loglanmali.

### S4 [ORTA] Genel `except Exception` genis
- **Konum:** `ingest_ostim_detail.py:92-93`, `ingest_ostim_detail.py:96-97`
- **Sorun:** Hangi hatalarin beklenip hangilerinin crash ettirilmesi gerektigi ayrilmamis. Veri bozulmasi durumunda commit icin sonraki batchlere devam edebilir.
- **Oneri:** Spesifik hatalari yakala: `sqlalchemy.exc.SQLAlchemyError`, `json.JSONDecodeError`, `KeyError`. Beklenmeyen hata durumunda trans.commit etme; sonraki batch'e gecmeden once alarm uret.

### S5 [ORTA] Dict `.get()` zincirleri okunaksiz
- **Konum:** `ingest_ostim_detail.py:71-76`
- **Sorun:** 6-7 satirlik tek satir zincir okumayi zorlastirir.
**Oneri:** Alanlari once `payload = rec.get(...)` ile normalize et, sonra kullan. Refactor ornegi:
```python
web = normalize_website(rec.get("web_sitesi"))
adres = (rec.get("adres") or "").strip() or None
vkn = extract_vkn(unvan)
parsel = extract_parsel(rec.get("osb_parsel")) or extract_parsel(adres)
```

### S6 [DUSUK] Tip ipucusu eksiklikleri
- **Konum:** `ingest_ostim_detail.py` fonksiyonlar
- **Sorun:** `def normalize_website(v)`, `def extract_vkn(unvan)`, `def extract_parsel(t)`: arguman tipleri acik degil. AGENTS.md tip guvenligi kurali.
- **Oneri:** `def normalize_website(v: str | None) -> str | None`

---

## 5. Hata Yonetimi Bulgulari

### H1 [ORTA] `batch_size` sabit, dinamik degil
- **Konum:** `ingest_ostim_detail.py:55`
- **Sorun:** `batch_size = 100` buyuk tablolarda uzun transaction + lock riski.
- **Oneri:** Argparse ile `--batch-size N` destekle veya DB motoruna gore adaptive (PostgreSQL icin 500, SQLite icin 100).

### H2 [ORTA] Tek connection uzerinde transaction yonetimi kirilgan
- **Konum:** `ingest_ostim_detail.py:56-95`
- **Sorun:** Tek `conn`, uzun sure acik. Hata durumunda `trans.commit()`/`rollback()` cagirilmiyor, transaction acik kalabilir.
- **Oneri:** `with engine.begin() as conn:` kullan. Veya manuel durumda `try/finally` ile `trans.close()` veya `conn.close()` garantisi.

### H3 [ORTA] `kayit hatasi` istatistik kaybi
- **Konum:** `ingest_ostim_detail.py:92-93`
- **Sorun:** `stats["errors"] += 1` ile sadece sayim tutuluyor; hangi firma, hangi hata kodu kayboluyor. Post-mortem icin yetersiz.
- **Oneri:** `error_samples` listesine `{unvan: unvan, error: repr(e)}` ornekleri topla (ilk 50).

### H4 [ORTA] UTF-8 BOM / encoding kenar durumu
- **Konum:** `ingest_ostim_detail.py:47`
- **Sorun:** `DETAY_PATH.read_text(encoding="utf-8")` BOM olmadan okur; eger onceki arac BOM eklediyse, ilk firma unvani `"\ufeffABC"` olur.
- **Oneri:** `encoding="utf-8-sig"` ile BOM toleransi.

---

## 6. Stil / UTF-8 Bulgulari

### ST1 [DUSUK] `print` yerine `log.info`
- **Konum:** `ingest_ostim_detail.py:105`
- **Sorun:** Son satirda `print(json.dumps(stats, ...))` var. Streamlit/dashboard tarafinda istense de tutarlilik icin `log.info` veya `click.echo` ile degistir.

### ST2 [DUSUK] f-string ve format karisimi
- **Konum:** `ingest_ostim_detail.py:91`
- **Sorun:** `log.info(f"Batch tamamlandi: {i+1}/{len(records)}")` f-string kullanmis; geri kalan yerlerde `%`-format` ve `str.format` karisik. Tek bir stile normalize et.

---

## 7. Onerilen Aksiyon Plani

| Oncelik | Aksiyon | Sorumlu |
|---------|---------|---------|
| Yuksek | `try/except: pass` kaldir (S3) | Cursor Grok |
| Yuksek | Retry/backoff ekle (P1) | Cursor Grok |
| Yuksek | Session/conn context manager (H2) | Cursor Grok |
| Orta | User-Agent env (G1) | Cursor Grok |
| Orta | ThreadPoolExecutor ile paralel detay (P2) | Cursor Grok |
| Orta | Common constants modulu (S2) | Cursor Grok |
| Orta | encoding=utf-8-sig (H4) | Cursor Grok |
| Dusuk | Tip ipuclari (S6) | Cursor Grok |
| Dusuk | f-string normalize (ST2) | Cursor Grok |

---

## 8. Test Bosluklari (Eklenmesi Gereken)

- `ostim_scraper._label_match`: farkli label varyasyonlari (":", bosluk, buyuk/kucuk harf).
- `kvkk_filtrele`: bireysel domain listesi testleri.
- `extract_vkn`: 10-haneli vs 11-haneli VKN davranisi.
- `ingest_ostim_detail.normalize_website`: `OstimMain` substring, None, bos string.
- `ingest_ostim_detail.extract_parsel`: uzun (>80 karakter) string'te None donusu.
- Batch boundary: 99, 100, 101 kayit ile commit sayisi.

---

## 9. Sonuc

Genel olarak: kod okunabilir, KVKK filtrelemesi ve label fallback zincirleri iyi dusunulmus. Ancak retry eksikligi, transaction yonetimi ve sessiz hata yutma en acil duzeltilmesi gereken noktalar.

**Refactor uygulandiktan sonra:**
1. Tum testler tekrar calistirilmali (pytest).
2. Coverage yine 80%+ olmali.
3. Secim modu (scraping_permission_router) entegrasyonu icin `OSTIM_ROUTE=allowed` env kontrolu eklenmeli.
