# ALTYAPI-AJAN-CAKISMA-01 — Brief (ihsan)

**Başlık:** [ALTYAPI-KİT] Eşzamanlı ajan çalışmasında kilit kapısı (4s)
**Öncelik:** P1 · **Kit:** `ALTYAPI-KİT` (D-196)
**Kilitli dosya:** `scripts/ajan_cakisma_kilidi.py`
**Bağımlılık:** yok
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif. Toplu iş birden çok brife bölünmez;
> tek brifte `## Faz A/B/C...` başlıklarıyla anlatılır. Faz başına ayrı dosya açmak yasak.

## Neden

FAZ-0 kök hijyeni çalışması **ihsan ajanı aktifken** yürütüldü. Pano'da
ihsan'a ait açık görev görünmediği için (3 açık görevin sahibi de `utku`)
"serbest çalışıyor" varsayıldı ve **dosya kilidi sorgulanmadan 130 dosya
taşındı**. Canlı ölçüm betiği `_defter_olcum.py` arşive kaydı (geri alındı).

Kanıt: `data/orchestrator/FAZ0_RAPOR_kok_hijyeni_2026-09-29_orkestrator.md`
Zaman çizelgesi: `_defter_olcum.py` 00:29:53 doğdu → 00:30:31 arşive taşındı.

AGENTS.md "Bunlardan birinin aktif işi varsa dokunma" kuralı **görev adı**
düzeyinde sorgulanarak çalıştır; **dosya kilidi** düzeyinde sorgulanmadı.
Panoda görev görünmemesi, dosyanın boşta olduğu anlamına gelmiyor.

## Doğrulanacak varsayım

> Zorunlu bölüm (D-66 brif sözleşmesi). Brief yazarken **sabitlenen** her tablo adı, kolon adı,
> fonksiyon imzası, satır numarası ve eşik değeri buraya bir madde olarak geçer.

- `scripts/gorev_kutusu.py` kilit okuma komutu **adı** varsayıldı. Farklıysa
  **dur**, panoya sorun aç, uydurma.
- `data/orchestrator/task_board.json` görev listesi kaynağı varsayıldı
  (`tb.STATE_DIR` üzerinden). Farklıysa **dur**, panoya sorun aç.
- `tests/test_kok_politikasi.py` içindeki `VAULT_KOK` (satır 80) ve
  `TEK_KULLANIMLIK_ONEK` (satır 84-86) tanımları **aynen korunacak**.
  Değiştirilecekse **dur**, panoya sor.
- `IZIN_KILIT_ESIK=<saniye>` eşiği varsayıldı. Kodda başka değer varsa
  **dur**, KAHİN'e sor.

## Adımlar

### Faz A — Kilit sorgu yardımcısı (en riskli faz, ilk)

1. `scripts/ajan_cakisma_kilidi.py` yaz: aktif kilitleri döndüren saf fonksiyon.
   - **Kök neden:** Kilit bilgisi panoda `dosyalar` alanında; serbest çalışan
     ajanın kilidi yoktur ama **dosya hareketi** vardır.
   - **Etkilenen dosya:** `scripts/ajan_cakisma_kilidi.py` (yeni)
   - **Doğrulama:** `python scripts/ajan_cakisma_kilidi.py --ajan ihsan`
     → kilit varsa liste basar, yoksa boş.

2. Aynı modüle "son N dakikada değişen dosya" sorgusunu ekle (eşik env'den).
   - **Doğrulama:** `python scripts/ajan_cakisma_kilidi.py --kayitli-son 5`
     → son 5 dakikada değişen dosyaları basar.

### Faz B — Taşıma kapısı (arşivleme iki aşamalı)

3. Toplu taşıma/arşivleme komutundan **önce** kilit kapısı çağrısı eklensin.
   Kilit görünüyorsa **işlemi reddet**, hangi dosyada hangi ajana bağlıysa
   hata mesajına yaz.
   - **Etkilenen dosya:** `scripts/gorev_at.py` veya taşımayı yapan komut
   - **Doğrulama:** kilitli dosya varken komut **non-zero** döner.

4. Aynı kapı **test dosyaları** için de geçerli olmalı (O3).
   - **Doğrulama:** kilitli bir `tests/` dosyasına yazma denemesi reddedilir.

## Kabul kriteri

- [ ] `python scripts/ajan_cakisma_kilidi.py --ajan <ajan>` çalışıyor ve
      kilit varsa dosya listesi basıyor.
- [ ] Kilitli dosyaya taşıma/yazma denemesi **reddediliyor** (non-zero exit).
- [ ] `tests/test_kok_politikasi.py` içindeki 2 mandal testi **bozulmadan**
      geçiyor: `python -m pytest tests/test_kok_politikasi.py -q` → 5 passed.
- [ ] Faz A + Faz B tek komutla doğrulanmış çıktı üretiyor.
- [ ] Bu brifin kilidi (`tests/test_kok_politikasi.py`) görev boyunca **serbest**;
      yalnız yeni dosya (`ajan_cakisma_kilidi.py`) kilitlidir.

## Kurallar (ALTYAPI-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle. Ayrı dosyaya yazma.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Teslimden önce** yukarıdaki `**Hub:**` dosyasının "Kapanan işler" bölümüne
  `ALTYAPI-AJAN-CAKISMA-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**:

- Brifteki bir varsayım kodda tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.
- Bir faz tıkandıysa → sorun aç, **sonraki faza geç**, zinciri durdurma.
- @mention aldıysan → P0 5-10 dk, P1 10-15 dk, P2 15-30 dk içinde cevap **zorunlu**.

```bash
python scripts/ajan_chat.py ac ihsan ALTYAPI-AJAN-CAKISMA-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id ALTYAPI-AJAN-CAKISMA-01
python scripts/chat_gonder.py --to cline --type hata --task-id ALTYAPI-AJAN-CAKISMA-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan ihsan --task-id ALTYAPI-AJAN-CAKISMA-01 --ozet "<ozet>"
```

Teslim öncesi zorunlu kapılar:
1. `python -m pytest tests/test_kok_politikasi.py -q` → 5 passed (mandal bozulmadı)
2. `python scripts/kodlama_denetim.py` → temiz
3. `hubs/ADMIN_DASHBOARD_HUB.md` "Kapanan işler" bölümüne görev satırı (B-14)
4. `ihsan_project_context.md` §KALDIĞIM YER + §Oturum Günlüğü güncellendi (D-219)

## Ilgili Nodlar
> **Zorunlu (D-218).** Obsidyen proje hafızasıdır. **En az 2 wikilink.**

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani]]
- [[Huginn Data Insights/AGENTS]] · D-55 · D-57 · D-66 · D-217 · D-221 · D-268
- [[Huginn Data Insights/ihsan_project_context]] · [[plans/_brief_sablon]]
- Kanıt: `data/orchestrator/FAZ0_RAPOR_kok_hijyeni_2026-09-29_orkestrator.md`
- Mandal: `tests/test_kok_politikasi.py:74-124`

