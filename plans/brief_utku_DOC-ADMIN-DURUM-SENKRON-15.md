# DOC-ADMIN-DURUM-SENKRON-15 — Brief (utku)

**Başlık:** [DOC] Bayat durum satırlarını senkronla → §8.4/§10 kanıtlı (1s)
**Öncelik:** P1 · **Kit:** `ADMIN-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`

## Neden
SSOT kendi kendisiyle çelişiyor: §14 satır 473-474'te EK BULGU-9 ve EK BULGU-10 **giderildi** yazıyor, ama §8.4 satır 323-324 hâlâ "**P0**" ve §10 satır 364 (sıra 1) hâlâ "P0 · Kritik" gösteriyor. Aynı şekilde §10 satır 366 (sıra 3) ve §12 G2 notu (satır 415) `last_login` eklendiğini yansıtmıyor. Bayat durum satırı = yanlış öncelik = yanlış iş sırası.

## Adımlar
1. §8.4 satır 323 (EK BULGU-9) ve 324 (EK BULGU-10): öncelik kolonunu `✅ KAPANDI` yap, kanıt olarak `_db_yardim.py` `tablo_var_mi()` + ilgili TASK-ID'yi yaz.
2. §10 satır 364 (sıra 1): `✅ bitti` — kapatan görevler `UI-ADMIN-SAHTE-KPI-01` / `UI-ADMIN-SAHTE-EXEC-02`.
3. §10 satır 366 (sıra 3) ve satır 368 (sıra 5): "girdisiz" ifadesi artık **yanlış** — `users.last_login` v0016 ile eklendi. Kalan gerçek eksiği yaz: arama/AI log yok → `VERI-ADMIN-AKTIVITE-LOG-13`.
4. §10 satır 369 (sıra 6, A9): MAU kapandı (`UI-ADMIN-MAU-08`), kalan eksik yalnız gerçek DAU → `UI-ADMIN-DAU-17`.
5. §12 G2 (satır 415) ve G4 (satır 417): blokaj durumunu güncelle, hangi alt-adımın bittiğini `(a)(b)(c)(d)` bazında işaretle.
6. §2 kapsama oranı satırlarını (satır 326-328) yeni gerçeğe göre tekrar hesapla; hesap yöntemini tek satırla belirt.

## Kabul kriteri
- [ ] §14 ile §8.4/§10/§12 arasında "kapandı ama açık görünüyor" çelişkisi kalmadı — her düzeltilen satır TASK-ID ile kanıtlı.
- [ ] Hiçbir satır kanıtsız `✅` işaretlenmedi (`dosya:satır` veya TASK-ID zorunlu).
- [ ] Yeni bölüm/tablo eklenmedi; yalnız mevcut satırlar güncellendi.

## Kurallar (ADMIN-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) + §14 (Revizyon Tablosu) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni tablo/bağımlılık ekleme; mevcut şema ile çöz.
- Bitince `python scripts/gorev_kutusu.py teslim --ajan utku --task-id DOC-ADMIN-DURUM-SENKRON-15 --ozet "<özet>"`

## Ilgili Nodlar
- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]]
