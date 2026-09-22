# Görev Panosu Kullanım Kılavuzu (DOCS-06)

> Kaynak: `src/company_master/orchestrator/task_board.py`
> Durum verisi: `data/orchestrator/task_board.json`
> İlgili: [[DOSYA_KILITLEME_PROTOKOLU]] · [[CHANGELOG]]

## 1. Amaç ve Kaynak Hiyerarşisi

Görev panosu, tüm ajanların (iç + harici) görevlerini tek yerden izleyen
merkezi sistemdir. Veri akışı:

```
data/orchestrator/task_board.json   (SSOT — ham veri)
        │  gorev_ekle / gorev_guncelle (otomatik)
        ▼
data/orchestrator/gorev_panosu.md   (Obsidian görünümü)
        │  agent_sync_yaz() (otomatik)
        ▼
AGENT_SYNC.md                       (kök senkron özeti)
```

`AI proje v1/V10/TODO.md`, insan tarafından okunan görev listesidir ve
panoyla tutarlı tutulur; **çakışma durumunda panonun JSON'u esastır.**
`AGENT_SYNC.md` otomatik üretilir; **elle büyük yeniden yazım yapılmaz.**

## 2. task_board.json Alan Şeması

| Alan | Tip | Açıklama |
|------|-----|----------|
| `task_id` | str | Benzersiz görev kimliği (örn. `P7-14`, `DOCS-05`) |
| `baslik` | str | Görev başlığı |
| `sahip` | str | Sorumlu ajan kimliği |
| `oncelik` | str | `P0` (kritik) … `P3` (düşük) |
| `durum` | str | `plan` / `aktif` / `review` / `done` / `blocked` |
| `baslangic` / `bitis` | str\|null | ISO-8601 zaman damgaları |
| `dosyalar` | list | Kilitle edilen dosya yolları |
| `not` | str | Serbest not alanı |
| `source` | str | `ic` (iç ajan) veya `harici` (harici ajan) |
| `from_agent` | str\|null | Görevi atayan ajan (harici görevlerde) |
| `attempts` | int | Retry sayacı (opsiyonel) |

## 3. Durum Yaşam Döngüsü

```
plan ──gorev_guncelle(durum="aktif")──► aktif ──► review ──► done
  ▲                                     │
  └────────────── blocked ◄─────────────┘
```

- `plan`: kuyrukta, henüz başlamadı.
- `aktif`: sahip ajan çalışıyor.
- `review`: çıktı üretildi, incelemede.
- `done`: tamamlandı; `bitis` dolu, dosya kilitleri bırakıldı.
- `blocked`: engel var; engel açıklaması `not` alanına yazılır.

## 4. API Kullanımı

### gorev_ekle

```python
from src.company_master.orchestrator import task_board as tb

tb.gorev_ekle("ORNEK-01", "Örnek görev", "mimar",
              oncelik="P1", dosyalar=[...],
              source="harici", from_agent="mimar")
```

- Aynı `task_id` tekrar eklenirse `ValueError: Gorev zaten var: ...`
  fırlatır (S-02/S-07 duplika koruması).
- `dosyalar` verildiyse kilitler **atomik** alınır
  (bkz. [[DOSYA_KILITLEME_PROTOKOLU]]).

### gorev_guncelle — `not` anahtar kelimesi tuzağı

`not` Python'da anahtar kelime olduğundan `gorev_guncelle(..., not=...)`
**sözdizimi hatasıdır**. Doğru kullanım:

```python
tb.gorev_guncelle("ORNEK-01", durum="done",
                  **{"not": "Tamamlandı"})
```

Bu davranış `test_gorev_guncelle_not_keyword_argument` testiyle garanti
altındadır (REFACTOR-01).

### Diğer Fonksiyonlar

| Fonksiyon | Amaç |
|-----------|------|
| `gorev_getir(task_id)` | Tek görevi sözlük olarak döner (yoksa `None`) |
| `gorev_listesi(durum=None)` | Tüm görevler; `durum` filtresi opsiyonel |
| `retry_istatistikleri(task_id)` | Retry/backoff ve context decay özeti |
| `handoff_ekle(task_id, agent_id, output_path, summary)` | Çıktı kaydı; aynı `task_id` tekrar gelirse `guncelleme_gecmisi` listesine ekler (duplicate-safe) |
| `handoff_tum()` | Tüm handoff kayıtları |

## 5. Görünüm Dosyalarını Yenileme

- `gorev_ekle`/`gorev_guncelle` çağrıları `_md_yaz()` üzerinden
  `gorev_panosu.md`'yi otomatik günceller. Markdown yazıcısı `gorulen_ids`
  setiyle duplika satırları atlar (S-07).
- `AGENT_SYNC.md` için: `tb.agent_sync_yaz()` — panodan tam yeniden üretim.
  Dosya "Otomatik Olusturuldu" stiliyle başlıyorsa tamamen yeniden yazılır;
  manuel içerik varsa otomatik bölüm sona eklenir.
- `data/orchestrator/AGENT_SYNC.md` kopyası kök dosyayla eş tutulur.

## 6. quick_task.py — Hızlı Harici Görev

```powershell
python scripts/quick_task.py --from-agent mimar --agent claude_code `
    --task ORNEK-99 --title "Araştırma" --task-type research `
    --run-mode orchestrator --review
```

Sıra: `brief_olustur` (workspace/external/<agent>/brief_<id>.md) →
`dispatch` (panoya kayıt + çalıştırma) → `--review` verilirse `review`
(PASS → done + handoff + AGENT_SYNC; FAIL → blocked).

Uçtan uca doğrulama: `tests/orchestrator/test_quick_task.py`
(VALIDATE-01).

## 7. Orkestratör CLI

```powershell
python -m src.company_master.orchestrator.cli dispatch <brief.json> `
    [--run-mode orchestrator|agent]
python -m src.company_master.orchestrator.cli review <task_id>
python -m src.company_master.orchestrator.cli status
python -m src.company_master.orchestrator.cli errors [--agent ...] [--task ...]
python -m src.company_master.orchestrator.cli sync
```

- Bilinen harici ajanlar: `cursor_grok`, `copilot`, `claude_code`,
  `roo_code`, `harici_ajan`.
- `orchestrator` modu görevi dahili çalıştırır (harici subprocess yok).

## 8. Test Kuralları

- Panoya yazan her test `tmp_path` + `monkeypatch` ile izole olmalı
  (bkz. [[DOSYA_KILITLEME_PROTOKOLU]] §7).
- Çalıştırma: `python -m pytest tests/orchestrator/ -q` — `pytest.ini`
  (`pythonpath = src`) sayesinde ek ortam değişkeni gerekmez.

## 9. Güncelleme Sorumlulukları

| Olay | Güncellenecek |
|------|---------------|
| Görev açıldı | `gorev_ekle` (pano otomatik) + `TODO.md` satırı |
| Görev bitti | `gorev_guncelle(durum="done")` + kilit bırakma + `TODO.md` + `CHANGELOG.md` |
| Karar değişti | `project_state.md` + gerekirse V9 bağlam dokümanı |
| Test eklendi | `CHANGELOG.md` test sayısı notu |

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ORKESTRASYON_AJANLAR_HUB]]
