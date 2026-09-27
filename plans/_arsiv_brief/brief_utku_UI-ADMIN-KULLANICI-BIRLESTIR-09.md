# UI-ADMIN-KULLANICI-BIRLESTIR-09 — Brief (utku)

**Başlık:** [UI] Üç kopya kullanıcı yönetimini taşı → tek modül (3s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** (kilit yok — kapsam brifte)

## Neden

Kullanıcı yönetimi **3 kopya** halinde (SSOT §8.3 C2). Kopyalar dururken her UI düzeltmesi 3 kez yapılıyor — erken birleştirme sonraki her görevi ucuzlatır.

## Adımlar

1. NAV-PLAN-01 §2.1 uyarınca tek uygulama: `admin_extras.render_user_management`.
2. `admin_musteriler.py:85` → yönlendir.
3. `musteri_yonetimi.py:66` → yönlendir.
4. Silme değil **yönlendirme** — çağrı noktaları kırılmasın.

## Kabul kriteri

- [ ] Üç giriş noktası da tek render fonksiyonuna düşüyor.
- [ ] Mevcut testler geçiyor, davranış aynı.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
