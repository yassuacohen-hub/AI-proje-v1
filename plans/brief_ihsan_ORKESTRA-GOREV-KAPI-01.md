# ORKESTRA-GOREV-KAPI-01 — Gorev atama kapisini duzelt

## Gorev Ozeti
Bugun `ADMIN-UX-SIDEBAR-TAB` brifsiz atandi: tetik `talimat` alani var olmayan
bir brif dosyasini isaret etti, pano `brief` alani bos kaldi, Utku isi brifsiz
baslatti. Bu D-66/D-80 ihlaliydi ve **arac izin verdigi icin** oldu. Bu gorev
ayni hatayi makine seviyesinde imkansiz kilar.

## Mevcut Durum (kanit)
- `scripts/gorev_at.py:223-227` — D-66 kontrolu var ama kapisi gevsek:
  ```python
  brief_yolu = Path(f"plans/brief_{args.ajan}_{args.task_id}.md")
  if not brief_yolu.exists() and not args.talimat:   # <-- "and" = kacak yolu
  ```
  `--talimat` dolu ise brif diskte olmasa da gorev panoya giriyor. Tam olarak
  bugunku ihlalin yolu bu.
- `brief_yolu` **goreli path** — `gorev_at.py` vault disindan calistirilirsa
  yanlis dizine bakar, `exists()` sessizce False doner.
- `gorev_ekle()` cagrisinda `brief=` ve `talimat=` **hic gecilmiyor** (bkz. 237-244);
  bu yuzden pano `brief` alani bos kaliyor.
- `gorev_at.py`'de `guncelle` alt komutu yok (Yasu ORKESTRA-BRIEF-TALIMAT-01 bulgusu)
  — duzeltme icin elle script yazmak gerekiyor, bu D-87 (tek komut) ihlali.

## Is Maddeleri
1. **Kapiyi sikilastir:** `and` → `or` mantigina gec. Kabul sarti (D-80, uc sart birlikte):
   brif dosyasi diskte var **VE** `--talimat` dolu. Biri eksikse `return 6`,
   hata metninde hangi sartin eksik oldugu yazsin.
2. `brief_yolu` mutlak yapilacak: `KOK / "plans" / f"brief_{ajan}_{task_id}.md"`.
   `data/orchestrator/<TASK>_brif_*.md` deseni de gecerli sayilir (D-66 iki yol tanir) —
   ikisinden biri varsa yeterli.
3. `gorev_ekle()` cagrisina `brief=<bulunan goreli yol>` ve `talimat=args.talimat`
   eklenecek; pano `brief` alani bir daha bos kalmayacak.
4. **`guncelle` alt komutu ekle** (D-87): 
   `python scripts/gorev_at.py guncelle --task-id X [--brief Y] [--talimat Z] [--oncelik P1] [--durum aktif]`
   → `tb.gorev_guncelle()` cagirir. `--brief` verilirse dosya varligi dogrulanir.
5. **Sessiz basari yasagi (risk 1):** `cmd_at` ve `guncelle` 0 kayit etkilediyse
   exit 0 donmeyecek — `return 1` + stderr mesaji. Ayni kural `scripts/tetik_senk.py`
   icin de: 0 dosya tarandiysa bu **hata**, basari degil.
6. **Pano cift gosterim bug'i (bugun tespit edildi):** `cmd_pano()` satir 305:
   ```python
   ajanlar = sorted({str(t.get("sahip") or "?") for t in tb.gorev_listesi()})
   ```
   Ajan listesi panodaki `sahip` alanlarindan turetiliyor. Panoda D-60 oncesi
   `sahip: "cline"` kayitlari var; `bekleyen_tetikler("cline")` alias tablosuyla
   `yasu`ya cozuluyor ve **ayni tetik dosyasi iki kez okunuyor**. Sonuc: pano
   ciktisinda ayni gorev hem `[cline]` hem `[yasu]` satirinda gorunuyor
   (kanit: 2026-09-23 11:09 pano ciktisinda ALTYAPI-KILIT-OTOMATIK-01 ve
   ALTYAPI-TETIK-ARSIV-01 cift listelendi; diskte tek kayit var).
   Duzeltme: `ajanlar = list(trigger.AJANLAR)` — kanonik liste tek kaynak (D-60).
   Bu yalnizca goruntu hatasidir, veri bozulmasi yok; yine de pano guvenilirligini
   dusurdugu icin bu gorevde kapatilacak.
7. Test: `tests/test_gorev_at_kapi.py`
   - brif yok + talimat dolu → exit 6 (eskiden 0 donuyordu, regresyon kilidi)
   - brif var + talimat bos → exit 6
   - brif var + talimat dolu → exit 0 **ve** panoda `brief` alani dolu
   - `guncelle --brief <olmayan dosya>` → sifirdan farkli exit
   - `tetik_senk` 0 dosya → sifirdan farkli exit
   - panoda `sahip: "cline"` kaydi varken `pano` ciktisi ayni task_id'yi bir kez listeler

## Dosyalar
- `scripts/gorev_at.py`
- `scripts/tetik_senk.py`
- `tests/test_gorev_at_kapi.py` (yeni)

## Kurallar
- D-66/D-80 makine zorlamasi, D-87 tek komut, D-86 cmd.exe, D-184 wikilink.
- Var olan `at` alt komutunun imzasi bozulmayacak; sadece dogrulama sikilasir.

## Teslim
```
python scripts/gorev_kutusu.py teslim --task-id ORKESTRA-GOREV-KAPI-01 --ajan ihsan --ozet "<ozet>" --cikti data/orchestrator/ORKESTRA-GOREV-KAPI-01_rapor_2026-09-23_ihsan.md
```

## Sure Tahmini
4s

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
