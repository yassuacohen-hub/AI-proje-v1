# Odin Deployment Mimarisi — İç/Müşteri Endpoint Ayrımı (D-310 Kural 1)

Bu dosya **kural gövdesi taşımaz** (D-211/D-220). Tek kaynak: `AGENTS.md` → **D-310**.
Burada sadece D-310 Kural 1'in sistem tarafında nasıl çalıştığı (somut endpoint/env/compose) yazılır.

## İki endpoint, tek kod tabanı (DRY — brief kuralı)

| | İç (🟢) | Müşteri (🟡) |
|---|---|---|
| Servis adı | `odin-internal` | `odin-customer` |
| Port | 5000 (iç ağ, dışa açılmaz) | 5001 (API gateway arkasında) |
| Auth anahtarı | `ODIN_INTERNAL_KEY` | `ODIN_CUSTOMER_KEY` |
| Veri görüşü | `company_master` tam erişim | `müşteri_id` filtreli DB view |
| `HUGINN_INTERNAL_DATA` erişimi | var | **yok** (env'de tanımsız) |
| Çıkış kapısı | yok (zaten iç) | `maskeleme_odin(metin, hedef="musteri")` **+ ölçüm kapısı** `odin_kapi_olcumu` / `odin_k4_gecerli_mi` (aşağıda) |

İki servis **aynı Python paketinden** (`src/company_master/odin_ai/`) deploy edilir; farkları sadece
başlatma env'i ve auth anahtarıdır — ayrı proje/ayrı repo YOK (brief Kural: "ayrı projeler değil").

## Docker Compose iskeleti (taslak)

```yaml
services:
  odin-internal:
    build: .
    command: python -m company_master.odin_ai.serve --role internal
    environment:
      - ODIN_INTERNAL_KEY=${ODIN_INTERNAL_KEY}
      - HUGINN_INTERNAL_DATA=${HUGINN_INTERNAL_DATA}
    ports: ["127.0.0.1:5000:5000"]
    networks: [internal_net]        # dışa açılmazlık AĞ katmanında, publish ile değil

  odin-customer:
    build: .
    command: python -m company_master.odin_ai.serve --role customer
    environment:
      - ODIN_CUSTOMER_KEY=${ODIN_CUSTOMER_KEY}
      # HUGINN_INTERNAL_DATA burada YOK — fiziksel sınır (D-310 Kural 1)
    ports: ["5001:5001"]
    networks: [public_net]
```

**Port notu (ölçülmüş çelişki düzeltmesi):** `ports: ["5000:5000"]` konteyneri **host'a
publish eder** — bu, "dışa açılmaz" demek değildir. Taslakta bu yüzden loopback'e
bağlandı (`127.0.0.1:5000:5000`). Gerçek koruma iki katmanlıdır ve ikisi de üretimde
yapılandırılmalıdır: (1) `internal_net` ağı dışarıya çıkmayan bir ağ olmalı, (2) host
firewall'ı 5000'i reddetmeli. **Tek başına publish etmemek yetmez** — yorum satırı
kapı sanılıyordu.

`company_master.odin_ai.serve` henüz yazılmadı — bu, eğitim pipeline görevinin (`ALTYAPI-ODIN-EGITIM-PIPELINE`,
utku, 2026-10-21) çıktısıdır. Bu belge sadece **nereye** deploy edileceğini önceden sabitler.

## Secrets yönetimi

- `ODIN_INTERNAL_KEY`, `ODIN_CUSTOMER_KEY`, `HUGINN_INTERNAL_DATA` → `.env` (git'e girmez, `.gitignore`'da zaten var).
- Üretimde: ortam değişkeni enjeksiyonu (platform secrets store), dosyaya yazılmaz.

## Çıkış akışı ve kapının üç katmanı

```
iç model çıktısı → maskeleme_odin(metin, hedef="musteri") → ÖLÇÜM → müşteri endpoint yanıtı
```

| Katman | Ne yapar | Nerede (ölçülmüş) | Durum |
|---|---|---|---|
| 1 · Fiziksel | Müşteri konteynerine `HUGINN_INTERNAL_DATA` verilmez | compose taslağı (aşağıda) | ✅ tanımlı |
| 2 · Metin maskesi | Yasak desenleri `ODIN_RED_METNI` ile değiştirir | `sunum.py:281` `maskeleme_odin()` | ⚠️ **denylist'tir, bağlı sır *değerini* bırakır** — `ODIN_INTERNAL_KEY=xyz` → `[İÇ VERİ — PAYLAŞILAMAZ]=xyz` |
| 3 · Ölçüm (**asıl kapı**) | Dört durum: `kacak` · `maskelendi` · `inceleme` · `temiz` | `sunum.py:342` `odin_kapi_olcumu()`, `sunum.py:373` `odin_kapi_denetle()`, `sunum.py:390` `odin_k4_gecerli_mi()` | ✅ tek uygulama (D-211 ikiz yasağı) |

**Katman 2 tek başına kapı sayılmaz.** K4 yeşili için: `kacak` = 0 **ve** çözülmemiş
`inceleme` = 0 — ikisini de `odin_k4_gecerli_mi()` sayar. Katman 2 yalnızca katman 3'ün
ölçtüğü metni *üretir*; kararı katman 3 verir. Katman 2, kalıntı bırırsa sonuç
`inceleme`'ye düşer — **otomatik yeşil üretilmez** (`sunum.py:333` `_KALAN_SIR`).

**K3 ayrı ölçümdür** (D-310 Kural 6): ≥ 8/10 senaryoda gerçek ret. Sırı temizlemek
ret sayılmaz; 10/10 `maskelendi` K4 için yeşil, K3 için kırmızı olabilir.

**V3 (müşteri endpoint) kapısı bugün kodda yoktur.** `maskeleme_odin()` imzası
`(metin, hedef="musteri")` — **`kaynak` parametresi yoktur**; V1/V2/V3 ayrımı kodda
uygulanmaz. Bu yüzden bu belge müşteri endpoint'i için V3 maskesinin *var olduğunu*
söylemez. V3 kapısının yazılması `ALTYAPI-ODIN-MASKE-V3-01` görevidir; o görev
bitmeden "çıkış kapısı uygulanıyor" denemez.

Kod: [`src/company_master/sunum.py:281`](Huginn Data Insights/src/company_master/sunum.py:281)
(maske) · `:342` (ölçüm) · `:390` (K4 kapısı) — senaryo ve ölçüm sözleşmesi için
bkz. `ODIN_PROMPT_INJECTION_SCENARIOS.md`.

## Ilgili Nodlar

- [[AGENTS.md:D-310]] · [[ODIN_GUVENLIK_ATIF]] · [[ODIN_PROMPT_INJECTION_SCENARIOS]] · [[ODIN_SECURITY_CHECKLIST]]
