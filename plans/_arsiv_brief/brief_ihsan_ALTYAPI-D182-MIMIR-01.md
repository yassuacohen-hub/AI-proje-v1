# ALTYAPI-D182-MIMIR-01 — MIMIR kanonik ajan listesinde yok

## Görev Özeti
`tests/test_d182_mimir.py::test_mimir_kanonik_ajan` kırık:
`assert 'mimir' in ('ihsan', 'utku', 'salih', 'yasu')`.
D-182 MIMIR'i 5. kanonik ajan ilan etti ama kod hiç güncellenmedi.

## Kök Neden (doğrulandı)
`src/company_master/orchestrator/trigger.py:50`
```python
AJANLAR: tuple[str, ...] = ("ihsan", "utku", "salih", "yasu")
```
Bu tuple tek doğruluk kaynağı; şu dosyalar ondan türüyor:
- `orchestrator/duzen.py:40` → `AJANLAR = list(trigger.AJANLAR)`
- `scripts/gorev_at.py:64` → `AJANLAR = trigger.AJANLAR`

## Çıktı
- `trigger.AJANLAR`'a `"mimir"` eklenecek
- `ajan_normalize` MIMIR varyantlarını (`Mimir`, `MIMIR`, `ajan mimir`) kanonik `mimir`'e çevirsin
- `data/orchestrator/triggers/mimir.jsonl` posta kutusu oluşsun (boş dosya yeterli)
- D-63 architect kapısı gözden geçirilsin: MIMIR architect alabilir mi? Kararı brief'e yaz,
  varsayım yapma — gerekirse KAHİN'e sor

## Yan Etki Uyarısı
`AJANLAR` genişleyince `gorev_at.py pano` tüm ajanların tetiğini tarar, `tetik_senk`
her ajan için dosya arar. `mimir.jsonl` yoksa sessiz atlama olmamalı — Öneri-1 ile
eklenen `exit 3` davranışı korunacak.

## Kabul Kriteri
```
set PYTHONIOENCODING=utf-8 && python -m pytest tests/test_d182_mimir.py -q
# 1 failed -> 0 failed
set PYTHONIOENCODING=utf-8 && python -m pytest tests/test_sessiz_basari.py tests/test_gorev_at_kapi.py tests/test_gorev_at_mod.py -q
# yesil kalmali
set PYTHONIOENCODING=utf-8 && python -m pytest tests/ -q --tb=line
# yeni kirik yok
```

## D-63 Architect Kapısı — Karar (2026-09-23, ihsan)

**Uygulanan:** `gorev_at.ARCHITECT_AJANLARI = ("ihsan", "utku")` **değişmedi**. MIMIR `--mod architect` ile görev açamaz → exit 5.

**Gerekçe (varsayım değil, D-182 metninden):**
- D-182 MIMIR'i "Orkestratör **Asistanı**" olarak tanımlar. Seviye 0 = salt-okunur, yalnız `TEKLIF:` yazabilir. Architect modu görev *açar* — Seviye 0 ile çelişir.
- Seviye 1 (abrakadabra + hmac) zaten tam devralma; devralmada MIMIR orkestratör kimliğiyle çalışır, ayrıca architect hakkı gerekmez.
- D-63 metni architect'i `ihsan`/`utku` ile sınırlar; D-182 bu listeyi genişletmez.

**Kilitlendi:** [`test_architect_modu_mimir_reddedilir()`](../tests/test_gorev_at_mod.py:71) — rc 5 + `HATA (D-63)`.

**KAHİN'e açık soru:** Seviye 1'de (devralma sonrası) MIMIR architect görevi açabilmeli mi? "Evet" ise `ARCHITECT_AJANLARI`'na `"mimir"` eklenir ve yukarıdaki test kabul testine döner. Karar gelene kadar mevcut kısıt yürürlükte.

**Yan not (D-182 gizlilik maddesi):** `"abrakadabra"` artık `AJAN_TAKMA_ADLAR` içinde bir anahtar. Bu bir ad eşlemesi, parola karşılaştırması değil; ama D-182 "parola sistem promptunda/logda görünmesin" diyor. `trigger.py` kaynak kodda görünüyor. Test bunu zorunlu kılıyor (`ajan_normalize("abrakadabra") == "mimir"`). KAHİN isterse bu anahtar kaldırılıp test güncellenebilir — o karar da KAHİN'in.

## Kurallar
- D-86 / D-66 / D-55 adlandırma
- Testi değiştirerek geçirme yasak

## Süre Tahmini
2 saat

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
