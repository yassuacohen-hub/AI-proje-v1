# yasu_project_context.md — Oturum Hafızası (D-219)

Şablon: [[Huginn Data Insights/_ajan_context_sablon]] · Tavan 200 satır.

## KALDIĞIM YER

- **Konum:** `ALTYAPI-TICARET-KANIT-01` — **pilot tamamlandı**, kanıt toplandı.
  Kalan: ihsan'a review tetiği + Düzey_3 satın alma kararı (KAHİN'inkidir).
- **Yapılanlar (2026-09-29, TOBB oturumu):**
  - **D-276 KÖK NEDEN:** TOBB girişi `data=` ile bozuluyordu. Form
    `enctype="multipart/form-data"` + JS `new FormData(this)` → **`files=`**
    şart. Doğrusunda sunucu tam olarak `"1"` döner. e-Devlet **kullanılmadı**.
  - **"Tüm Ankara tek seferde" → MÜMKÜN DEĞİL** (ölçüldü): sunucu
    `"Sicil No veya En Az 5 Karakter Ticaret Unvanı Giriniz"` diye reddediyor.
    İl+tarih tek başına sonuç vermiyor. Gerçek toplu yol = `TicaretUnvani`
    (AKANA → **71 ilan tek istekte**, sayfalama yok).
  - **AKANA pilotu (448217) tamamlandı:** 4 ilan + GUID + ham PDF indirildi,
    `IlanKaniti` kapısından geçirildi (`data/kanit/*.json`).
  - **D-277:** vision-LLM OCR yolu kuruldu (9Router, 739 model arasından
    `gemini/gemini-3.8-flash`). Sonra **D-278** ile pasife alındı.
  - **D-278 DÜZELTME:** KAHİN "gövde metinleri XML/ham metin olarak iletilir"
    dedi → **doğrulandı** (resmî Abonelik sayfası, "HİZMET SUNUŞ ŞEKLİ"
    sütunu = **WEB SERVİS**). Düzey_1 = *aranamaz* PDF; **Düzey_2/3 = aranabilir
    + makine-okunur TSM/XML**. → **OCR'a gerek yok**, PDF'e de gerek yok.
  - **Ücretsiz üye PDF'i ise gerçekten scan** (ölçüldü: `font=0`, `Tj=0`,
    3 görsel XObject, A4@200DPI) → yalnız o yol OCR'a muhtaç.
  - **Düzey_3 veri seti (1.427.688 TL):** NACE ana+alt, **Vergi No**,
    Vergi Dairesi, UAVT Adres Kodu, Ortaklar (sermaye dahil), Temsilciler,
    Amaç Konu, Müfterek Listesi (JSON). → projenin **tam boşlukları**.
  - **D-279 KAHİN itirazı (KAPSAM TESPİTİ DOĞRU):** "1 aylık ücretle tüm
    firma bilgisi toplanmaz" dedi. Ölçüldü (`scripts/abonelik_kapsam_olcer.py`):
    * *"1 aylık"* → **yanlış** (sayfada **"(Yıllık)"**, 251 iş günü).
    *"Sadece o dönemin verisi, aradığımız veri orada değil"* → **doğru**:
    AKANA'nın 4 ilanının yalnızca **2'si 2026 → %50 kapsam**.
    → **DÜZEY_3 ALINMAYACAK.** D-278'in satın alma önerisi geri çekildi.
  - **D-280 "OCR daha ucuz" ÖLÇÜLDÜ (kısmen çürütüldü):**
    `scripts/ocr_maliyet_olcer.py` — 7 model, **1'i** çalışıyor
    (`openai/gpt-4o-mini`; gemini'ler 403/402/boş cevap).
    Ölçüm: **5,89 sn / 49.146 token** sayfa başına.
    Projeksiyon: 14.000 → **~23 saat** · 930.000 → **~63 gün**.
    → Tam yıllık kapsamda OCR pratik DEĞİL; 14.000'de denenebilir.
    **Kök neden (istemci):** gpt-4o-mini HTTP 200 dönüyor ama JSON sonuna
    `data: [DONE]` (SSE) ekleniyor → `r.json()` patlıyordu. `_cevap_ayikla()`
    ile düzeltildi. → "OCR çalışmıyor" sandım, **istemci hatalıydı**.
    **OCR doğruluk riski:** gpt-4o-mini MERSİS'i `001203074100024` (15 hane)
    okudu; gerçek `0012032074100024` (17 hane). **D-274 kapısı yakaladı**
    (`None` → reddedildi). Regresyon testi eklendi.
- **Pasifleştirme (D-278):** `scripts/gazete_ocr.py` **silinmedi** —
  `OCR_ETKIN=False` + `OcrPasifHatasi` kapısı + `--aktif`/`--durum` bayrakları.
  Kapalıyken **HTTP atılmıyor**. `tests/test_gazete_ocr_pasif.py` (11 test).
- **Kritik bağlam:** SADECE
  `plans/rapor_yasu_BROWSERUSE-TICARET-SICIL-01.md` (EK-1 §16-23, EK-2 §24-26)
  · `data/kanit/` · `data/pdf_analiz.json` · `scripts/tobb_oturum.py`
- **Sonraki adım:** ihsan'a review tetiği → KAHİN'e Düzey_3 kararı sor.
- **Görev:** `ALTYAPI-TICARET-KANIT-01` · **Son okunan karar:** `D-278`


## Oturum Açılış (60 saniye, bu sırayla)

1. **§KALDIĞIM YER** — yukarıdaki blok.
2. **§Tuzaklar** + **§Sabitler**.
3. `python scripts/gorev_kutusu.py liste --ajan yasu`
4. `python scripts/ajan_chat.py oku --ajan yasu` (D-210 cevap süresi: P0 5-10dk, P1 10-15dk, P2 15-30dk)
5. [[Huginn Data Insights/AGENTS]] son karar no ≠ `D-268` ise aradakileri oku (D-168).
6. İncelenen brifin **§Doğrulanacak varsayım** maddeleri gerçekten doğrulanmış mı — kanıt `dosya:satır` var mı?

**§KALDIĞIM YER pano ile çelişiyorsa pano üstündür.**

## Kimlik

- **Ajan:** `yasu` (araç: cline)
- **Rol:** Denetim/review ajanı — kod inceleme, güvenlik, mimari uyum, doküman doğrulama.
- **Kit:** `ADMIN-KİT` (D-196)
- **Mülkü:** review raporları, denetim notları; inceleme sırasında **okuma** her yere açık
- **Mülkü değil:** üretim kodu (utku'nun mülkü) — kusur bulursan **düzeltmezsin**, chat ile bildirirsin
- **Rapor hattı:** bulgu → `ihsan`; `salih` raporları sana gelir

## Proje Temel Bilgileri

- **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Kural kaynağı:** [[Huginn Data Insights/AGENTS]] — tek SSOT, kural kopyalamak yasak
- **Test:** `python -m pytest tests/ -q` → **4457 test toplanıyor; kırık sayısı
  `lastfailed`'a bakılmadan ölçülür** (D-268, 2026-09-29)
- **Denetim testleri:** `tests/test_naming_audit.py` (D-57), `tests/test_brief_sablon_denetim.py`
  (D-217/D-218), `tests/test_kok_politikasi.py` (D-221/D-241 + kök yarısı)

## Sabitler (doğrulanmış gerçekler)

- Brif şablonu **tek**: `plans/_brief_sablon.md`. `brief_TEMPLATE.md` D-217'de silindi.
- Brif baseline: `tests/_brief_baseline.txt` — 112 kayıt, **yalnız küçülür** (mandal)
- Admin menü: 6 kök (D-214/D-215); KVKK Proje altında
- **Görev başlığı ok işareti `→` (U+2192)** olmak zorunda; ASCII `->` reddedilir (D-57)
- **Brif bölüm başlığı `## Ilgili Nodlar` ASCII `I`** ile yazılır; Türkçe `İ` reddedilir (D-217)
- Görev atama sırası: **brif önce** (D-66) → **D-217 denetimi** → **sonra atama**
- Arşiv: `_ARSIV_tek_kullanimlik/` (130 dosya, 459 KB, içerik bozulmadı)
- `_ajan_context_sablon.md` **kökte kalır**; 3 referans onu okuyor (D-219)
- `AGENTS.md` son karar: **D-268** (satır 3943)

## Tuzaklar (aynı hatayı iki kez yapma)

- "Yapıldı" beyanı `dosya:satır` kanıtı taşımıyorsa → doğrulanmamış iddia → **reddet**, kanıt iste
- Pano kaydının dosyası kod tabanında yok → hayalet görev (D-216) → arşiv öner, kod yazılmasına izin verme
- Aynı işin iki dosyaya yazılması → D-211 ikiz ihlali → hangisi kanonik, diğeri silinir
- **`.pytest_cache/lastfailed` kanıt DEĞİLDİR** → 330 bayat kayıt görüldü, fiilen 18 passed
  → kırık test iddiası **canlı koşudan** gelir (D-268)
- **Pano boş ≠ dosya boşta** → görev kaydı olmayan ajan da dosya yazabilir; FAZ-0'da
  canlı ölçüm betiği arşive kaydı → taşıma/yazma öncesi **dosya hareketine** bak
  (ALTYAPI-AJAN-CAKISMA-01)
- Türkçe `İ` ile yazılan `## İlgili Nodlar` → D-217 reddediyor; ASCII `I` kullan
- D-57 başlığında ASCII `->` → reddedilir; PowerShell'de `[char]0x2192` kullan
- **Bir kütüphane "boş döndü" dedi → scan mı, metin katmanı mı AYIRT ETMEDEN
  karar verme.** KAHİN PDF'i okuyabiliyordu, ben "metin katmanı yok" dedim,
  gerekçemi ölçmedim → yanlış karar. `scripts/pdf_kanit_analiz.py` ile ölç:
  `font`/`Tj`/`ToUnicode` sayacı + görsel XObject (D-277/D-278).
- **Kullanıcının alan bilgisi varsa doğrula, reddetme.** "Gövdeler XML olarak
  iletilir" → resmî abonelik tablosunun **WEB SERVİS** sütunu doğruladı;
  iki günlük OCR işi boşa çıktı. Önce **tabloyu/sayfayı oku**, sonra kestik.
- **`multipart/form-data` şüphesi:** HTML'de `enctype` + `new FormData(this)`
  varsa `data=` değil `files=` gönder; sunucu sessizce `0` dönüyor (D-276).
- **Test kırmızıysa önce koddan şüphelen.** Bu turda `test_zorla_bayragi_akitir`
  kırmızıydı ve gerçekten **kod** hatalıydı: `IPUCLARI` tanımsızdı.
- **PowerShell konsolu UTF-8 bozar** (`│` → `┼`): dosyayı `Out-File` ile yazma,
  Python içinde yaz; doğrulamayı `x.encode('unicode_escape')` ile yap.


## Bilinen Açıklar (kapsam dışı backlog)

- 112 brif D-217 şablonuna uymuyor — bilinçli mandal, geriye dönük düzeltilmiyor
- `_ARSIV_tek_kullanimlik/` 130 dosya: silinip silinmeyeceği **KAHİN kararı bekliyor**
- `scripts/kodlama_denetim.py` 36 mojibake bildiriyor — NACE script'lerinde, köklü değil
- `ALTYAPI-AJAN-CAKISMA-01` (P1, ihsan) atandı — kilit kapısı; brif `plans/brief_ihsan_...md`
- **OSTIM izin yasağı:** `OSTIM_TEMIZ` izin gelene kadar yayımlanamaz/dağıtılamaz (KAHİN: "izin en son plan")
- **İVEDIK kaynak listesinden düşürüldü** (D-301) — 4 yöntem denendi, hiçbiri açmadı; veri silinmedi, yalnızca kaynak kullanımı sonlandı

## Sık Komutlar

```bash
python scripts/gorev_kutusu.py liste --ajan yasu
python scripts/gorev_kutusu.py al --ajan yasu --task-id <TASK_ID>
python scripts/ajan_chat.py ac yasu <TASK_ID> "<sorun>" --cozum "<oneri>"
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id <TASK_ID> --ozet "<özet>"
```

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/_ajan_context_sablon]]
- [[plans/_brief_sablon]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]