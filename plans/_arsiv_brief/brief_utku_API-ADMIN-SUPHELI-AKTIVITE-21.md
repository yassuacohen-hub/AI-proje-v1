# API-ADMIN-SUPHELI-AKTIVITE-21 — Brief (utku)

**Başlık:** [API] Şüpheli aktivite kurallarını yaz → 3 sinyalli güvenlik uyarısı (3s)
**Öncelik:** P2 · **Kit:** ADMIN-KİT (`AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`)
**Kilitli dosya:** `src/company_master/admin_audit.py`
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — kapanista "Kapanan isler" bolumune task_id satiri yazilir (B-14).
**Bağımlılık:** `API-ADMIN-AKTIVITE-YAZ-14` (`user_activity_log` kayıtları)

## Neden

SSOT §9 K10 (satır 349) "❌ yok", §10 sıra 11 (satır 374), §12 G9 (satır 422): hesap devralma veya toplu veri sızdırma girişimi şu an **hiçbir yerde alarm üretmiyor**. Bu güvenlik açığıdır; erken tespit olmadan ihlal ancak müşteri şikâyetiyle öğrenilir.

Bu tur **yalnız tespit** kapsar. Otomatik hesap kilitleme, oturum sonlandırma veya e-posta bildirimi **bu göreve dahil değildir** — yanlış pozitifin gerçek kullanıcıyı kilitlemesi riski ölçüm yapılmadan alınmaz.

## Doğrulanacak varsayım
- `src/company_master/admin_audit.py` mevcut ve şüpheli aktivite mantığı buraya eklenecek varsayıldı. Dosya yoksa **dur**, yeni modül açmadan panoya sorun aç.
- **Kritik:** "Farklı ülkeden giriş" kuralı, olay kaydında **ülke kodu veya IP alanı** bulunmasını gerektirir. `-13` şemasında (`id`/`user_id`/`olay_tipi`/`olay_zamani`/`detay`/`basarili`) böyle bir kolon **yok**; IP'nin `detay` JSONB içine yazılacağı varsayıldı. `-14` bunu yazmıyorsa bu kural **uygulanamaz**: **dur**, panoya sorun aç, kuralı sessizce atlama veya uydurma veriyle yazma.
- IP'den ülke çözümlemesi için mevcut bir yol var varsayıldı. Yoksa yeni bağımlılık ekleme (D-kural) — **dur**, KAHİN'e sor.
- "Toplu dışa aktarım" için ayrı bir olay tipi yazılıyor varsayıldı. `-13`'ün üç tipinde (`giris`/`arama`/`ai_kullanim`) böyle bir tip yok: **dur**, önce olay tipini tanımlat.
- Eşikler bu brief'te sabitlendi: 5 dakikada 5 başarısız giriş; 24 saatte 2 farklı ülke; mesai dışı penceresi 00:00–06:00. SSOT'ta başka değer varsa **dur**, KAHİN'e sor.
- `olay_zamani` `TIMESTAMPTZ` ve karşılaştırmalar **UTC** üzerinden varsayıldı; 00:00–06:00 penceresi de UTC. Yerel saat bekleniyorsa **dur** — yanlış saat dilimi yanlış alarm üretir.
- Kural çıktısı yalnız **işaretleme/uyarı**; otomatik hesap kilitleme yok varsayıldı. Kilitleme isteniyorsa KAHİN onayı şart.

## Adımlar

1. `admin_audit.py` içine saf kural fonksiyonları ekle. Her biri olay listesi alır, `bool` döner:
   - `supheli_basarisiz_giris(olaylar, pencere_dk=5, esik=5) -> bool` → 5 dakikalık pencerede `olay_tipi='giris' AND basarili=FALSE` sayısı **>5**.
   - `supheli_cok_ulkeli_ip(olaylar, pencere_saat=24, esik=2) -> bool` → 24 saatlik pencerede farklı ülke kodu sayısı **>2**.
   - `supheli_gece_toplu_export(olaylar, baslangic_saat=0, bitis_saat=6, esik=1) -> bool` → yerel saat 00:00–06:00 arasında toplu export olayı **>=1**.
2. Birleştirici: `supheli_skor(olaylar) -> int` → tetiklenen kural sayısı (0–3). `supheli_etiket(skor) -> str` → `{0:"Temiz", 1:"İzle", 2:"Şüpheli", 3:"Kritik"}`.
3. Tüm eşikler **parametre + modül sabiti** olsun; sihirli sayı gömülmesin. SSOT'a kanıt verilebilmeli.
4. Kenar durumlar docstring'e yazılsın: boş olay listesi → tüm kurallar `False`, skor `0`. Ülke kodu `None` olan kayıt **farklı ülke sayılmaz** (eksik veri şüphe üretmez).
5. Zaman dilimi: pencere hesapları `TIMESTAMPTZ` üzerinden UTC'de yapılsın; gece penceresi kullanıcının yerel saatine çevrilsin. Karışıklık docstring'te açıkça belirtilsin.
6. Fonksiyonlar saf tutulsun — DB sorgusu içermesin, olay listesi dışarıdan verilsin. Böylece test edilebilir kalır.
7. Test: `tests/test_admin_audit.py` — her kural için eşik sınırı (5 ve 6 başarısız giriş; 2 ve 3 ülke), boş liste, `None` ülke kodu, gece/gündüz sınırı (05:59 / 06:00).

## Kabul kriteri

- [ ] Üç kural fonksiyonu + `supheli_skor` + `supheli_etiket` `admin_audit.py` içinde
- [ ] Fonksiyonlar saf (DB erişimi yok), olay listesi parametreyle geliyor
- [ ] Eşikler modül sabiti ve parametre olarak tanımlı
- [ ] Boş liste ve `None` ülke kodu istisna fırlatmıyor
- [ ] Otomatik kilitleme/bildirim **eklenmedi** (kapsam dışı, tespit-only)
- [ ] Eşik sınır testleri yeşil
- [ ] SSOT §9 K10, §10 sıra 11, §12 G9 satırları `dosya:satır` kanıtıyla güncellendi

## Kurallar (ADMIN-KİT · D-196)

1. Görev başında `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md` oku.
2. Görev sonunda yalnız §7 (İzlenebilirlik Matrisi) ve §14 (Revizyon Tablosu) işle; başka dosyaya ilerleme yazma.
3. Her "yapıldı" iddiası `dosya:satır` kanıtlı olmalı.
4. Kural tabanlı ilke: önce eşik kuralları, yanlış pozitif oranı ölçülür, gerekirse sonra ML. Anomali modeliyle başlama.
5. Teslim sonrası `git add -A && git commit && git push` (D-193).

## Ilgili Nodlar

- [[Huginn Data Insights/AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
