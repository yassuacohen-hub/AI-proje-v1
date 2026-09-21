# Brief: ALTYAPI-BILGI-TABANI-03 — Bilgi Tabanı / Runbook Güncelleme

**Görev ID:** ALTYAPI-BILGI-TABANI-03
**Sahip:** SALİH (Test Danışman)
**Öncelik:** P2
**Tahmini Süre:** 2s
**Dosyalar:** `docs/RUNBOOK.md`, `docs/UYUM_DENETIM_2026-09-20.md`

---

## DURUM
Zincir adımı 3 (son, SALİH). Önceki: **ALTYAPI-BENCHMARK-02** (tamamlanınca otomatik tetiklenir).

---

## AMAÇ
İki belge üret: (1) operasyon runbook'u, (2) AGENTS.md/D-kural uyum denetimi. Kod yazımı YOK.

---

## İŞ MADDELERİ

### 1. Runbook (docs/RUNBOOK.md)
Aşağıdaki senaryolar için adım adım talimat (mevcut komutları belgeleştir, yeni script yazma):

- **API çökerse ne yapılır?**
  - Log kontrolü: `logs/app.log`
  - Restart: `docker compose up -d --build api`
  - Health check: `curl http://localhost:8000/health`

- **Streamlit donarsa ne yapılır?**
  - `python scripts/streamlit_restart.py --durum`
  - `python scripts/streamlit_restart.py`

- **Test süiti kırmızı çıkarsa ne yapılır?**
  - `python -X utf8 -m pytest tests/ -q --lf` (son başarısızları tekrar çalıştır)
  - Hata sınıflandırma: flaky mi, gerçek regresyon mu

- **VPN/ağ hatası olursa ne yapılır?**
  - AJAN_DETAY §13 referansı
  - Bulgu notu düşme prosedürü

- **Kilit çakışması olursa ne yapılır?**
  - `python scripts/gorev_kutusu.py bak --ajan <ad>`
  - `lock_birak` çağrısı örneği

### 2. Uyum Denetimi (docs/UYUM_DENETIM_2026-09-20.md)
AGENTS.md'deki şu kuralları **fiilen kontrol et** (dosya var mı, script çalışıyor mu — kod yazma, sadece doğrula):

| Kural | Kontrol Yöntemi | Sonuç |
|---|---|---|
| D-55 rapor adlandırma | `data/orchestrator/*_rapor_*.md` dosya adları regex kontrolü | ✓/✗ |
| D-57 görev başlığı | `python scripts/gorev_at.py pano` çıktısında başlık formatı | ✓/✗ |
| Kodlama denetimi | `python scripts/kodlama_denetim.py` çalıştır, sonucu yaz | ✓/✗ |
| BOM/mojibake | Aynı komut çıktısından | ✓/✗ |
| Kilit disiplini | `task_board.json`'da açık kalmış kilit var mı (durum=aktif, uzun süredir güncellenmemiş) | Liste |

Her satır için: ✓ (uyumlu) / ✗ (ihlal, örnek dosya adıyla) / bulgu notu.

---

## KISITLAR
- **Kod yazma YASAK.** Yalnız iki markdown belge + komut çıktısı okuma.
- Rapor/belge dosyaları dışında hiçbir dosyaya dokunma.

---

## TESLİM
- Rapor yazımı ve teslim komutları **YASU üzerinden** yürür (D-59).
- SALİH belgeleri yazar, YASU teslim eder.
- D-67 rapor formatı ve D-55 renk sınıfı geçerli.

---

## DEĞERLENDİRME KRİTERLERİ
1. ✓ RUNBOOK.md 5 senaryo da adım adım, komutlar doğru
2. ✓ UYUM_DENETIM.md tablosu 5 satır dolu, gerçek komut çıktısına dayalı
3. ✓ İhlal bulunursa bulgu_defteri.md'ye referans verilmiş
4. ✓ Hiçbir kod dosyası değişmemiş
5. ✓ Belgeler UTF-8, BOM yok

---

## SONRAKI GÖREV
Yok — SALİH zinciri tamamlandı (3/3).
