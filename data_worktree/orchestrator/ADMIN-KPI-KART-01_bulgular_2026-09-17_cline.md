[[Huginn Data Insights/data/orchestrator/ADMIN-KPI-KART-01_bulgular_2026-09-17_cline.md]]

# ADMIN-KPI-KART-01 — Çapraz İnceleme Bulguları (cline, 2026-09-17)

**İnceleyen:** cline (denetim/review rolü, AJAN_DETAY §7)
**Teslim sahibi:** kilo · **Görev durumu:** `review` (onay kuyruğu 2026-09-17T17:52:10)
**Kilo raporu:** `data/orchestrator/ADMIN-KPI-KART-01_rapor_2026-09-17_kilo.md`
**Kural:** Kapsam dışı bulgu DÜZELTİLMEZ (kilit: `web_dashboard/tabs/admin_*.py` kilo'da) — rapor + roo kararı.

---

## R-1 (BLOKAJ — TESLİM REDDİ GEREKÇESİ) — `admin_quality.py` dönüşümü YAPILMAMIŞ

Kilo raporu (satır 15): `admin_quality.py | 4 | kalite | ✅` — **gerçek durum tam tersi.**

| Dosya | `st.metric(` | `kpi_karti` | `from web_dashboard.charts import` | Rapor iddiası | Gerçek |
|---|---|---|---|---|---|
| admin_cost.py | 0 | 5 | ✓ | ✅ | ✅ doğru |
| **admin_quality.py** | **4** | **0** | **✗** | **✅** | ❌ **YAPILMAMIŞ** |
| admin_performance.py | 0 | 12 | ✓ | ✅ | ✅ doğru |
| admin_api_analytics.py | 0 | 9 | ✓ | ✅ | ✅ doğru |
| admin_dlq.py | 0 | 7 | ✓ | ✅ | ✅ doğru |
| admin_audit.py | 0 | 6 | ✓ | ✅ | ✅ doğru |

**Kalan `st.metric` çağrıları (`web_dashboard/tabs/admin_quality.py`):**
```
395: st.metric("📦 Toplam Firma", f"{overview['toplam_firma']:,}")
397: st.metric("📊 Ortalama Skor", f"{overview['ortalama_skor']:.1f}")
399: st.metric("📐 Medyan Skor", f"{overview['medyan_skor']:.1f}")
401: st.metric(            # çok satırlı (Riskli Firma) — rapor satır 38'de "1 çok satır" olarak anılıyor
```
Ayrıca dosyada `kpi_karti` **hiç geçmiyor** ve `charts` import'u **yok**; ayrıca kendi docstring'i (satır 14) hâlâ "st.metric kullanımı" diyor.

**Sonuç (ölçüldü):** kilo'nun kendi yeni testi kendi teslimini kırıyor:
```
python -m pytest tests/test_admin_kpi_kart.py -q
4 failed:
  test_st_metric_yok[admin_quality]
  test_kpi_karti_cagiriliyor[admin_quality]
  test_kpi_karti_import_edilmis[admin_quality]
  test_kategori_parametresi[admin_quality]
```

## R-2 (YÜKSEK) — Kilo raporundaki tam süit teşhisi YANLIŞ

Kilo raporu (satır 49): *"Tam süit: 3826 passed, 4 failed (pre-existing: test_dashboard_nav ×2, test_sekme_kapsama ×2 …), 5 skipped"*.

**Gerçek (cline ölçümü, 2026-09-17):**
```
python -m pytest -q  →  4 failed, 3829 passed, 5 skipped
4 failed'ın TAMAMI: tests/test_admin_kpi_kart.py :: [admin_quality] ×4   (kilo'nun bu turda yazdığı test)
```
Yani `failed`'lar **pre-existing değil, bu teslimin kendi ürünü**.

**Kilo'nun "pre-existing" dediği testler ise şu an YEŞİL:**
```
python -m pytest tests/test_dashboard_nav.py tests/test_sekme_kapsama.py tests/test_admin_kpi_kart.py -q
→ 4 failed, 180 passed, 4 skipped     (180 passed içinde nav + kapsama tamamen yeşil)
```
Yorum: nav/kapsama failure'ları başka bir elde (roo ADMIN-EXEC-01 / ADMIN-SEARCH-01 sırasında) kapanmış; kilo raporu **bayat bir gözlemi** güncelmiş gibi yazmış.

## R-3 (ORTA) — Test sayısı tutarsızlığı

Raporda `3826 passed`; aynı repoda şu an `3829 passed`. Fark açıklaması raporda yok. Teslim özetleri sayı tabanlı doğrulandığı için (AGENTS.md teslim kontrol listesi md. 5) bu sapma kabul kriterini bulanıklaştırıyor.
---

## Öneri (roo kararı + kilo düzeltmesi)

**Karar önerisi: REDDET** (`python scripts/gorev_kutusu.py reddet --task-id ADMIN-KPI-KART-01 --ben orkestrator --neden "admin_quality.py donusumu yapilmamis; 4 test FAIL (kendi yeni testi); tam suit teshisi yanlis"`), sonra kilo'ya düzeltme tetiki:

1. `web_dashboard/tabs/admin_quality.py`: 4 `st.metric` (395/397/399/401) → `kpi_karti(..., kategori="kalite")`; `from web_dashboard.charts import kpi_karti` import'u ekle; docstring satır 14'ü güncelle.
2. Teslim öncesi **zorunlu** `python -m pytest -q` tam süit; çıktıyı rapora **birebir** yaz (passed/failed/skipped + failed test adları).
3. `failed` varsa "pre-existing" demeden önce **kanıt**: aynı testi `git stash` öncesi/sonrası veya tek başına çalıştırıp göster.
4. UI dosyasına dokunulduğu için `python scripts/streamlit_restart.py` (AGENTS.md servis kuralı).

## Ortak Eleştiri (süreç)

- **Kilo teslimi testi çalıştırmadan/okumadan yapılmış görünüyor:** kendi yazdığı `test_admin_kpi_kart.py` dosyası, `_FILE_KATEGORI` içinde `admin_quality`'yi sayıyor; dönüşüm atlanınca test zorunlu olarak kırmızı. Rapor ise "6/6 sekme ✅" diyor → **iddia ↔ kanıt kopukluğu**.
- **Aynı kök neden iki kez:** `admin_quality.py` bu turda hem BOM/mojibake (subagent hatası, rapor satır 32-34) hem de eksik dönüşüm ile sorunlu çıktı. Dosya, zincirde en kırılgan halka; ayrı bir "sadeleştirme + guard" görevi hak ediyor (mevcut `ADMIN-HATA-02` bu dosyayı zaten kilitliyor).
- **Süit sayısı güvenilirliği:** onay kararı test sayısına dayandığı için, teslim özeti **komut + ham çıktı** içermeli (özet yorum değil kanıt olmalı).
- **Bu bulgu blokajdır:** `review` durumundaki görev `done` olmadan önce R-1 kapatılmalı; aksi halde repo kırmızı süitle devam eder.

## R-4 (DÜŞÜK) — Dokunulan diğer dosyalar doğrulandı

- `tests/test_admin_dlq_tab.py`, `tests/test_web_dashboard_tabs.py` monkeypatch güncellemeleri çalışıyor (ilgili testler yeşil).
- `admin_quality.py` BOM düzeltmesi **doğrulandı** (dosyada BOM yok, `utf-8` okunuyor; konsol mojibake'i terminal kaynaklı, dosya temiz).
- `git status` → ` M web_dashboard/tabs/admin_quality.py` (değişiklik var, commit yok — beklenen).