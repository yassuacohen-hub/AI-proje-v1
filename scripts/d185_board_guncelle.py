# -*- coding: utf-8 -*-
"""D-185: DASH-UX-02a split (v1/v2) panoya islenir. Idempotent.

Kullanim:
  python scripts/d185_board_guncelle.py
"""
from __future__ import annotations

import json
from pathlib import Path

PANO = Path(__file__).resolve().parent.parent / "data" / "orchestrator" / "task_board.json"

V1_NOT = (
    "D-185 split v1: sadece admin_sistem.py yazilir, web_dashboard/tabs/__init__.py'ye "
    "DOKUNULMAZ. SECTIONS kaydi DASH-UX-02a-SECTIONS (v2) gorevinde, MENUTREE sonrasi. "
    "Brief: plans/brief_utku_DASH-UX-02a-v1.md"
)

V2_GOREV = {
    "task_id": "DASH-UX-02a-SECTIONS",
    "id": "DASH-UX-02a-SECTIONS",
    "baslik": "[DASH-UX] DASH-UX-02a-SECTIONS: admin_sistem sekmesini SECTIONS'a kaydet",
    "sahip": "utku",
    "oncelik": "P1",
    "durum": "plan",
    "baslangic": None,
    "bitis": None,
    "dosyalar": ["web_dashboard/tabs/__init__.py"],
    "not": (
        "D-185 split v2: DASH-UX-02a (v1) onaylandiktan + ADMIN-UX-MENUTREE-01 bitince "
        "yapilir. SECTIONS kaydi + full regresyon."
    ),
    "source": "ic",
    "from_agent": None,
    "blokaj": ["DASH-UX-02a", "ADMIN-UX-MENUTREE-01"],
    "talimat": (
        "admin_sistem sekmesini SECTIONS'a ekle. MENUTREE'nin Ayarlar cikarma ve grup "
        "duzenlemesinin ustune yaz. K1 kalibrasyonu v1 raporundan alinir. "
        "pytest tests/ -q tamamen yesil olmali."
    ),
    "mod": "code",
    "brief": "plans/brief_utku_DASH-UX-02a-v2.md",
}


def main() -> int:
    gorevler = json.loads(PANO.read_text(encoding="utf-8"))
    degisti = False

    for gorev in gorevler:
        if gorev.get("task_id") == "DASH-UX-02a":
            if gorev.get("not") != V1_NOT:
                gorev["not"] = V1_NOT
                gorev["brief"] = "plans/brief_utku_DASH-UX-02a-v1.md"
                degisti = True
                print("[OK] DASH-UX-02a -> v1 notu/brief guncellendi")
            else:
                print("[ATLA] DASH-UX-02a zaten v1 notunda")
        elif gorev.get("task_id") == "DASH-UX-02b":
            yeni_blokaj = ["SENTEZ-01", "DASH-UX-02a-SECTIONS"]
            if gorev.get("blokaj") != yeni_blokaj:
                gorev["blokaj"] = yeni_blokaj
                gorev["not"] = (
                    "D-185: 02b artik DASH-UX-02a-SECTIONS (v2) bitince baslar; "
                    "K1 kalibrasyonu v1 raporundan. Brief: plans/brief_utku_DASH-UX-02b.md"
                )
                degisti = True
                print("[OK] DASH-UX-02b -> blokaj v2'ye kaydirildi")
            else:
                print("[ATLA] DASH-UX-02b blokaji zaten dogru")

    mevcut = {g.get("task_id") for g in gorevler}
    if "DASH-UX-02a-SECTIONS" not in mevcut:
        gorevler.append(V2_GOREV)
        degisti = True
        print("[OK] DASH-UX-02a-SECTIONS gorevi eklendi")
    else:
        print("[ATLA] DASH-UX-02a-SECTIONS zaten var")

    if degisti:
        PANO.write_text(
            json.dumps(gorevler, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print("[OK] task_board.json yazildi")
    else:
        print("[OK] Degisiklik yok (idempotent)")

    # Self-check: zincir dogru mu?
    kontrol = {g["task_id"]: g for g in json.loads(PANO.read_text(encoding="utf-8")) if "task_id" in g}
    assert "DASH-UX-02a-SECTIONS" in kontrol, "v2 gorevi panoda yok"
    assert kontrol["DASH-UX-02a-SECTIONS"]["blokaj"] == ["DASH-UX-02a", "ADMIN-UX-MENUTREE-01"]
    assert "DASH-UX-02a-SECTIONS" in kontrol["DASH-UX-02b"]["blokaj"], "02b v2'ye bagli degil"
    assert "__init__.py" not in " ".join(kontrol["DASH-UX-02a"]["dosyalar"]), "v1 hala __init__.py'ye bagli"
    print("[OK] Self-check gecti: v1 -> v2 -> 02b zinciri dogru")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
