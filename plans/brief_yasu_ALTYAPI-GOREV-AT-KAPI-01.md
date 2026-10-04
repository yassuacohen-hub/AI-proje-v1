# ALTYAPI-GOREV-AT-KAPI-01 — Brief (yasu)

**Başlık:** [ALTYAPI] gorev_at.py cmd_at'i duzelt -> kapi_gecer() kilit kapisindan gecer (3s)
**Öncelik:** P1 · **Kit:** `ALTYAPI` (AGENTS.md D-196)
**Kilitli dosya:** `scripts/gorev_at.py`
**Bağımlılık:** `ALTYAPI-AJAN-CAKISMA-01` (kapandı, 2026-10-03 — `kapi_gecer()` bu görevde üretildi)
**Hub:** `hubs/ORKESTRASYON_AJANLAR_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

## Neden

`scripts/ajan_cakisma_kilidi.py` modülü `ALTYAPI-AJAN-CAKISMA-01` görevinde yazıldı, 12 testle
doğrulandı (`tests/test_ajan_cakisma_kilidi.py`), ve hub kaydında (`hubs/ADMIN_DASHBOARD_HUB.md`
satır 45-60) `kapi_gecer()` için açıkça **"geri çağrılabilir fonksiyon"** notu bırakıldı — yani
üretildi ama hiçbir yerden çağrılmıyor. Doğruladım: `scripts/gorev_at.py` içinde
`ajan_cakisma_kilidi` veya `kapi_gecer` adına **sıfır referans** var (`gorev_at.py:1-541` tam
tarandı).

Bu arada görev atama zincirinde ZATEN bir kilit kapısı var:
`src/company_master/orchestrator/task_board.py:587-605` (`_lock_alan`, `gorev_ekle()` içinden
`task_board.py:321-324`'te çağrılıyor) — ama bu fonksiyon `bayat()` (D-303, 24 saatten eski
kilit = sahipsiz) kontrolü yapmıyor. Bir ajan 24 saat önce kilitleyip bırakmışsa, `_lock_alan`
onu sonsuza kadar geçerli sayıp yeni atamayı `PermissionError` ile reddeder — oysa
`kapi_gecer()` (`ajan_cakisma_kilidi.py:104-116`) `aktif_kilitler()` (`ajan_cakisma_kilidi.py:52-55`)
üzerinden bayat kilitleri zaten eliyor. Ayrıca `hareket_uyarisi()`
(`ajan_cakisma_kilidi.py:85-101`) — başka bir ajanın kilit kapsamında yakın zamanda dosya
değişikliği olduysa uyarı üretir — `_lock_alan`'da hiç yok.

Sonuç: iki kapı aynı `data/orchestrator/file_locks.json`'u okuyor ama farklı kurallarla. Görev:
`kapi_gecer()`'i `cmd_at()` akışına ekleyip D-303 muafiyetini ve hareket uyarısını atama anında
da geçerli kılmak — `_lock_alan`'ı DEĞİŞTİRMEDEN, ona ek bir ön-kapı olarak.

## Doğrulanacak varsayım

- `scripts/gorev_at.py:244-332` (`cmd_at`) fonksiyonunun `tb.gorev_ekle(...)` çağrısından ÖNCE
  (D-58/D-57/D-66/D-80/D-217 kapılarından sonra, `scripts/gorev_at.py:302-319`'daki try bloğunun
  hemen öncesinde) uygun bir ekleme noktası olduğu varsayıldı. Farklıysa **dur**, panoya sorun aç.
- `ajan_cakisma_kilidi.kapi_gecer(yollar, ajan=None, kilitler=None) -> (bool, str)` imzası
  (`scripts/ajan_cakisma_kilidi.py:104-116`) sabit varsayıldı — `yollar` dosya listesi,
  `ajan` atanan ajan adı, dönüş `(gecer_mi, mesaj)`. Farklıysa **dur**, panoya sorun aç.
- `args.ajan` ve `args.dosya` (`_ayristir_liste` ile parse edilmiş, `scripts/gorev_at.py:48-51`)
  `cmd_at` içinde zaten mevcut varsayıldı — yeni bir argparse alanı GEREKMEZ. Farklıysa **dur**.
- Reddedilme durumunda yeni bir exit code kullanılacak: mevcut `PermissionError`→2 ile
  çakışmaması için **exit code 4** ("HATA (çakışma): ...") kullanılacağı varsayıldı. Farklı bir
  kod şeması isteniyorsa **dur**, KAHİN'e sor.
- `_lock_alan` (`task_board.py:587-605`) DEĞİŞTİRİLMEYECEK — bu görev sadece `gorev_at.py`'ye
  ön-kapı ekler, `task_board.py`'ye dokunmaz (dosya kilidi: `scripts/gorev_at.py` ile sınırlı).

## Adımlar

1. `scripts/gorev_at.py` başına `from ajan_cakisma_kilidi import kapi_gecer, hareket_uyarisi`
   (veya proje import yoluna göre doğru modül yolu) ekle.
2. `cmd_at()` içinde, `tb.gorev_ekle(...)` çağrısından önce: `args.dosya` listesi boş değilse
   `gecer, mesaj = kapi_gecer(dosyalar, ajan=args.ajan)` çağır. `gecer is False` ise mesajı
   yazdır (`print(f"HATA (çakışma): {mesaj}")`) ve `return 4`.
3. Aynı noktada `uyari = hareket_uyarisi()` çağır; `uyari` None değilse ekrana bilgi satırı olarak
   yazdır (atamayı DURDURMAZ, sadece bilgilendirir — `print(f"UYARI: {uyari}")`).
4. `tests/test_ajan_cakisma_kilidi.py`'ye veya yeni bir `tests/test_gorev_at_kapi.py`'ye şu
   senaryoyu ekle: bayat (24h+) kilit varken `cmd_at` çağrısı artık `_lock_alan`'ın
   `PermissionError`'una düşmeden (çünkü `kapi_gecer` zaten bayatı eledi ve geçti, `_lock_alan`
   kendi içinde zaten aynı sahip değilse engeller — burada ayrı ajan senaryosu net test et)
   beklenen davranışı gösterir.

## Kabul kriteri

- [ ] `scripts/gorev_at.py` içinde `kapi_gecer()` çağrısı var, `tb.gorev_ekle` öncesinde çalışıyor.
- [ ] Başka ajana ait AKTİF (bayat değil) kilitli dosyaya atama denemesi exit code 4 ile reddedilir,
      mesajda `kapi_gecer()`'in ürettiği çakışma metni görünür.
  - [ ] Başka ajana ait BAYAT (>24h) kilitli dosyaya atama denemesi `kapi_gecer` kapısından geçer
      (reddedilmez) — `_lock_alan` kendi kuralıyla ayrıca değerlendirilir, bu görev onu değiştirmez.
- [ ] `hareket_uyarisi()` None değilse ekrana yazılır, atamayı engellemez.
- [ ] Yeni/değişen test dosyası `pytest` ile yeşil.

## Kurallar (ADMIN-KİT · D-196)

- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut `ajan_cakisma_kilidi.py` modülünü kullan.
- `_lock_alan`/`task_board.py`'ye DOKUNMA — bu görevin kapsamı sadece `gorev_at.py`.
- **Teslimden önce** `hubs/ORKESTRASYON_AJANLAR_HUB.md`'nin "Kapanan işler" bölümüne
  `ALTYAPI-GOREV-AT-KAPI-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)

- Brifteki ekleme noktası (`tb.gorev_ekle` öncesi) kodda tutmuyorsa → `ac` ile sorun aç,
  **uydurma, durma**.
- Exit code 4 başka bir anlamda kullanılıyorsa → sorun aç, **devam etme**.

```bash
python scripts/ajan_chat.py ac yasu ALTYAPI-GOREV-AT-KAPI-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id ALTYAPI-GOREV-AT-KAPI-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id ALTYAPI-GOREV-AT-KAPI-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id ALTYAPI-GOREV-AT-KAPI-01 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).** İnsan tetiği bekleme; tek komutla nöbete gir:

```bash
python scripts/gorev_kutusu.py nobet --ajan yasu
```

- Çıkış `0` = **İŞ VAR** → hemen yap: soruya cevap yaz, görevi `al`.
- Çıkış `3` = 60 dk iş gelmedi → ihsan'a kısa rapor yaz, sonra kapat.
- `nobet` dönmeden "bitti" denmez.

## Ilgili Nodlar

- [[Huginn Data Insights/scripts/ajan_cakisma_kilidi]]
- [[Huginn Data Insights/scripts/gorev_at]]
- [[Huginn Data Insights/src/company_master/orchestrator/task_board]]
- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
- [[Huginn Data Insights/AGENTS]]
