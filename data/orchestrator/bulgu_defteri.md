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
2026-10-12 | VERI-OZELLIK-MATRISI-SIM-01 | utku | 🟢 | paketler.py mojibake fix (97 double-encoded UTF-8 sequences) + D-321 teslim kapisi: chat.teslim_kontrol_et ajan argumani eklendi; ajanin kendi actigi bypass kaydi (kimden==ajan) kendi teslimini kilitlemez. tests/test_ozellik_matrisi.py 4/4 green. | D-321 | kapandi: chat.py:448 filtre + gorev_kutusu.py:177 ajan gonderildi; probe7 ile dogrulandi (with utku -> engel False)
2026-10-12 | UI-PAKET-ROZET-01 | utku | 🟢 | _features() rozet mapping: var->'', Yakinda aktif · <eta>, Planlanıyor; caller loop st.write('- {oz} · {rozet}') | D-321 | kapandi:web_dashboard/tabs/paketler.py:183-193 + 319-325
2026-10-21 | SINYAL-3KAYNAK-TASARIM-01 | yasu | 🟢 | Tasarim belgesi yazildi: KAP+RG+DMO birlestirme matrisi, dedup filtresi, 3 kademe paket tablosu ve musteri kullanim senaryosu; teslimde kod yok, tasarim belgesi kanittir. | kapandi:docs/strateji/SINYAL_PAKET_TASARIM.md
