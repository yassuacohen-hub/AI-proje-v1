# UI-ADMIN-UPSELL-22 — Brief (utku)

**Başlık:** [UI] Upsell adaylarını 3 koşullu kuralla listele → satış aksiyon listesi (2s)
**Öncelik:** P2 · **Kit:** ADMIN-KİT (`AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`)
**Kilitli dosya:** `web_dashboard/tabs/musteri_yonetimi.py`
**Bağımlılık:** `API-ADMIN-CHURN-3SINYAL-16` (churn etiketinin 3 sinyalli hâli)

## Neden

SSOT §9 K7 (satır 346) "❌ yok": kota doygunluğuna yaklaşan sağlıklı müşteriler hiçbir yerde listelenmiyor. Satış tarafı upsell fırsatını ancak müşteri limite çarpıp şikâyet edince öğreniyor — yani **en kötü anda**.

Girdi hazır: `credit_ledger` tablosu veritabanında mevcut, ek migration gerekmez. Yalnız churn etiketi `-16` ile güncellenecek.

## Adımlar

1. `musteri_yonetimi.py` içine yeni bölüm: **Upsell Adayları**.
2. Doygunluk hesabı: her müşteri için kullanılan/kota oranını `credit_ledger` üzerinden çıkar. Birden fazla kota tipi varsa `doygunluk = max(oranlar)` — en önce hangi limite çarpacaksa o belirleyicidir.
3. Aday kuralı (üçü birden sağlanmalı):
   - `doygunluk >= 0.85`
   - `churn_etiketi ∈ {"Yok", "Düşük"}` (kaynak: `churn.risk_etiketi_3sinyal`, `-16` çıktısı)
   - son 30 gün kullanım büyümesi `> 0`
4. Eşikler modül sabiti olsun: `UPSELL_DOYGUNLUK_ESIK = 0.85`. Sihirli sayı gömme.
5. Kota `0` veya `None` olan müşteride bölme yapma — o müşteri listeden **çıkarılır**, `0.0` doygunluk uydurulmaz.
6. Tabloyu `st.dataframe` ile göster: `musteri`, `doygunluk_%`, `churn_etiketi`, `buyume_%`, `paket`. Doygunluğa göre azalan sırala. AgGrid **yasak** (§8.3 C6).
7. `credit_ledger` tablosu yoksa `_db_yardim.tablo_var_mi()` ile **"veri kaynağı yok"** rozeti göster, sahte liste üretme (`UI-ADMIN-SAHTE-KPI-01` deseni).
8. Test: üç koşulun her birinin tek başına elediği vaka, `kota=0` vakası, `doygunluk=0.85` tam sınır vakası (dahil olmalı).

## Kabul kriteri

- [ ] `musteri_yonetimi.py` içinde Upsell Adayları bölümü var
- [ ] Üç koşul birlikte uygulanıyor (AND), tek koşulla liste üretilmiyor
- [ ] `doygunluk = max(oranlar)` kuralı uygulandı
- [ ] `kota=0`/`None` müşteride bölme hatası yok, müşteri listeden çıkarılıyor
- [ ] Eşik modül sabiti olarak tanımlı
- [ ] Tablo yoksa "veri kaynağı yok" rozeti, sahte liste yok
- [ ] AgGrid kullanılmadı
- [ ] Sınır testleri yeşil
- [ ] SSOT §9 K7 satırı `dosya:satır` kanıtıyla güncellendi

## Kurallar (ADMIN-KİT · D-196)

1. Görev başında `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` oku.
2. Görev sonunda yalnız §7 (İzlenebilirlik Matrisi) ve §14 (Revizyon Tablosu) işle; başka dosyaya ilerleme yazma.
3. Her "yapıldı" iddiası `dosya:satır` kanıtlı olmalı.
4. Kural tabanlı ilke: önce üç koşullu eşik, dönüşüm oranı ölçülür, gerekirse sonra skor modeli. ML ile başlama.
5. Teslim sonrası `git add -A && git commit && git push` (D-193).

## Ilgili Nodlar

- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
