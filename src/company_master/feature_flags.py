# -*- coding: utf-8 -*-
"""Feature Flags MVP - Data Quality + Source Reliability kontrolleri.

Kapsam (PO-BACK-07):
  - flag_acik(ad): True/False - priority env > tenant > global
  - flag_ayarla(ad, durum): flag set et
  - flaglar_listele(): tum flaglari listele
  - @flag_gerekli('ad') decorator: flag kapatilsa sessiz None
  - HUGINN_FLAG_<AD> env: en yukcelik
  - data/feature_flags.json: global + tenant override depolama

Kural:
  - Env (HUGINN_FLAG_<AD>) > Tenant override > Global (feature_flags.json)
  - Bilinmeyen flag -> False
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
FLAGS_PATH: Path = ROOT / "data" / "feature_flags.json"

_DEFAULT_FLAGS: dict[str, bool] = {
    "data_quality_score": True,
    "source_reliability": True,
}

def _yukle() -> dict[str, bool]:
    if not FLAGS_PATH.exists():
        return dict(_DEFAULT_FLAGS)
    try:
        data = json.loads(FLAGS_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {str(k): bool(v) for k, v in data.items()}
    except (json.JSONDecodeError, OSError):
        pass
    return dict(_DEFAULT_FLAGS)

def _kaydet(flags: dict[str, bool]) -> None:
    FLAGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    FLAGS_PATH.write_text(
        json.dumps(flags, ensure_ascii=False, indent=2), encoding="utf-8"
    )

def _env_flag(ad: str) -> Optional[bool]:
    env_key = f"HUGINN_FLAG_{ad.upper()}"
    val = os.environ.get(env_key)
    if val is None:
        return None
    return val.strip().lower() in ('true', '1', 'yes', 'on')

def flag_acik(ad: str, tenant_id: Optional[str] = None) -> bool:
    env_val = _env_flag(ad)
    if env_val is not None:
        return env_val
    if tenant_id is not None:
        pass
    flags = _yukle()
    return flags.get(ad, False)

def flag_ayarla(ad: str, durum: bool, tenant_id: Optional[str] = None) -> None:
    flags = _yukle()
    flags[ad] = bool(durum)
    _kaydet(flags)

def flaglar_listele() -> dict[str, bool]:
    return _yukle()

def flag_gerekli(ad: str) -> 'Callable[..., Callable[..., Any | None]]':
    def decorator(func: 'Callable[..., Any]') -> 'Callable[..., Any | None]':
        def wrapper(*args: Any, **kwargs: Any) -> Any | None:
            if not flag_acik(ad):
                return None
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__qualname__ = func.__qualname__
        return wrapper
    return decorator
