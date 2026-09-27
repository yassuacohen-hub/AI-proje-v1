# API-ADMIN-CHURN-FONKSIYON-06 — Brief (ihsan)

**Başlık:** [API] Churn risk fonksiyonunu yaz → churn.py saf fonksiyon (2s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/churn.py`

## Neden

Churn zincirinin 3. halkası. SSOT §9 K1 — PRD'de P0, kodda yok. **Kural tabanlı başla**, ML'e sonra yüksel (SSOT §9 ilke).

## Adımlar

1. **Bağımlılık:** API-ADMIN-LASTLOGIN-YAZ-05.
2. Yeni dosya `src/company_master/churn.py` · `risk_etiketi(son_giris, bugun) -> str`.
3. **Saf fonksiyon** — DB'ye dokunmaz, parametre alır. Test edilebilirliği bu sağlar.
4. Doctest ile örnekle (sınır günler dahil).
5. Tek sinyal (`last_login`) ile başla; arama/AI log tablosu **şimdilik atlanır** (SSOT §12 G2).

## Kabul kriteri

- [ ] `risk_etiketi()` doctest'leri geçiyor.
- [ ] Sınır değerler (bugün giriş, hiç giriş yok = None) tanımlı.

## Kurallar (ADMIN-KİT · D-196)

- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan <ajan> --task-id <TASK> --ozet "<özet>"`

## Ilgili Nodlar

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
