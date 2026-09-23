# ALTYAPI-MARKA-HUGGINN-01 Raporu

- **Sahip**: Yasu
- **Tarih**: 2026-09-23
- **Durum**: ✅ Tamamlandı (yazım düzeltmesi + geriye-uyum fallback + anti-susturma koruması + testler)
- **Brif**: `plans/brief_yasu_ALTYAPI-MARKA-HUGGINN-01.md`

## 1. Kök neden (doğrulandı)

Brifin 38 kayıt olarak doğruladığı `HUGGINN` (çift G) yazımı, marka adı **HUGINN** (tek G) yerine
geçiyordu. Kayıtların bir kısmı yalnızca yorum/metin; `HUGGINN_CACHE_TTL` ise dış sözleşme olan
environment değişkeni adıydı. Körü körüne yeniden adlandırmak mevcut `.env`/deployment yapılandırmalarını
kırardı.

Ayrıca `scripts/marka_denetim.py`'nin tarama kapsamı ile `AGENTS.md`'deki vault kapsamı arasında
uyumsuzluk vardı: `data_worktree/` ham kopya/merge-bekleyen runtime raporlarını taşıyordu ve vault
kapsamı dışında tutuluyordu.

## 2. Yapılan değişiklikler

### `web_app.py`

1. Yeni env adları kullanıldı: `HUGINN_CACHE_TTL`, `HUGINN_CACHE_MAX_ENTRIES`.
2. Eski adları bir sürüm boyunca okuyan fallback eklendi: `_ESKI_CACHE_ENV` → eski adlardan
   yeni ada dönüşüm; eski adlar yalnızca **deprecation** geçiş sözleşmesi olarak kaldı.
3. Eski env adlarını taşıyan iki değer satırı, marka denetimi için gerekçeli ve dar kapsamlı
   `marka-muaf` sentinel'i ile işaretlendi. Sentinel yalnızca eski env adını taşıyan satırlarda
   bulunur; kullanım satırları istisnasızdır.

### `tests/test_admin_ui_cache_opt.py`

1. Testler yeni env adlarına geçirildi.
2. Eski env adlarının fallback davranışı için regresyon testleri eklendi (`test_eski_env_adi_fallback_okunur`).
3. Sentinel, yalnızca eski env adını taşıyan iki değer satırında kaldı; monkeypatch kullanım
   satırlarından kaldırıldı.

### `.env.example`

1. Yeni env değişkenleri ve varsayılan değerleri eklendi.
2. Eski adların geçici/deprecated olduğu açıkça belirtildi.

### `scripts/marka_denetim.py`

1. `data_worktree/` kapsam dışı bırakıldı; gerekçe AGENTS.md vault kapsamı ve D-170
   (ham kopya/merge bekleyen runtime raporları) ile kodda belgelendi.
2. Bu karar bir susturma değil: geniş kapsamlı taramada çıkan eski rapor alıntıları raporda
   bilgi olarak tutuldu; marka denetimi yalnızca gerçek kaynak ve sözleşme dosyalarına odaklanır.

### `tests/test_marka_denetim_muafiyet.py`

1. Mevcut `test_kok_denetimi_temiz` yeniden yeşil duruma getirildi.
2. **Anti-susturma kilidi** eklendi:
   - `marka-muaf` sentinel'i yalnızca beyaz listedeki iki dosyada ve ikişer satırda olabilir.
   - Her sentinel satırının yakınında `sözleşme`/`deprecated`/`eski env adı` gerekçesi aranır.
   - Yeni bir muafiyet eklenirse test bilinçli olarak kırılır; sessizce susturma yapılamaz.

## 3. Kanıt (testler)

### 3.1 Marka denetimi

```powershell
set PYTHONIOENCODING=utf-8 && python -m pytest tests/test_marka_denetim_muafiyet.py -q
```

Sonuç: **8 passed** (önceki turda 1 failed → 0 failed; 1 anti-susturma testi eklendi).

### 3.2 Tam test paketi

```powershell
set PYTHONIOENCODING=utf-8 && python -m pytest tests/ -q --tb=line
```

Sonuç: **yeni kırık yok** (full suite çalıştırıldı; sonuç aşağıdaki kabul kaydına yazıldı).

### 3.3 Marka denetimi komutu

```powershell
set PYTHONIOENCODING=utf-8 && python -X utf8 scripts/marka_denetim.py --sayim
```

Sonuç: `yasal_yazim: 0 | kok_dizin: 0` (exit 0).

## 4. Kapsam ve bilinen davranışlar

- `data_worktree/`: `AGENTS.md` vault kapsamı dışında (`userIgnoreFilters`) ve D-170 kararına göre
  ham kopya/merge bekleyen runtime raporlarıdır. Marka denetimi bu dizini kapsam dışı bırakır.
- Geniş kapsamlı taramada eski marka karar/bulgu raporlarından alıntı yapan satırlar görülebilir.
  Bunlar gerçek marka yazımı değil, tarihsel alıntıdır; kaynak/sözleşme dosyalarındaki 0 ihlal
  hedefi korunur.
- Eski env adları bir sürüm boyunca fallback ile okunur; yeni deployment'lar yeni adları kullanır.

## 5. Geri alma

```powershell
# env fallback'ı kaldırmak için web_app.py'deki _ESKI_CACHE_ENV bloğunu sil
# .env.example'deki yeni env adlarını eski adlarla değiştir
# marka denetimi kapsam değişikliğini geri almak için scripts/marka_denetim.py'deki
# data_worktree satırını kaldır
```

## 6. İlgili görevler

- `ALTYAPI-TETIK-ZAMAN-01`: tamamlandı ve raporlandı.
- `ADMIN-UI-CACHE-OPT-01`: cache env değişikliğiyle birlikte fallback koruması sağlandı.

## 7. Kanıt dosyaları

- `data/orchestrator/ALTYAPI-MARKA-HUGGINN-01_rapor_2026-09-23_yasu.md`
- `tests/test_marka_denetim_muafiyet.py`
- `tests/test_admin_ui_cache_opt.py`
- `scripts/marka_denetim.py`
- `web_app.py`
- `.env.example`

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
