# ALTYAPI-ODIN-DENETIM-RAPORU — Brief (yasu)

**Başlık:** [ALTYAPI] Odin üretim öncesi GO/NO-GO kararını denetle → ALTYAPI-ODIN-DENETIM-RAPORU_2026-10-31_denetim.md (10d)
**Öncelik:** P1 · **Kit:** `DENETIM` (AGENTS.md D-196)
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır.

## Neden

Odin modelinin eğitimi bitmiş (ALTYAPI-ODIN-EGITIM-PIPELINE), security test'leri yapılmış (TEST-ODIN-PROMPT-INJECTION), kalite metrikleri ölçülmüş. Ama produksiyona geçmeden önce **bütün çıktıları bir denetim kaynağında toplayan ve risk değerlendirmesi yapan** bir rapor yazılmalı. Bu rapor:

- Eğitim verisi kaynağı (D-248, D-252 uyumluluğu)
- Güvenlik test sonuçları (D-310 maskeleme kapısı, prompt-injection başarı)
- Kalite metrikler (accuracy, latency, diversity)
- Ücretsiz dönem tüketimi (2026-11-01'e kadarı)
- **Üretim hazırlığı:** "GO/NO-GO" kararı

YASU denetim alanı: Hiçbir verimiz sızdı mı? Veri hazırlama D-248 uyumlu muydu? Test coverage yeterli muydi?

## Doğrulanacak varsayım

- Önceki 5 görev tamamlanmış: tasarım, EVREN doğrulaması, veri hazırlama, eğitim, test.
- Tüm çıktılar (eğitim veri, model dosyası, metrik, test log) erişilebilir.
- D-310 karar kriterlerine karşı ölçülebilir metrik var.

## Adımlar

1. **Veri denetimi (2s):**
   - `data/odin_training_data.csv/jsonl` okunur
   - Satır sayısı, örnek çeşitliliği doğrulanır
   - TCKN, müşteri kimliği, şirket sırrı var mı taranır (regex + manual sample)
   - D-248 (kişisel veri), D-252 (NACE kaynağı) checklist

2. **Güvenlik denetimi (1s):**
   - TEST-ODIN-PROMPT-INJECTION sonuçları incelenir
   - Başarısız testler varsa: neden riskli, çözüm plan yazılı mı?
   - D-310 maskeleme kapısı implementasyonu (iç→müşteri flow) kodu incelenir
   - Auth anahtar yönetimi (env var vs dosya) kaydedilir

3. **Kalite denetimi (30d):**
   - `data/odin_training_metrics_<date>.csv` okunur
   - Accuracy >70%, latency <500ms kriterlerine karşı check
   - Eğitim kurumu (EVREN) sonuçları vs beklenti farkları analiz edilir
   - Aşırı fit risk (training vs validation accuracy farkı >15%) nota alınır

4. **Ücretsiz dönem tüketimi (30d):**
   - EVREN private eğitim API'sine yapılan çağrılar sayılır
   - Harcanan compute credit (GPU-hour, vb.) tahmin edilir
   - Dönem bittiğinde (2026-11-01) maliyet artışı tahmini

5. **GO/NO-GO kararı (1s):**
   - Eğer tüm kriterler geçmişse: **GO** — produksiyona taşı
   - Eğer kritik risk varsa (güvenlik test başarısız, accuracy <70%, veri sızıntı riski): **NO-GO** — adım geri, çözüm planı yaz

6. **Rapor yazma (1s):**
   - Tablo: veri/güvenlik/kalite/maliyet denetim sonuçları
   - Açık sorunlar (varsa)
   - Rekomendasyonlar (örn. "Müşteri modeli prompt'unu şu şekilde güncelleyin")
   - GO/NO-GO cümlesi

## Kabul kriteri

- [ ] Veri denetimi tamamlanmış: satır sayısı, çeşitlilik, TCKN scan, D-248/D-252 checklist
- [ ] Güvenlik denetimi tamamlanmış: TEST-ODIN-PROMPT-INJECTION sonuçları, maskeleme kodu inceleme
- [ ] Kalite denetimi tamamlanmış: accuracy/latency/diversity vs kabul kriteri
- [ ] Ücretsiz dönem tüketimi tahmin edilmiş
- [ ] GO/NO-GO kararı yazılmış (ve gerekçesi)
- [ ] Açık sorunlar varsa çözüm planı kapsanmıştır

## Kurallar (DENETIM-KİT · D-196)

- Denetim: bağımsız (başka görevleri tamamlayan ajan değil, YASU yapmalı)
- Kanıt: tüm bulguları destekleyen dosyalar referans alınmalı
- Rapor: NO-GO ise, produksiyona geçiş DURUR (D-239 "Kapanan İşin Hafıza Kaydı" rule'ü)

## Ajan chat zorunlu (D-210 · D-217)

```bash
python scripts/ajan_chat.py ac yasu ALTYAPI-ODIN-DENETIM-RAPORU "<sorun>" --cozum "<oneri>"
python scripts/chat_gonder.py --to ihsan --type rapor --task-id ALTYAPI-ODIN-DENETIM-RAPORU --mesaj "<metin>"
```

- Başlangıç: "YASU Odin denetim raporunu yazıyor; veri/güvenlik/kalite audit 31 Ekim'de"
- Sonuç: "Denetim tamamlandı, GO kararı / NO-GO (varsa sebebi), produksiyona hazır [EVET/HAYIR]"

## Teslim

- `data/orchestrator/ALTYAPI-ODIN-DENETIM-RAPORU_2026-10-31_denetim.md` (main report)
- Denetim checklist'i (CSV/tablo, tüm maddeler)
- Varsa açık sorun + çözüm planı
- GO/NO-GO dokümanı

## Ilgili Nodlar

- [[D-310]] — Model Eğitim Güvenlik Sınırı
- [[D-248]] — Kişisel Veri Saklılığı
- [[D-252]] — NACE Üç Katman
- [[D-239]] — Kapanan İşin Hafıza Kaydı
- [[D-224]] — Kırmızı Test Doğrulama
- [[ALTYAPI-ODIN-UYARLAMA-01]], [[ALTYAPI-EVREN-PRIVATE-DOGRULAMA]], [[VERI-ODIN-EGITIM-VERISI-HAZIRLA]], [[ALTYAPI-ODIN-EGITIM-PIPELINE]], [[TEST-ODIN-PROMPT-INJECTION]] — Denetim kaynakları
