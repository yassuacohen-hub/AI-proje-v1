# UI-ADMIN-DAU-17 — Brief (utku)

**Başlık:** [UI] Gerçek DAU kartını yaz → admin_kpi.py aktivite sorgusu (2s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_dashboard/tabs/admin_kpi.py`
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — kapanista "Kapanan isler" bolumune task_id satiri yazilir (B-14).

## Neden
SSOT §12 G4 (satır 417): "gerçek DAU için ayrı olay tablosu gerekir" — `-13`/`-14` ile o tablo geliyor, blokaj kalkıyor. §10 sıra 6 (satır 369) A9'u P1 tutuyor. Şu an panelde yalnız MAU var (`UI-ADMIN-MAU-08`); DAU'suz MAU tek başına angajman ölçmez.

## Doğrulanacak varsayım
- `web_dashboard/tabs/admin_kpi.py:41` satırındaki `load_admin_kpi_summary()` KPI'ların tek üretim noktası varsayıldı. Satır kaymışsa fonksiyonu **adıyla** bul; başka üretim noktası varsa **dur**, panoya sorun aç.
- `admin_kpi.py:102-115` ve `:399-402` aralıkları sahte/sabit KPI üreten yerler varsayıldı. İçerik farklıysa **dur**, körlemesine değiştirme.
- `web_dashboard/tabs/_db_yardim.py` içindeki `tablo_var_mi()` yardımcısı mevcut ve tablo yokluğunda güvenli `False` dönüyor varsayıldı. Yoksa **dur**, kendi kontrolünü uydurma.
- DAU kaynağı `-13`'ün `user_activity_log` tablosu (`olay_tipi='giris'`, son 24 saat) varsayıldı. Tablo yoksa DAU **0 gösterilmez**, "veri yok" gösterilir.
- Mevcut MAU değeri gerçek veriden geliyor varsayıldı ve bu görevde dokunulmayacak. MAU de sahteyse **dur**, kapsamı KAHİN'e bildir.
- Gün sınırı UTC varsayıldı (`TIMESTAMPTZ`). Yerel saat bekleniyorsa KAHİN'e sor.

## Adımlar
1. `load_admin_kpi_summary()` (`admin_kpi.py:41`) içine DAU sorgusu: `user_activity_log` üzerinden son 24 saatte **distinct** `user_id`.
2. DAU/MAU oranını da hesapla (yapışkanlık göstergesi) — ek sorgu değil, mevcut MAU değeriyle bölme.
3. **Tablo yoksa sahte sıfır gösterme:** `_db_yardim.tablo_var_mi()` kullan, yoksa `"veri kaynağı yok"` rozeti — `UI-ADMIN-SAHTE-KPI-01` deseninin aynısı (`admin_kpi.py:102-115`, `:399-402`).
4. MAU=0 iken oran hesaplarken bölme hatası verme.

## Kabul kriteri
- [ ] DAU kartı ve DAU/MAU oranı panelde görünüyor.
- [ ] `user_activity_log` yokken kart "veri kaynağı yok" rozetiyle çiziliyor, `0` göstermiyor.
- [ ] Assert tabanlı test: normal durum, tablo yok durumu, MAU=0 kenar durumu.

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; `st.dataframe`/Plotly dışına çıkma (§8.3 C6).
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id UI-ADMIN-DAU-17 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
