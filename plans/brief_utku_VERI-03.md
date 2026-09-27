# VERI-03 — Proxy rotasyonu

**Sahip:** utku · **Öncelik:** P2 · **Süre tahmini:** 2s
**Eski kimlik:** WK-03 (D-222'de devredildi; `WK-` öneki D-57 kanonik alan listesinde yok)

## Neden bu görev var

D-222 denetiminde **hiç başlanmamış** olarak ölçüldü. `archive` durumunda gömülü
olduğu için backlog'da görünmüyordu.

## Kapsam

Tarama isteklerinde IP/proxy rotasyonu.

Çıktı: `src/scrapers/proxy_rotation.py`

## Başlamadan önce ölç — bu görev VERI-02'ye bağlı

**Önce VERI-02 yapılmalı.** Gerekçe: proxy rotasyonu bir ihtiyaca cevaptır,
kendi başına değer üretmez. Ölçülecekler:

1. Gerçekten engelleniyor muyuz? Hangi kaynak, hangi sıklıkta, hangi hata kodu?
   **Ölçüm yoksa bu görev yazılmamalı** — YAGNI.
2. Kaynağa saygılı gecikme + `robots.txt` uyumu sorunu zaten çözüyor mu? Çözüyorsa
   proxy'ye hiç gerek yok, en ucuz çözüm budur.
3. Proxy havuzu nereden gelecek? Ücretli servis kararı ürün sahibinindir, ajanın değil.

## Kabul ölçütü

- Yalnızca 1. maddede somut engellenme ölçümü varsa kod yazılır.
- Kimlik bilgileri koda gömülmez.
- En az bir çalıştırılabilir kontrol bırakır.

## Bilinçli sınır

ponytail: tavan = sıralı rotasyon, sağlık kontrolü yok. Yükseltme yolu = ölü
proxy görülünce sağlık kontrolü ekle.
