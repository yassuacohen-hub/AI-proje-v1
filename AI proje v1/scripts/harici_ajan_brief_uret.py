#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Harici ajan brief üretme scripti.

harici_ajan_gorevleri.json'u okuyup her ajan icin
workspace/external/{ajan}/brief.md uretir.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "data" / "orchestrator"
HARICI_GOREVLER = STATE_DIR / "harici_ajan_gorevleri.json"
EXTERNAL_DIR = ROOT / "workspace" / "external"

AJANLAR = {
    "copilot": {
        "ad": "GitHub Copilot",
        "rol": "CI/CD, test, deploy, operasyon otomasyonu",
    },
    "claude_code": {
        "ad": "Claude Code",
        "rol": "Mimari dokümantasyon, güvenlik denetimi, teknik borç",
    },
    "cursor_grok": {
        "ad": "Cursor Grok",
        "rol": "Code review, refactor, test üretme",
    },
}


def _read_json(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _gorev_sec(gorevler: list[dict], ajan_id: str) -> list[dict]:
    return [g for g in gorevler if g.get("ajan") == ajan_id]


def _brief_ust(ajan_id: str, gorevler: list[dict]) -> str:
    ajan = AJANLAR.get(ajan_id, {})
    satir = f"""# {ajan.get('ad', ajan_id)} — Otomatik Görev Brief'i

> **Paket ID:** `EXT-{ajan_id.upper()}-{datetime.now().strftime('%Y%m%d')}`
> **Tarih:** {datetime.now().isoformat(timespec='seconds')}
> **Proje:** Huginn Data Insights — Ankara B2B Company Master
> **Rol:** {ajan.get('rol', ajan_id)}
> **Öncelik:** P0/P1/P2

---"""
    return satir


def _gorev_bolumu(gorev: dict) -> str:
    return f"""
## Görev: {gorev.get('gorev_id')} — {gorev.get('baslik', '')}

**Açıklama:** {gorev.get('aciklama', '')}

### Beklenen Çıktı
- **Dosya:** `{gorev.get('beklenen_cikti', '')}`
- **Bağımlılıklar:** {', '.join(gorev.get('bagimliliklar', [])) or 'Yok'}

### Kabul Kriterleri
- Görev dosyalarını oku, sadece izin verilen dosyaları değiştir.
- Çıktıyı `workspace/external/{gorev.get('ajan', '')}/output/` altına yaz.
- Tamamlanınca `harici_ajan_sonuc_topla.py` çalıştır.
"""


def _kisitlar() -> str:
    return """
## Kısıtlar
1. Proje kökü DEĞİŞTİRİLEMEZ.
2. Harici ajan `workspace/external/{ajan}/output/` dışına dosya yazamaz.
3. `.env` / secret / KVKK verisine erişim YOK.
4. Üretim veritabanına erişim YOK.
5. Kod değişikliği yalnızca görevle ilgili dosyalara yapılır.
"""


def _baglam() -> str:
    return """
## Bağlam Dosyaları
- `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
- `AI proje v1/V10/TODO.md`
- `data/orchestrator/task_board.json`
- `AGENT_SYNC.md`
"""


def uret() -> None:
    if not HARICI_GOREVLER.exists():
        print(f"Harici ajan gorevleri dosyasi yok: {HARICI_GOREVLER}")
        return

    gorevler = _read_json(HARICI_GOREVLER)
    if not gorevler:
        print("Harici ajan gorevleri bos.")
        return

    for ajan_id in AJANLAR:
        gorev = _gorev_sec(gorevler, ajan_id)
        if not gorev:
            continue

        parca = [_brief_ust(ajan_id, gorev)]
        for g in gorev:
            parca.append(_gorev_bolumu(g))
        parca.append(_kisitlar())
        parca.append(_baglam())

        brief_path = EXTERNAL_DIR / ajan_id / "brief.md"
        _write_text(brief_path, "\n".join(parca))
        print(f"Brief uretildi: {brief_path}")


if __name__ == "__main__":
    uret()
