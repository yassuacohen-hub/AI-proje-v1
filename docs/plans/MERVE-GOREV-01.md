# MERVE-GOREV-01 — Merve'nin ilk işi (Continue sohbetine yapıştır)

**Kim:** Merve 👩‍💻 (Continue IDE) · **Neden:** kimlik + tablo + eleştiri defteri kuralını tek seferde sınamak.
**Not:** Merve panoya girmez, `gorev_kutusu.py` kullanılmaz. İş doğrudan sohbette verilir.

## Yapıştırılacak metin

```
Merve merhaba. İlk işin küçük:

docs/ROO_ELESTIRI_NOTLARI.md dosyasını aç, §7 "Dikkat Notları Defteri" bölümünü oku.
Sonra web_dashboard/tabs/__init__.py dosyasına bak — 500+ satırlık tek bir SECTIONS listesi var.

Bana iki şey ver:
1. Bu dosyada gördüğün en önemli 1 riski anlat (uzun yazma).
2. Aynı riski eleştiri defteri formatında hazır not olarak yaz:
   tarih · konu · ne gördün · neden sorun · öneri

Sonunda özet tablonu unutma.
```

## Beklenen (kabul kriteri)

| Kontrol | Beklenen |
|---------|----------|
| Hitap | "KAHİN" der, "sahip" demez |
| Dil | Türkçe, az teknik terim, terim varsa günlük karşılığı yanında |
| Üslup | Kısa, bir espri olabilir, laf kalabalığı yok |
| Bitiş | 3 satırlık özet tablosu |
| Eleştiri notu | `tarih · konu · ne gördün · neden sorun · öneri` biçiminde |
| Rol sınırı | Dosyaya kendisi yazmaz; "roo'ya görev verelim" der |

## Sonuç
Merve'nin çıktısı beklentiyi karşılarsa prompt sabitlenir. Sapma varsa
`docs/continue_system_prompt.md` ilgili bölümü düzeltilip `python scripts/continue_config_kur.py` tekrar çalıştırılır.
