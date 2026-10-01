# ALTYAPI-ODIN-EGITIM-PIPELINE — Brief (utku)

**Başlık:** [ALTYAPI] Odin eğitim hattını yaz → scripts/odin_training_pipeline.py (7d)
**Öncelik:** P1 · **Kit:** `ADMIN` (AGENTS.md D-196)
**Hub:** `hubs/TOOLS_SCRIPTS_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır.

## Neden

Eğitim verisi hazır olunca (VERI-ODIN-EGITIM-VERISI-HAZIRLA'dan çıkacak), modeli EVREN'de eğitmek gerekir. Bu görev:
- EVREN private eğitim API'sini çağrıp eğitim başlatır
- İlerlemeyi izler (ETA, hata log'u)
- Eğitim bittikten sonra model ağırlıklarını indir ve sakla
- Kalite metriği hesapla (validation set üzerinde accuracy, latency)

## Doğrulanacak varsayım

- EVREN private eğitim API'nin kaynaklar (documentation, authentication) ALTYAPI-EVREN-PRIVATE-DOGRULAMA'da tanımlanmış.
- Eğitim verisi formatı (CSV/JSONL), veri limitleri, output model formatı (ONNX / PyTorch) biliniyor.
- Eğitim süresi tahmin ediliyor (tipik LoRA: 2-6 saat, EVREN infrastructure'ü bilinendir).

## Adımlar

1. **API bağlantı (30d):** EVREN'in eğitim endpoint'ine Python client yazma:
   ```python
   # Pseudo-code
   client = EVRENTrainingClient(api_key=ODIN_INTERNAL_KEY)
   job = client.train(
       training_file="s3://huginn-bucket/odin_training_data.csv",
       model_name="odin-base-huginn",
       method="lora",  # Eğer LoRA desteklerse
       hyperparams={"lr": 1e-4, "epochs": 3}
   )
   ```

2. **İlerleme izleme (1s):** Polling loop:
   ```python
   while job.status != "completed":
       status = client.get_job_status(job.id)
       log(f"Status: {status.progress}% - ETA: {status.eta}")
       time.sleep(60)  # Her dakika kontrol et
   ```

3. **Hata işleme (30d):**
   - Eğitim başlanamazsa: network hatası, API rate limit, veri formatı sorunu, quota aşımı
   - Her hata için retry mantığı (max 3 denemem exponential backoff)
   - Hata logu: `data/odin_training_error.log`

4. **Model indirme (30d):** Eğitim bitince:
   ```python
   model_bytes = client.download_model(job.id)
   with open("data/models/odin_model_20261021.bin", "wb") as f:
       f.write(model_bytes)
   # Hash doğrulama (MD5/SHA256)
   ```

5. **Kalite ölçümü (1s):**
   - Validation set (eğitim verisinin %10-20'si) üzerinde model çalıştır
   - Metrikler:
     - **Doğruluk (Accuracy):** Sınıflandırma için % match, özet için ROUGE score
     - **Hız (Latency):** ms cinsinden avg inference time
     - **Çeşitlilik:** Örnek-çeşitliliğin modelin çıktısına etkisi (cherry-pick riski)
   - CSV'de sonuç: `data/odin_training_metrics_20261021.csv`

6. **Rapor yazma (30d):** Çıkıntılar, uyarılar, model versiyonu, ücretsiz dönemi kullanım yüzdesi

## Kabul kriteri

- [ ] EVREN API'ye başarıyla bağlantı kurulmuş (auth test geçti)
- [ ] Eğitim başlatılmış ve completion log'u var
- [ ] Model dosyası indirilmiş ve hash doğrulaması geçmiş
- [ ] Kalite metrikleri hesaplanmış (accuracy, latency, diversity scores)
- [ ] Kalite ölçümleri kabul edebilir: accuracy >70%, latency <500ms
- [ ] Hata günlüğü: eğer herhangi bir kısıl varsa (örn. veri limit) açıkça yazılmış

## Kurallar (ALTYAPI-KİT · D-196)

- Model ağırlıkları **git'e gitmez**, bulut depolama (S3 vs) veya local backup server'a gider.
- Eğitim verisi EVREN'de silme politikası: raporda yazılmalı (kaç gün sonra silinir?)
- Ücretsiz dönemi tüketme yüzdesi hesaplanmalı (2026-11-01'e kadar ne kadar harcanmış?)

## Ajan chat zorunlu (D-210 · D-217)

```bash
python scripts/ajan_chat.py ac utku ALTYAPI-ODIN-EGITIM-PIPELINE "<sorun>" --cozum "<oneri>"
python scripts/chat_gonder.py --to salih --type koordinasyon --task-id ALTYAPI-ODIN-EGITIM-PIPELINE --mesaj "<metin>"
```

- Başlangıç: "UTKU eğitim pipeline'ını kuruyor; EVREN API'ye bağlanış ve job submit 21 Ekim'de"
- Sonuç: "Eğitim tamamlandı, model indirimi başarılı, accuracy [X]%, latency [Y]ms, model versiyonu [odin-v1-20261021]"

## Teslim

- `scripts/odin_training_pipeline.py` (main script, idempotent)
- `data/models/odin_model_<date>.bin` (model ağırlıkları, backup yolunu belirt)
- `data/odin_training_metrics_<date>.csv` (kalite metriği)
- `data/orchestrator/ALTYAPI-ODIN-EGITIM-PIPELINE_rapor_2026-10-21_uretim.md`

## Ilgili Nodlar

- [[D-310]] — Model Eğitim Güvenlik Sınırı
- [[ALTYAPI-EVREN-PRIVATE-DOGRULAMA]] — EVREN API doğrulaması
- [[VERI-ODIN-EGITIM-VERISI-HAZIRLA]] — Eğitim verisi hazırlama
