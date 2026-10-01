# ALTYAPI-EVREN-PRIVATE-DOGRULAMA — EVREN Özel Eğitim Hizmeti Araştırması

**Araştıran:** yasu (denetim) · **Tarih:** 2026-10-01
**Kurallar:** D-260 (beyan değil kanıt) · D-196 (denetim kiti)
**Erişim:** `https://evren.ssyz.org.tr` + `evren-llmapi.ssyz.org.tr` (anahtar `...D70M`)

> 🔄 **2026-10-01 18:4x — DÜZELTME.** İlk turda "eğitim hizmeti YOK"
> denmişti. Panel sayfaları (`/models`, `/universe`, `/billing`, `/training`)
> incelendiğinde **eğitim hizmetinin VAR olduğu** görüldü: "Eğitilmiş
> modelleri yönetin", "Eğitim Başlat", GPU Kredi Hesaplayıcı.
> **Ancak kapsam GÖRÜNTÜ işleme (YOLO/SAM-2) — LLM eğitimi değil.**
> Ayrıntı: [§15 Düzeltme](#15-düzeltme--önceki-tespit).

---

# 🟡 BULGU: Eğitim hizmeti **VAR**, ama **görüntü (vision) odaklı**

EVREN'de model eğitimi **mevcut** — GPU kiralama (Slurm + Apptainer + 64×H200)
üzerinden. Ancak kanıtlar hizmetin **görüntü işleme (Faz 1 — YOLO/SAM-2)**
üzerine kurulu olduğunu gösteriyor. **LLM fine-tuning (Odin) desteği kanıtlanamadı.**

| Soru | Cevap | Kanıt |
|---|---|---|
| Eğitim hizmeti var mı? | ✅ **VAR** | `/training` sayfası, GPU Kredi Hesaplayıcı, "Eğitim Başlat" butonu |
| **LLM** eğitimi var mı? | ❌ **Kanıtlanamadı** | Hesaplayıcı `imgsz` (görüntü boyutu) kullanıyor; "Faz 1 — Görüntü İşleme"; `TrainingPage`'de "LLM" **0 kez** |
| Fine-tune API'si var mı? | ❌ **YOK** | 10 uç → 404 |

> ⚠️ **D-310'a etisi:** "Odin (fine-tuned LLM) EVREN'de eğitilecek"
> varsayımı **hâlâ kanıtsız**. Eğitim altyapısı var ama **görüntü**
> odaklı görünüyor.

---

## 0. Kanıt Yöntemi (genişletilmiş)

İlk tur 3 kaynak taradı. Panel turu **6 kaynağa** çıkarıldı:

| Kaynak | Yöntem | Kapsam |
|---|---|---|
| Frontend JS paketi | 667.083 B, regex | Sayfa metinleri, SSS, menü |
| `/assets/ModelsPage` | 11.233 B | "Eğitilmiş modelleri yönetin" |
| `/assets/UniversePage` | 25.938 B | Keşif Merkezi, model paylaşımı |
| `/assets/TrainingPage` | 6.457 B | "HPC kümesindeki eğitim işlerini yönetin" |
| `/assets/GpuCreditCalculator` | 25.608 B | Fiyat/kapasite hesabı |
| `/assets/BillingPage` | 41.211 B | Kredi yönetimi |
| LLM API + Panel API | 28 uç canlı | Uç doğrulama |



---

## 2. Kanıt 1 — Anahtar kelime taraması (JS paketi)

| Anahtar kelime | Bulunma |
|---|---|
| `fine-tune` | **0 kez** |
| `finetune` / `fine_tune` | **0 kez** |
| `LoRA` / `lora` / `qLoRA` | **0 kez** |
| `adapter` | **0 kez** |
| `peft` | **0 kez** |
| `custom model` | **0 kez** |
| `eğitim API` | **0 kez** |

**`private` kelimesi 9 kez geçiyor ama hiçbiri hizmet değil** — hepsi
C++/C#/JS sözdizimi tanımlayıcı listeleri (`"private","protected","public"`).
Bu, brief'in varsayımının kaynağı olabilir: "private" kelimesi görülüp
"private eğitim" sanılmış.

---

## 3. Kanıt 2 — Canlı API uç taraması

### 3.1 Eğitim uçları — tamamı 404

| Uç | HTTP |
|---|---|
| `GET /fine_tuning/jobs` | 404 |
| `GET /fine-tuning/jobs` | 404 |
| `GET /fine_tune` | 404 |
| `GET /finetune` | 404 |
| `GET /training/jobs` | 404 |
| `GET /jobs` | 404 |
| `GET /train` | 404 |
| `GET /tuning` | 404 |
| `GET /adapters` | 404 |
| `GET /models/fine-tunable` | 404 |

**Hiçbiri yok.**

### 3.2 Var olan uçlar

| Uç | HTTP | Not |
|---|---|---|
| `GET /models` | **200** | 13 model |
| `GET /chat/completions` | 405 | POST gerekir (var) |
| `GET /embeddings` | 405 | POST gerekir (var) |
| `GET /rerank` | 405 | POST gerekir (var) |
| `GET /ocr` | 405 | POST gerekir (var) |
| `GET /audio/transcriptions` | 405 | POST gerekir (var) |
| `GET /responses` | 405 | POST gerekir (var) |

*(405 = yöntem yanlış, uç **var**.)*

### 3.3 Katalog alanları — fine-tune alanı yok

`GET /models` → 13 model. Alan kümesi:

```
capabilities, context_length, created, default_max_output_tokens,
id, modalities, object, owned_by, precision, pricing, task
```

**Fine-tune/egitim/tune içeren alan: YOK.** `task` değerleri
`chat`, `ocr`, `embedding`, `rerank`, `audio` — hepsi çıkarım.

---

## 4. Kanıt 3 — Panel API

| Uç | HTTP |
|---|---|
| `GET /api/v1/llm/finetuning` | 404 |
| `GET /api/v1/llm/training` | 404 |
| `GET /api/v1/llm/jobs` | 404 |
| `GET /api/v1/llm/pricing` | 404 |
| `GET /api/v1/llm/quotas` | 404 |
| `GET /api/v1/gpu` | 404 |
| `GET /api/v1/billing` | 404 |
| **`GET /api/v1/training/jobs`** | **401** ⚠️ |

⚠️ **`/training/jobs` 401 — uç VAR, oturum istiyor.** Eğitim işleri
**panel üzerinden** yürütülüyor. Panel erişimi olmadığımdan içerik
görülemedi.

---

## 5. EVREN'in Gerçek Eğitim Modeli

SSS'ten (`/pricing` sayfası):

> **S: EVREN model eğitimini nasıl çalıştırır?**
> C: Eğitim işleri **Slurm üzerinden Apptainer konteynerleriyle bare-metal HPC
> kümesinde** çalışır. **8 düğüm × 8 H200 GPU, InfiniBand NDR 400G** ağ ile
> bağlıdır. Kullanıcılar kredi (CR) ekonomisi üzerinden GPU saati harcar;
> eğitim metrikleri canlı olarak izlenir.

```
❌ "Modelimi API ile fine-tune et"     → YOK
✅ "Slurm işi başlatayım, H200 kiralamak istiyorum" → VAR
```

| Kapsam | Var mı | Kanıt |
|---|---|---|
| Fine-tuning API'si | ❌ | 10 uç → 404 |
| LoRA/qLoRA servisi | ❌ | JS'te 0 kelime |
| Model deposu | ❌ | Katalog alanı yok |

---

## 6. Fiyatlandırma

### 6.1 Çıkarım — 0.00 CR

`/v1/models` → 13 model, hepsi `prompt_token_price: 0.0`,
`free_until: 2026-11-01`. **LLM çıkarımı 1 Kasım'a kadar ücretsiz.**

### 6.2 Eğitim fiyatı — sayısal değer YOK

Hiçbir yerde katsayı belirtilmiyor. SSS'ten:

> **S: Eğitim maliyeti nasıl hesaplanır?**
> C: Maliyet, **seçilen model mimarisinin saatlik kredi katsayısı ile tahmini
> eğitim süresinin çarpımıdır.** GPU sayısı, düğüm sayısı ve veri kümesi
> boyutu süreyi etkiler. Sistem iş başlamadan bakiyenizi kontrol eder;
> yetersizse iş başlatılmaz ve önceden uyarı verilir.

**Fiyat = `model_mimarisi × saatlik_katsayı × eğitim_süresi`**
Katsayılar panele giriş gerektiriyor → **bu görevde ölçülemedi.**

### 6.3 Kredi kazanma

> Kredi; veri etiketleme görevleri, doğrulama (review), açık veri seti ve
> model paylaşımı ile topluluk katkıları üzerinden kazanılır.

**Kredi satın alınmıyor, katkıyla kazanılıyor** (panelde "Kredi Al"
butonu `/billing` sayfasına gider).

### 6.4 HOLD → SETTLE → RELEASE

| Aşama | Davranış |
|---|---|
| HOLD | Eğitim başlarken kredi bloke edilir |
| SETTLE | İş tamamlanınca kesinleşir |
| RELEASE | Başarısız olursa iade edilir |

---

## 7. Yasal / Teknik Şartlar

| Konu | Bulgu | Kanıt |
|---|---|---|
| LLM trafiği yurt dışına çıkar mı | **Hayır** | SSS: "yurt içindeki kendi bare-metal altyapısında işlenir" |
| Eğitim verisi saklanıyor mu | ⚠️ **Belirtilmemiş** | Silme politikası sayfada yok |
| Model çıktısı kimin mülkü | ⚠️ **Belirtilmemiş** | İfade yok |
| SLA / uptime | ❌ Yok | Şart md. 5: "kesin SLA kapsam dışı" |
| API anahtarı kapsamı | Hesap + org düzeyinde | SSS + `X-Evren-*` başlıkları |

> ⚠️ **Eksikler kritik:** D-248 (KVKK) ve D-310 (iç/müşteri ayrımı) için
> "eğitim verisi eğitim sonrası silinir mi?" ve "fine-tuned model kimin
> mülkü?" sorularının **yazılı cevabı yok.**

### LLM API şartları (zaten kabul edildi)

- Versiyon 1, `is_material: true`, `accepted: true`
- KVKK kapsamında işleme; unutulma hakkı mekanizması mevcut

---

## 8. Veri Limitleri

| Limit | Değer | Kaynak |
|---|---|---|
| Maks. eğitim örneği | **Belirtilmemiş** | — |
| Maks. context (eğitim) | **Belirtilmemiş** | — |
| Model boyutu seçimi | **Belirtilmemiş** | Panel (`/admin/e/architectures`) |
| GPU tipi | NVIDIA H200 | SSS |
| Küme | 8 düğüm × 8 GPU = 64 H200 | SSS + `/infrastructure` |
| Ağ | InfiniBand NDR 400G | SSS |
| İş zamanlayıcı | Slurm + Apptainer | SSS |

---

## 15. DÜZELTME — Önceki Tespit

### 15.1 Ne değişti

| Konu | İlk tespit | Düzeltilmiş |
|---|---|---|
| Eğitim hizmeti | 🔴 "YOK" | 🟡 **VAR** (görüntü odaklı) |
| GPU kiralama | ✅ VAR | ✅ VAR (aynen) |
| LLM fine-tune | ❌ Kanıtlanamadı | ❌ **Hâlâ kanıtlanamadı** |

**Hatanın nedeni:** İlk turda yalnız LLM API'si (`evren-llmapi.ssyz.org.tr`)
ve ana JS paketi tarandı. Panel sayfaları (`/models`, `/training`,
`/universe`, `/billing`) **ayrı chunk dosyaları** olarak yükleniyor —
ana paketteki 667 KB'de bu sayfaların içeriği yok. Bu chunk'lar
taranmadığı için "Eğitilmiş modelleri yönetin" gibi ifadeler görülmedi.

### 15.2 Panel turunda bulunanlar

**Modeller sayfası** (`ModelsPage`, 11.233 B):
```
title: "Modeller"
description: "Eğitilmiş modelleri yönetin"
Boş durum: "Henüz modeliniz yok"
         "Bir eğitim başlatın ya da topluluğun paylaştığı modelleri
          Keşif Merkezi'nde inceleyin."
Butonlar: [Eğitim Başlat]  [Keşif Merkezi]
Filtreler: architecture · modality · visibility · stage
```

**Eğitim sayfası** (`TrainingPage`, 6.457 B):
```
"HPC kümesindeki eğitim işlerini yönetin"
```

**Eğitim yaşam döngüsü** (ana JS, olay invalidation):
```js
"training.started"  → ["training-jobs","training-queue-status",
                      "gpu-status","admin","gpu","billing"]
"training.completed"→ ["training-jobs","training-job", ...,
                      ["models"],["billing"], ...]
"training.stopped"  → ...
"training.deleted"  → ...
"model.created"     → ["models"],["my-stats"],["marketplace"]
```

> ⚠️ **`training.completed` → `["models"]`**: Eğitim tamamlandığında model
> otomatik olarak kaydediliyor. Yani **model üretim akışı var**.

**Keşif Merkezi** (`UniversePage`, 25.938 B): topluluğun paylaştığı
modeller/veri setleri (`marketplace`, `universe` query key'leri).

### 15.3 Neden yine de "Odin için uygun değil"

Eğitim hizmeti var, **ama kapsamı görüntü**:

| Kanıt | Değer |
|---|---|
| GPU Kredi Hesaplayıcı başlığı | **"Faz 1 — Görüntü İşleme"** |
| Hesaplayıcı parametresi | `imgsz` (görüntü çözünürlüğü), `batch`, `epochs` |
| Hesaplayıcı metinleri | "Görüntü Çözünürlüğü", "Throughput Tabanlı Süre Tahmini" |
| Ana JS'te görev izleri | `YOLO` (3), `SAM-2` (4) |
| `TrainingPage`'de "LLM" | **0 kez** |
| Hesaplayıcıda "LoRA"/"fine"/"token" | **0 kez** |

Hesaplayıcı girdileri: `gpu_count`, `item_count`, `epochs`, `imgsz`,
`batch`, `val_period`, `architecture` → **`imgsz` bir görüntü parametresidir**,
LLM'de (token tabanlı) kullanılmaz.

### 15.4 Revize edilmiş karar

| Konu | Değerlendirme |
|---|---|
| Eğitim altyapısı | ✅ Var (64× H200, Slurm) |
| Görüntü modeli (YOLO/SAM-2) eğitimi | ✅ **Kullanılabilir** |
| **LLM (Odin) fine-tuning** | ⚠️ **Panelden doğrulanmalı** — `/admin/e/training_presets` ve `/admin/e/architectures` sayfaları LLM desteği listeliyor olabilir |
| Fine-tune API | ❌ Yok (10 uç 404) |

**Sonraki adım (panele erişim gerekir):** `/admin/e/training_presets`
sayfasında LLM mimarisi/preset varsa Odin eğitimi mümkündür. Erişim
olmadan **kesin hüküm verilemez**.

### 15.5 Bu düzeltme neyi değiştirir

- `ALTYAPI-EVREN-PRIVATE-DOGRULAMA` raporu: 🔴 YOK → 🟡 VAR (görüntü)
- `ALTYAPI-ODIN-DENETIM-RAPORU` (NO-GO) K6 uyarısı: güçleniyor
  ("eğitim ucu yok" → "eğitim ucu **görüntü** için var, LLM için kanıtsız")
- D-310: güncelleme gerekli — "fine-tune edilecek" ifadesi
  "görüntü modeli mi, LLM mi?" sorusuna cevap vermeli

---

## 16. Panel Sayfaları — Güncel Tablo

| Sayfa | HTTP | Boyut | Bulgu |
|---|---|---|---|
| `/models` | 200 | 10.143 B | "Eğitilmiş modelleri yönetin" |
| `/training` | 200 | 10.143 B | "HPC kümesindeki eğitim işlerini yönetin" |
| `/universe` | 200 | 10.143 B | Keşif Merkezi (model/veri paylaşımı) |
| `/billing` | 200 | 10.143 B | Kredi yönetimi (CR/h, GPU) |
| `/guide` | 200 | 10.143 B | Rehber |

*(HTML boyutları aynı — hepsi SPA kabuğu; içerik JS chunk'larında.)*

### Erişim gerektiren (401 ötesi) sayfalar

| Sayfa | Kanıt |
|---|---|
| `/admin/e/training_presets` | "Eğitim Ön Ayarları" menü girdisi |
| `/admin/e/architectures` | "Model Mimarileri" menü girdisi |
| `/admin/e/training_cost_factors` | "Maliyet Faktörleri" menü girdisi |
| `/admin/e/gpu_partitions` | "GPU Bölümleri" menü girdisi |
| `/admin/e/org_plans` | "Org Planları" — kurum planı/limitleri |
| `/admin/llm/pricing` | LLM fiyatlandırma (CR/token) |
| `/admin/llm/registry` | LLM Model Registry |
| `/admin/llm/routing` | Otomatik yönlendirme |
| `/admin/llm/kvkk` | KVKK/Retention politikası |
| `/admin/llm/corpus` | Korpus incelemesi (KVKK-hassas) |

> Bu sayfalar **kanonik kaynak** olabilir; LLM eğitim desteği
> `/admin/e/training_presets` ve `/admin/e/architectures` içinde aranmalı.

| Çıkarım context | Model bazlı, en yüksek 1M | `/v1/models` |

**Brief'in "minimum 500 örnek" varsayımı hiçbir yerde geçmiyor.**

---

## 9. Huginn (Odin) İçin Değerlendirme

### 9.1 Kısa cevap: **Doğrudan EVREN = uygun değil**

| Sorun | Açıklama |
|---|---|
| Fine-tune API yok | Kendi LoRA script'ini yazıp Slurm işi sunmak gerekir |
| Eğitim ortamı yok | PyTorch/transformers/peft kurulumu kullanıcıda |
| Veri limiti belirsiz | Ne kadar veri/token — yazılı yok |

---

## 11. Kesin Cevaplar (brief'in soruları)

| Soru | Cevap |
|---|---|
| Private eğitim hizmeti? | 🔴 **YOK** (10 uç 404 + JS 0 kelime) |
| Fiyatlandırma? | Çıkarım **0.00 CR** (1 Kasım'a kadar). Eğitim: **sayısal yok** |
| Trial var mı? | Yok; ücretsiz dönem genel |
| 2026-11-01 sonrası? | Belirtilmemiş |
| Maks. eğitim örneği? | **Belirtilmemiş** |
| Maks. context? | **Belirtilmemiş** |
| Model boyutu? | **Belirtilmemiş** (panel) |
| Hardware/ETA? | 64× H200, Slurm+Apptainer |
| Model çıktısı kimin? | ⚠️ **Belirtilmemiş** |
| Veri silinir mi? | ⚠️ **Belirtilmemiş** |
| SLA? | ❌ Yok (şart md. 5) |
| Huginn için uygun mu? | ⚠️ **Kısmen** — çıkarım EVET, eğitim HAYIR |

---

## 12. Doğrulama Eksikleri (panel erişimi gerekir)

| # | Doğrulanamayan | Nasıl |
|---|---|---|
| V1 | Saatlik kredi katsayıları | Panel → Eğitim İşleri |
| V2 | Eğitim veri limiti | Panel → Eğitim İşleri → form |
| V3 | Model mülkiyeti (yasal) | **Resmî e-posta** |
| V4 | Veri silme politikası | **Resmî e-posta** |

> **YASU denetim notu:** Brief'in *"bulguların temeli sayfa fotoğrafı /
> kayıt / resmî email teyidiyle doğrulanmıştır"* maddesi **kısmen
> karşılandı** — sayfa + canlı API teyit edildi, resmî e-posta alınamadı.
> V3 ve V4 hukuki konular; panel açıklaması yeterli kanıt değildir.

---

## 13. Tavsiye

| Karar | Gerekçe |
|---|---|
| EVREN çıkarımına **devam** | Ücretsiz, yurt içi, KVKK kontrollü |
| Fine-tune için EVREN'e **bağımlı olma** | API yok, limit/mülkiyet belirsiz |
| Eğitim için **kendi altyapını kur** (veya GPU kirala) | Tam kontrol, KVKK uyum |
| Panel erişimi al → V1-V2 ölç | Bütçe planlaması için |
| Resmî e-postaya V3-V4 sor | Hukuki risk yazılı cevap istiyor |

---

## 14. Kanıt Dizini

| Kanıt | Konum |
|---|---|
| Bu rapor | `docs/EVREN_PRIVATE_EGITIM_DOGRULAMA.md` |
| Uç tarama scripti | `scripts/evren_egitim_uc_taramasi.py` |
| Sayfa JS'i | `https://evren.ssyz.org.tr/assets/index-BZQjHWD4.js` (667.083 B) |
| SSS kaynağı | JS `li` nesnesi (`/pricing`) |
| Şart metni | `GET /v1/terms/text` (3.500 krkt) |
| LLM katalog | `GET /v1/models` (13 model) |
| İlgili rapor | `data/orchestrator/ALTYAPI-ODIN-DENETIM-RAPORU_2026-10-31_denetim.md` |

**Erişim:** 2026-10-01, anahtar `evren_llm_...D70M`

---

*yasu · araştırma/denetim · 2026-10-01 · D-260 kanıt temelli*

| Veri sahipliği belirsiz | Model mülkiyeti, veri silme yazılı değil |
| Maliyet belirsiz | Saatlik kredi katsayısı panele bağlı |

### 9.2 Ama şu mümkün

| Yol | Durum |
|---|---|
| **Çıkarım** (Huginn için) | ✅ **1 Kasım'a kadar ücretsiz** — 13 model |
| **GPU kiralaması** | ✅ Var (krediyle) — kendi eğitim kodunla |
| **Kredi kazanma** | Veri etiketleme + model paylaşımı |

### 9.3 Önerilen yol

```
1. Kredi biriktir (etiketleme katkısıyla)
2. Huginn'da kendi LoRA eğitim scriptini yaz
3. Slurm işi olarak H200 kirala
4. Eğitilen modeli yerelde çalıştır (tam KVKK kontrolü)
5. EVREN çıkarım API'sini yedek/fallback olarak kullan
```

**Bu yol D-310'un iç/müşteri ayrımını da korur** — model Huginn'de,
veri dışarı çıkmaz.

---

## 10. Riskler

| # | Risk | Derece | Açıklama |
|---|---|---|---|
| R1 | **Veri sahipliği belirsiz** | 🔴 | Fine-tuned model kimin mülkü? Yazılı cevap yok |
| R2 | **Veri silme politikası yok** | 🔴 | Eğitim verisi tutuluyor mu? KVKK riski |
| R3 | Maliyet belirsiz | 🟡 | Saatlik katsayı panele bağlı |
| R4 | SLA yok | 🟡 | "Kesin SLA kapsam dışı" (şart md. 5) |
| R5 | Kredi yetersizse iş başlamaz | 🟡 | Önceden uyarı, iade |
| R6 | 1 Kasım sonrası çıkarım ücretli | 🟡 | `free_until: 2026-11-01` |
| R7 | `deepseek-v4-flash` kaldırılacak | 🟢 | `v4.1-flash` ile değişecek |

| **GPU kiralaması (Slurm + H200)** | ✅ | SSS + `/admin/gpu` |
| Eğitim iş takibi (`/training/jobs`) | ✅ | 401 (panel) |
| Eğitim ön ayarları | ✅ | `/admin/e/training_presets` |
| GPU bölümleri | ✅ | `/admin/e/gpu_partitions` |

---

## 6. Panel Ekran Kanıtı — 401'in arkasında ne var (2026-10-01, Ürün Sahibi oturumu)

Ürün Sahibi panele girip ATÖLYE → Eğitim ekranını paylaştı. `401`'in
arkasındaki içerik böylece **ölçüldü** (D-260: ekran kanıttır, 401 değil).

| Ölçülen | Değer |
|---|---|
| Eğitim konsolu | **VAR** — "HPC kümesindeki eğitim işlerini yönetin" |
| Müsait GPU | **6 / 64** |
| Kredi | **1.020 CR** |
| Mevcut iş | 0 |
| Ön koşul | *"Henüz projeniz yok. Eğitim bir proje üzerinden yürütülür."* |

**"Eğitim Başlat" modalındaki görev tipleri — tamamı görü:**
Nesne Tespiti · Segmentasyon · Sınıflandırma · Poz Tahmini · Döndürülmüş Kutu

**Model aileleri:** YOLO26, YOLO11, YOLOv10, YOLOv9, YOLOv8, RT-DETR.
Çalışma adı placeholder'ı: `ör. yolo26m-deneme-3`.

### Sonuç: rapor doğrulandı, kapsamı netleşti

```
Bölüm 1-5 iddiası:   "LLM fine-tune ucu yok"             -> DOGRU
Ekran kanıtı ekler:  "eğitim konsolu var, ama görü için" -> YENI
Birleşik gerçek:     EVREN eğitim = YOLO/RT-DETR görü modelleri.
                     Odin (metin/LLM) bu konsoldan eğitilemez.
```

**Kalan tek belirsizlik:** Model Ailesi listesi ekranda RT-DETR'den sonra
kesik; proje açılmadan Veri Seti/Versiyon alanları kilitli. Ama 5 görü
görev tipi + 6 görü model ailesi + `yolo26m` placeholder + 16 API ucunun
404'ü aynı yöne işaret ediyor.

**Ucuz kapatma yolu:** panelden boş proje aç (0 CR), modalı tekrar aç,
Model Ailesi listesini sonuna kadar kaydır. 5 dakika.

---

## 7. "Yeni Veri Seti" ekranı — belirsizlik KAPANDI (2026-10-01)

Ürün Sahibi `evren.ssyz.org.tr/datasets` → **Yeni Veri Seti** modalını paylaştı.
Eğitim zincirinin ilk halkası burası; hangi veri tipinin kabul edildiğini
**veri seti katmanı** belirler, model katmanı değil.

| Veri Tipi | Durum | Okuma |
|---|---|---|
| **Görsel** | ✅ seçili/aktif | kabul: avi, avif, bmp, gif, heic, heif, jpeg, jpg, mkv, mov, mp4, png, svg, tif, tiff, webm, webp |
| **Medikal** | ✅ aktif | DICOM vb. görü türevi |
| Ses | ⬜ **soluk / tıklanamaz** | planlı, açık değil |
| **Metin** | ⬜ **soluk / tıklanamaz** | **LLM yolu burada ve KAPALI** |
| Çoklu | ⬜ **soluk / tıklanamaz** | planlı, açık değil |

### Bu ne anlama geliyor

```
"Metin" sekmesi YOK olsaydı  -> EVREN LLM egitimini hic dusunmemis demekti
"Metin" sekmesi VAR ama SOLUK -> yol haritasinda, HENUZ ACILMAMIS
```

Yani fark şu: **imkânsız değil, henüz açık değil.** Beklemenin bir adresi
var; "hiç olmayacak" demek yanlış olur.

### Nihai kapanış

| Soru | Cevap | Kanıt |
|---|---|---|
| EVREN'de eğitim altyapısı var mı? | **Evet** | Eğitim konsolu, 6/64 GPU, 1.020 CR |
| LLM/metin eğitilebilir mi? | **Hayır, bugün** | Metin veri tipi pasif |
| Bu bir panel ayarı mı? | **Hayır** | Sekme ürün tarafında kapalı, hesap tarafında değil |
| Gelecekte açılır mı? | **Muhtemel** | Sekme yer tutuyor = yol haritasında |
| Odin 31 günde EVREN'de eğitilir mi? | **Hayır** | Tek yol: açılma tarihini EVREN'e sormak |

**D-310 düzeltmesi:** "ücretsiz dönemde EVREN'de fine-tune ederiz" varsayımı
**çürütüldü**. Yerine: (a) EVREN'e Metin sekmesinin açılma tarihi sorulur,
(b) bu arada Odin **prompt + RAG** ile kurulur (eğitim gerektirmez),
(c) gerçek fine-tune ihtiyacı kanıtlanırsa yerel/başka sağlayıcı değerlendirilir.
