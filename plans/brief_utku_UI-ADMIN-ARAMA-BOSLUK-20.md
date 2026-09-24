# UI-ADMIN-ARAMA-BOSLUK-20 — Brief (utku)

**Başlık:** [UI] Sonuçsuz arama frekans raporunu yaz → içerik boşluk raporu (2s)
**Öncelik:** P2 · **Kit:** ADMIN-KİT (`AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`)
**Kilitli dosya:** `web_dashboard/tabs/admin_quality.py`
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — kapanista "Kapanan isler" bolumune task_id satiri yazilir (B-14).
**Bağımlılık:** `API-ADMIN-AKTIVITE-YAZ-14` (arama olaylarının `user_activity_log` tablosuna yazılması)

## Neden

SSOT §9 K9 (satır 348) "❌ yok", §10 sıra 12 (satır 375) açık: kullanıcı arıyor, sonuç çıkmıyor, kimse bilmiyor. Sonuçsuz arama = **veri setinin nerede eksik olduğunun doğrudan kanıtı**. Bu rapor, hangi sektörü/bölgeyi beslemek gerektiğini tahminle değil ölçümle söyler.

Bu görev `-14` bitmeden çalıştırılamaz — girdi tablosu yoksa sayfa "veri kaynağı yok" rozeti göstermelidir, sahte liste değil.

## Doğrulanacak varsayım
- `-14` tamamlanmış ve arama olayları `olay_tipi='arama'` ile yazılıyor varsayıldı. Yazılmıyorsa bu ekran boş kalır: **dur**, bağımlılığı bildir.
- Sonuçsuz arama `basarili=FALSE` ile işaretleniyor varsayıldı. `-14` başka bir işaretleme kullanıyorsa **dur**, sorguyu ona göre düzelt.
- Arama teriminin `detay` JSONB alanında (ör. `detay->>'terim'`) tutulduğu varsayıldı — `-13`'te ayrı `terim` kolonu **yok**. Anahtar adı farklıysa **dur**, panoya sorun aç, uydurma anahtar okuma.
- `BOSLUK_MIN_FREKANS=3` eşiği bu brief'te sabitlendi. SSOT'ta başka değer varsa **dur**, KAHİN'e sor.
- Ekranda gösterilecek alanlar `terim` / `frekans` / `ilk_gorulme` / `son_gorulme` — hepsi tek sorgudan türetilebilir varsayıldı (`MIN`/`MAX`/`COUNT`). Türetilemiyorsa **dur**.
- Ekranın yeri `web_dashboard/tabs/admin_quality.py` varsayıldı. Dosya/sekme yapısı farklıysa **dur**, yeni sekme açmadan doğrula.
- Arama terimleri kullanıcı girdisidir: ekranda **ham HTML olarak basılmaz**, kaçışlanır. Bu güvenlik koşulu varsayım değil, zorunluluktur.

## Adımlar

1. `admin_quality.py` içine yeni bölüm: **İçerik Boşluk Raporu**.
2. Sorgu: `user_activity_log` tablosundan `olay_tipi = 'arama' AND basarili = FALSE` kayıtları, son 30 gün.
3. **Normalize:** terimi karşılaştırmadan önce `strip()` + `lower()` + çoklu boşluk tekile indirme uygula. Normalize edilmiş terim üzerinden grupla ki "ERP  Yazılım" ile "erp yazılım" aynı satıra düşsün.
4. **Frekans:** normalize terim başına sayım, azalan sırala.
5. **Eşik:** yalnız `frekans >= 3` olan terimler listelensin. Tek seferlik yazım hatası gürültüsü rapora girmesin. Eşik modül sabiti olsun (`BOSLUK_MIN_FREKANS = 3`), sihirli sayı yok.
6. Tabloyu `st.dataframe` ile göster: `terim`, `frekans`, `ilk_gorulme`, `son_gorulme`. AgGrid **yasak** (§8.3 C6).
7. Tablo yoksa veya kayıt sıfırsa `_db_yardim.tablo_var_mi()` kontrolü ile **"veri kaynağı yok"** rozeti göster — `0` veya boş tablo gösterip metrik varmış izlenimi verme (`UI-ADMIN-SAHTE-KPI-01` deseni, `admin_kpi.py:102-115`).
8. Test: normalize fonksiyonu için birim test (`"  ERP  Yazılım "` ve `"erp yazılım"` aynı anahtara düşüyor), eşik altı terimin listeye girmediği test.

## Kabul kriteri

- [ ] `admin_quality.py` içinde İçerik Boşluk Raporu bölümü var
- [ ] Normalize edilmiş terim üzerinden gruplama yapılıyor
- [ ] `frekans >= 3` eşiği modül sabiti olarak tanımlı
- [ ] Tablo yoksa "veri kaynağı yok" rozeti, sahte sıfır yok
- [ ] AgGrid kullanılmadı
- [ ] Normalize ve eşik testleri yeşil
- [ ] SSOT §9 K9 ve §10 sıra 12 satırları `dosya:satır` kanıtıyla güncellendi

## Kurallar (ADMIN-KİT · D-196)

1. Görev başında `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` oku.
2. Görev sonunda yalnız §7 (İzlenebilirlik Matrisi) ve §14 (Revizyon Tablosu) işle; başka dosyaya ilerleme yazma.
3. Her "yapıldı" iddiası `dosya:satır` kanıtlı olmalı.
4. Kural tabanlı ilke: önce normalize + frekans + eşik. Semantik kümeleme/ML bu turda **yok**.
5. Teslim sonrası `git add -A && git commit && git push` (D-193).

## Ilgili Nodlar

- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
