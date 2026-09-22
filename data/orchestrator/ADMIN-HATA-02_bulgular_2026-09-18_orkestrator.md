# ADMIN-HATA-02 — Bulgu Notu (kapsam dışı, düzeltilmedi)

Tarih: 2026-09-18
Kaynak: tam test süiti koşusu (P0 admin girişi doğrulaması sırasında)

## Bulgu 1 — `admin_error_handling.py` ADMIN-UI-10 kalıbına uymuyor

Kırık testler (2):

```
tests/test_sayfa_iskeleti.py::test_ekran_page_header_kullanir[admin_error_handling]
tests/test_sayfa_iskeleti.py::test_ekran_section_kullanir[admin_error_handling]
```

Hata:

```
assert 'PageHeader' in {'Any', 'Callable', 'Exception', 'F', 'TypeVar', '_admin_logger', ...}
```

Sebep: `web_dashboard/tabs/admin_error_handling.py` `PageHeader` ve `section`
kullanmıyor. `tests/test_sayfa_iskeleti.py` her ekran modülünde bu ikisini şart
koşuyor (ADMIN-UI-10).

İki geçerli çözüm:
1. Modüle `PageHeader` + `section` ekle (tercih edilen — tutarlı ekran iskeleti).
2. Modül gerçek bir "ekran" değilse `test_sayfa_iskeleti.py` MUAF sözlüğüne
   gerekçesiyle ekle.

Dosya `ADMIN-HATA-02` kapsamında kilitli olduğu için orkestratör dokunmadı.

## Bulgu 2 — `tests/test_mcp_transport.py` toplama hatası (ayrı görev)

```
ModuleNotFoundError: No module named 'mcp.server.mcpserver'
```

Tek başına tüm süitin toplanmasını durduruyor (`Interrupted: 1 error during
collection`). Geçici olarak `--ignore=tests/test_mcp_transport.py` ile geçildi.
`ADMIN-HATA-02` ile ilgisiz; ayrı görev açılmalı.

## Bulgu 3 — Docker/DB notları (dokümana girecek)

- Sağlık ucu `/api/health`; `/health` 404 döner.
- `docker-compose.yml` içindeki `db` servisi `profiles: ["localdb"]` ile
  varsayılan `docker compose up` sırasında **açılmaz**. Gerçek DB uzakta,
  `.env` `DATABASE_URL` üzerinden. Yerel `db` konteyneri yalnız dev/test.


## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]


- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]
