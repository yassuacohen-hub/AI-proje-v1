# VERI-RAG-KORPUS-01 — Teslim Raporu (üretim)

**Tarih:** 2026-10-02 · **Rol:** üretim (UTKU) · **Kilitli dosya:** `src/company_master/vector/service.py`
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` → "Kapanan isler" (B-14)
**Ölçüm kaynağı:** canlı Supabase (`companies`), D-238

## Ne yapıldı

`vector/service.py` içinde firma satırı → aranabilir metin dönüştürücüsü kuruldu (331 satır). Mevcut haldeydi; bu turda **kabul kriterleri canlı veride ölçüldü** ve mandal kırılarak doğrulandı.

- `KORPUS_ALANLARI` — **beyaz liste**, 10 kolon. Siyah liste yok: yeni kolon eklenince sızmaz.
  - `description` **çıkarıldı**: 632 dolu kaydın 624'ü (%98,7) adres deseni. Kolonun adı "description" ama içeriği adres — korpusa koymak D-247 ihlaliydi. Yerine `sector_name` (7.595 dolu, adres deseni **0**).
  - `tax_number` yok: D-248 gereği TCKN de bu kolona yazılabiliyor.
- `korpus_kunyesi()` — her metnin sonunda `firma_id · kaynak_adı · güncelleme_tarihi`. **Künyesiz kayıt üretilemiyor.**
- `KORPUS_KISISEL_DESENLER` — TCKN / telefon / e-posta deseni. TCKN deseni **hex-duyarlı** (`(?<![0-9A-Fa-f])\d{11}(?![0-9A-Fa-f])`); sınır olmadan künyedeki UUID hex kuyrukları 11 haneli sayı gibi görünüyor ve canlı ölçümde **44 gerçek kaydı** yanlışlıkla reddediyordu.
- `chunk_gerekli()` / `korpus_icerigi()` / `korpus_kayitlarini_uret()` — batch'li, hata toleranslı üretim.

## Kabul kriterleri — ölçülen değerler

| # | Şart | Kanıt | Sonuç |
|---|---|---|---|
| 1 | Metin uzunluğu ortancası ≥ 80 | 50 örneklem: **215,0** · tam korpus (9.412): **213,0** karakter | ✅ |
| 2 | Kişisel veri sızıntısı 0 | 9.412 metnin tamamı tarandı → **0 eşleşme** | ✅ |
| 3 | Tekil firma **ve** kayıt ayrı yazıldı | kayıt **9.412** · tekil firma **9.412** (`count(DISTINCT company_id)` = 9.412) | ✅ |
| 4 | Başarısız kayıtlar listelendi | **0** başarısız — liste boş, sebep yok | ✅ |
| 5 | Her chunk'ta kaynak künyesi var | Mandal kırılarak doğrulandı (aşağıda) | ✅ |
| 6 | `pytest tests/ -q` yeşil | **18 failed / 4957 passed** — aşağıdaki "Bulgular" maddesi | ⚠️ kırmızılar bana ait değil |

### Üç varsayım

| # | Varsayım | Ölçüm | Karar |
|---|---|---|---|
| 1 | Metin üretilebilir | ortanca 213–215 karakter, min 163 / maks 273 | geçti |
| 2 | Kişisel veri sızmıyor | 0 eşleşme | geçti |
| 3 | Chunk gerekli mi | 200 karakteri geçen: 6.358 / 9.412 (**%67,6**) · **maksimum 306** · embedder penceresi (448) aşan: **0 / 9.412** | **CHUNK YAPILMAZ** |

**Varsayım 3'te ilk hükmüm yanlıştı ve ölçümle düzeltildi.** Brief 200 karakter
işaretini soruyor; ölçüm "%67,6 geçiyor" diyor ve ilk turda "CHUNK YAPILIR"
yazdım. Doğru karar veren eşik 200 değil **embedder penceresidir** (448) —
korpusun **maksimumu 306**, yani hiçbir kayıt pencereyi aşmıyor. Kırpmak
taşıma maliyeti getirir, kazandırmaz. Kısa vadede ölçüm ikisini de yazdı;
karar embedder penceresine göre verildi.

Ayrıca düzeltme: teslim özetinde "en uzun 448 karakter = %1,56" yazıyordu.
Güncel canlı ölçüm **maksimum 306** ve 448 üstü **0**. Fark ölçüldü, kayda
geçti — özet değil ölçüm esas alınır (D-260).

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `src/company_master/vector/service.py` | +331 satır — korpus üretimi (görevin kilitli dosyası) |
| `scripts/rag_korpus_olcum.py` | Yeni — kabul ölçüm aracı (salt okuma, idempotent) |
| `hubs/OSINT_VERI_TOPLAMA_HUB.md` | "Kapanan isler" satırı (B-14) |
| `skills/services/ticaret_sicili_kanit.py` | TSG-04 bağımlılıkları (aynı oturum, aşağıda) |

## Test sonuçları

```
tests/test_rag_korpus.py  ->  57 passed
tests/vector/             ->  73 passed
toplam                    -> 130 passed
tam süit                  ->  18 failed / 4957 passed / 12 skipped (197 sn)
kodlama_denetim --kapsam git -> temiz (20 değişen dosya, allowlist dışı ihlal yok)
```

### Mandal kırma denemeleri (D-256/4)

| Deneme | Sonuç |
|---|---|
| Temel hal | 57 passed |
| `+ KUNYE_AYRAC + kunye` kaldırıldı | **8 failed** → geri alındı → 57 passed |
| Beyaz listeye `primary_email` eklendi | **1 failed** (`test_kisisel_kolonlar_listede_yok`) → geri alındı → 57 passed |

## Bulgular

- 🟡 **Tam süit 18 kırmızı; hiçbiri bu göreve ait değil.** Ölçüldü, varsayılmadı:
  - 6 × `test_brief_sablon_denetim` — D-312'de kayıtlı brif şablonu borcu
  - 4 × pano / D-57 (`test_naming_audit`, `test_pano_d57_kalici` ×2, `test_pano_denetim_tetik`)
  - 2 × `test_kok_politikasi`, 2 × `test_dokuman_politikasi`
  - 1 × `test_gorev_kutusu_arsiv`, 1 × `test_d309_ders_kapisi`, 1 × `test_d272_borc_defteri`
  - 1 × `test_dusurulen_kolon` → **`scripts/yasu_canli_olcum_d260.py:47,48`**: goc 0036'da düşürülen kolon üretim koduna geri sızmış (D-268 deseni). YASU'nun dosyası, dokunulmadı.
  - 1 × `test_kodlama_denetim::test_guard_bom_ratchet` → **`scripts/continue_haftalik_bildir.py`**: BOM'lu. SALİH'in dosyası, dokunulmadı.
- 🟡 `test_kok_politikasi` ve `test_dokuman_politikasi` kırmızıları D-241/D-220 kök izleme kurallarına bağlı; bu görev onları değiştirmedi.
- 🔵 `source_name` beyaz listede ama ölçümde kaç firmanın dolu olduğu yazılmadı. Alan boşsa künye eksik kalır — `korpus_kunyesi()` "bilinmiyor" yazıyor, yani künye **yine de** üretiliyor. Künyesizlik kapısı çalışıyor; izlenmesi gereken tek eksik bu alanın doluluk oranı.

## Eksik / erteleme

- **Bu görev indeksi yazmaz, metin üretir.** Vektör indeksine yazma `ALTYAPI-RAG-EMBEDDER-01` bağımlılığının kapsamında (brif `## Bağımlılık`). Bu görev "indeksle" diyor ama kilitli dosya ve kabul kriterleri metin üretiminde kalıyor; gerçek yazma `odin_ai/rag` tarafında.
- **Bu oturumda yapılan ikinci iş:** `skills/services/ticaret_sicili_kanit.py` içinde `ILAN_TURU_ESLEME` (17 anahtar, `data/kanit/*.json`'dan ölçülen tam değerler) + `olay_esle()` eklendi. Eşleme **tam eşleşme** (alt dizi değil) — testler monkeypatch'li anahtarla bunu zorluyor. İki adımlı arama: önce metin olduğu gibi, sonra ASCII katlanmış; böylece ham (`tsg_rapor`) ve normalize büyük-harf (`tsg_yazici`) çağrı yolları **tek anahtar kümesiyle** karşılanıyor (D-211 ikiz yok). `tests/test_tsg_zincir.py` + `tests/test_tsg_rapor.py` = **28 passed**. Bu, `VERI-TSG-ESLEME-CASE-01` kapsamındadır; ayrı teslim edilir.
- **Ölçüm aracı geride bırakıldı:** `scripts/rag_korpus_olcum.py`. Salt okuma ve idempotent; tekrar koşulabilir. Silinmedi — teslim sonrası doğrulamada kullanılır (teslim kontrol listesi madde 5).

## Öz-eleştiri

- **Ne iyi gitti:** Kabul kriterlerini beyanla değil canlı DB'den ölçtüm; 9.412 metnin tamamını taradım, "50 örnekte 0 sızıntı" yerine "tamamında 0 sızıntı" dedim.
- **Ne kötü gitti:** Mandalı kırmak için PowerShell inline `python -c` kullandım; komut sessizce bozuldu ve **hiçbir şey değişmedi**. Test yine yeşildi, yani yanlışlıkla "mandal çalışıyor" dedim. D-86'da yazılı: tek satırdan uzun iş `scripts/*.py` dosyasına. Kırmayı edit aracıyla tekrarladım, o zaman gerçekten kırıldı.
- **Zamanı ne yedi:** `firma_korpus_metni` tuple döndürüyor, `kisisel_veri_tara` ise desen adı listeliyor — ölçüm betiğini iki kez düzelttim. Fonksiyon imzasını okumadan betik yazdım.
- **Yarın neyi değiştireceğim:** Yeni bir arac/test yazmadan önce hedef fonksiyonun **imzasını** okuyacağım; `python -c` inline patch yerine dosya yazacağım.

## Ilgili Nodlar

- [[hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[src/company_master/vector/service]]
- [[tests/test_rag_korpus]]
- [[AGENTS]]