"""VERI KARSILASTIRMA: eldeki veri seti vs diger kaynak (D-283).

KAHIN'in sorusu (2026-09-29): *"en onemli sey kiyaslama; elimizdeki veriyi
zenginlestirecek mi onu olcelim."*

Bu arac SADECE mevcut dosyalari okur, HICBIR istek atmaz:
  1. Her dosyanin kolon bazli doluluk oranini cikarir
  2. Kolonlar arasindaki Cakismayi (K-2 ihlali) olcer
  3. Ayni unvani iki kaynakta sayar -> GERCEKTEN zenginlestirme var mi?
  4. Kaynak basina kirilim verir (hangi alan nereden geliyor)

Kurallar: docs/VERI_KAYNAK_KURALLARI.md (K-1..K-5)
Kullanim: python scripts/veri_karsilastir.py
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter, defaultdict
from typing import Any, Optional

KOK = pathlib.Path(__file__).resolve().parents[1]
DATA = KOK / "data" / "ostim"
CIKTI = KOK / "data" / "karsilastirma_raporu.json"

DOSYALAR = ["firmalar_full.jsonl", "firmalar_vkn_ekli.jsonl"]

KOLONLAR = [
    "unvan", "adres", "telefonler", "emailler", "web_sitesi",
    "vergi_no", "sektor", "nace_code", "nace_name_tr",
    "nace_source", "nace_confidence", "sosyal_medya", "yetkili",
    "osb_parsel", "slug", "kaynak", "cekilme_tarihi",
]


def dolu(s: Any) -> bool:
    """Bos deger sayimi bosluk, bos liste/dict, None."""
    if s is None:
        return False
    if isinstance(s, (list, dict, str)):
        return len(s) > 0
    return True


def unvan_anahtari(u: Optional[str]) -> str:
    """Unvan karsilastirma anahtari (buyuk/kucuk, noktalama, TR harfleri)."""
    if not u:
        return ""
    t = u.strip().upper()
    for a, b in [("İ", "I"), ("Ş", "S"), ("Ğ", "G"), ("Ü", "U"),
                 ("Ö", "O"), ("Ç", "C")]:
        t = t.replace(a, b)
    t = "".join(ch for ch in t if ch.isalnum() or ch.isspace())
    return " ".join(t.split())




def yukle(dosya: str) -> list[dict]:
    """JSONL dosyasini okur. Hatali satirlar atlanir (sayim raporlanir)."""
    p = DATA / dosya
    if not p.is_file():
        return []
    out = []
    for satir in p.read_text(encoding="utf-8").splitlines():
        if satir.strip():
            try:
                out.append(json.loads(satir))
            except json.JSONDecodeError:
                pass
    return out


def kolon_istatistik(kayitlar: list[dict]) -> dict:
    n = len(kayitlar)
    if not n:
        return {"kayit": 0}
    st = {}
    for k in KOLONLAR:
        if not any(k in s for s in kayitlar):
            continue
        d = sum(1 for s in kayitlar if dolu(s.get(k)))
        st[k] = {"dolu": d, "oran_yuzde": round(100 * d / n, 1)}
    return {"kayit": n, "kolonlar": st}


def cakisma_analizi(kayitlar: list[dict]) -> dict:
    """K-2 ihlali olcumu: coklu kaynakli kayit + NACE hane dagilimi.

    VERI_KAYNAK_KURALLARI.md kaniti: ASO'nun resmi 6 haneli NACE'i ile
    OSTIM'in 4 haneli varsayilani ayni tabloda ayni islemi gordu -> 592 resmi
    kayit 5705 cop icinde kayboldu. Bu, ayni hatanin tekrarlanip
    tekrarlanmadigini olcer.
    """
    tur_dagilim = Counter()
    nace_hane = Counter()
    karisik = []

    for s in kayitlar:
        k = s.get("kaynak")
        if isinstance(k, (list, tuple, set)):
            tur_dagilim[",".join(sorted(map(str, k)))] += 1
            if len(k) > 1:
                karisik.append(s.get("unvan"))
        else:
            tur_dagilim[str(k)] += 1
        nc = s.get("nace_code")
        if nc:
            nace_hane[len(str(nc).replace(".", ""))] += 1

    return {
        "kaynak_dagilimi": dict(tur_dagilim.most_common(15)),
        "nace_hane_dagilimi": dict(sorted(nace_hane.items())),
        "coklu_kaynakli_kayit": len(karisik),
        "coklu_kaynakli_ornek": [u for u in karisik[:5] if u],
    }


def karsilastir(a: list[dict], b: list[dict]) -> dict:
    """Iki veri setini unvan anahtarinda karsilastirir.

    SORU: b, a'yi ZENGINLESTIRIYOR MU? Yani b'de olup a'da olmayan unvan
    var mi, ve eslesen unvanlarda a'da bos olan alanlari b dolduruyor mu?
    """
    ia = {unvan_anahtari(s.get("unvan")): s for s in a if s.get("unvan")}
    ib = {unvan_anahtari(s.get("unvan")): s for s in b if s.get("unvan")}
    ka, kb = set(ia), set(ib)
    ortak = ka & kb

    zenginlestirme: dict = defaultdict(int)
    ornekler: dict = defaultdict(list)
    for u in ortak:
        sa, sb = ia[u], ib[u]
        for k in KOLONLAR:
            if k not in sb:
                continue
            if not dolu(sa.get(k)) and dolu(sb.get(k)):
                zenginlestirme[k] += 1
                if len(ornekler[k]) < 3:
                    ornekler[k].append(sa.get("unvan"))

    return {
        "a_kayit": len(a), "b_kayit": len(b),
        "a_tekil_unvan": len(ka), "b_tekil_unvan": len(kb),
        "ortak_unvan": len(ortak),
        "b_ile_yeni_unvan": len(kb - ka),
        "a_ile_kalan_unvan": len(ka - kb),
        "ortusma_yuzde": round(100 * len(ortak) / max(len(ka), 1), 1),
        "zenginlestirilen_kolonlar": dict(
            sorted(zenginlestirme.items(), key=lambda x: -x[1])
        ),
        "ornekler": {k: v for k, v in ornekler.items()},
    }



if __name__ == "__main__":
    veri = {d: yukle(d) for d in DOSYALAR}
    rapor = {
        "dosyalar": {
            d: {**kolon_istatistik(veri[d]), **cakisma_analizi(veri[d])}
            for d in DOSYALAR
        }
    }
    if len(DOSYALAR) == 2:
        rapor["karsilastirma"] = karsilastir(veri[DOSYALAR[0]], veri[DOSYALAR[1]])

    CIKTI.write_text(json.dumps(rapor, ensure_ascii=False, indent=2),
                     encoding="utf-8")
    for d, v in rapor["dosyalar"].items():
        print("=" * 58)
        print(f"{d}  -> {v['kayit']} kayit")
        for k, s in sorted(v["kolonlar"].items(),
                           key=lambda x: -x[1]["oran_yuzde"]):
            print(f"   {k:20s} %{s['oran_yuzde']:<6} ({s['dolu']}/{v['kayit']})")
        print("   kaynak dagilimi:", v["kaynak_dagilimi"])
        print("   NACE hane       :", v["nace_hane_dagilimi"])
        print("   coklu kaynakli  :", v["coklu_kaynakli_kayit"])
    if "karsilastirma" in rapor:
        print("=" * 58)
        k = rapor["karsilastirma"]
        for a, b in k.items():
            if a not in ("zenginlestirilen_kolonlar", "ornekler"):
                print(f"   {a:26s} {b}")
        print("   zenginlestirilen:", k["zenginlestirilen_kolonlar"])
    print(CIKTI)
