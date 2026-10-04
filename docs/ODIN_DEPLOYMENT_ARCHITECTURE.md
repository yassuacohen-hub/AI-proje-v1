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
| Çıkış kapısı | yok (zaten iç) | `maskeleme_odin(metin, hedef="musteri")` zorunlu |

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
    ports: ["5000:5000"]
    networks: [internal_net]        # dışa açılmaz

  odin-customer:
    build: .
    command: python -m company_master.odin_ai.serve --role customer
    environment:
      - ODIN_CUSTOMER_KEY=${ODIN_CUSTOMER_KEY}
      # HUGINN_INTERNAL_DATA burada YOK — fiziksel sınır (D-310 Kural 1)
    ports: ["5001:5001"]
    networks: [public_net]
```

`company_master.odin_ai.serve` henüz yazılmadı — bu, eğitim pipeline görevinin (`ALTYAPI-ODIN-EGITIM-PIPELINE`,
utku, 2026-10-21) çıktısıdır. Bu belge sadece **nereye** deploy edileceğini önceden sabitler.

## Secrets yönetimi

- `ODIN_INTERNAL_KEY`, `ODIN_CUSTOMER_KEY`, `HUGINN_INTERNAL_DATA` → `.env` (git'e girmez, `.gitignore`'da zaten var).
- Üretimde: ortam değişkeni enjeksiyonu (platform secrets store), dosyaya yazılmaz.

## Çıkış akışı (maskeleme kapısı zaten kodda — D-310 Kural 2)

```
iç model çıktısı → maskeleme_odin(metin, hedef="musteri") → müşteri endpoint yanıtı
```

Kod: [`src/company_master/sunum.py:281`](Huginn Data Insights/src/company_master/sunum.py:281) — zaten uygulanmış, test için bkz. `ODIN_PROMPT_INJECTION_SCENARIOS.md`.

## Ilgili Nodlar

- [[AGENTS.md:D-310]] · [[ODIN_GUVENLIK_ATIF]] · [[ODIN_PROMPT_INJECTION_SCENARIOS]] · [[ODIN_SECURITY_CHECKLIST]]
