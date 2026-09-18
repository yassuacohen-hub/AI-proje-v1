# -*- coding: utf-8 -*-
"""CL-03 — Bagimlilik+statik guvenlik taramasi (offline, CI-guvenli).

Kapsam:
1. requirements pinlerini bilinen-zayif listeyle karsilastirir
   (bilinen_zayiflar.json) — pip-audit/safety yoksa da calisir.
2. Aktif kodu regex desenleriyle statik tarar (guvenlik_desenleri.json).
3. Bu klasore rapor yazar: CL-03_guvenlik_raporu.md + tarama_sonuc.json

Calistirma: python data/orchestrator/security_audit/guvenlik_taramasi.py
Cikis kodu: KRITIK bulgu varsa 1, yoksa 0.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

KOK = Path(__file__).resolve().parents[3]
AUDIT_DIR = Path(__file__).resolve().parent


def _json_yukle(ad: str):
    return json.loads((AUDIT_DIR / ad).read_text(encoding="utf-8"))


def _surum_karsilastir(kurulu: str, op: str, esik: str) -> bool:
    def _parca(s: str):
        out = []
        for p in re.split(r"[.\-+]", s):
            out.append(int(p) if p.isdigit() else p)
        return out

    def _cmp(a, b):
        pa, pb = _parca(a), _parca(b)
        for x, y in zip(pa, pb):
            if type(x) is type(y):
                if x != y:
                    return -1 if x < y else 1
            elif str(x) != str(y):
                return -1 if str(x) < str(y) else 1
        return (len(pa) > len(pb)) - (len(pa) < len(pb))

    c = _cmp(kurulu, esik)
    return {"<": c < 0, "<=": c <= 0, "==": c == 0, ">=": c >= 0, ">": c > 0}[op]
def _gereksinimleri_oku() -> dict:
    """requirements-*.txt -> {paket: surum}."""
    paketler: dict = {}
    for ad in ("requirements-app.txt", "requirements-dev.txt"):
        yol = KOK / ad
        if not yol.exists():
            continue
        for satir in yol.read_text(encoding="utf-8").splitlines():
            satir = satir.strip()
            if not satir or satir.startswith(("#", "-")):
                continue
            m = re.match(r"^([A-Za-z0-9_.\-\[\]]+)\s*([<>=!~]+)?\s*([A-Za-z0-9_.\-+*]+)?", satir)
            if not m:
                continue
            isim = re.sub(r"\[.*\]", "", m.group(1)).lower().replace("_", "-")
            ham = (m.group(3) or "").strip()
            if not ham or ham == "*" or not ham[0].isdigit():
                continue  # >= / ~= gibi aralik pinleri degerlendirme disi
            surum = ham.rstrip(",").split(",")[0].strip()
            paketler.setdefault(isim, surum)
    return paketler


def _kurulu_surumler() -> dict:
    try:
        import importlib.metadata as md

        return {d.metadata["Name"].lower().replace("_", "-"): d.version for d in md.distributions()}
    except Exception:
        return {}


def bagimlilik_tara() -> list:
    veri = _json_yukle("bilinen_zayiflar.json")
    pinli = _gereksinimleri_oku()
    kurulu = _kurulu_surumler()
    bulgular = []
    for kayit in veri["kayitlar"]:
        ad = kayit["paket"]
        surum = pinli.get(ad, "")
        if not surum:
            continue
        for z in kayit["zayiflar"]:
            try:
                if _surum_karsilastir(surum, z["op"], z["surum"]):
                    bulgular.append({
                        "tur": "bagimlilik", "siddet": z["siddet"], "paket": ad,
                        "pinli_surum": surum, "kurulu_surum": kurulu.get(ad, "?"),
                        "cve": z["cve"], "aciklama": z["aciklama"], "onerilen": z["onerilen"],
                    })
            except Exception:
                continue
    return bulgular


UZANTI = {".py", ".js", ".html", ".sh", ".ps1", ".yml", ".yaml"}

ATLANACAK = {
    ".git", "__pycache__", "node_modules", ".venv", ".venv_test",
    ".kilo", "_trash", "tmp",
    "AI proje v1", "cop_kutusu_2026_09_09", "data", "workspace", ".agents",
}


def _taranacak_dosyalar():
    for yol in KOK.rglob("*"):
        if not yol.is_file() or yol.suffix.lower() not in UZANTI:
            continue
        rel = yol.relative_to(KOK)
        if any(p in ATLANACAK for p in rel.parts):
            continue
        yield yol


def statik_tara() -> list:
    desenler = _json_yukle("guvenlik_desenleri.json")["desenler"]
    derlenmis = [(d, re.compile(d["regex"])) for d in desenler]
    bulgular = []
    for yol in _taranacak_dosyalar():
        try:
            metin = yol.read_text(encoding="utf-8-sig", errors="ignore")
        except Exception:
            continue
        satirlar = metin.splitlines()
        for d, rx in derlenmis:
            for m in rx.finditer(metin):
                no = metin.count("\n", 0, m.start()) + 1
                satir = satirlar[no - 1].strip()[:200] if no <= len(satirlar) else ""
                s = satir.lstrip()
                if s.startswith("#") or s.startswith("//"):
                    continue
                if any(iz in satir for iz in d.get("izinli_gecis", [])):
                    continue
                bulgular.append({
                    "tur": "statik", "siddet": d["siddet"], "kural": d["id"],
                    "dosya": str(yol.relative_to(KOK)), "satir": no,
                    "ornek": satir, "aciklama": d["aciklama"],
                })
    return bulgular


def rapor_yaz(bag: list, statik: list):
    tum = bag + statik
    kritik = [b for b in tum if b["siddet"] == "kritik"]
    yuksek = [b for b in tum if b["siddet"] == "yuksek"]
    simdi = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    md = [
        "# CL-03 Guvenlik Tarama Raporu", "",
        f"Tarih: {simdi}",
        "Kapsam: requirements pinleri + statik kod taramasi (arsiv/veri/workspace haric)", "",
        "## Ozet", "",
        f"- Toplam bulgu: **{len(tum)}** (kritik: {len(kritik)}, yuksek: {len(yuksek)})",
        f"- Bagimlilik: {len(bag)} | Statik: {len(statik)}", "",
    ]
    md += ["## Bagimlilik Bulgulari", ""]
    if bag:
        for b in bag:
            md.append(f"- [{b['siddet']}] `{b['paket']}` pinli={b['pinli_surum']} "
                      f"kurulu={b['kurulu_surum']} — {b['cve']}: {b['aciklama']} "
                      f"(onerilen: {b['onerilen']})")
    else:
        md.append("Bulgu yok.")
    md += ["", "## Statik Tarama Bulgulari", ""]
    if statik:
        for b in statik:
            md.append(f"- [{b['siddet']}] `{b['kural']}` {b['dosya']}:{b['satir']} — "
                      f"{b['aciklama']} | `{b['ornek']}`")
    else:
        md.append("Bulgu yok.")
    md += ["", "## Sonuc", "",
           ("**KRITIK bulgu var — mudahale gerekli.**" if kritik else "**Kritik bulgu yok.**"), ""]
    md_yol = AUDIT_DIR / "CL-03_guvenlik_raporu.md"
    json_yol = AUDIT_DIR / "tarama_sonuc.json"
    md_yol.write_text("\n".join(md), encoding="utf-8")
    json_yol.write_text(json.dumps(
        {"tarih": simdi, "toplam": len(tum), "bulgular": tum},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return md_yol, json_yol


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    bag = bagimlilik_tara()
    statik = statik_tara()
    md_yol, json_yol = rapor_yaz(bag, statik)
    print(json_yol.read_text(encoding="utf-8") if a.json else md_yol.read_text(encoding="utf-8"))
    return 1 if any(b["siddet"] == "kritik" for b in bag + statik) else 0


if __name__ == "__main__":
    sys.exit(main())
