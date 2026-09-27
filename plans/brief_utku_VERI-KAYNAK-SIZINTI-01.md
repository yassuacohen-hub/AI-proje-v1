# Brif — VERI-KAYNAK-SIZINTI-01: ostim kaydında ASO biçimli payload

**Başlık:** [VERI] TEŞHİS: ostim kaydında ASO biçimli payload (102 kayıt) (2s)
**Öncelik:** P2 · **Kit:** `VERI` (AGENTS.md D-196)
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

**Sahip:** utku · **Süre:** 2s · **Veren:** ihsan
**Tür:** TEŞHİS (düzeltme ikinci adım, ölçümden sonra karar)

---

## Neden
`VERI-SEKTOR-01` ölçümü sırasında çıktı. `source_records` içinde
`source_name='ostim.org.tr'` olan **102 kayıt**, ASO'nun biçiminde veri
taşıyor:

```
2SSOFT YAZILIM BİLİŞİM A.Ş.        | sektor="35. MESLEK GRUBU" | kaynak=None
5S OTOMOTİV İMALAT SAN. TİC. A.Ş.  | sektor="24. MESLEK GRUBU" | kaynak=None
AKKOR ISIL İŞLEM ÇELİK İMALAT      | sektor="38. MESLEK GRUBU" | kaynak=None
AHMET SEÇEN                        | sektor="21. MESLEK GRUBU" | kaynak=None
```

**Neden bu yanlış:** OSTİM bir organize sanayi bölgesi, ASO bir ticaret/sanayi
odası. "N. MESLEK GRUBU" ASO'nun oda içi gruplama biçimi; OSTİM sitesinde bu
ifade geçmez. Ayrıca `raw_payload.kaynak` alanı `None` — diğer ostim
kayıtlarında bu alan dolu.

## 2. İki olasılık

**(a) Yanlış `source_id`.** ASO kazıyıcısı veya yükleyici, 102 kaydı ostim'in
kaynak kimliğiyle yazmış. Bu durumda düzeltme basit: `source_id` güncellenir.

**(b) Birleştirme kirlenmesi.** Aynı firma iki kaynakta bulunmuş, tekilleştirme
sırasında ASO'nun payload'ı ostim kaydının üzerine yazılmış. Bu durumda sorun
tek seferlik değil — **tekilleştirme mantığında** ve her yeni çekimde tekrar
eder.

Ayrım kritik: (a) 102 satırlık tek seferlik tamir, (b) kod hatası.

## Adımlar

Ölçüm adımları — kod yazmadan önce:

1. **102 kaydın `raw_payload` anahtar kümesini** ostim'in normal
   payload'ıyla karşılaştır. ASO anahtarları
   (`naceKod`, `naceDetay`, `ticaretSicilNo`, `meslekGrubu`) varsa → (a).
   ostim anahtarları (`slug`, `osb_parsel`, `nace_confidence`) da varsa → (b),
   payload'lar birleşmiş.

2. **Aynı firmanın ASO kaydı da var mı?** `raw_name` veya vergi no ile
   `source_name='aso.org.tr'` içinde ara. Varsa → çift kayıt, (b) lehine.

3. **`source_records` birincil anahtarı ve tekilleştirme kısıtı ne?**
   Şemada `unique(source_id, raw_external_id)` gibi bir kısıt varsa, aynı
   dış kimlik iki kaynakta çakışıyor olabilir.

4. **102 sayısı kapalı mı?** `sektor` dışında ASO'ya özgü başka alan
   (`ticaretSicilNo`, `naceDetay`) ostim kayıtlarında kaç yerde var?
   Sayı 102'den büyükse sızıntı `sektor` alanından geniş.

## 4. Karar noktası

Ölçüm (a) derse: `source_id` düzeltme betiği + tek satır rapor → kapat.

Ölçüm (b) derse: **görev genişler.** Tekilleştirme mantığı gözden geçirilir,
regresyon testi yazılır. Bu durumda yeni brif istenir, bu görev teşhis
raporuyla kapanır.

## Kabul kriteri
- Hangi olasılığın doğru olduğu **kanıtla** yazılı (payload anahtar karşılaştırması)
- Sızıntının gerçek boyutu ölçülü (102 mi, daha fazla mı)
- (a) ise düzeltme uygulanmış + öncesi/sonrası sayı raporda
- (b) ise kök neden dosya:satır olarak işaretli, yeni görev önerisi yazılı
- **Veri silinmemiş.** Şüpheli kayıt düzeltilir veya işaretlenir, atılmaz

## 6. Uyarı

Bu 102 kayıt **zararsız görünüyor** çünkü sektör alanı şu an hiçbir yerde
kullanılmıyor. `VERI-SEKTOR-01` sektör adını `companies`'e taşıdığında bu
kayıtlar panoda "35. MESLEK GRUBU" diye görünür hale gelir.

**Sıralama önerisi:** bu teşhis SEKTOR-01'den *önce* veya *paralel* yapılsın.
Sonrasına bırakılırsa kirli veri arayüze çıkar.

---

*ponytail: sadece teşhis, düzeltme koşullu. Skipped: tekilleştirme refaktörü,
add when: ölçüm (b) derse.*

## Doğrulanacak varsayım

> D-66 brif sözleşmesi. Her madde bu brifin gövdesinde **ölçülmüş** bir değere dayanır.
> Kodda tutmayan madde varsa **dur**, panoya sorun aç, uydurma.

- `source_records` içinde `source_id` = ostim olan 102 kayıtta ASO biçimli payload varsayıldı. Sayı farklıysa yeniden ölç.
- İki olasılık olduğu varsayıldı: (a) yanlış `source_id`, (b) birleştirme kirlenmesi. **Ölçüm kararı vermeden kod yazılmayacak.**
- Bu görev **teşhis** türü: çıktı bir ölçüm raporu; düzeltme ikinci adım ve ayrı karar.

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Varsayım tutmuyorsa, bir faz tıkandıysa veya @mention aldıysan
chat'e yazmak **zorunludur** — brifi yeniden okuyup beklemek değil.

```bash
python scripts/ajan_chat.py ac utku VERI-KAYNAK-SIZINTI-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-KAYNAK-SIZINTI-01
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-KAYNAK-SIZINTI-01 --ozet "<ozet>"
```

Teslimden önce `hubs/VERI_KALITESI_HUB.md` dosyasının "Kapanan işler" bölümüne `VERI-KAYNAK-SIZINTI-01`
satırını yaz (B-14 kapısı) — yazılmazsa teslim reddedilir.

## Ilgili Nodlar

- [[hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
