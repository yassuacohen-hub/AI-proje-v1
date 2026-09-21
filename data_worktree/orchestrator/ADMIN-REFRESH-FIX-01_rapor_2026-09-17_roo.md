[[Huginn Data Insights/data/orchestrator/ADMIN-REFRESH-FIX-01_rapor_2026-09-17_roo.md]]

# ADMIN-REFRESH-FIX-01 — Otomatik yenileme tercihi kaydedilmiyordu (roo)

- **Tarih:** 2026-09-17
- **Ajan:** roo (orkestratör, kendi işi)
- **Öncelik:** P2
- **Durum:** done (kod + test + denetim + restart tamam)

## 1. Bulgu (kök neden)

`web_dashboard/tabs/admin_auto_refresh.py` içindeki aç/kapat butonu bloğunda sıra şöyleydi:

```
st.session_state[...] = not acik
st.rerun()                 # <-- script burada durur
ayar_kaydet(...)           # <-- HİÇ ÇALIŞMIYOR (ölü kod)
```

`st.rerun()` scripti anında yeniden başlattığı için altındaki kalıcı kayıt satırları
hiçbir zaman çalışmadı. Sonuç: kullanıcı otomatik yenilemeyi açsa/kapatsa da tercih
diske yazılmıyor, sayfa yenilenince eski değere dönüyordu.

İkinci bulgu: `web_dashboard/tabs/admin_panel.py` → `aktif_kullanici()` içinde
`st.session_state` okuması `except Exception: pass` ile sessizce yutuluyordu
(hata görünmez, teşhis imkânsız).

## 2. Değişiklikler

| Dosya | Değişiklik |
|---|---|
| `web_dashboard/tabs/admin_auto_refresh.py` | `_ayar_kaydet_guvenli(kullanici_id, acik, aralik) -> str \| None` saf yardımcı eklendi; misafir/`None` kimlikte yazmaz; hata olursa `log.warning` + `"TipAdi: mesaj"` metni döner. Buton bloğunda kayıt **rerun'dan ÖNCE** çağrılır, hata varsa `st.caption("⚠️ Tercih kaydedilemedi: …")`. `MISAFIR_KIMLIK` sabiti + modül logger'ı eklendi. |
| `web_dashboard/tabs/admin_panel.py` | `aktif_kullanici()` içindeki sessiz `except` → `except Exception as exc: _log.debug(...)` (Streamlit bağlamı dışında test/CLI çalışması bozulmadan loglanır). |
| `tests/test_admin_auto_refresh.py` | +7 test: misafir/None kaydetmez (parametrize), iki anahtarın da yazıldığı, hata metni + log, **rerun öncesi kayıt regresyon testi**, kayıt hatasında uyarı caption'ı, modülde `except: pass` kalmadığı. |
| `tests/test_admin_panel_tab.py` | +2 test: `aktif_kullanici` kimlik çözümü (trim/boş → misafir) ve `session_state` patlarsa misafir + DEBUG log. Dosya sonu newline düzeltildi. |

## 3. Doğrulama

- `pytest tests/test_admin_auto_refresh.py -q` → **15 passed**
- `pytest tests/test_admin_panel_tab.py tests/test_admin_auto_refresh.py -q` → **24 passed**
- Toplu: `test_admin_auto_refresh + test_admin_panel_tab + test_admin_yonetim + test_sayfa_iskeleti` → **118 passed in 1.67s**
- `python scripts/kodlama_denetim.py` → dokunulan 4 dosya için uyarı yok
- `python scripts/streamlit_restart.py` → DURDURULDU 27472 / BASLADI PID 2084, sağlık ok

## 4. Notlar

- Regresyon testi (`test_toggle_tercihi_rerun_oncesi_kaydeder`) bug'ın geri gelmesini
  engeller: `st.rerun` `RuntimeError` fırlatacak şekilde taklit edilir; kayıt çağrıları
  rerun'dan önce toplanmış olmalıdır.
- Commit atılmadı (sahip kararı: commit sabah, toplu).
