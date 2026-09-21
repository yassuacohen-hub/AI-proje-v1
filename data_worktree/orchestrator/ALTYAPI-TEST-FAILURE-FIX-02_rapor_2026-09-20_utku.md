# ALTYAPI-TEST-FAILURE-FIX-02 Raporu

**Tarih:** 2026-09-20  
**Ajan:** utku (Üretim/Kilo)  
**Görev ID:** ALTYAPI-TEST-FAILURE-FIX-02  
**Öncelik:** P1

---

## Ne yapıldı

`tests/test_mcp.py` dosyasındaki 2 başarılamayan test düzeltildi:

1. `TestApifyAdapter::test_apify_run_actor_no_client`
2. `TestApifyAdapter::test_apify_run_actor_with_mock_client`

**Sorun:** Testler, paylaşılan `mcp_spend_log.jsonl` dosyası üzerinden günlük harcama limitini (5.0 credit) aşıyordu. Bugünkü tarihli (2026-09-20) 20+ kayıt zaten logda vardı, bu yüzden yeni testler "Günlük harcama limiti aşıldı: 0.50 > 0.00 kalan" hatası alıyordu.

**Çözüm:** `TestPolicyEngine` sınıfındaki diğer testlerde yapılan gibi, `monkeypatch` fixture'ı ile `SPEND_LOG` ortam değişkenini geçici bir dosyaya (`tmp_path / "spend.jsonl"`) yönlendirdim. Böylece her test izole bir harcama logu kullanıyor ve birbirini etkilemiyor.

---

## Değişen dosyalar

- `tests/test_mcp.py` — 2 test fonksiyonuna `tmp_path, monkeypatch` parametreleri eklendi, `monkeypatch.setattr` ile `SPEND_LOG` izole edildi.

---

## Test sonuçları

```
pytest tests/test_mcp.py -v --tb=short
============================= 38 passed in 0.84s ==============================
```

Tüm 38 test yeşil.

---

## Bulgular

🟢 **Tamam:** MCP entegrasyon testleri artık izole çalışıyor, paylaşılan state sorunu çözüldü.  
🔵 **Öneri:** Diğer test dosyalarında da benzer paylaşılan state sorunları olabilir (örn. `test_gorev_trigger.py`, `test_gorev_nobetci.py` vs. `kanit` alanı eksikliği hatası veriyor), bunlar ayrı görevlerde giderilmeli.

---

## Eksik / erteleme

- Yok. Görev hedefleri tam karşılandı.