# Bulgu Defteri (D-67 · D-318)

**Tek kanonik dosya.** Ajan başına ayrı bulgu defteri yoktur ve açılmaz —
ölçüm: hiçbir ajan kendi defterini tutmuyor, ayrı defter ihtiyacı doğrulanmamış
varsayımdır (D-224). Dört ayrı defter olsaydı aynı bulgu dört yere yazılır,
karşılaştırması kaybolur ve ikiz yapı doğardı (D-211).

**Tek yazıcı:** `scripts/bulgu_defteri.py`. Elle satır eklenmez.

**Zorlayıcı:** `gorev_kutusu.py teslim` teslimden önce bu dosyada görev
`task_id`'sini arar; bulunamazsa teslim reddedilir (D-239: kural gövdesi tek
yerde, üretim komutu onu çağırır).

**Satır formatı (6 alan, borular):**

```
tarih | task_id | rol | renk | özet | karar
```

| Alan | Kural |
|---|---|
| `tarih` | `YYYY-AA-GG` |
| `task_id` | panodaki kanonik kimlik |
| `rol` | ajan kanonik adı (`ihsan` · `utku` · `salih` · `yasu`) |
| `renk` | 🔴 acil · 🟡 dikkat · 🟢 tamam · 🔵 öneri |
| `özet` | tek cümle; sayı varsa ölçülmüş sayı |
| `karar` | `görev:<ID>` · `D-NNN` · `kapandı:<kanıt>` · `red: <gerekçe>` |

**Karar sütunu boş bırakılmaz.** D-67: orkestratör her satırı üç seçenekten
biriyle işler — görev açar, karara bağlar, gerekçeyle reddeder. Boş satır
işlenmemiş bulgudur ve denetimde kırmızı yanar.
2026-10-03 | ALTYAPI-KREDI-CUZDANI-01 | yasu | 🟢 | brief 3 varsayimi yanlisti: companies PK'si id degil company_id (UUID). 0050 numarasi D-323'te alinmisti; goc 0051 yazildi. psycopg execute() tek ifade kabul ediyor; BEGIN/COMMIT ve COMMENT kaldirildi. | kapandi: 0051 + kredi.py 55 satir + test 4/4; SQLAlchemy 2.x icin begin() kullanildi (connect() rollback yapip kayit yitiriyordu)
