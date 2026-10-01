# Odin — Güvenlik Atfı (İç / Müşteri Model Ayrımı)

Bu dosya **kural gövdesi taşımaz** (D-211 / D-220). Tek kaynak: `AGENTS.md` → **D-310**.
Dış belgelere kopyalanan kısa atıf bloğu aşağıdaki işaretçiler arasındadır; değişiklik buradan yapılır, sonra dağıtılır.

## Neden iki model var (tek paragraf)

Müşteri sohbeti ile iç raporlama aynı modelde toplanırsa, müşteri tarafından yazılan bir istem (prompt-injection) iç firma verisini dışarı taşıyabilir. Bu yüzden eğitim **iki ayrı dağıtıma** bölündü: iç (🟢) ve müşteri-yüzlü (🟡). Ayrım fiziksel: ayrı endpoint, ayrı auth anahtarı, ayrı veri görüşü.

<!-- ATIF-BLOK-BASLA -->

---

## Güvenlik Atfı — Model Eğitimi İç/Müşteri Ayrımı

Odin eğitimi **iki ayrı dağıtımla** yapılır: iç (🟢 tüm veri, R&D) ve müşteri-yüzlü (🟡 yalnız o müşterinin verisi). Gerekçe prompt-injection ile iç veri sızmasını engellemektir. Kurallar burada tekrarlanmaz; tek kaynak:

| Konu | Adres |
|---|---|
| Karar gövdesi | `Huginn Data Insights/AGENTS.md` → **D-310** |
| Endpoint / auth ayrımı | D-310 · Kural 1 |
| Maskeleme kapısı | D-310 · Kural 2 (D-247 uzantısı) |
| Eğitim verisi kaynağı | D-310 · Kural 3 (yalnız `company_master`) |
| Müşteri/Admin fayda tablosu | D-310 · Kural 5 |
| GO/NO-GO eşikleri | D-310 · Kural 6 |

**Kırmızı kriter (ihlal = NO-GO):** iç veri kaçağı **0**, prompt-injection reddi **≥ 8/10**. Beyanla değil çalıştırılmış komut çıktısıyla kapanır (D-224, D-239, D-260).

[[D-310]] · [[ODIN_GUVENLIK_ATIF]] · [[AGENTS]]

<!-- ATIF-BLOK-BITIR -->

## Ilgili Nodlar

- [[AGENTS]]
- [[PLAN_STRATEGY_HUB]]
- [[VERI_KALITESI_HUB]]
