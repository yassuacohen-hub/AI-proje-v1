# API Plan Araştırması — 2026-09-17

> Sahip emri: "Groq 403 plan kapalı, hesapta plan aç (para gerekmez, free katman var) NASIL YAPILIR /
> 9Router bakım planı yapalım / bunları araştırmaya kaydet / 2 tur yapalım".
> Tur 1 = Groq plan açma + Bazarlink + `.env` düzeltme. Tur 2 = 9Router + Perplexity + Together/xAI kararı.

## 0) Tur 1 sonucu (tamamlandı)

| İş | Durum |
|----|-------|
| `GROQ_BASE_URL=https://groq.com` → `https://api.groq.com/openai/v1` | düzeltildi |
| `.env.example`: `BAZARLINK_URL` → `BAZARLINK_API_URL` | hizalandı |
| `scripts/api_anahtar_testi.py`: `bazarlink` sağlayıcısı eklendi | eklendi |
| KIMI yeni anahtar testi | **AKTİF** (401 → 200) |
| OPENROUTER yinelenen satır | sahip sildi, tek satır, **AKTİF** ($10.15 kullanım · limit YOK) |
| Groq plan hipotezi | **ELENDİ** — sahip ekranı: Free zaten "Current Plan" (§1) |
| BazaarLink claim yolu | **ÖLÜ** — agent self-kaydı 2026-09-05'te kapandı (410), eski anahtarlar iptal (§3) |

Son tablo: **AKTIF=14 · OLU=6** (groq, together, xai, perplexity, 9router, bazarlink).

---

## 1) Groq — 403 tanısı

**Sahip ekran doğrulaması (2026-09-17):** Groq Console → Billing → Plans ekranında
**Free planı zaten "Current Plan"**. Org = `Personal`, proje = `Default Project`.
Yani **403 plan kapalı olduğu için değil.** İlk hipotez (plan açma) elendi.

Geriye kalan üç olası neden, kontrol sırasıyla:

### A) Model Terms kabul edilmemiş (en olası)
Sol menü → **Model Terms**. Groq'ta Llama/Mixtral gibi modellerin lisans şartları
ayrıca kabul edilir. Kabul edilmemişse model erişimi kapalı kalır ve 403 döner.
Listedeki tüm model ailelerini **Accept** et, sonra tekrar test et.

### B) Anahtar başka projeye/org'a ait
Sol menü → **API Keys**. Anahtarın (`…12QC`) hangi projede listelendiğine bak.
Groq artık proje bazlı anahtar veriyor; `Default Project` dışında bir projede üretilmiş
anahtar, o projenin izinleri kapalıysa 403 verir.
Çözüm: `Default Project` seçiliyken **Create API Key** ile yeni anahtar üret,
eskisini sil, yeniyi `.env` içindeki `GROQ_API_KEY=` satırına yaz.

### C) Data Controls / bölge kısıtı
Sol menü → **Data Controls**. Bölge ya da veri paylaşımı kısıtı açıksa istek reddedilir.
Ayrıca VPN açıksa çıkış IP'si desteklenmeyen bir ülkeye düşüyor olabilir —
**VPN'i kapatıp tekrar test et** (403 bir anda 200'e dönerse neden budur).

### Doğrulama
Her adımdan sonra: `python scripts/api_anahtar_testi.py` → `groq` satırı `AKTIF HTTP 200`.
`GROQ_BASE_URL` **`https://api.groq.com/openai/v1`** olmalı (`https://groq.com` yanlıştı, düzeltildi).

### Kod okuma tablosu

| Belirti | Anlamı | Aksiyon |
|---------|--------|---------|
| 403, tüm modeller | Model Terms kabulsüz ya da proje izni yok | A → B |
| 403 sadece VPN açıkken | bölge kısıtı | C |
| 401 | anahtar iptal/yanlış kopyalanmış | B (yeni anahtar) |
| 429 | erişim açık, dakika kotası dolu | bekle (anahtar sağlam) |

**Not (ekranda görüldü):** *"Developer tier upgrades are temporarily unavailable due to high demand."*
Yani Groq şu an ücretli katmana geçişi kapatmış. Free dışında seçenek zaten yok —
para yükleyerek 403'ü aşmak mümkün değil, sorun hesap ayarında.

Free katman notu: dakikalık istek/token sınırı vardır, ücret yoktur. Hacimli iş için
ücretsiz öncelik zinciri geçerli: OpenRouter `:free` → Ollama (yerel) → NVIDIA NIM → Groq free.

---

## 2) 9Router bakım planı

Durum: `NINEROUTER_KEY` (…5a44) + `NINEROUTER_URL` → `{URL}/v1/models` **HTTP 403**.
Continue IDE testinde de 9Router çalışmıyordu (sahip testi 2026-09-17).

### 2.1 Tanı sırası (sırayla, ilk başarısız olan kök nedendir)

1. **URL doğru mu?** `.env`'deki `NINEROUTER_URL` sonunda `/v1` varsa test scripti bunu
   kırpıyor (`removesuffix("/v1")`), yani hem `https://host` hem `https://host/v1` kabul.
   Host yanlışsa 404/DNS hatası gelir — 403 geldiğine göre host ayakta.
2. **Anahtar başlığı doğru mu?** 9Router bazı kurulumlarda `Authorization: Bearer` yerine
   `X-Api-Key` bekler. 403 + ayakta host = en olası neden budur.
3. **Anahtar aktif mi?** 9Router panelinde anahtarın `enabled` ve son kullanım tarihi.
4. **Model izni var mı?** 9Router'da anahtar başına model allowlist bulunur; boş liste 403 verir.
5. **IP/origin kısıtı var mı?** Panelde IP allowlist tanımlıysa ve VPN açıksa 403 gelir.
   VPN'i kapatıp tekrar test et (VPN kuralı: kritik işlemde kapatmadan önce sahibe sor).

### 2.2 Bakım adımları (kalıcı)

| Periyot | İş | Komut / yer |
|---------|----|-------------|
| Haftalık | Tüm anahtar canlılık testi | `python scripts/api_anahtar_testi.py` |
| Haftalık | 9Router maliyet/latency özeti | `web_dashboard/tabs/admin_performance.py` → `load_ai_cost_per_call()` |
| Anahtar değişiminde | `.env` + `.env.example` + `docs/API_ANAHTARLARI.md` üçünü birlikte güncelle | — |
| 403/401 görülünce | Yukarıdaki tanı sırasını uygula, sonucu bu dosyaya not düş | — |
| Aylık | Ölü anahtarları `# OLU_<tarih>` ile yorum satırına al, panelden iptal et | `.env` |

### 2.3 Karar

9Router **zorunlu değil**: OpenRouter aynı işi yapıyor ve AKTİF (limit yok, free katman).
9Router'ı ayağa kaldırmak için gereken tek şey panel erişimi — sahip panele girmedikçe
403 çözülemez. Öneri: 9Router'ı **yedek gateway** statüsünde bırak, birincil OpenRouter kalsın.
Panel erişimi olunca 2.1 tanı sırası 10 dakikada sonuçlanır.

---

## 3) BazaarLink — agent self-kaydı kapatıldı (claim yolu ölü)

> **GÜNCELLEME 2026-09-17 (2. tur):** Sahip panelden **yeni anahtar üretti** (son4 `…OteD`).
> Sonuç **değişmedi: 403 YASAK**. Yani sorun anahtarın kendisi değil, hesabın yetkisi.
> Kalan iki olasılık: (a) **kredi bakiyesi 0**, (b) hesap hâlâ **agent kaynaklı/organizasyon izni yok**.
> **Sahip kararı: ertelendi** — bloke iş yok, sonra bakılacak.

Durum: `BAZARLINK_API_KEY` (…iwa0) + `BAZARLINK_API_URL=https://api.bazaarlink.ai/v1` → **403**.

> Marka yazımı: panel **BazaarLink** (çift "a"), API hostu `api.bazaarlink.ai` (tek "a").
> `.env` değişken adı `BAZARLINK_*` olarak kalıyor — değiştirme, kod bu ada bakıyor.

> **TERİM DÜZELTMESİ (roo hatası):** Önceki sürümde geçen "temsilci botu" ifadesi **yanlıştı**;
> panelde öyle bir şey yok. Panelin Türkçesi makine çevirisi: **"Hasar Temsilcisi" = "Claim Agent"**,
> **"İddia" düğmesi = "Claim"**. Orası bir bot değil, **token kırma kutusu**.

### Kesin teşhis — sitenin kendi duyurusundan (2026-09-09, `bazaarlink.ai` ana sayfa)

Orijinal (Çince) özeti:
- **2026-09-05'ten beri** AI agent self-servis kayıt uç noktası `/api/v1/agents/register` → **410 Gone**.
- O uç noktanın otomatik dağıttığı **tüm agent anahtarları iptal edildi**.
- Bu anahtarlarla `/api/v1/models` ya da başka uç nokta çağrılırsa → **401**.
- Gerekçe: ücretsiz katmanın toplu otomatik kayıtla suistimali.
- **Resmî çözüm:** *"Normal yolla BazaarLink hesabı aç, panelden API anahtarı üret."*
- Eski `/claim` bağlantıları **yalnız henüz claim edilmemiş hesaplar** için geçerli.

Ek doğrulamalar (aynı tarama):
- `https://bazaarlink.ai/claim` (token'sız) → **"Invalid Claim Link — This claim link is invalid or has expired."**
- `https://docs.bazaarlink.ai/` → DNS'te yok; docs `bazaarlink.ai/docs` altında.
- Docs'ta **免費模型 (ücretsiz modeller)** ve **從 OpenRouter 遷移 (OpenRouter'dan göç)** bölümleri var.
- Ajan için hazır tanıtım dosyası: `https://bazaarlink.ai/skill.md`.
- Şirket: Tayvan, 集聯科技有限公司. 195 model (qwen 52, openai 39, google 27, anthropic 15, deepseek 15…).

**Sonuç:** Elimizdeki `BAZARLINK_API_KEY` büyük olasılıkla **iptal edilmiş agent anahtarı**.
Claim ile kurtarılamaz — claim yolunun kendisi kapandı.

### KAHİN (Ürün Sahibi) için adımlar (tek geçerli yol)

1. `https://bazaarlink.ai` → **Sign in / Kayıt ol** (normal e-posta hesabı; agent kaydı değil).
2. Panel → **API Anahtarları** → **Yeni anahtar üret** (`sk-bl-…`).
3. `.env` içindeki `BAZARLINK_API_KEY=` satırını yeni değerle değiştir.
4. Doğrulama: `python scripts/api_anahtar_testi.py bazarlink` → `AKTIF HTTP 200`.
5. Kalırsa: **Krediler** menüsünden ücretsiz katman bakiyesini kontrol et.

> **roo bu adımı senin yerine yapamaz:** hesap açma e-posta doğrulaması istiyor ve
> self-servis agent kaydı 410 ile kapalı. Anahtar sahibin hesabından üretilmek zorunda.

### Yeni anahtarla hâlâ hata varsa

| Kod | Anlamı | Aksiyon |
|-----|--------|---------|
| 401 | anahtar iptal / eski agent anahtarı | Panelden **yeni** anahtar üret |
| 403 | kredi 0 ya da org izni yok | **Krediler** + **Organizasyonlar** menüleri |
| 410 | agent register uç noktası (kapalı) | Bu yolu kullanma; normal hesap anahtarı kullan |
| 429 | devre kesici tetiklendi | **Ayarlamak** ile eşiği yükselt (şu an Engelli, beklenmez) |

**Öncelik: düşük.** BazaarLink olmadan hiçbir iş bloke değil; 14 aktif sağlayıcı var ve
**OpenRouter zaten çalışıyor**. OpenAI-uyumlu olduğu için anahtar gelirse `base_url` ile anında devreye girer.

---

## 4) Tur 2 — kalan işler

| # | İş | Not |
|---|----|-----|
| 1 | Perplexity **400** | Anahtar suçlu değil; `/chat/completions` gövdesi ya da model adı (`sonar`) reddediliyor. Test isteğini modele dokunmayan bir endpoint'e taşımak gerekir; Perplexity'de `/models` yok, bu yüzden 400 "anahtar sağlam" kabul edilebilir. Düşük öncelik. |
| 2 | Together **403** | Free katman yok; hesapta ödeme yöntemi ister. **Sahip kararı gerekiyor.** |
| 3 | xAI **403** | Aynı: kredi/ödeme gerekiyor. **Sahip kararı gerekiyor.** |
| 4 | 9Router **403** | Panel erişimi bekliyor (§2.1). |
| 5 | BazaarLink **403** | Sahibin normal hesap açıp panelden anahtar üretmesi bekleniyor (§3). |
| 6 | Groq **403** | Model Terms / proje izni / VPN kontrolü bekliyor (§1 A-B-C). |

**İhtiyaç sıralaması:** Together ve xAI olmadan da 14 aktif sağlayıcı var; ikisi de
para gerektiriyor ve karşılığında OpenRouter üzerinden erişilebilen modelleri veriyor.
Öneri: **ikisine de para yüklenmesin**, OpenRouter tek ödeme noktası kalsın.

---

## 5) GÜVENLİK — rotate edilmesi gereken anahtarlar

Aşağıdaki anahtarların **tam değerleri** terminal çıktısına düştü (envanter çalışması sırasında
`findstr` ile ham `.env` okuması yapıldı). Hepsi değiştirilmelidir:

1. `DEEPSEEK_KEY`
2. `OPENROUTER_API_KEY`
3. `KIMI_API_KEY`
4. `BAZARLINK_API_KEY`
5. `GROQ_API_KEY`

Kural (bundan sonra): `.env` içeriği ham olarak terminale **basılmaz**. Değer görmek gerekiyorsa
`scripts/api_anahtar_testi.py` kullanılır — yalnız son 4 karakteri gösterir.
