"""ErrorLedger persistence for orchestrator."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from src.company_master.orchestrator.models import ErrorLedgerEntry

#: FIX-LEDGER-01 — Windows'ta ``os.replace`` ara sıra ``PermissionError``
#: (WinError 5/32) fırlatır (AV tarayıcı / Explorer kısa süreli kilit).
#: Kısa retry sorunu çözer; testlerde ``monkeypatch`` ile ayarlanabilir.
REPLACE_DENEME = 3
REPLACE_BEKLEME_SN = 0.05


def _atomik_degistir(kaynak: Path, hedef: Path) -> None:
    """``os.replace`` — geçici kilitlerde kısa bekleyerek yeniden dener."""
    son_hata: OSError | None = None
    for deneme in range(REPLACE_DENEME):
        try:
            os.replace(kaynak, hedef)
            return
        except PermissionError as exc:  # pragma: no cover - platform bağımlı
            son_hata = exc
            if deneme < REPLACE_DENEME - 1:
                time.sleep(REPLACE_BEKLEME_SN * (deneme + 1))
    assert son_hata is not None
    raise son_hata


class ErrorLedger:
    def __init__(self, path: str | Path = "workspace/.error_ledger.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self._entries = data
                else:
                    self._entries = data.get("entries", [])
            except (json.JSONDecodeError, OSError):
                self._entries = []

    def _save(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps({"entries": self._entries}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        _atomik_degistir(tmp, self.path)

    def add(self, entry: ErrorLedgerEntry) -> None:
        self._entries.append(entry.to_dict())
        self._save()

    def add_dict(self, entry: dict[str, Any]) -> None:
        self._entries.append(entry)
        self._save()

    def all(self) -> list[dict[str, Any]]:
        return list(self._entries)

    def by_task(self, task_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e.get("task_id") == task_id]

    def by_agent(self, agent_id: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e.get("agent_id") == agent_id]

    def clear(self) -> None:
        self._entries = []
        self._save()
