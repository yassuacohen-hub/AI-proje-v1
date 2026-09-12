# -*- coding: utf-8 -*-
"""9R-05 (GECICI): 9router provider envanteri.

- DB `providerConnections` tablosunu okur (tum provider'lar), `data` JSON'ini
  parse eder, secret alanlari maskeler.
- Canli API katalogu ceker: /api/health, /v1/models, /v1/models/embedding,
  /v1/models/web (NINEROUTER_URL/KEY `.env`'den -> `ninerouter_client`).
- Cikti: `scripts/_9r05_provider_envanter.json` (UTF-8) + konsol ozeti.

NOT: Gecici kesif scripti; sonraki adimda temizlenecek. Baska dosyaya dokunmaz.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# --- proje kokunu sys.path'e ekle (src import icin) ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:  # once src-deseni, sonra eski paket deseni
    from src.company_master.gateway.ninerouter_client import (
        NineRouter,
        NineRouterError,
    )
except ImportError:  # pragma: no cover
    from company_master.gateway.ninerouter_client import (
        NineRouter,
        NineRouterError,
    )

DB_DEFAULT = Path.home() / "AppData/Roaming/9router/db/data.sqlite"
OUT = Path(__file__).resolve().parent / "_9r05_provider_envanter.json"

# firecrawl/tavily/ollama/openai disindakiler "YENI" sayilir
BILINEN_PROVIDERLAR = {"firecrawl", "tavily", "ollama", "openai"}

SECRET_TERMS = ("key", "token", "secret", "pass", "auth", "apikey")
SQL_TABLO = "providerConnections"
SQL_PRECEDENCE = (
    "provider", "authType", "name", "priority", "isActive", "data", "updatedAt"
)


# ---------------------------------------------------------------- maskeleme
def _is_secret(anahtar: Any) -> bool:
    k = str(anahtar).lower()
    return any(t in k for t in SECRET_TERMS)


def _maskele(v: Any) -> str:
    """Ilk 4 + son 4 karakteri goster, ortasini *** yap."""
    s = str(v)
    if len(s) <= 8:
        return "***"
    return f"{s[:4]}...{s[-4:]}"


def _maskele_rek(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            k: (_maskele(v) if _is_secret(k) else _maskele_rek(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_maskele_rek(i) for i in obj]
    return obj


# ---------------------------------------------------------------- DB
def _db_dosya(db_path: Path) -> Path:
    return Path(db_path)


def _db_providerlar(con: sqlite3.Connection) -> list[dict[str, Any]]:
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT provider, authType, name, priority, isActive, data, updatedAt "
        f"FROM {SQL_TABLO} ORDER BY provider"
    ).fetchall()

    kayitlar = []
    for r in rows:
        provider = r["provider"]
        data_raw = r["data"]
        data = None
        if data_raw:
            try:
                data = json.loads(data_raw)
            except Exception:  # noqa: BLE001 — ham metin olabilir
                data = {"HAM": str(data_raw)[:400]}

        d = data if isinstance(data, dict) else {}
        ozet = {
            "testStatus": d.get("testStatus"),
            "lastError": d.get("lastError"),
            "errorCode": d.get("errorCode"),
            "backoffLevel": d.get("backoffLevel"),
            "rateLimitedUntil": d.get("rateLimitedUntil"),
        }
        # capability kilitleri: ust duzey modelLock_* + providerSpecificData.icindekiler
        kilitler: dict[str, Any] = {}
        for k, v in d.items():
            kl = str(k).lower()
            if kl.startswith("modellock") or kl.startswith("model_lock"):
                kilitler[k] = _maskele_rek(v)
        psd = d.get("providerSpecificData")
        if isinstance(psd, dict):
            for k, v in psd.items():
                kl = str(k).lower()
                if kl.startswith("modellock") or kl.startswith("model_lock"):
                    kilitler[f"providerSpecificData.{k}"] = _maskele_rek(v)

        is_yeni = provider not in BILINEN_PROVIDERLAR

        kayitlar.append(
            {
                "provider": provider,
                "authType": r["authType"],
                "name": r["name"],
                "priority": r["priority"],
                "isActive": r["isActive"],
                "updatedAt": r["updatedAt"],
                "isYeni": is_yeni,
                "durum": {
                    **ozet,
                    "modelLocks": kilitler,
                },
                "providerSpecificData": _maskele_rek(
                    psd if isinstance(psd, dict) else {}
                ),
                "data_maskeli": _maskele_rek(data),
            }
        )
    return kayitlar


def _db_sema(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute(f"PRAGMA table_info({SQL_TABLO})").fetchall()
    return [
        {"cid": r[0], "name": r[1], "type": r[2], "notnull": r[3], "dflt": r[4], "pk": r[5]}
        for r in rows
    ]


# ---------------------------------------------------------------- canli API
def _kisa_hata(exc: Exception) -> str:
    return f"{type(exc).__name__}: {str(exc)[:300]}"


def _api_cekirdegi(fn, ad: str) -> dict[str, Any]:
    try:
        sonuc = fn()
        return {"durum": "ok", ad: sonuc}
    except NineRouterError as exc:
        return {"durum": "hata", ad: _kisa_hata(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"durum": "hata", ad: _kisa_hata(exc)}


def _model_ozet(m: dict[str, Any]) -> dict[str, Any]:
    ozet: dict[str, Any] = {}
    for k in ("id", "object", "owned_by", "kind", "created", "updatedAt"):
        if m.get(k) not in (None, ""):
            ozet[k] = m[k]
    for dk in ("dimension", "dimensions", "embedding_size", "vector_size", "length"):
        if dk in m and m[dk] is not None:
            ozet["dimension"] = m[dk]
            break
    # pricing/free sinyali — API'de varsa yakala
    for pk in ("price", "pricing", "cost", "free", "isFree", "tier", "billing"):
        if pk in m and m[pk] is not None:
            ozet.setdefault("pricing", {})[pk] = m[pk]
    return _maskele_rek(ozet)  # guvenlik: gizli anahtar olmasin


def _combo_bul(modeller: list[dict[str, Any]], capability: str) -> list[dict[str, Any]]:
    combos = []
    for m in modeller:
        owned = str(m.get("owned_by", "")).lower()
        mid = str(m.get("id", "")).lower()
        if owned == "combo" or "combo" in mid:
            combos.append(
                {
                    "id": m.get("id"),
                    "capability": capability,
                    "neden": "owned_by=combo" if owned == "combo" else "id=*combo*",
                    "kind": m.get("kind") if capability == "web" else None,
                }
            )
    return combos


def _pricing_ara(chat: list[dict[str, Any]]) -> dict[str, Any]:
    ilgili_anahtarlar: set[str] = set()
    for m in chat:
        for k in m.keys():
            kl = k.lower()
            if any(t in kl for t in ("price", "cost", "free", "tier", "billing")):
                ilgili_anahtarlar.add(k)
    if ilgili_anahtarlar:
        return {"var": True, "anahtarlar": sorted(ilgili_anahtarlar)[:15]}
    return {
        "var": False,
        "not": "API yanitinda fiyat/free bilgisi yok (config tabanli free listesi Adim 2'de)",
    }


def _topla(timeout: float) -> dict[str, Any]:
    nr = NineRouter(timeout=timeout)
    sonuc: dict[str, Any] = {}

    # gateway /api/health (raw yanit icin _request)
    try:
        g = nr._request("GET", "/api/health")  # noqa: SLF001 — kesif ecde cesitli
        sonuc["gateway"] = {
            "durum": "ok",
            "ok": bool(g.get("ok")) if isinstance(g, dict) else g,
            "url": nr.base_url,
            "yanit_ozet": (
                {k: v for k, v in g.items() if not _is_secret(k)} if isinstance(g, dict) else g
            ),
        }
    except NineRouterError as exc:
        sonuc["gateway"] = {
            "durum": "hata",
            "ok": False,
            "url": nr.base_url,
            "hata": _kisa_hata(exc),
        }
    except Exception as exc:  # noqa: BLE001
        sonuc["gateway"] = {"durum": "hata", "ok": False, "url": nr.base_url, "hata": _kisa_hata(exc)}

    # model katalogu
    katalog: dict[str, Any] = {}
    arama = {
        "chat": lambda: nr.list_models(""),
        "embedding": lambda: nr.list_models("embedding"),
        "web": lambda: nr.list_models("web"),
    }
    for ad, fn in arama.items():
        ham = _api_cekirdegi(fn, "liste")
        if ham["durum"] == "ok":
            liste = ham["liste"] if isinstance(ham["liste"], list) else []
            katalog[ad] = {
                "durum": "ok",
                "adet": len(liste),
                "liste": [_model_ozet(m) for m in liste],
            }
        else:
            katalog[ad] = {"durum": "hata", "adet": 0, "liste": [], "hata": ham.get("liste")}

    combo = []
    combo += _combo_bul(katalog.get("chat", {}).get("liste", []), "chat")
    combo += _combo_bul(katalog.get("embedding", {}).get("liste", []), "embedding")
    combo += _combo_bul(katalog.get("web", {}).get("liste", []), "web")
    katalog["combo"] = combo

    katalog["pricing"] = _pricing_ara(katalog.get("chat", {}).get("liste", []))
    sonuc["katalog"] = katalog

    # VPN notu: ag hatasi var mi?
    hatali = [
        k for k, v in katalog.items()
        if isinstance(v, dict) and v.get("durum") == "hata"
    ]
    if sonuc.get("gateway", {}).get("durum") == "hata":
        hatali.append("gateway")
    if hatali:
        sonuc["vpnNotu"] = (
            "Olası neden: VPN aktif ise kapatıp tekrar deneyin (AGENTS.md kurallı). "
            f"Hatali uclar: {', '.join(hatali)}"
        )
    else:
        sonuc["vpnNotu"] = None
    return sonuc


# ---------------------------------------------------------------- konsol
def _isaret(v) -> str:
    s = str(v).lower()
    if s in ("available", "ok", "1", "true"):
        return "OK "
    if s in ("unavailable", "false", "0"):
        return "XX "
    return "-- "


def _konsol_ozet(meta: dict, providerlar: list[dict], canli: dict) -> str:
    lines: list[str] = []
    lines.append("=" * 78)
    lines.append(f"9Router Provider Envanteri — {meta['generatedAtTR']}")
    lines.append(f"DB: {meta['dbPath']}  |  kayit={meta['kayitSayisi']}")
    g = canli.get("gateway", {})
    if g.get("durum") == "ok":
        lines.append(f"Gateway /api/health: OK  —  {g.get('url')}")
    else:
        lines.append(
            f"Gateway /api/health: HATA  —  {g.get('hata', 'bilinmiyor')}"
        )
    lines.append("")

    lines.append("--- Provider Durumu (DB providerConnections) ---")
    yeni = []
    for p in providerlar:
        dur = p["durum"]
        durum_txt = str(dur.get("testStatus") or "-")
        hata_txt = str(dur.get("lastError") or "-")[:60]
        hata_kod = dur.get("errorCode")
        kilitler = dur.get("modelLocks") or {}
        kilit_txt = ",".join(
            f"{k.replace('modelLock_','')}={v}" for k, v in kilitler.items()
        ) or "-"
        backoff = dur.get("backoffLevel")
        rl = dur.get("rateLimitedUntil")
        ok_is = _isaret(durum_txt)
        etiket = "YENI" if p.get("isYeni") else "    "
        if p.get("isYeni"):
            yeni.append(p["provider"])
        kilit_km = f"| kilit={kilit_txt}" if kilit_txt != "-" else ""
        hata_km = f"| hata={hata_txt}" if hata_txt != "-" else ""
        if hata_kod not in (None, ""):
            hata_km += f" ({hata_kod})"
        lines.append(
            f"[{etiket}] {p['provider']:<16} pri={p['priority']!s:<3} "
            f"aktif={p['isActive']!s:<3} durum={ok_is}/{durum_txt:<12} "
            f"backoff={backoff} rateLimited={rl} {hata_km} {kilit_km}"
        )
    lines.append("")

    kt = canli.get("katalog", {})
    for ad in ("chat", "embedding", "web"):
        blok = kt.get(ad, {})
        if blok.get("durum") == "ok":
            ids = [m.get("id") for m in blok.get("liste", [])]
            goster = ", ".join(str(i) for i in ids[:12])
            if len(ids) > 12:
                goster += f" ... (+{len(ids)-12})"
            lines.append(f"{ad:<10} ({blok.get('adet')}): {goster}")
        else:
            lines.append(f"{ad:<10}: HATA — {blok.get('hata', '-')}")

    kombinasyon = kt.get("combo", [])
    if kombinasyon:
        lines.append("Combo modeller (owned_by=combo / id=*combo*):")
        for c in kombinasyon:
            kind_txt = f" [kind={c.get('kind')}]" if c.get("kind") else ""
            lines.append(f"  - {c.get('id')}  (capability={c.get('capability')}, {c.get('neden')}){kind_txt}")
    else:
        lines.append("Combo modeller: yok")

    prc = kt.get("pricing", {})
    lines.append(f"Free/pricing bilgisi: {'VAR (' + prc.get('anahtarlar','').__str__() + ')' if prc.get('var') else 'bilgi yok'}")
    if canli.get("vpnNotu"):
        lines.append("")
        lines.append(f"[!] {canli['vpnNotu']}")
    lines.append("=" * 78)
    return "\n".join(lines)


# ---------------------------------------------------------------- main
def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="9router provider envanteri (gecici kesif)")
    ap.add_argument("--db", default=str(DB_DEFAULT), help="9router data.sqlite yolu")
    ap.add_argument("--timeout", type=float, default=20.0, help="API timeout (sn)")
    args = ap.parse_args()

    db_path = _db_dosya(args.db)
    if not db_path.exists():
        print("DB yok:", db_path)
        return 1

    con = sqlite3.connect(str(db_path))
    try:
        sema = _db_sema(con)
        providerlar = _db_providerlar(con)
    finally:
        con.close()

    canli = _topla(args.timeout)

    meta = {
        "generatedAtUTC": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generatedAtTR": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dbPath": str(db_path),
        "kayitSayisi": len(providerlar),
        "tabloSemasi": sema,
    }
    yeni_liste = [p["provider"] for p in providerlar if p.get("isYeni")]

    paket = {
        "meta": meta,
        "gateway": canli.get("gateway"),
        "providers": providerlar,
        "yeniSaglayicilar": yeni_liste,
        "katalog": canli.get("katalog"),
        "vpnNotu": canli.get("vpnNotu"),
    }

    OUT.write_text(
        json.dumps(paket, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ozet = _konsol_ozet(meta, providerlar, canli)
    print(ozet)
    print(f"\nJSON -> {OUT}  (UTF-8, {OUT.stat().st_size} byte)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())