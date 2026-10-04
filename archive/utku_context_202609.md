# utku_project_context.md arsivi — 2026-09 (D-219)

D-219: eski oturum bloklari bu dosyaya tasinir; §Öz-eleştiri **hic** tasinmaz.

### 2026-09-27 — VERI-KAYNAK-BAG-01 + VERI-NACE-SOZLUK-01 + VERI-NACE-TEMIZ-01 + TEST-BACKLOG-20 + VERI-HAYALET-TEMIZ-01 tamamlandı (onay bekliyor)

- **Görevler:** `VERI-KAYNAK-BAG-01` (P0), `VERI-NACE-SOZLUK-01` (P0), `VERI-NACE-TEMIZ-01` (P1), `TEST-BACKLOG-20` (P1), `VERI-HAYALET-TEMIZ-01` (P0)
- **Yapılan VERI-KAYNAK-BAG-01:**
  - Migration 0023: source_records.company_id kolonu eklendi + FK
  - 5252 eşleşme (37.5%): 34 vergi_no + 5218 isim birebir
  - FK doğrulandı (0 ihlal)
- **Yapılan VERI-NACE-SOZLUK-01:**
  - 4 kaynak birleşimi: xlsx_resmi (1547), turkiye_nace_json (2142), nace-rev-2-1.json (1562), nace-rev-2.json (1482)
  - 3319 NACE kodu yüklendi, seviye 6/4/2/1 dolu
  - Eşleşme %92.9 (4252/4574), 47.79.04 ve 47.79 var
- **Yapılan VERI-NACE-TEMIZ-01:**
  - 7614 NN.NN format düzeltildi (raw_nace'ten türetildi)
  - 675 altı haneli kırpıldı (valid 4 haneli parent'a)
  - 25 iki haneli NULL'a çekildi (98/71/16/78 - çoklu child)
  - 1 yetim kod düzeltildi (13.92.11)
  - Sonuç: NN.NN 8289 (valid), 6-digit 0, 2-digit 0, yetim 0
- **Yapılan TEST-BACKLOG-20:** 6 faz, 20 failed → 0, 348 test passed
- **Yapılan VERI-HAYALET-TEMIZ-01:** 4591 hayalet kayıt silindi, UNIQUE INDEX (migration 0022), vergi_no 761 korundu
- **Doğrulama:** Tüm 5 görev `review` durumunda, onay bekliyor
- **Kalan / bloke:** VERI-02 ve VERI-NACE-COKLU-01 bloke (P0 onayı bekliyor)
- **Öğrenilen tuzak:** 5 görev tek seferde onay kuyruğuna girdi, tek tek onaylanmalı

### 2026-09-26 — D-215/D-216 menü kaydı

- **Görev:** `UI-ADMIN-MENU-D215216`
- **Yapılan:** D-215 (Gelir Kapısı, paket_kredi taşıma, maliyet→Metrikler, Güvenlik Kapısı kök) + D-216 hayalet arşivleme geriye dönük panoya işlendi
- **Doğrulama:** `pytest tests/test_naming_audit.py -q` → 9 passed
- **Commit:** `9650bf1`
- **Kalan / bloke:** yok
- **Öğrenilen tuzak:** pano kaydı ile kod tabanı çapraz kontrol edilmeden görev alınmamalı (→ §Tuzaklar)

> **Oturumu kapatmadan:** §KALDIĞIM YER'i güncelle + **Son okunan karar** no'yu tazele.
