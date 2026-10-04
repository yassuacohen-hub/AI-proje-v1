# VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01 — Teslim Raporu

**Tarih:** 2026-10-04 · **Rol:** Üretim/Hacim · **Öncelik:** P2

## Ne yapıldı

ASO verisinin iki bağımsız yükleme yolu tek yolda birleştirildi (D-211).

| Konu | Önce | Sonra |
|---|---|---|
| Yükleme yolu | `scripts/ingest_aso_data.py` + `src/company_master/etl/ingest_aso.py` | yalnız `src/company_master/etl/ingest_aso.py` |
| Eşleştirme | kesin + fuzzy `LIKE '%unvan[:20]%'` | **yalnız kesin** |
| Ham dosya seçimi | `glob` (kendi ürettiği raporu buluyordu) | `KAYNAK_DOSYA` sabiti |
| Kaynak kaydı | eksik/dağınık | `(source_id, external_id)` idempotent upsert |
| Sicil ölçümü | `kimlik_dogrula()` (VKN kapısı) | `sicil_dogrula()` (D-267 kapısı) |

**Eşleştirme ölçümü (brif varsayımının çürütülmesi).** Eski script fuzzy eşleştirme
taşıyordu. Ölçüldü: 722 tekil unvanın **673'ünde** ilk 20 karakter birden fazla yanlış
aday üretiyor — çünkü OSTİM verisinde ortak `(İFLAS NEDENİYLE) TASFİYE HALİNDE`
öneki var. Yanlış firmayı zenginleştirmek, hiç eşleştirmemekten kötüdür. Fuzzy
taşınmadı; kesin eşleşme korundu.

**Dosya kararı — brif kısmen çöktü (D-233).**

| Dosya | Karar | Gerekçe |
|---|---|---|
| `data/aso/aso_full.jsonl` | **kanonik** | 1091 satır / 722 tekil unvan / 0 bozuk JSON / 0 `?` |
| `aso_full_filtered.jsonl` | `data/aso/_eski/` | aynı 722 unvan + türetilmiş skor; canlı tüketicisi yok |
| `aso_full_clean_report.json` | `data/aso/_eski/` | yalnız üretim raporu |
| `aso_full_clean.jsonl` | **YERİDE KALDI** | aşağıdaki bulgu |

`aso_full_clean.jsonl` brifte "taşınacak" yazıyordu. Ölçüm bunu çürüttü: dosya
`scripts/osb_tarama.py:52` `KORUNAN` listesinde (SHA-256 kilidi
`data/osb_tarama/_kaynak_kilidi.json`) ve `scripts/osb_veri_seti_uret.py` 9
`kaynaklar` referansı üretiyor. Canlı kod bakan yol kopya değil **bağımlılıktır**
(D-233). Bu bir ikiz ingest yolu değil, OSB'nin kendi kalite filtresinden geçmiş
girdisi.

## Değişen dosyalar

| Dosya | İşlem |
|---|---|
| `src/company_master/etl/ingest_aso.py` | yeniden yazıldı (348 satır): kesin eşleşme, `source_records` idempotency, deterministik `content_hash`, koşullu zenginleştirme, `--kuru` |
| `tests/test_ingest_aso_glob.py` | yeni, 57 test |
| `scripts/ingest_aso_data.py` | **silindi** (ikiz yol) |
| `data/aso/_eski/aso_full_filtered.jsonl` | arşivlendi |
| `data/aso/_eski/aso_full_clean_report.json` | arşivlendi |
| `data/aso/aso_full_filtered.jsonl` | kökteki birebir ikiz kopyası silindi |
| `hubs/VERI_KALITESI_HUB.md` | kapanış satırı eklendi |
| `data/orchestrator/bulgu_defteri.md` | 7 bulgu |

**Dokunulmayanlar:** `data/aso/aso_full.jsonl` (306 satır başkasının commit
edilmemiş değişikliği), `scripts/osb_tarama.py`, `scripts/osb_veri_seti_uret.py`,
`data/osb_tarama/_kaynak_kilidi.json`.

## Test sonuçları

```
python -X utf8 -m pytest tests/test_ingest_aso_glob.py -q     -> 57 passed in 2.81s
python -X utf8 scripts/kodlama_denetim.py --kapsam git       -> bu dosyalarda temiz
python -X utf8 -c "... ingest_aso_data(dry_run=True)"        -> 1091 okundu -> 722 yazilabilir
```

Kuru koşu çıktısı (canlı DB'ye **hiç** yazılmadı):

```
okunan satir 1091 · yazilabilir satir 722 · eklendi 0 · kesin eslesme 0
zenginlestirilen 0 · kaynak kaydi 0 (kimliksiz: 0) · gecersiz sicil 1
```

**Mandal sayıları:** 57 testin tamamı yeni göreve ait. Üç mandal **kırılarak**
doğrulandı (D-256/4): fuzzy `LIKE` tarama mandalı, çağrı tabanlı VKN kapısı
mandalı, `raw_payload` NULL birleşim mandalı.

**Mandalın kendi kör noktası bulundu ve kapatıldı.** İlk denemede fuzzy `LIKE`
mandalı, modülün **docstring'inde** geçen açıklayıcı `LIKE` kelimesini ihlal
sayıyordu (yanlış pozitif). Aynı hata ikinci kez `kimlik_dogrula()` kontrolünde
tekrarladı. Metin taraması yerine AST'ye geçildi: `_kod_metinleri()` docstring'leri
hariç string sabitlerini, `_cagrilan_adlar()` gerçek çağrı noktalarını ölçüyor.
D-245 ("doluluk geçerlilik değildir") mandala da uygulandı: kuralı **anlatmak**,
kuralı **çağırmamaktır**.

## Bulgular

🟡 **Brif varsayımı çöktü (D-233).** Ayrıntı ve kanıt yukarıda; istisna modül
docstring'ine ve teste yazıldı.

🟡 **Yanlış kapı bir alarmı 1091'e şişirdi.** Eski ölçüm ticaret sicilini VKN
kapısından geçiriyordu ve `geçersiz kimlik: 1091 / 1091` diyordu. Doğru kapı
(`sicil_dogrula`, D-267) aynı koşuda **1** gerçek geçersiz veriyor. Kilitli
dosyadan dışarı taşınmadı ama **adı ve kapısı yanlıştı**; düzeltildi.

🟡 **Taşıma değil kopyalama yapılmıştı.** `aso_full_filtered.jsonl` `_eski/`'ye
kopyalanmış, kökte birebir ikizi duruyordu (sha256 `d120269b972afbe2`, 773672
bayt). Rapor "taşındı" derken disk "kopyalandı" diyordu. Kökteki ikiz silindi.

🟡 **`data/aso/aso_full.jsonl` 306 satır commit edilmemiş ve bana ait değil.**
HEAD 785 satır, disk 1091 satır. Bu görevde ölçülen 722 tekil unvan, iki kümenin
birleşimi. Dosyaya dokunulmadı (D-309/2: başkasının işine sessizce dokunma).
Commit öncesi sahipliği netleşmeli.

🔵 **`raw_payload` güncellemesi NULL veriyi sessizce yutuyordu.**
`NULL || '{}'` Postgres'te `NULL` → mevcut ham veri kaybolur, hata verilmez.
`COALESCE` ile güçlendirildi.

🔵 **`dry_run` canlıya bağlanabiliyordu.** `engine or get_engine()` ifadesi
`dry_run`'dan bağımsız değerlendiriliyor. Artık kuru koşuda motor kurulmuyor.

🔵 **Pre-commit kancasını 4 dosya durduruyor** (`scripts/kazima_jina_fallback.py`,
`kazima_qwen_classify.py` + testleri; hepsi eksik satır sonu). Bu görevdeki
değil; kapsam dışı bulgu olarak kayda geçti, dokunulmadı.

## Eksik / erteleme

### Bilinen kırmızılar (bu görevden **değil**, açıkça kayda geçirildi)

| Test | Ölçüm | Kime ait |
|---|---|---|
| `test_kural4_yasak_ad_kalibi_artmiyor` | yasak ad kalıbı **16** dosyada, tavan 15 | paylaşılmış; bu görevin dosyası değil |
| `test_d320_ajan_context_dosyalari` | §Öz-eleştiri işaretı kanonik şablonla uyumsuz | önceki teslimden kayıtlı |
| `test_d272_borc_defteri_eksiksiz` | `BORC-CHAT-TEK-KANAL-01` AGENTS.md'de var, borç defterinde yok | önceki teslimden kayıtlı |
| `kodlama_denetim.py --kapsam git` | **4** dosya eksik satır sonu (`kazima_jina_fallback.py`, `kazima_qwen_classify.py` + testleri) | kapsam dışı; pre-commit kancasını durduruyor |

Bu görevin ürettiği hiçbir test kırmızı değil: `tests/test_ingest_aso_glob.py`
57/57 yeşil. `_eski/` klasörü Kural 4 sayımına **girmiyor** (mandal yalnız `*.md`
sayıyor; klasörde `.jsonl`/`.json` var) — ölçüldü, varsayılmadı.

### Kalan işler

| Konu | Durum |
|---|---|
| Canlı ingest | **Çalıştırılmadı.** Kuru koşuyla kanıtlandı; `company_id` dönüşlü INSERT + kaynak upsert canlıda denenmedi (D-244: kanıtsız üretim işi kapatılmaz) |
| `aso_full_clean.jsonl` kalıcı kararı | `BORC-OSB-TEMIZ-GECIS`: OSB tüketicisi önce kanonik dosyaya geçirilmeli, sonra bu dosya tüketicisiz kalır (D-236) |
| `aso_full.jsonl` 306 satır | Sahiplik netleşmeli; görev kapsamı dışı |
| Fuzzy eşleşme | Kalıcı olarak yok. Unvan çeşitliliği artarsa ayrı görevde normalize sözlükle açılabilir |
| `pre-commit` 4 dosya | Kapsam dışı; KAHİN kararı bekliyor |

## Öz-eleştiri

Mandalı **kendim** yazmış, sonra kendi kör noktasına takıldım: docstring'teki
kural açıklamasını ihlal saydım ve kodu değiştirmek yerine metin taramasını
AST'ye çevirdim. Doğrusu ilk adımda kuralı **SQL'e** bakarak yazmaktı (fuzzy
`LIKE` yalnız SQL'de aranır), metin taramasını seçmemekti. Aynı hata ikinci kez
`kimlik_dogrula()` kontrolünde çıktı — iki farklı test, tek kök neden: **metin
taraması kuralı değil yorumu ölçer.**

İkinci ders: "taşıdım" dedim, diskte **kopyaydı**. Dosya işlemlerini SHA-256 ile
doğrulamadan "taşındı" demek, D-260'ın tam tersi — beyan kanıt değil.

## İlgili Nodlar

- [[Huginn Data Insights/plans/brief_utku_VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01]]
- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/src/company_master/etl/ingest_aso.py]]
- [[Huginn Data Insights/tests/test_ingest_aso_glob.py]]
- [[Huginn Data Insights/data/orchestrator/bulgu_defteri]]