# TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01 — Brief (salih)

**Başlık:** [TEST] conftest.py pano-koruma fixture'ı canlı dış yazımı "kalıntı" sanıp eziyor (~3h)
**Öncelik:** P1 · **Kit:** `TOOLS_SCRIPTS_HUB` (AGENTS.md D-196)
**Kilitli dosya:** `tests/conftest.py`
**Hub:** `hubs/TOOLS_SCRIPTS_HUB.md` — ZORUNLU (B-14).

## Neden

Bulgu kaydı `data/orchestrator/bulgu_defteri.md:109` (ihsan 🔴, 2026-10-03):
`task_board.json` 19:25'te 134→131 göreve geri sarıldı (18:30 atanan 3 görev silindi).
`git checkout` 19:50 denemesi **7 saniye içinde tekrar ezildi** — o anda tam suite pytest
(PID 20624, 19:49) koşuyordu. `tests/conftest.py:83-128` (`_pano_dosyalari_yalitim`) +
`tests/conftest.py:48-80` (`_uretim_verisi_dokunulmaz`) `task_board.json`'ı test oturumu
başında bir kez okuyup oturum sonunda geri yazıyor (session-scoped snapshot); bu süre
içinde başka bir ajanın canlı attığı gerçek görev, suite'in elindeki eski kopya tarafından
"test kalıntısı" sanılıp sessizce siliniyor.

## Doğrulanacak varsayım

- `tests/conftest.py:48-80` + `83-128` içindeki fixture'ların session/function scope'u ve
  snapshot-restore zamanlaması varsayıldı; kodu aç, gerçek scope'u doğrula. Farklıysa **dur**,
  chat'e yaz.
- `task_board.json` dosyasının tek SSOT olduğu, testlerin onu okumaması/yazmaması gerektiği
  varsayıldı (TEST-SYNC-01/TEST-ISO-02 niyeti). Farklı bir niyet koddan çıkarsa **dur**, sor.
- Sorunun kökü "snapshot al → suite boyu sakla → suite sonu geri yaz" deseni; "testler gerçek
  dosyaya hiç dokunmamalı" ise çözüm farklı olabilir (ör. fixture'ın gerçek dosyayı hiç okumaması,
  yalnızca mock/tmp_path üzerinden çalışması). İkisi arasında seç, gerekçeyi brife yaz.

## Adımlar

1. `tests/conftest.py` içindeki `_uretim_verisi_dokunulmaz` ve `_pano_dosyalari_yalitim`
   fixture'larının gerçek `task_board.json`'a ne zaman/nasıl dokunduğunu ölç (satır numarası +
   okuma/yazma anı).
2. Kök nedeni doğrula: suite başlarken aldığı snapshot, suite bitene kadar bellekte eski kalıyor;
   suite ortasında başka süreç gerçek dosyayı güncellerse, suite sonundaki "geri yükleme" o güncel
   veriyi eski snapshot ile eziyor.
3. Düzelt: testler gerçek `task_board.json`'a **hiç dokunmasın** (yalnızca `tmp_path` yoluna
   yazsın) — zaten `_pano_dosyalari_yalitim` bunu `monkeypatch.setattr` ile büyük ölçüde yapıyor;
   asıl sızıntı `_uretim_verisi_dokunulmaz`'ın (varsa) gerçek dosyayı okuyup geri yazması. O
   davranışı kaldır veya `tmp_path`'e yönlendir.
4. Eş zamanlı yazım riskini azalt: `task_board.py`'de zaten `_pano_kilit()` var — test fixture'ı
   bu kilidi atlıyorsa, atlamasın ya da gerçek dosyaya dokunma ihtiyacını tamamen ortadan kaldır.

## Kabul kriteri

- [ ] Testler artık gerçek `task_board.json`'ı okumuyor/yazmıyor (ölçüm: suite koşarken başka
      terminalde `tb.gorev_ekle(...)` ile atılan görev, suite bitince panoda hâlâ duruyor).
- [ ] Yeni/düzeltilmiş `tests/test_pano_sema.py` veya ilgili test: suite ortasında dış yazımı
      simüle eden bir regresyon testi (gerçek dosyayı tmp_path kopyasıyla taklit edip suite'in
      onu ezmediğini doğrular).
- [ ] Mevcut test suite'i (`pytest tests/ -q`) yeşil kalır.

## Kurallar (ADMIN-KİT · D-196)
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut `monkeypatch`/`tmp_path` araçlarıyla çöz.
- **Teslimden önce** `hubs/TOOLS_SCRIPTS_HUB.md` "Kapanan işler" bölümüne `TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01` satırı yaz.

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak.

```bash
python scripts/ajan_chat.py ac salih TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan salih --task-id TEST-PANO-SNAPSHOT-DISARIDAN-YAZIM-01 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).**

```bash
python scripts/gorev_kutusu.py nobet --ajan salih
```

## Ilgili Nodlar

- [[Huginn Data Insights/data/orchestrator/bulgu_defteri.md]] — satır 109
- [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]]
