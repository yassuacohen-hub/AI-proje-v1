# -*- coding: utf-8 -*-
"""Rozet modeli — Kullanıcı ilerleme takibi."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class UserProgress:
    kullanici_id: str
    rozetler: dict[str, int] = field(default_factory=dict)
    toplam_puan: int = 0


def rozet_ver(
    kullanici_id: str,
    rozet_id: str,
    puan: int = 1,
    *,
    veritabani_yol: str | Path | None = None,
) -> UserProgress:
    mevcut = _yukle(kullanici_id, veritabani_yol)
    rozetler = dict(mevcut.rozetler)
    mevcut_puan = rozetler.get(rozet_id, 0)
    rozetler[rozet_id] = mevcut_puan + max(0, puan)
    toplam = sum(rozetler.values())
    ilerleme = UserProgress(
        kullanici_id=kullanici_id,
        rozetler=rozetler,
        toplam_puan=toplam,
    )
    _kaydet(ilerleme, veritabani_yol)
    return ilerleme


def karsilastir(
    bir: UserProgress,
    iki: UserProgress,
) -> dict[str, Any]:
    bir_set = set(bir.rozetler.keys())
    iki_set = set(iki.rozetler.keys())
    return {
        "ortak_rozetler": sorted(bir_set & iki_set),
        "sadece_bir": sorted(bir_set - iki_set),
        "sadece_iki": sorted(iki_set - bir_set),
        "bir_toplam": bir.toplam_puan,
        "iki_toplam": iki.toplam_puan,
        "fark": abs(bir.toplam_puan - iki.toplam_puan),
    }


def _yukle(kullanici_id: str, yol: str | Path | None) -> UserProgress:
    if yol is None:
        return UserProgress(kullanici_id=kullanici_id)
    path = Path(yol)
    if not path.exists():
        return UserProgress(kullanici_id=kullanici_id)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return UserProgress(kullanici_id=kullanici_id)
    if not isinstance(data, dict):
        return UserProgress(kullanici_id=kullanici_id)
    kullanici = data.get(kullanici_id)
    if not isinstance(kullanici, dict):
        return UserProgress(kullanici_id=kullanici_id)
    rozetler = {
        str(k): int(v)
        for k, v in kullanici.get("rozetler", {}).items()
        if isinstance(k, (str, int, float))
        and isinstance(v, (int, float))
    }
    toplam = sum(rozetler.values())
    return UserProgress(
        kullanici_id=kullanici_id,
        rozetler=rozetler,
        toplam_puan=toplam,
    )


def _kaydet(ilerleme: UserProgress, yol: str | Path | None) -> None:
    if yol is None:
        return
    path = Path(yol)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    else:
        data = {}
    data[ilerleme.kullanici_id] = asdict(ilerleme)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
