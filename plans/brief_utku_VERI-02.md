# VERI-02 — OSB ihale izleyicisi

**Sahip:** utku · **Öncelik:** P1 · **Süre tahmini:** 3s
**Eski kimlik:** WK-02 (D-222'de devredildi; `WK-` öneki D-57 kanonik alan listesinde yok)

## Neden bu görev var

D-222 denetimi panodaki 65 kaydı tek tek ölçtü. Bu iş **hiç başlanmamış**: adı 42
dosyada geçiyor ama tek satır kod yok. `archive` durumunda gömülü kaldığı için
kimse görmüyordu. Gerçek backlog'a alındı ki tekrar unutulmasın.

## Kapsam

OSB (Organize Sanayi Bölgesi) ihale ilanlarını düzenli aralıkla izleyip yeni
ilanı tespit etmek.

Çıktı: `src/scrapers/osb_tender_monitor.py`

## Başlamadan önce ölç

Kod yazmadan önce şu üçü **ölçülecek**, varsayılmayacak:

1. Hangi OSB kaynakları izlenecek — liste var mı, yoksa kim belirliyor?
2. Kaynak HTML mi, RSS mi, API mi? Zaten çözülmüş bir tarayıcı altyapısı var mı
   (`src/scrapers/` altında yeniden yazılacak bir şey olmasın)?
3. "Yeni ilan" nasıl tanımlanıyor — kalıcı durum nerede tutulacak?

Bu üçü netleşmeden yazılan kod büyük olasılıkla çöpe gider.

## Kabul ölçütü

- Yeni ilan tespiti tekrarlanabilir: aynı ilan iki kez "yeni" sayılmaz.
- Kaynak erişilemezse görev sessizce başarılı olmaz — hata görünür.
- En az bir çalıştırılabilir kontrol bırakır.

## Bilinçli sınır

ponytail: tavan = tek kaynak + zamanlanmış tetik yok. Yükseltme yolu = kaynak
sayısı 1'i geçtiğinde kaynak listesini yapılandırmaya taşı; izleme sıklığı
konuşulunca tetiğe bağla.
