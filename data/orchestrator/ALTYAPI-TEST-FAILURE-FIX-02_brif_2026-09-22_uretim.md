# ALTYAPI-TEST-FAILURE-FIX-02 — Üretim Brief

**Görev:** Test hatası düzelt — tests/test_mcp.py  
**Ajan:** utku (Üretim)  
**Öncelik:** P1  
**Tarih:** 2026-09-22

## Özet

MCP entegrasyonu testleri `test_mcp.py`'de hata veriyor. Root cause şu anda bilinmiyor ama test çalıştırma sırasında timeout veya assertion failure gözleniyor. Hatayı tanımla, test detayını al, düzeltme yap, tüm test suite yeşil olana kadar doğrula.

## Adımlar

1. **Test çalıştır:** `pytest tests/test_mcp.py -v` — hata mesajını tam kaydet.
2. **Debug:** Hata stacktrace'ini oku. MCP mock setup'ı kontrol et, timeout ayarlarını gözden geçir.
3. **Düzelt:** Hatayı kaynağında kapat (test veya kod).
4. **Doğrula:** `pytest tests/test_mcp.py -v` yeşil olana kadar. Tüm suite: `pytest tests/ -v`.
5. **Teslim Not:** Hata türü, çözüm, test durumu.

## Dosyalar

- `tests/test_mcp.py` — **kilitli** (düzenle)
- `Huginn Data Insights/src/` — ilgili kod

## Gözlemler

- Diğer testler geçiyor mu, sadece MCP mi hata veriyor?
- Mock data eksik mi, seed sorunu mu?
- Windows timeout sorunu olabilir (oto_nobetci oto_destek modunda çalışıyor).

**Teslim:** Hatayı, düzeltmeyi ve test sonucunu not etmiş halde.
