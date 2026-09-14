# -*- coding: utf-8 -*-
"""MRK-02h — Huginn i18n disa aktarim uretici."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Final

from company_master.i18n import sozluk

KOK: Final[Path] = Path(__file__).resolve().parent
HEDEF: Final[Path] = KOK.parent.parent.parent / "web_dashboard" / "js" / "messages.js"

HUGINN_ONEKLERI = ("menu_h_", "eylem_", "durum_", "veri_", "huginn_")
ODIN_ORTAK = (
    "odin_baglanti_koptu",
    "odin_sunucu_hatasi",
    "odin_zaman_asimi",
    "muninn_yetki_yok",
    "muninn_oturum_doldu",
)

TON_IKON_VARSAYILAN = {
    "info": "info",
    "success": "check_circle",
    "warning": "warning",
    "danger": "error",
    "neutral": "circle",
}


def huginn_anahtarlari() -> tuple[str, ...]:
    kayitlar = sozluk()
    secilen = []
    for anahtar in sorted(kayitlar):
        if any(anahtar.startswith(onek) for onek in HUGINN_ONEKLERI) or anahtar in ODIN_ORTAK:
            secilen.append(anahtar)
    return tuple(secilen)


def kayit_donustur(anahtar: str, kayit: dict, dil: str) -> dict:
    ham = kayit.get(dil)
    if isinstance(ham, str):
        metin = ham
    elif isinstance(ham, dict):
        metin = ham.get("usta") or ham.get("cirak") or ""
    else:
        metin = ""
    ton = kayit.get("ton", "neutral")
    ikon = kayit.get("ikon") or TON_IKON_VARSAYILAN.get(ton, "circle")
    return {"metin": metin, "katman": kayit.get("katman", "cerceve"), "ton": ton, "ikon": ikon}


def js_uret() -> str:
    kayitlar = sozluk()
    anahtarlari = huginn_anahtarlari()
    tr_blok = []
    en_blok = []
    for anahtar in anahtarlari:
        kayit = kayitlar[anahtar]
        tr_blok.append('  "{0}": {1}'.format(anahtar, json.dumps(kayit_donustur(anahtar, kayit, "tr"), ensure_ascii=False)))
        en_blok.append('  "{0}": {1}'.format(anahtar, json.dumps(kayit_donustur(anahtar, kayit, "en"), ensure_ascii=False)))
    tr_str = ",\n".join(tr_blok)
    en_str = ",\n".join(en_blok)
    return f"""// -*- coding: utf-8 -*-
// OTOMATIK URETILDI - ELLE DUZENLEMEYIN
// Kaynak: src/company_master/i18n/ses.json + ui.json
// Uretici: src/company_master/i18n/disa_aktar.py
// Uretim: python -m company_master.i18n.disa_aktar

export const MESSAGES = {{
  "tr": {{
{tr_str}
  }},
  "en": {{
{en_str}
  }}
}};

export const VARSAYILAN_DIL = "tr";
export const VARSAYILAN_SEVIYE = "usta";

let _dil = VARSAYILAN_DIL;

export function dilAyarla(dil) {{
  if (dil in MESSAGES) {{ _dil = dil; }}
  return _dil;
}}

export function aktifDil() {{ return _dil; }}

export function ses(anahtar, parametreler) {{
  const tablo = MESSAGES[_dil] || MESSAGES[VARSAYILAN_DIL];
  let kayit = tablo[anahtar];
  if (!kayit) {{ kayit = MESSAGES[VARSAYILAN_DIL][anahtar]; }}
  if (!kayit) {{
    return {{ metin: anahtar, katman: "veri", ton: "neutral", ikon: "circle", bulundu: false }};
  }}
  let metin = kayit.metin;
  if (parametreler) {{
    for (const [ad, deger] of Object.entries(parametreler)) {{
      metin = metin.split("{{" + ad + "}}").join(String(deger));
    }}
  }}
  return {{ metin: metin, katman: kayit.katman, ton: kayit.ton, ikon: kayit.ikon, bulundu: true }};
}}

export function t(anahtar, parametreler) {{
  return ses(anahtar, parametreler).metin;
}}
"""


def yaz(hedef: Path | None = None) -> Path:
    hedef = hedef or HEDEF
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_text(js_uret(), encoding="utf-8", newline="\n")
    return hedef


def kontrol(hedef: Path | None = None) -> bool:
    hedef = hedef or HEDEF
    if not hedef.exists():
        return False
    return hedef.read_text(encoding="utf-8") == js_uret()


def main() -> int:
    parser = argparse.ArgumentParser(description="Huginn i18n mesaji uretici")
    parser.add_argument("--kontrol", action="store_true")
    parser.add_argument("--hedef", type=Path, default=None)
    args = parser.parse_args()
    hedef = args.hedef or HEDEF
    if args.kontrol:
        if kontrol(hedef):
            print("GUNCEL : " + str(hedef))
            return 0
        print("FARK VAR : " + str(hedef) + " guncel degil")
        print("Cozum    : python -m company_master.i18n.disa_aktar")
        return 1
    yaz(hedef)
    print("URETILDI : " + str(hedef))
    print("ANAHTAR  : " + str(len(huginn_anahtarlari())))
    print("DIL      : tr, en")
    return 0


if __name__ == "__main__":
    sys.exit(main())
