# UI-ADMIN-CHURN-KOLON-07 — Brief (ihsan)

**Başlık:** [UI] Churn risk kolonunu yaz → musteri_yonetimi.py listesi (1s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** (kilit yok — kapsam brifte)

## Neden

Churn zincirinin 4. halkası — hesap görünür hale gelir.

## Adımlar

1. **Bağımlılık:** API-ADMIN-CHURN-FONKSIYON-06.
2. `musteri_yonetimi.py` · `_giris_aktinligi()` **satır 216** SQL'ine risk kolonu ekle.
3. Risk etiketini `churn.risk_etiketi()` ile hesapla — UI'da mantık tekrarlama.

## Kabul kriteri

- [ ] Müşteri listesinde risk kolonu görünüyor, `last_login` boşsa bozulmuyor.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
