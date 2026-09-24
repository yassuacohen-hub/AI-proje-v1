# UI-ADMIN-CRAWL-KONTROL-19 — Brief (utku)

**Başlık:** [UI] Crawl işlerine tetikle/durdur aksiyonu ekle → operatör kontrol paneli (3s)
**Öncelik:** P1 · **Kit:** ADMIN-KİT (`AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`)
**Kilitli dosya:** `web_dashboard/tabs/webhook_monitor.py`

## Neden

SSOT §8.1 A8 (satır 272), §10 sıra 10 (satır 373) ve §12 G8 (satır 421): crawl/besleme işleri **izlenebiliyor ama yönetilemiyor**. Operatör takılan bir işi görüyor, müdahale için terminale geçiyor. Bu, admin panelin "tek cam" vaadini bozan en görünür boşluk.

Girdi hazır — `webhook_monitor.py` iş listesini zaten okuyor. Eklenen tek şey aksiyon katmanı.

## Doğrulanacak varsayım
- `webhook_monitor.py` crawl iş listesini okuyan mevcut bileşen varsayıldı ve aynı veri kaynağı kontrol için yeniden kullanılabilir. Farklı kaynak kullanıyorsa **dur**, panoya sorun aç.
- İş durum adları `beklemede` / `calisiyor` / `basarisiz` / `durduruldu` varsayıldı. Gerçek durum kümesi farklıysa **dur**, kodun sabitinden oku, uydurma.
- Admin rol kontrolü için projede hâlihazırda bir desen var varsayıldı; yeni yetki mekanizması yazılmayacak. Desen yoksa **dur**, KAHİN'e sor.
- `admin_audit` kayıt altyapısının bu akışta kullanılabilir olduğu **doğrulanmadı** — belirsiz. Yoksa kontrol eylemleri denetim kaydı olmadan yayına alınmaz: **dur**, panoya sorun aç.
- Tablo bileşeni olarak AgGrid **yasak** (SSOT §8.3 C6); yerleşik tablo bileşeni yeterli varsayıldı. Yetmiyorsa KAHİN'e sor.
- Durdur/yeniden dene eylemleri geri alınamaz üretim etkisi taşır; onay adımı (tıklama teyidi) zorunlu varsayıldı. Aksi isteniyorsa KAHİN onayı şart.

## Adımlar

1. `webhook_monitor.py` içindeki iş listesi tablosunun yanına satır bazlı iki aksiyon ekle: **Tetikle** ve **Durdur**.
2. Aksiyonlar yalnız uygun durumlarda etkin olsun:
   - **Tetikle** → iş durumu `beklemede` / `basarisiz` / `durduruldu` iken
   - **Durdur** → iş durumu `calisiyor` iken
   Diğer durumlarda düğme `disabled`.
3. **Durdur** yıkıcı bir aksiyondur. İki adımlı onay uygula: düğmeye basıldığında `st.session_state` ile bir onay kutusu açılır ("X işini durdurmak istediğinize emin misiniz?"), yalnız ikinci onaydan sonra çağrı yapılır. Tek tıkla iş durdurulamaz.
4. Her aksiyon sonrası `admin_audit` benzeri bir satır kaydı bırak (kim, hangi iş, hangi aksiyon, ne zaman). Kayıt altyapısı yoksa `API-ADMIN-SUPHELI-AKTIVITE-21` ile hizalanacak bir `TODO` yorumu bırak, sahte kayıt yazma.
5. Aksiyon çağrısı başarısız olursa `st.error` ile gerçek hata mesajını göster — sessizce yut ma, sahte başarı gösterme.
6. Yetki kapısı: aksiyonlar yalnız admin rolüne görünsün. Rol kontrolü mevcut desenle aynı olsun.
7. UI kısıtı: AgGrid **yasak** (§8.3 C6 reddedildi). Yalnız `st.dataframe` + `st.button` / `st.columns`.

## Kabul kriteri

- [ ] İş listesinde satır bazlı Tetikle/Durdur aksiyonları görünüyor
- [ ] Aksiyonlar duruma göre etkin/pasif (yanlış durumda tıklanamıyor)
- [ ] Durdur aksiyonu iki adımlı onay gerektiriyor
- [ ] Başarısız çağrıda gerçek hata mesajı gösteriliyor, sahte başarı yok
- [ ] Aksiyonlar admin olmayan role görünmüyor
- [ ] AgGrid kullanılmadı
- [ ] SSOT §8.1 A8, §10 sıra 10, §12 G8 satırları `dosya:satır` kanıtıyla güncellendi

## Kurallar (ADMIN-KİT · D-196)

1. Görev başında `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` oku.
2. Görev sonunda yalnız §7 (İzlenebilirlik Matrisi) ve §14 (Revizyon Tablosu) işle; başka dosyaya ilerleme yazma.
3. Her "yapıldı" iddiası `dosya:satır` kanıtlı olmalı.
4. Veri kaynağı yoksa `0` gösterme — `_db_yardim.tablo_var_mi()` ile "veri kaynağı yok" rozeti kullan (`UI-ADMIN-SAHTE-KPI-01` deseni).
5. Teslim sonrası `git add -A && git commit && git push` (D-193).

## Ilgili Nodlar

- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
