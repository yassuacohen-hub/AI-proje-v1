"""Orkestrator - Merkezi Gorev Panosu ve dosya-lock takibi.

Eski sistemde "herkes herkesin ne yaptigini surekli bir listede takip ediyordu"
mekanizmasinin yeniden kurulumu:

- data/orchestrator/task_board.json   -> gorevler (atama, durum, sahiplik)
- data/orchestrator/file_locks.json   -> dosya sahiplik lock'lari (cakisma onleme)
- data/orchestrator/state.json        -> orkestrator canli durumu

Ajanlar (ic + dis) panoya gorev atar/ceker; iki ajan ayni dosyayi ayni anda
sahiplenemez.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
STATE_DIR = ROOT / "data" / "orchestrator"

TASK_BOARD = STATE_DIR / "task_board.json"
FILE_LOCKS = STATE_DIR / "file_locks.json"
STATE_JSON = STATE_DIR / "state.json"
TASK_MD = STATE_DIR / "gorev_panosu.md"

GOREV_DURUMLARI = ("plan", "aktif", "review", "done", "blocked")


def _ensure() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not TASK_BOARD.exists():
        TASK_BOARD.write_text("[]", encoding="utf-8")
    if not FILE_LOCKS.exists():
        FILE_LOCKS.write_text("{}", encoding="utf-8")
    if not STATE_JSON.exists():
        STATE_JSON.write_text("{}", encoding="utf-8")


def _read_json(path: Path) -> Any:
    _ensure()
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    _ensure()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8")


# ---- Gorev Panosu ----
def gorev_ekle(
    task_id: str,
    baslik: str,
    sahip: str,          # ic ajan id veya harici ajan id
    oncelik: str = "P1",
    baslangic: str | None = None,
    bitis: str | None = None,
    dosyalar: list[str] | None = None,
) -> dict:
    """Panoya gorev ekle. dosyalar -> file-lock sahipligi de alir."""
    _ensure()
    board = _read_json(TASK_BOARD)
    if any(t["task_id"] == task_id for t in board):
        raise ValueError(f"Gorev zaten var: {task_id}")
    task = {
        "task_id": task_id,
        "baslik": baslik,
        "sahip": sahip,
        "oncelik": oncelik,
        "durum": "plan",
        "baslangic": baslangic or datetime.now().isoformat(timespec="seconds"),
        "bitis": bitis,
        "dosyalar": dosyalar or [],
        "not": "",
    }
    # Atomik: once tum lock'lar denenir; hata olursa gorev eklenmez.
    if dosyalar:
        for d in dosyalar:
            _lock_alan(sahip, d, task_id)
    board.append(task)
    _write_json(TASK_BOARD, board)
    _md_yaz(board)
    return task


# ---- K7: Retry Context Decay ----
MAX_ATTEMPTS = 3


def retry_istatistikleri(task_id: str) -> dict:
    """Gorev icin retry istatistikleri (context decay icin)."""
    gorev = gorev_getir(task_id)
    if not gorev:
        return {"attempts": 0, "backoff_sn": 0, "context_mode": "full"}
    attempts = gorev.get("attempts", 0)
    # Exponential context decay: her retry'de context %50 azalir
    if attempts <= 1:
        mode = "full"       # ~3000 token
    elif attempts == 2:
        mode = "hatali"     # ~1000 token (sadece hata + dosyanin degisen kisimlari)
    else:
        mode = "handoff"    # ~500 token (sadece handoff)
    backoff_sn = 2 ** (attempts - 1) * 60  # 60s, 120s, 240s
    return {"attempts": attempts, "backoff_sn": backoff_sn, "context_mode": mode}


def gorev_guncelle(task_id: str, durum: str | None = None, **fields) -> dict | None:
    board = _read_json(TASK_BOARD)
    for t in board:
        if t["task_id"] == task_id:
            if durum:
                if durum not in GOREV_DURUMLARI:
                    raise ValueError(f"Gecersiz durum: {durum}")
                t["durum"] = durum
                # K7: Failed durumunda attempts artir
                if durum == "failed":
                    t["attempts"] = t.get("attempts", 0) + 1
            t.update(fields)
            if durum in ("done", "blocked"):
                t["bitis"] = datetime.now().isoformat(timespec="seconds")
            _write_json(TASK_BOARD, board)
            _md_yaz(board)
            return t
    return None


def gorev_getir(task_id: str) -> dict | None:
    """Tek görevi getir (delta-only okuma)."""
    for t in gorev_listesi():
        if t["task_id"] == task_id:
            return t
    return None


def okuma_listesi_olustur(task_id: str) -> list[str]:
    """K6: Agent icin otomatik 'ne okunmalı' listesi.
    
    Agent bu listeden fazla dosya acamaz (exploration yasak).
    Tasarruf: ~1500-3000 token/oturum.
    """
    gorev = gorev_getir(task_id)
    if not gorev:
        return []
    
    # Gorevin dosyalari
    dosyalar = list(gorev.get("dosyalar", []))
    
    # Sahip ajana bagli dosya eslemesi
    sahip = gorev["sahip"]
    sahip_dosyalari = {
        "gelistirici": ["src/company_master/etl", "src/company_master/db", "scripts"],
        "mimar": ["src/company_master/schema", "src/company_master/db"],
        "kalite": ["tests", "data/kpi_raporu.md"],
        "arastirmaci": ["AI proje v1/V10/07_referanslar", "scripts/mersis_api_research.md"],
        "web_kazima": ["src/company_master/engine", "src/company_master/utils"],
        "koordinatör": ["AI proje v1/V10", "AGENT_SYNC.md"],
    }
    
    for dizin in sahip_dosyalari.get(sahip, []):
        if dizin not in dosyalar:
            dosyalar.append(dizin)
    
    # Mevcut olmayan dosyalari filtrele (token bosa harcanmasin)
    mevcut = []
    ROOT = Path(__file__).resolve().parents[3]
    for d in dosyalar:
        if (ROOT / d).exists():
            mevcut.append(d)
    
    return mevcut[:5]  # Maksimum 5 okunacak (token limiti)


def gorev_brief(task_id: str) -> str | None:
    gorev = gorev_getir(task_id)
    if not gorev:
        return None
    locks = locklar()

    brief = f"""## Gorev Brief: {gorev['task_id']}

**Gorev:** {gorev['baslik']}
**Sahip:** {gorev['sahip']}
**Oncelik:** {gorev['oncelik']}
**Durum:** {gorev['durum']}

### Dosyalar (sadece bunlari ac)
{chr(10).join(f"  - {d}" for d in gorev.get("dosyalar", [])) if gorev.get("dosyalar") else "  (dosya belirtilmemis)"}

### Aktif Lock'lar
{chr(10).join(f"  - {d} ({lk['sahip']})" for d, lk in locks.items()) if locks else "  (kilit yok)"}

### Kurallar
- Sadece yukaridaki dosyalari ac ve degistir
- Baska dosya acma (exploration yasak)
- Gorev bitince: gorev-guncelle {task_id} --durum done
- Basarisiz olursa: gorev-guncelle {task_id} --durum blocked --not "hata_aciklamasi"
"""
    return brief


# ---- K3: Session Handoff ----
HANDOFF_FILE = STATE_DIR / "handoffs.json"


def handoff_yaz(task_id: str, tamamlandi: str, sonraki_adim: str = "",
                dikkat_edilmesi: str = "") -> None:
    handoffs: dict = {}
    if HANDOFF_FILE.exists():
        handoffs = json.loads(HANDOFF_FILE.read_text(encoding="utf-8"))
    handoffs[task_id] = {
        "tamamlandi": tamamlandi,
        "sonraki_adim": sonraki_adim,
        "dikkat_edilmesi": dikkat_edilmesi,
        "tarih": datetime.now().isoformat(timespec="seconds"),
    }
    HANDOFF_FILE.write_text(json.dumps(handoffs, ensure_ascii=False, indent=2),
                            encoding="utf-8")


def handoff_oku(task_id: str) -> dict | None:
    if not HANDOFF_FILE.exists():
        return None
    return json.loads(HANDOFF_FILE.read_text(encoding="utf-8")).get(task_id)


def handoff_tum() -> dict:
    if not HANDOFF_FILE.exists():
        return {}
    return json.loads(HANDOFF_FILE.read_text(encoding="utf-8"))


def agent_sync_olustur() -> str:
    """task_board.json'dan AGENT_SYNC.md icerigi olusturur."""
    board = gorev_listesi()
    handoffs = handoff_tum()
    lines = [
        "# AGENT_SYNC — Otomatik Olusturuldu (task_board'dan)",
        "",
        f"> Son guncelleme: {datetime.now().isoformat(timespec='seconds')}",
        f"> Kaynak: data/orchestrator/task_board.json",
        "",
        "## Aktif Isler",
        "",
        "| Gorev | Baslik | Sahip | Oncelik | Durum |",
        "|-------|--------|-------|---------|-------|",
    ]
    for t in board:
        if t["durum"] not in ("done",):
            lines.append(f"| {t['task_id']} | {t['baslik'][:40]} | {t['sahip']} | "
                         f"{t['oncelik']} | {t['durum']} |")
    lines += ["", "## Tamamlananlar (Son 10)", "",
              "| Gorev | Baslik | Sahip | Bitis |", "|-------|--------|-------|-------|"]
    done = [t for t in board if t["durum"] == "done"][-10:]
    for t in done:
        lines.append(f"| {t['task_id']} | {t['baslik'][:40]} | {t['sahip']} | "
                     f"{t.get('bitis', '-')[:10]} |")
    if handoffs:
        lines += ["", "## Son Handoff'lar", ""]
        for tid, h in list(handoffs.items())[-5:]:
            lines.append(f"- **{tid}**: {h.get('tamamlandi', '')[:50]}")
    return "\n".join(lines) + "\n"


def agent_sync_yaz() -> None:
    """AGENT_SYNC.md'yi board'dan otomatik yeniden yazar."""
    ROOT = Path(__file__).resolve().parents[3]
    sync_path = ROOT / "AGENT_SYNC.md"
    # Sadece ilk satir "Otomatik" degilse, basina uyari ekle
    icerik = agent_sync_olustur()
    # Mevcut dosyayi koru, sadece otomatik bolumleri guncelle
    if sync_path.exists():
        mevcut = sync_path.read_text(encoding="utf-8")
        # Eger dosya otomatik olusturulmus stile uyuyorsa tamamen yeniden yaz
        if "Otomatik Olusturuldu" in mevcut or mevcut.strip().startswith("# AGENT_SYNC"):
            sync_path.write_text(icerik, encoding="utf-8")
        else:
            # Manuel icerik varsa, otomatik bolumu sona ekle
            if "## Otomatik Ozet (task_board)" not in mevcut:
                mevcut += "\n\n## Otomatik Ozet (task_board)\n\n" + icerik
            sync_path.write_text(mevcut, encoding="utf-8")
    else:
        sync_path.write_text(icerik, encoding="utf-8")


def gorev_listesi(durum: str | None = None) -> list[dict]:
    board = _read_json(TASK_BOARD)
    if durum:
        return [t for t in board if t["durum"] == durum]
    return board


# ---- Dosya Lock (cakisma onleme) ----
def _lock_alan(sahip: str, dosya: str, task_id: str) -> None:
    locks = _read_json(FILE_LOCKS)
    if dosya in locks and locks[dosya]["sahip"] != sahip:
        raise PermissionError(
            f"{dosya} zaten {locks[dosya]['sahip']} tarafindan kilitli "
            f"(gorev: {locks[dosya]['task_id']})"
        )
    locks[dosya] = {
        "sahip": sahip,
        "task_id": task_id,
        "kilitlendi": datetime.now().isoformat(timespec="seconds"),
    }
    _write_json(FILE_LOCKS, locks)


def lock_birak(dosya: str, sahip: str) -> bool:
    locks = _read_json(FILE_LOCKS)
    if locks.get(dosya, {}).get("sahip") == sahip:
        del locks[dosya]
        _write_json(FILE_LOCKS, locks)
        return True
    return False


def lock_durum(dosya: str) -> dict | None:
    return _read_json(FILE_LOCKS).get(dosya)


def locklar() -> dict:
    return _read_json(FILE_LOCKS)


# ---- Canli Durum ----
def durum_guncelle(key: str, **fields) -> None:
    state = _read_json(STATE_JSON)
    entry = state.get(key, {})
    entry.update(fields)
    entry["updated_at"] = datetime.now().isoformat(timespec="seconds")
    state[key] = entry
    _write_json(STATE_JSON, state)


def durum_getir(key: str | None = None) -> Any:
    state = _read_json(STATE_JSON)
    return state if key is None else state.get(key)


# ---- Markdown gorunum (Obsidian/AGENT_SYNC icin) ----
def _md_yaz(board: list[dict]) -> None:
    lines = [
        "# Gorev Panosu — Orkestrator",
        "",
        "> Merkezi gorev listesi: herkes herkesin ne yaptigini takip eder.",
        "> Kaynak: `data/orchestrator/task_board.json` — Obsidian okumasi icin disa aktarilir.",
        "",
        "## Aktif Isler",
        "",
        "| Gorev | Baslik | Sahip | Oncelik | Durum | Dosyalar |",
        "|-------|--------|-------|---------|-------|----------|",
    ]
    aktif = [t for t in board if t["durum"] not in ("done",)]
    for t in aktif:
        dos = ", ".join(t["dosyalar"][:3]) if t["dosyalar"] else "-"
        lines.append(f"| {t['task_id']} | {t['baslik']} | {t['sahip']} | "
                     f"{t['oncelik']} | {t['durum']} | {dos} |")
    lines += ["", "## Tamamlananlar", "",
              "| Görev | Baslik | Sahip | Bitis |", "|-------|--------|-------|-------|"]
    done = [t for t in board if t["durum"] == "done"]
    for t in done:
        lines.append(f"| {t['task_id']} | {t['baslik']} | {t['sahip']} | {t.get('bitis', '-')} |")
    TASK_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")