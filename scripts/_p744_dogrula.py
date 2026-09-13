# -*- coding: utf-8 -*-
"""P7-44 gecici dogrulama: navigasyon kayit defteri tutarliligi.

Streamlit runtime olmadan calisir; ciktiyi dosyaya yazar.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.disable(logging.WARNING)

KOK = Path(__file__).resolve().parents[1]
for p in (str(KOK), str(KOK / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from web_dashboard.tabs import (  # noqa: E402
    SECTIONS,
    gruplar,
    render_fonksiyonu,
    tab_getir,
    tab_url_getir,
    varsayilan_tab,
)

satirlar: list[str] = []
hata = 0


def kontrol(ad: str, kosul: bool, detay: str = "") -> None:
    global hata
    if kosul:
        satirlar.append(f"[OK]   {ad}")
    else:
        hata += 1
        satirlar.append(f"[FAIL] {ad} {detay}")


kontrol("SECTIONS 8 bolum", len(SECTIONS) == 8, f"-> {len(SECTIONS)}")

anahtarlar = [t.anahtar for t in SECTIONS]
urller = [t.url_path for t in SECTIONS]
kontrol("anahtarlar benzersiz", len(set(anahtarlar)) == len(anahtarlar))
kontrol("url_path benzersiz", len(set(urller)) == len(urller))
kontrol("varsayilan = ana_kontrol", varsayilan_tab().anahtar == "ana_kontrol")
kontrol("tab_getir('paketler')", getattr(tab_getir("paketler"), "anahtar", None) == "paketler")
kontrol("tab_getir('yok') -> None", tab_getir("yok") is None)
kontrol("tab_url_getir('/Paketler/')", getattr(tab_url_getir("/Paketler/"), "anahtar", None) == "paketler")
kontrol("tab_url_getir('') -> None", tab_url_getir("") is None)

gruplama = gruplar()
kontrol("2 grup", len(gruplama) == 2, f"-> {list(gruplama)}")
kontrol("grup toplami = 8", sum(len(v) for v in gruplama.values()) == 8)

satirlar.append("")
satirlar.append("--- Bolum -> render fonksiyonu cozumlemesi ---")
for t in SECTIONS:
    fn = render_fonksiyonu(t)
    if not t.hazir:
        durum = "PLACEHOLDER (beklenen: " + (t.bekleyen_gorev or "-") + ")"
        kontrol(f"{t.anahtar}: hazir=False -> None", fn is None)
    else:
        durum = f"{t.modul}.{t.fonksiyon}"
        kontrol(f"{t.anahtar}: callable", callable(fn), f"-> {durum} COZULEMEDI")
    satirlar.append(f"  {t.ikon} {t.baslik:<12} | {t.grup:<22} | ?bolum={t.url_path:<12} | {durum}")

satirlar.append("")
satirlar.append(f"SONUC: {'TUM KONTROLLER GECTI' if hata == 0 else str(hata) + ' HATA'}")

cikti = "\n".join(satirlar)
Path(KOK / "tests" / "_p744_sonuc.txt").write_text(cikti, encoding="utf-8")
print(cikti)
sys.exit(1 if hata else 0)
