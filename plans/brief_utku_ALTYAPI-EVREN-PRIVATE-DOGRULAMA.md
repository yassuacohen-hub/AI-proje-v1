# ALTYAPI-EVREN-PRIVATE-DOGRULAMA — Brief (utku)

**Başlık:** [ALTYAPI] EVREN private eğitim hizmetini araştır → docs/EVREN_PRIVATE_EGITIM_DOGRULAMA.md (7d)
**Öncelik:** P0 · **Kit:** `ADMIN` (AGENTS.md D-196)
**Hub:** `hubs/PLAN_STRATEGY_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır.

## Neden

EVREN LLM Gateway'in https://evren.ssyz.org.tr/llm sayfasında açık modellerde "indirim ve destek" ile "private eğitim" hakkında bilgi olduğu söyleniyor. Huginn Insights'ın kendi fine-tuned modelini (Odin) EVREN'de eğitmek istiyoruz. Ama ne tür eğitim hizmeti (LoRA, full fine-tune, domain-specific), hangi veri limitleri (örnek sayısı, context), fiyatlandırma (neden sonra ödeme mi?) gibi kritik detaylar test edilmedi.

Bu görev: sayfayı oku, fiyat/kapsam/veri limitleri/hukuki şartları bir raporda topla. Sonraki görevler (VERI-ODIN-EGITIM-VERISI-HAZIRLA, ALTYAPI-ODIN-EGITIM-PIPELINE) bu bilgiye bağlı.

## Doğrulanacak varsayım

- EVREN private eğitim hizmeti vardır (sadece API erişim değil).
- Fiyatlandırma "indirim" içeriyor (2026-11-01'e kadar bedava veya çok ucuz).
- Veri limitleri makul (minimum 500 örnek, maximum çıktı tokenı, context window).
- Eğitim modeli LoRA veya qLoRA (tam fine-tune değil — pahalı/yavaş).

## Adımlar

1. **Sayfayı oku (30d):** https://evren.ssyz.org.tr/llm → gelen HTML/markdown'ı not al.
   
2. **Kapsam bölümü ara (30d):** "private eğitim", "model fine-tune", "LoRA", "custom model" gibi anahtar kelimeler.

3. **Fiyatlandırma ekstraktı (30d):** 
   - Bedava mı, indirimli mi, full price mi? Hangisi ne kadar?
   - Kuruluş müşteri mi, sabit fiyat mı?
   - Trial süresi var mı?
   - 2026-11-01 sonrası maliyeti nedir?

4. **Veri limitleri (30d):**
   - Maksimum eğitim örneği sayısı
   - Maksimum context (instruction+response)
   - Model boyutu (parametreler), çıkış max_tokens limiti
   - Hardware (CPU/GPU, ETA)

5. **Yasal/Teknik Şartlar (30d):**
   - Model outputu kimin? (Huginn mülk müdür, EVREN mülk müdür, shared?)
   - Veri silinme politikası (eğitim sonrası veriler silinir mi?)
   - SLA / uptime garantisi

6. **Rapor yazma (30d):** Bulguları tabulasyonu (Fiyat Tablosu, Kapsam Tablosu, Riskler, Öneriler)

## Kabul kriteri

- [ ] https://evren.ssyz.org.tr/llm sayfası tamamen okunmuş (HTML structure, tüm bölümleri)
- [ ] Private eğitim hizmeti varlığı onaylanmış (var/yok)
- [ ] Fiyatlandırma tablo (bedava dönemi, full price, trial) yazılmış
- [ ] Veri limitleri tablo (örnek count, context, model boyutu) yazılmış
- [ ] Yasal şartlar bölümü (outputu kimi, veri silme, SLA) yazılmış
- [ ] Öneriler: Huginn için uygun mu, yükseltme ne zaman yapılmalı, bütçe nedir
- [ ] YASU denetim: "bulguların temeli sayfa fotoğrafı / kayıt / resmi email teyidiyle doğrulanmıştır"

## Kurallar (VERI-KİT · D-196)

- Sayfa snapshot'ı rapor ektesi (ya da URL + erişim tarih/saati).
- Hukuki şartları tamamını oku (şart değişirse yeni eğitim verisi gelmiyebilir, örneğin).
- Fiyatı "indirim" değil kesin fiyat olarak raporda yaz.

## Ajan chat zorunlu (D-210 · D-217)

```bash
python scripts/ajan_chat.py ac utku ALTYAPI-EVREN-PRIVATE-DOGRULAMA "<sorun>" --cozum "<oneri>"
python scripts/chat_gonder.py --to ihsan --type rapor --task-id ALTYAPI-EVREN-PRIVATE-DOGRULAMA --mesaj "<metin>"
```

- Başlangıç: "UTKU sayfayı okumaya başlıyor; EVREN private eğitim hizmeti detayları 7 Ekim'e kadar rapor olacak"
- Sonuç: "Sayfa okundu, private eğitim [VAR/YOK], fiyat [X TL/ay], veri limiti [Y örnek], Huginn için uygun [EVET/HAYIR]"

## Teslim

- `docs/EVREN_PRIVATE_EGITIM_DOGRULAMA.md` (main report)
- Sayfa snapshot / referans bağlantı (ek)
- `data/orchestrator/ALTYAPI-EVREN-PRIVATE-DOGRULAMA_rapor_2026-10-07_uretim.md`

## Ilgili Nodlar

- [[D-310]] — Model Eğitim Güvenlik Sınırı
- [[EVREN-YOL-HARITASI.md]] — EVREN Gateway durum (canlı test sonuçları)
- [[KARAR-RAPORU.md]] — Mevcut karar raporu (EVREN method seçimi)
