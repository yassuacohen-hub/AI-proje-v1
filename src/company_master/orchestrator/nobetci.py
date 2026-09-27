# -*- coding: utf-8 -*-
"""ORCH-09: Otomatik tetikleme nöbetçi.

- Görev panosunda bekleyen tetik bir sürede (kademe_sn) çalışmazsa alarm/log oluşturur, ses uyarısı verir ve opsiyonel Telegram bildirir.
"""
from __future__ import annotations

import json, os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Yerel paket importları
from src.company_master.orchestrator import task_board as tb
from src.company_master.orchestrator.trigger import (
    ajan_normalize,
    bekleyen_tetikler,
    tetik_uyari_ekle,
)

# ---- Yardımcı -----------------
def _simdi() -> str:
    return datetime.now().isoformat(timespec="seconds")

def _data_dir(data_dir: Path | None) -> Path:
    return Path(data_dir) if data_dir else tb.STATE_DIR

# ---- Config -------------------
def nobetci_ayar_oku(data_dir: Path | None = None) -> dict[str, Any]:
    default = {"kademe_sn": 600, "kanallar": ["log", "ses"], "telegram": False}
    yol = _data_dir(data_dir) / "nobetci.json"
    if yol.exists():
        try:
            default = json.loads(yol.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    # dosya yoksa yarat
    nobetci_ayar_yaz(default, data_dir)
    return default

def nobetci_ayar_yaz(ayar: dict[str, Any], data_dir: Path | None = None) -> None:
    yol = _data_dir(data_dir) / "nobetci.json"
    yol.parent.mkdir(parents=True, exist_ok=True)
    tb.atomic_write_text(yol, json.dumps(ayar, ensure_ascii=False, indent=2))

# ---- Geçmiş tetik tespiti ----
def geciken_tetikler(data_dir: Path | None = None, kademe_sn: int | None = None) -> list[dict[str, Any]]:
    if kademe_sn is None:
        kademe_sn = nobetci_ayar_oku(data_dir).get("kademe_sn", 600)
    now = datetime.now()
    result: list[dict[str, Any]] = []
    for dosya in sorted((_data_dir(data_dir) / "triggers").glob("*.jsonl")):
        ajan = dosya.stem
        for k in bekleyen_tetikler(ajan, data_dir):
            try:
                t = datetime.fromisoformat(k["tarih"])
            except Exception:
                continue
            if now - t > timedelta(seconds=kademe_sn):
                rec = dict(k)
                rec["ajan"] = ajan
                rec["gecikme_sn"] = int((now - t).total_seconds())
                rec["gecikme_dk"] = round(rec["gecikme_sn"] / 60, 1)
                result.append(rec)
    return result
# D-236: ALARM dosyası kaldırıldı. Kimse otomatik okumuyordu (tek tüketici iki
# elle komuttu) ve içeriği tetik kaydının (uyari_sayisi/uyari_tarihi) kopyasıydı.
# 282 kaydın 38'i kapalı görevlere aitti. Bekleyen işler artık pano_denetim'in
# tek satırında görünür.

# ---- Ses uyarısı ----------------
def _ses_uyarisi() -> None:
    """FIX-NOB-02: Tek ve kısa bip (koşu başına en fazla bir kez çağrılır)."""
    try:
        import winsound
        winsound.Beep(800, 150)
    except Exception:
        pass

# ---- Telegram -------------------
def _telegram_mesajat(msg: str, ayar: dict[str, Any]) -> bool | None:
    telegram = ayar.get("telegram")
    if not telegram or isinstance(telegram, bool):
        return None
    token = telegram.get("bot_token") or os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return None
    try:
        import requests
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": msg, "parse_mode": "HTML"}, timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return None

# ---- Tetik fırlatma -------------
def tetik_firlat(kayit: dict[str, Any], ayar: dict[str, Any], data_dir: Path | None = None) -> dict[str, Any]:
    data_dir = _data_dir(data_dir)
    ajan = kayit["ajan"]
    task_id = kayit["task_id"]
    sayi = kayit.get("uyari_sayisi", 0) + 1
    tetik_uyari_ekle(ajan, task_id, data_dir)
    gorev = tb.gorev_getir(task_id) or {}
    log = data_dir / "trigger_log.jsonl"
    entry = {"ts": _simdi(), "kaynak": "nobetci", "ajan": ajan, "task_id": task_id,
             "tetik_sayisi": sayi}
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    if "telegram" in ayar.get("kanallar", []) and ayar.get("telegram"):
        msg = f"🔔 ORCH-09 UYARI: {task_id} ({gorev.get('baslik','')}) — {ajan} {sayi}. kez uyandı."
        _telegram_mesajat(msg, ayar)
    return {"task_id": task_id, "ajan": ajan, "tetik_sayisi": sayi}

def tetik_gecikmis_yap(ajan: str, task_id: str, sure_sn: int, data_dir: Path | None = None) -> None:
    yol = _data_dir(data_dir) / "triggers" / f"{ajan_normalize(ajan) or ajan}.jsonl"
    if not yol.exists(): return
    recs = [json.loads(l) for l in yol.read_text(encoding="utf-8").splitlines() if l.strip()]
    eski = datetime.now() - timedelta(seconds=sure_sn)
    for r in recs:
        if r.get("task_id") == task_id and r.get("durum") == "bekliyor":
            r["tarih"] = eski.isoformat(timespec="seconds")
    tb.atomic_write_text(yol, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs))

def nobet_tut(data_dir: Path | None = None, ayar: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Geciken tetikleri fırlatır.

    FIX-NOB-02: Ses, tetik başına değil **koşu başına en fazla bir kez** ve yalnızca
    **ilk kez** uyarılan (daha önce hiç uyarılmamış) tetik varsa çalar. Böylece
    eski/tekrarlayan gecikmeler her koşuda yeniden ötmez.
    """
    if ayar is None: ayar = nobetci_ayar_oku(data_dir)
    if ayar.get("devre_disi"): return []
    geciken = geciken_tetikler(data_dir, ayar.get("kademe_sn", 600))
    ilk_kez_var = any(int(k.get("uyari_sayisi", 0) or 0) == 0 for k in geciken)
    sonuc = [tetik_firlat(k, ayar, data_dir) for k in geciken]
    if sonuc and ilk_kez_var and "ses" in ayar.get("kanallar", []):
        _ses_uyarisi()
    return sonuc
