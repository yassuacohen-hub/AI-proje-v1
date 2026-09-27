# ALTYAPI-MARKA-HUGGINN-01 — 'HUGGINN' yazım hatası (38 kayıt)

## Görev Özeti
`tests/test_marka_denetim_muafiyet.py::test_kok_denetimi_temiz` kırık:
`yasal_yazim` listesi 38 kayıt döndürüyor. Marka **HUGINN** (tek G),
kodda **HUGGINN** (çift G) geçiyor.

## Kök Neden (doğrulandı)
```
web_app.py:282: 'HUGGINN' -> # ADMIN-UI-CACHE-OPT-01: TTL artik env ile ayarlanabilir (HUGGINN_CACHE_TTL sn).
tests/test_admin_ui_cache_opt.py:24: 'HUGGINN' -> monkeypatch.delenv("HUGGINN_CACHE_TTL", raising=False)
... +36 kayit
```

## DİKKAT — env değişken adı kırılır
`HUGGINN_CACHE_TTL` bir **ortam değişkeni adı**. Düzeltince `HUGINN_CACHE_TTL` olur.
Bu geriye dönük uyumsuzdur. Yapılacak:
1. Önce 38 kaydın tam listesini çıkar: `python scripts/marka_denetim.py` (ya da testin çağırdığı fonksiyon)
2. Yorum/metin geçişlerini doğrudan düzelt
3. Env adı gibi **sözleşme** olan yerlerde: yeni ad `HUGINN_CACHE_TTL`, eski ad
   `HUGGINN_CACHE_TTL` bir sürüm boyunca fallback olarak okunmaya devam etsin
4. `.env.example` / docs varsa birlikte güncelle

## Çıktı
- 38 kaydın hepsi temizlenmiş
- Env geçişi için fallback + tek satırlık deprecation yorumu
- `tests/test_admin_ui_cache_opt.py` de düzeltilecek (izlenmeyen dosya, başka ajanın işi —
  dokunmadan önce ORKESTRATÖR'e sor, çakışma riski var)

## Kabul Kriteri
```
set PYTHONIOENCODING=utf-8 && python -m pytest tests/test_marka_denetim_muafiyet.py -q
# 1 failed -> 0 failed
set PYTHONIOENCODING=utf-8 && python -m pytest tests/ -q --tb=line
# yeni kirik yok
```

## Kurallar
- D-86: `set PYTHONIOENCODING=utf-8 &&`
- D-66: kanıtsız kapanış yok
- Muafiyet listesine ekleyerek susturmak YASAK — gerçek yazım düzelecek

## Süre Tahmini
3 saat

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
