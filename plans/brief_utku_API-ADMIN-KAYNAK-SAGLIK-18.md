# API-ADMIN-KAYNAK-SAGLIK-18 — Brief (utku)

**Başlık:** [API] Kaynak sağlık skorunu ölç → 3 kovalı rozet + DLQ birikme hızı (2s)
**Öncelik:** P1 · **Kit:** ADMIN-KİT (`AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`)
**Kilitli dosya:** `src/company_master/kaynak_guvenilirlik.py`
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — kapanista "Kapanan isler" bolumune task_id satiri yazilir (B-14).

## Neden

SSOT §9 K4 (satır 343) "🟡 kısmi" durumda: kaynak güvenilirlik modülü var (`kaynak_guvenilirlik.py:161`) ama tekil bir **sağlık skoru** ve operatörün tek bakışta okuyabileceği kova yok. Admin panelde "hangi kaynak bozuldu" sorusu hâlâ elle log okuyarak yanıtlanıyor.

Bu görev **bloklu değil** — girdi tabloları (`source_records`, DLQ kayıtları) veritabanında hâlihazırda mevcut. Etki/maliyet oranı yüksek: yeni tablo yok, yeni migration yok, saf hesap fonksiyonu.

## Doğrulanacak varsayım
- `src/company_master/kaynak_guvenilirlik.py:161` civarındaki fonksiyon sağlık hesabının tek yeri varsayıldı. Satır kaymışsa fonksiyonu **adıyla** bul; ikinci hesap yeri varsa **dur**, panoya sorun aç.
- `source_records` tablosu ve DLQ kayıtları veritabanında mevcut, kaynak başına başarı/başarısızlık sayısı çıkarılabiliyor varsayıldı. Tablo/kolon yoksa **dur**, uydurma sorgu yazma.
- Eşikler `SAGLIK_ESIK_YESIL=0.95` ve `SAGLIK_ESIK_TURUNCU=0.70` varsayıldı (bu brief'te sabitlendi). Kodda veya SSOT'ta başka değer varsa **dur**, KAHİN'e sor — sessizce birini seçme.
- `tests/test_kaynak_guvenilirlik.py` mevcut ve yeni testler oraya eklenecek varsayıldı. Dosya yoksa **dur**, ayrı test dosyası açmadan önce doğrula.
- Kayıt sayısı sıfır olan kaynak "yeşil" sayılmaz; ayrı "veri yok" durumu gerekir varsayıldı. Aksi bekleniyorsa KAHİN'e sor.
- Sağlık oranı penceresi (son N gün) SSOT'ta tanımlı varsayıldı; tanım yoksa **dur**, pencereyi kendin uydurma.

## Adımlar

1. `kaynak_guvenilirlik.py` içine saf fonksiyon ekle:
   `saglik_skoru(basarili: int, toplam: int) -> float` → `toplam == 0` ise `0.0` döndür (bölme hatası verme), aksi halde `basarili / toplam`.
2. Kova fonksiyonu ekle: `saglik_rozeti(oran: float) -> str`
   - `oran >= 0.95` → `"🟢 Sağlıklı"`
   - `oran >= 0.70` → `"🟠 Bozulma var"`
   - `oran < 0.70` → `"🔴 Kritik"`
   Eşikler modül seviyesinde sabit olarak tanımlansın (`SAGLIK_ESIK_YESIL = 0.95`, `SAGLIK_ESIK_TURUNCU = 0.70`) ki SSOT'a kanıt verilebilsin.
3. DLQ birikme hızı: `dlq_birikme_hizi(dlq_adet_simdi: int, dlq_adet_onceki: int, saat_farki: float) -> float` → saat başına birikme. `saat_farki <= 0` ise `0.0`.
4. Mevcut `kaynak_guvenilirlik.py:161` fonksiyonunu **bozma** — yeni fonksiyonlar ek olarak yazılır, çağıranlar etkilenmez.
5. Docstring'lere kova eşiklerini ve `toplam == 0` / `saat_farki <= 0` kenar durumlarını açıkça yaz.
6. Test: `tests/test_kaynak_guvenilirlik.py` içine eşik sınırlarını (0.95, 0.94999, 0.70, 0.69999) ve sıfır bölen durumlarını kapsayan testler ekle.

## Kabul kriteri

- [ ] `saglik_skoru`, `saglik_rozeti`, `dlq_birikme_hizi` fonksiyonları `kaynak_guvenilirlik.py` içinde
- [ ] `toplam == 0` ve `saat_farki <= 0` durumunda istisna fırlatmıyor, `0.0` dönüyor
- [ ] Eşikler modül sabiti olarak tanımlı (sihirli sayı yok)
- [ ] Mevcut `kaynak_guvenilirlik.py:161` fonksiyonunun imzası değişmedi
- [ ] Eşik sınır testleri yeşil
- [ ] SSOT §9 K4 satırı `dosya:satır` kanıtıyla güncellendi

## Kurallar (ADMIN-KİT · D-196)

1. Görev başında `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` oku.
2. Görev sonunda yalnız §7 (İzlenebilirlik Matrisi) ve §14 (Revizyon Tablosu) işle; başka dosyaya ilerleme yazma.
3. Her "yapıldı" iddiası `dosya:satır` kanıtlı olmalı.
4. Kural tabanlı ilke: önce eşik/kova, ölçüm sonrası gerekirse ML. ML ile başlama.
5. Teslim sonrası `git add -A && git commit && git push` (D-193).

## Ilgili Nodlar

- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
