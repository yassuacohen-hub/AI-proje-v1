# ADMIN-NAV-HAZIR-01 — Bayat `hazir=False` üst sayfaları aç (roo, P2)

## Sorun
`web_dashboard/tabs/__init__.py` SECTIONS içinde:
- `veri_kalite` (L499-509): `hazir=False, bekleyen_gorev="NAV-IA-01"` — NAV-IA-01 panoda **done**; alt sekmeler (kpi/kalite/arama/executive) mevcut. Ayrıca blok girintisi bozuk (0 boşluk).
- `musteri_onizleme` (L510-521): `hazir=False, bekleyen_gorev="NAV-IA-02"` — NAV-IA-02 **done**; alt sekmeler (paketler/pazarlama) mevcut.
- `tab_url_getir` L619-623: `except Exception: pass` sessiz.

Sonuç: iki üst sayfa admin panelde hâlâ "hazırlanıyor" placeholder gösteriyor; içerik hazır olduğu hâlde kullanıcıya kapalı.

## Yapılacaklar
| # | İş | Not |
|---|----|-----|
| 1 | `veri_kalite`, `musteri_onizleme` → `hazir=True`, `bekleyen_gorev` kaldır | `__post_init__` doğrulaması varsa kontrol et |
| 2 | L499-509 girintiyi tuple içi 4 boşluğa düzelt | Salt biçim |
| 3 | L619-623 sessiz `pass` → `_LOG.debug("session_state yok: %s", exc)` | Streamlit dışı çağrılarda normal durum → debug seviyesi |
| 4 | Test `tests/test_admin_sekme_durum.py`: panoda `done` olan `bekleyen_gorev` referansı kalmadığını doğrula (`hazir=False` ise `bekleyen_gorev` panoda `done` OLMAMALI) | Pano okunamıyorsa skip DEĞİL, listeyi sabit ver |
| 5 | Restart + pytest (tabs testleri) + kodlama_denetim | Commit YOK (sabah) |

## Kilitli dosyalar
- `web_dashboard/tabs/__init__.py` (roo)
- `tests/test_admin_sekme_durum.py`

## Tahmin
~30 dk.
