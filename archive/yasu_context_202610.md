# yasu_project_context arşivi — 202610

> **D-219 arşivi.** `yasu_project_context.md` 213 satıra (tavan 200) çıktığı için
> eski oturum blokları buraya taşındı. Taşıma tarihi: 2026-10-02.
> **Bu dosya güncel hafıza DEĞİLDİR** — güncel olan `yasu_project_context.md`.
> Aşağıdakiler tarihsel kayıttır; karar verirken **AGENTS.md** ve pano üstündür.

## Arşivlenen oturum: ALTYAPI-TICARET-KANIT-01 (2026-09-29 → 2026-09-30)

Bu blok 2026-10-02'de arşivlendi. O tarihte `§KALDIĞIM YER` içindeydi; görev
sonradan kapandı, bu yüzden ayrıntı güncel hafızaya taşınmadı.
Kaynak commit: `a01f020` (0043 göçü), `921e5ed` (D-309), `eaa89f7` (D-306).

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
- **Sonraki adım (o tarihte):** ihsan'a review tetiği → KAHİN'e Düzey_3 kararı sor.
- **Görev:** `ALTYAPI-TICARET-KANIT-01` · **Son okunan karar:** `D-278`

### Bu arşivden taşınan dersler (güncel hafızaya taşınmadı, burada kalıyor)

- `multipart/form-data` şüphesi: HTML'de `enctype` + `new FormData(this)`
  varsa `data=` değil `files=` gönder; sunucu sessizce `0` dönüyor (D-276).
- **Kütüphane "boş döndü" dedi → scan mı metin katmanı mı AYIRT ETMEDEN karar verme**
  (D-277/D-278). KAHİN PDF'i okuyabiliyordu; ölçmedim, yanlış karar verdim.

---

## Ilgili Nodlar

- [[Huginn Data Insights/yasu_project_context]] — güncel hafıza (bu dosya arşivdir)
- [[Huginn Data Insights/archive/yasu_context_202609]] — önceki arşiv dönemi (Eylül 2026 oturum günlüğü)
- [[Huginn Data Insights/archive/ihsan_context_202609]] — aynı tavan taşmasını yaşayan ajanın arşivi (konvansiyon örneği)
- [[Huginn Data Insights/AGENTS]] — D-219 (ajan hafızası) · D-218 (graf) · D-276 · D-277 · D-278 · D-279 · D-280
