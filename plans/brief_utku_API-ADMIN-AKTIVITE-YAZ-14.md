# API-ADMIN-AKTIVITE-YAZ-14 — Brief (utku)

**Başlık:** [API] Giriş/arama/AI olaylarını log'a yaz → web_app.py + arama uçları (2s)
**Öncelik:** P0 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `web_app.py` (+ arama/AI çağrı uçları)

## Neden
SSOT §8.4 EK BULGU-8 (satır 322): aktivite verisi sıfır. `VERI-ADMIN-AKTIVITE-LOG-13` tabloyu açar ama **boş tablo değer üretmez**. K1 3-sinyal (§9:340), K9 (§9:348), G4 DAU (§12:417) bu yazma akışına bağlı.

## Adımlar
1. `API-ADMIN-LASTLOGIN-YAZ-05` desenini örnek al: `web_app.py:2232` + fallback `:2246` — aynı giriş noktasına `olay_tipi='giris'` INSERT ekle.
2. Tek ortak yardımcı yaz: `aktivite_yaz(user_id, olay_tipi, detay=None, basarili=True)` — tekrar eden INSERT kodu olmasın.
3. Arama ucuna `olay_tipi='arama'`, `detay={"terim": ..., "sonuc_adedi": N}`, `basarili = sonuc_adedi > 0`.
4. AI/MIMIR çağrı ucuna `olay_tipi='ai_kullanim'`.
5. **Log yazımı asla ana akışı düşürmez**: INSERT `try/except` içinde, hata yalnız loglanır, kullanıcı isteği başarısız olmaz.

## Kabul kriteri
- [ ] `aktivite_yaz()` için assert tabanlı test: başarılı yazma + DB hatası durumunda sessiz geçiş (ana akış kesilmez).
- [ ] Başarısız arama (`sonuc_adedi=0`) `basarili=False` olarak kaydediliyor — K9 girdisi hazır.
- [ ] Giriş akışı log tablosu yokken de çalışmaya devam ediyor.

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; `-13` ile gelen şemayı kullan.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id API-ADMIN-AKTIVITE-YAZ-14 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
