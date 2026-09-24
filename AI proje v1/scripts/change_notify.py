#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Y14: Degisiklik bildirimi - yeni firma / skor degisimi -> Telegram.

Calisma prensibi: DB'deki mevcut durumu snapshot dosyasina yazar
(data/orchestrator/change_notify_state.json). Her calismada onceki
snapshot ile karsilastirir; yeni firma ve esigi asan skor
degisimlerini Telegram'a gonderir.

Kullanim:
    python scripts/change_notify.py --baseline   # izlemeyi baslat
    python scripts/change_notify.py --check      # degisiklik varsa bildir
    python scripts/change_notify.py --daily      # gunluk ozet gonder
    python scripts/change_notify.py --check --no-send  # kuru calistirma
"""
from __future__ import annotations

import argparse
import html
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

STATE_PATH = ROOT / "data" / "orchestrator" / "change_notify_state.json"
LOG_PATH = ROOT / "logs" / "change_notify.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("change_notify")


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning("snapshot okunamadi (%s), sifirdan baslaniyor", exc)
        return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def fetch_current() -> dict[str, Any]:
    """DB'den mevcut durumu ceker: {rows: {id: {name, score}}, counts: {...}}."""
    from company_master.db.connection import get_engine
    from sqlalchemy import text

    eng = get_engine()
    with eng.connect() as conn:
        rows = conn.execute(text(
            "SELECT company_id::text AS cid, legal_name, "
            "COALESCE(data_quality_score, 0)::float AS score "
            "FROM companies"
        )).fetchall()
        counts = {
            "companies": conn.execute(text("SELECT COUNT(*) FROM companies")).fetchone()[0],
            "source_records": conn.execute(text("SELECT COUNT(*) FROM source_records")).fetchone()[0],
            "avg_score": float(conn.execute(
                text("SELECT COALESCE(AVG(data_quality_score),0) FROM companies")).fetchone()[0]),
        }
    data = {r[0]: {"name": r[1] or "?", "score": float(r[2] or 0)} for r in rows}
    return {"rows": data, "counts": counts}


def diff_snapshots(old: dict, new: dict, threshold: float = 10.0) -> dict[str, Any]:
    """Iki {id: {name, score}} snapshot'ini karsilastirir (saf fonksiyon)."""
    old_ids, new_ids = set(old), set(new)
    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)
    changed: list[dict] = []
    for cid in old_ids & new_ids:
        o = old[cid].get("score") or 0
        n = new[cid].get("score") or 0
        d = n - o
        if abs(d) >= threshold:
            changed.append({"id": cid, "name": new[cid].get("name", "?"),
                            "old": round(o, 1), "new": round(n, 1), "delta": round(d, 1)})
    changed.sort(key=lambda r: abs(r["delta"]), reverse=True)
    return {"added": added, "removed": removed, "changed": changed}


def _esc(s: Any) -> str:
    return html.escape(str(s), quote=False)


def format_change_message(diff: dict, new: dict, counts: dict, top: int = 10) -> str:
    lines = ["\U0001F514 <b>Huginn Degisiklik Bildirimi</b>",
             "<i>%s</i>" % datetime.now().strftime("%d.%m.%Y %H:%M"), ""]
    if diff["added"]:
        lines.append("\U0001F195 <b>Yeni firma: %d</b>" % len(diff["added"]))
        for cid in diff["added"][:top]:
            lines.append("\u2022 %s" % _esc(new[cid].get("name", "?")[:60]))
        if len(diff["added"]) > top:
            lines.append("<i>... +%d firma daha</i>" % (len(diff["added"]) - top))
        lines.append("")
    ups = [c for c in diff["changed"] if c["delta"] > 0][:top]
    downs = [c for c in diff["changed"] if c["delta"] < 0][:top]
    if ups:
        lines.append("\U0001F4C8 <b>Skoru yukselen: %d</b>" % len(ups))
        for c in ups:
            lines.append("\u2022 %s: %s -> <b>%s</b> (+%s)"
                         % (_esc(c["name"][:50]), c["old"], c["new"], c["delta"]))
        lines.append("")
    if downs:
        lines.append("\U0001F4C9 <b>Skoru dusen: %d</b>" % len(downs))
        for c in downs:
            lines.append("\u2022 %s: %s -> <b>%s</b> (%s)"
                         % (_esc(c["name"][:50]), c["old"], c["new"], c["delta"]))
        lines.append("")
    if diff["removed"]:
        lines.append("\U0001F5D1\uFE0F <i>Silinen kayit: %d</i>\n" % len(diff["removed"]))
    lines.append("\U0001F4CA Toplam: <b>%s</b> firma | Ort. kalite: <b>%.1f</b>/100"
                 % (f"{counts.get('companies', 0):,}", counts.get("avg_score", 0)))
    return "\n".join(lines)


def format_daily(counts: dict) -> str:
    from company_master.db.connection import get_engine
    from sqlalchemy import text
    try:
        eng = get_engine()
        with eng.connect() as conn:
            buckets = conn.execute(text(
                "SELECT CASE WHEN data_quality_score>=80 THEN '80-100' "
                "WHEN data_quality_score>=60 THEN '60-79' "
                "WHEN data_quality_score>=40 THEN '40-59' ELSE '0-39' END b, "
                "COUNT(*) FROM companies GROUP BY 1 ORDER BY 1 DESC")).fetchall()
        dag = " | ".join("%s: %s" % (b, f"{c:,}") for b, c in buckets)
    except Exception as exc:
        dag = "(dagilim alinamadi: %s)" % exc
    return "\n".join([
        "\U0001F4CA <b>Gunluk Ozet</b>",
        "<i>%s</i>" % datetime.now().strftime("%d.%m.%Y %H:%M"), "",
        "\u2022 Toplam firma: <b>%s</b>" % f"{counts.get('companies', 0):,}",
        "\u2022 Kayit (source_records): <b>%s</b>" % f"{counts.get('source_records', 0):,}",
        "\u2022 Ort. kalite: <b>%.1f</b>/100" % counts.get("avg_score", 0),
        "\u2022 Dagilim: %s" % dag,
    ])



def send(text: str, no_send: bool = False) -> bool:
    if no_send:
        print(text)
        return True
    from company_master.utils.telegram_bot import send_message
    try:
        res = send_message(text)
    except Exception as exc:
        log.error("telegram gonderim hatasi: %s", exc)
        return False
    ok = bool(res.get("ok"))
    if not ok:
        log.error("telegram gonderim basarisiz: %s", res)
    return ok


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description="Y14 degisiklik bildirimi")
    ap.add_argument("--baseline", action="store_true", help="izlemeyi baslat, mesaj atma")
    ap.add_argument("--check", action="store_true", help="degisiklik varsa bildir")
    ap.add_argument("--daily", action="store_true", help="gunluk ozet gonder")
    ap.add_argument("--threshold", type=float, default=10.0)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--no-send", action="store_true", help="telegram'a gonderme")
    a = ap.parse_args(argv)

    cur = fetch_current()
    now = datetime.now(timezone.utc).isoformat()

    if a.baseline:
        save_state({"rows": cur["rows"], "counts": cur["counts"], "last_run": now})
        log.info("baseline kaydedildi: %d firma", len(cur["rows"]))
        print("Baseline kaydedildi: %d firma izleniyor." % len(cur["rows"]))
        return 0

    state = load_state()
    if not state.get("rows"):
        save_state({"rows": cur["rows"], "counts": cur["counts"], "last_run": now})
        send("\U0001F441\uFE0F <b>Degisiklik izleme baslatildi</b>\n"
             "\u2022 Izlenen firma: <b>%s</b>\n"
             "<i>%s</i>" % (f"{len(cur['rows']):,}", datetime.now().strftime("%d.%m.%Y %H:%M")),
             no_send=a.no_send)
        log.info("ilk calisma: baseline olusturuldu (%d firma)", len(cur["rows"]))
        return 0

    diff = diff_snapshots(state["rows"], cur["rows"], threshold=a.threshold)
    n_change = len(diff["added"]) + len(diff["changed"]) + len(diff["removed"])
    log.info("karsilastirma: +%d yeni, %d skor degisimi, -%d silinen",
             len(diff["added"]), len(diff["changed"]), len(diff["removed"]))

    if a.daily:
        send(format_daily(cur["counts"]), no_send=a.no_send)
    elif n_change == 0:
        log.info("degisiklik yok, sessiz cikiliyor")
        print("Degisiklik yok.")
    else:
        ok = send(format_change_message(diff, cur["rows"], cur["counts"], top=a.top),
                  no_send=a.no_send)
        if not ok:
            return 2

    save_state({"rows": cur["rows"], "counts": cur["counts"], "last_run": now})
    return 0


if __name__ == "__main__":
    sys.exit(main())
