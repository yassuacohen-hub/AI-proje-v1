# ALTYAPI-EVREN-PRIVATE-DOGRULAMA — Üretim Raporu

**Tarih:** 2026-10-01 · **Ajan:** yasu · **Görev:** EVREN private eğitim araştırması

---

## Özet

**EVREN'de "private eğitim" (fine-tuning) hizmeti YOKTUR.** EVREN, GPU
kiralaması (self-service HPC) modeliyle çalışmaktadır. Fine-tune API'si,
LoRA servisi veya model deposu bulunmamaktadır.

**Çıkarım (inference) ise 1 Kasım 2026'ya kadar tamamen ücretsizdir** (0.00 CR).

---

## Üretilen Çıktılar

| Dosya | Boyut | İçerik |
|---|---|---|
| `docs/EVREN_PRIVATE_EGITIM_DOGRULAMA.md` | ~14 KB | Ana rapor (14 bölüm) |
| `scripts/evren_egitim_uc_taramasi.py` | ~3 KB | 28 uç canlı tarama (tekrarlanabilir kanıt) |

---

## Yapılan İş

### 1. Kaynak toplama (D-260)

| Kaynak | Yöntem | Sonuç |
|---|---|---|
| Frontend JS (667.083 B) | Regex tarama | `fine-tune`/`LoRA`/`qLoRA`/`peft`/`adapter` = **0 kez** |
| LLM API | 17 uç canlı HTTP | 10 eğitim ucu → **404** |
| Panel API | 11 uç canlı HTTP | `/training/jobs` → **401** (oturum gerekli) |

### 2. Katalog analizi

`GET /v1/models` → 13 model. Alan kümesinde fine-tune/eğitim alanı **yok**.
`task` değerleri: `chat`, `ocr`, `embedding`, `rerank`, `audio` — hepsi çıkarım.

### 3. SSS çıkarımı

Sayfalar JS ile render edildiği için SSS metinleri JS paketinden çıkarıldı.
Eğitim işleyişinin **Slurm + Apptainer + 64× H200** olduğu, kredi ekonomisinin
**HOLD → SETTLE → RELEASE** ile yürüdüğü doğrulandı.

---

## Kesin Bulgular

| Konu | Sonuç | Kanıt |
|---|---|---|
| Fine-tuning API | 🔴 **YOK** | 10 uç 404 |
| LoRA/qLoRA servisi | 🔴 **YOK** | JS'te 0 kelime |
| Model deposu | 🔴 **YOK** | Katalog alanı yok |
| GPU kiralaması | ✅ **VAR** | Slurm+Apptainer, 64× H200 |
| Çıkarım fiyatı | ✅ **0.00 CR** | `free_until: 2026-11-01` |
| Eğitim fiyatı | ⚫ **Sayısal yok** | Panele bağlı |
| Veri limiti | ⚫ **Yazılı yok** | Panele bağlı |
| Model mülkiyeti | ⚠️ **Yazılı yok** | Resmî e-posta gerekli |
| Veri silme politikası | ⚠️ **Yazılı yok** | Resmî e-posta gerekli |
| SLA | ❌ **Yok** | Şart md. 5 |

---

## Teslim Kriterleri Durumu

| Kriter | Durum |
|---|---|
| Sayfa tamamen okundu | ✅ JS'ten metin çıkarıldı |
| Private eğitim varlığı onaylandı | ✅ **YOK** (çift kanıt) |
| Fiyatlandırma tablosu | ✅ Çıkarım + formül |
| Veri limitleri tablosu | ✅ Belirtilmemiş olarak işaretlendi |
| Yasal şartlar bölümü | ✅ Belirtilmemiş olarak işaretlendi |
| Öneriler | ✅ 5 maddelik tavsiye |
| **YASU denetim: resmî e-posta teyidi** | ⚠️ **KISMEN** — sayfa + canlı API var, e-posta yok |

---

## Açık Sorunlar

| # | Sorun | Çözüm |
|---|---|---|
| A1 | Eğitim fiyat katsayıları ölçülemedi | Panel → Eğitim İşleri |
| A2 | Veri limiti ölçülemedi | Panel → Eğitim İşleri → form |
| A3 | **Model mülkiyeti yazılı değil** | **Resmî e-posta** (hukuki) |
| A4 | **Veri silme politikası yazılı değil** | **Resmî e-posta** (KVKK) |

---

## Önerilen Sonraki Adım

```
Fine-tune için EVREN'e bağımlı olma.
→ Kendi LoRA eğitim script'ini Huginn'da yaz
→ Slurm işi ile H200 kirala (krediyle)
→ Modeli yerelde çalıştır (tam KVKK kontrolü)
→ EVREN çıkarımını yedek/fallback olarak kullan
```

Bu yol D-310'un iç/müşteri ayrımını da korur: model ve veri Huginn'de kalır.

---

## D-310 Bağlantısı

Bu araştırma, `ALTYAPI-ODIN-DENETIM-RAPORU` (NO-GO) raporundaki
"EVREN'de fine-tune ucu yok" tespitini **bağımsız olarak doğruladı**.
D-310'un *"EVREN ücretsiz döneminde fine-tune edilecek"* varsayımının
dayanağı bulunamadı — **ihsan'a karar güncellemesi önerilir.**

---

*yasu · 2026-10-01 · D-260 kanıt temelli · D-196 denetim kiti*
