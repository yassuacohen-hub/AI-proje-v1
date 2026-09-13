#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""P7-24 — ASO ve OSTIM Veri Kalite Raporu.

Amac
----
`data/aso/*.jsonl` ve `data/ostim/*.jsonl` ham kaynaklarini ortak bir semaya
cevirip alan doluluk, kalite skoru, kopya ve kirlilik (boilerplate) analizini
tek raporda toplar.

Kalite skoru, veritabani tarafindaki kanonik formulle (bkz.
`scripts/quality_recalc_fast.py`) birebir ayni agirliklari kullanir:

    VKN 15 + adres 15 + telefon 15 + e-posta 15 + web 10
    + NACE 15 + OSB parsel 10 + ticaret adi 5   (tavan 100)

Onemli bulgu (kirlilik / contamination)
---------------------------------------
OSTIM kayitlarinin bir kismi firmaya degil, OSB portalina ait ortak degerler
tasiyor (orn. `web_sitesi = https://www.ostimistihdam.com`, sosyal medya
hesaplari OSTIM OSB'nin kendi hesaplari). Bu degerler "web sitesi var" diye
sayilirsa kalite skoru yapay olarak sisiyor. Rapor hem **ham** hem de
**temizlenmis** (kirlilik dusulmus) skoru yan yana verir.

Kullanim
--------
    python scripts/quality_report.py
    python scripts/quality_report.py --json-out data/quality/rapor.json
    python scripts/quality_report.py --md-out data/quality/rapor.md --sessiz
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

# Windows konsolu (cp1254) Turkce/Unicode karakterlerde cokebiliyor.
for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------

#: Kanonik kalite skoru agirliklari (DB ile ayni).
AGIRLIKLAR: dict[str, int] = {
    "vkn": 15,
    "adres": 15,
    "telefon": 15,
    "eposta": 15,
    "web": 10,
    "nace": 15,
    "parsel": 10,
    "ticaret_adi": 5,
}

#: VKN/TCKN format kontrolu (10 veya 11 hane).
VKN_DESENI = re.compile(r"^\d{10,11}$")

#: Basit e-posta format kontrolu.
EPOSTA_DESENI = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")

#: Telefon: sadece rakamlar alindiktan sonra 10-13 hane makul kabul edilir.
TELEFON_MIN_HANE = 10
TELEFON_MAKS_HANE = 13

#: NACE kodu: 2 haneden baslayip nokta ile derinlesen kod (orn. 43.21.01).
NACE_DESENI = re.compile(r"^\d{2}(\.\d{1,2}){0,3}$")

#: Firmaya degil portala ait oldugu bilinen domainler (kirlilik).
PORTAL_DOMAINLERI: tuple[str, ...] = (
    "ostimistihdam.com",
    "ostim.org.tr",
    "ostim.com.tr",
    "ostimteknopark.com.tr",
    "aso.org.tr",
)

#: Anlamsiz / placeholder kabul edilen degerler.
BOS_SAYILAN = {"", "-", "--", "yok", "bilinmiyor", "n/a", "na", "null", "none", "0"}

#: Varsayilan girdi dosyalari (kaynak adi -> dosya yolu).
VARSAYILAN_GIRDILER: dict[str, str] = {
    "aso": "data/aso/aso_full.jsonl",
    "ostim": "data/ostim/firmalar_full.jsonl",
    "ostim_detayli": "data/ostim/firmalar_detayli.jsonl",
}


# ---------------------------------------------------------------------------
# Yardimcilar
# ---------------------------------------------------------------------------


def _metin(deger: Any) -> str:
    """Herhangi bir degeri kirpilmis metne cevirir; anlamsizsa bos dondurur."""
    if deger is None:
        return ""
    if isinstance(deger, (list, tuple)):
        for oge in deger:
            metin = _metin(oge)
            if metin:
                return metin
        return ""
    if isinstance(deger, dict):
        return ""
    metin = str(deger).strip()
    if metin.lower() in BOS_SAYILAN:
        return ""
    return metin


def _liste(deger: Any) -> list[str]:
    """Tek deger veya listeyi temiz metin listesine cevirir."""
    if deger is None:
        return []
    if isinstance(deger, (list, tuple)):
        ham = list(deger)
    else:
        ham = [deger]
    cikti: list[str] = []
    for oge in ham:
        if isinstance(oge, dict):
            continue
        metin = str(oge).strip()
        if metin and metin.lower() not in BOS_SAYILAN:
            cikti.append(metin)
    return cikti


def _sadece_rakam(metin: str) -> str:
    return re.sub(r"\D", "", metin or "")


def _domain(url: str) -> str:
    """URL'den domain cikarir (www. atilir, kucuk harfe cevrilir)."""
    if not url:
        return ""
    temiz = re.sub(r"^[a-zA-Z]+://", "", url.strip()).lower()
    temiz = temiz.split("/")[0].split("?")[0].split("#")[0]
    if temiz.startswith("www."):
        temiz = temiz[4:]
    return temiz


def portal_mi(url: str) -> bool:
    """Verilen URL firmaya degil OSB/oda portalina mi ait?"""
    d = _domain(url)
    if not d:
        return False
    return any(d == p or d.endswith("." + p) for p in PORTAL_DOMAINLERI)


def vkn_gecerli(vkn: str) -> bool:
    """VKN format kontrolu (10-11 hane, hepsi ayni rakam degil)."""
    rakam = _sadece_rakam(vkn)
    if not VKN_DESENI.match(rakam):
        return False
    return len(set(rakam)) > 1


def eposta_gecerli(eposta: str) -> bool:
    return bool(EPOSTA_DESENI.match(eposta.strip())) if eposta else False


def telefon_gecerli(telefon: str) -> bool:
    rakam = _sadece_rakam(telefon)
    return TELEFON_MIN_HANE <= len(rakam) <= TELEFON_MAKS_HANE


def nace_gecerli(kod: str) -> bool:
    return bool(NACE_DESENI.match(kod.strip())) if kod else False


def unvan_anahtari(unvan: str) -> str:
    """Kopya tespiti icin unvani normalize eder (noktalama/bosluk/buyuk-kucuk)."""
    if not unvan:
        return ""
    metin = unvan.casefold()
    # Turkce karakterleri sadelestir (I/i sorunu dahil)
    eslesme = str.maketrans("çğıöşüâîû", "cgiosuaiu")
    metin = metin.translate(eslesme)
    metin = re.sub(r"[^a-z0-9]+", " ", metin)
    return re.sub(r"\s+", " ", metin).strip()


# ---------------------------------------------------------------------------
# Normalizasyon: kaynak semalari -> ortak sema
# ---------------------------------------------------------------------------


def normalize_kayit(ham: dict[str, Any], kaynak: str) -> dict[str, Any]:
    """Kaynak bagimsiz ortak semaya cevirir.

    Ortak alanlar: unvan, vkn, adres, telefon, eposta, web, nace, parsel,
    ticaret_adi, sektor + kirlilik bayraklari.
    """
    unvan = _metin(ham.get("unvan") or ham.get("legal_name") or ham.get("firma_adi"))

    telefonlar = _liste(ham.get("telefonlar") or ham.get("telefonler") or ham.get("telefon"))
    epostalar = _liste(ham.get("emailler") or ham.get("eposta") or ham.get("email"))

    web_ham = _metin(ham.get("web_sitesi") or ham.get("website") or ham.get("web"))
    web_portal = portal_mi(web_ham)

    sosyal = ham.get("sosyal_medya") if isinstance(ham.get("sosyal_medya"), dict) else {}
    sosyal_linkler = [_metin(v) for v in (sosyal or {}).values()]
    sosyal_linkler = [s for s in sosyal_linkler if s]
    sosyal_portal = bool(sosyal_linkler) and all(portal_mi(s) for s in sosyal_linkler)

    nace = _metin(ham.get("naceKod") or ham.get("nace_code") or ham.get("nace"))
    vkn = _metin(ham.get("vergi_no") or ham.get("tax_number") or ham.get("vkn"))
    parsel = _metin(ham.get("osb_parsel") or ham.get("parsel"))

    # ASO'da ticaret sicil no ayri bir kimlik alani; ticaret adi yerine gecmez
    # ama kaynak izlenebilirligi icin tasiyoruz.
    sicil = _metin(ham.get("ticaretSicilNo") or ham.get("ticaret_sicil_no"))

    return {
        "kaynak": kaynak,
        "unvan": unvan,
        "unvan_anahtari": unvan_anahtari(unvan),
        "vkn": vkn,
        "vkn_gecerli": vkn_gecerli(vkn),
        "adres": _metin(ham.get("adres") or ham.get("address")),
        "telefonlar": telefonlar,
        "telefon_gecerli": any(telefon_gecerli(t) for t in telefonlar),
        "epostalar": epostalar,
        "eposta_gecerli": any(eposta_gecerli(e) for e in epostalar),
        "web": web_ham,
        "web_portal": web_portal,
        "web_temiz": "" if web_portal else web_ham,
        "sosyal_link_sayisi": len(sosyal_linkler),
        "sosyal_portal": sosyal_portal,
        "nace": nace,
        "nace_gecerli": nace_gecerli(nace),
        "parsel": parsel,
        "sektor": _metin(ham.get("sektor") or ham.get("meslekGrubu")),
        "ticaret_sicil_no": sicil,
        "yetkili": _metin(ham.get("yetkili") or ham.get("yetkililer")),
    }


# ---------------------------------------------------------------------------
# Skorlama
# ---------------------------------------------------------------------------


def kalite_skoru(kayit: dict[str, Any], *, kirlilik_dus: bool = True) -> float:
    """Kanonik agirliklarla 0-100 arasi kalite skoru.

    `kirlilik_dus=True` iken portal kaynakli web sitesi puan getirmez.
    """
    skor = 0
    if kayit.get("vkn"):
        skor += AGIRLIKLAR["vkn"]
    if kayit.get("adres"):
        skor += AGIRLIKLAR["adres"]
    if kayit.get("telefonlar"):
        skor += AGIRLIKLAR["telefon"]
    if kayit.get("epostalar"):
        skor += AGIRLIKLAR["eposta"]

    web = kayit.get("web_temiz") if kirlilik_dus else kayit.get("web")
    if web:
        skor += AGIRLIKLAR["web"]

    if kayit.get("nace"):
        skor += AGIRLIKLAR["nace"]
    if kayit.get("parsel"):
        skor += AGIRLIKLAR["parsel"]
    if kayit.get("sektor"):
        skor += AGIRLIKLAR["ticaret_adi"]

    return float(min(skor, 100))


def skor_kovasi(skor: float) -> str:
    """Skoru okunabilir kovaya yerlestirir."""
    if skor >= 80:
        return "80-100 (cok iyi)"
    if skor >= 60:
        return "60-79 (iyi)"
    if skor >= 40:
        return "40-59 (orta)"
    if skor >= 20:
        return "20-39 (zayif)"
    return "0-19 (cok zayif)"


# ---------------------------------------------------------------------------
# Okuma
# ---------------------------------------------------------------------------


def jsonl_oku(yol: Path) -> Iterable[dict[str, Any]]:
    """JSONL dosyasini satir satir okur; bozuk satirlari atlar."""
    if not yol.exists():
        return
    with yol.open("r", encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue
            try:
                veri = json.loads(satir)
            except json.JSONDecodeError:
                continue
            if isinstance(veri, dict):
                yield veri


# ---------------------------------------------------------------------------
# Analiz
# ---------------------------------------------------------------------------


def kaynak_analiz(kaynak: str, yol: Path) -> dict[str, Any]:
    """Tek kaynak icin doluluk/kalite/kopya/kirlilik istatistigi uretir."""
    kayitlar = [normalize_kayit(h, kaynak) for h in jsonl_oku(yol)]
    toplam = len(kayitlar)

    if toplam == 0:
        return {
            "kaynak": kaynak,
            "dosya": str(yol.relative_to(ROOT)) if yol.is_relative_to(ROOT) else str(yol),
            "mevcut": yol.exists(),
            "toplam_kayit": 0,
            "doluluk": {},
            "gecerlilik": {},
            "kirlilik": {},
            "kopya": {},
            "skor": {},
        }

    alanlar = ["unvan", "vkn", "adres", "telefonlar", "epostalar", "web", "nace", "parsel", "sektor"]
    doluluk = {
        alan: {
            "dolu": sum(1 for k in kayitlar if k.get(alan)),
            "oran": round(100 * sum(1 for k in kayitlar if k.get(alan)) / toplam, 2),
        }
        for alan in alanlar
    }

    def _gecerlilik(dolu_alan: str, bayrak: str) -> dict[str, Any]:
        dolu = [k for k in kayitlar if k.get(dolu_alan)]
        gecerli = sum(1 for k in dolu if k.get(bayrak))
        return {
            "dolu": len(dolu),
            "gecerli": gecerli,
            "hatali": len(dolu) - gecerli,
            "gecerlilik_orani": round(100 * gecerli / len(dolu), 2) if dolu else 0.0,
        }

    gecerlilik = {
        "vkn": _gecerlilik("vkn", "vkn_gecerli"),
        "telefon": _gecerlilik("telefonlar", "telefon_gecerli"),
        "eposta": _gecerlilik("epostalar", "eposta_gecerli"),
        "nace": _gecerlilik("nace", "nace_gecerli"),
    }

    web_dolu = [k for k in kayitlar if k.get("web")]
    portal_web = [k for k in web_dolu if k.get("web_portal")]
    portal_sosyal = [k for k in kayitlar if k.get("sosyal_portal")]
    domain_sayaci = Counter(_domain(k["web"]) for k in web_dolu if _domain(k["web"]))

    kirlilik = {
        "web_dolu": len(web_dolu),
        "web_portal_kaynakli": len(portal_web),
        "web_portal_orani": round(100 * len(portal_web) / len(web_dolu), 2) if web_dolu else 0.0,
        "sosyal_medya_portal_kaynakli": len(portal_sosyal),
        "gercek_firma_web_sitesi": len(web_dolu) - len(portal_web),
        "en_sik_domainler": domain_sayaci.most_common(10),
    }

    unvan_sayaci = Counter(k["unvan_anahtari"] for k in kayitlar if k["unvan_anahtari"])
    kopya_unvanlar = {u: s for u, s in unvan_sayaci.items() if s > 1}
    vkn_sayaci = Counter(_sadece_rakam(k["vkn"]) for k in kayitlar if k.get("vkn"))
    kopya_vkn = {v: s for v, s in vkn_sayaci.items() if s > 1}

    kopya = {
        "benzersiz_unvan": len(unvan_sayaci),
        "kopya_unvan_grubu": len(kopya_unvanlar),
        "kopya_unvan_kayit": sum(kopya_unvanlar.values()) - len(kopya_unvanlar),
        "kopya_vkn_grubu": len(kopya_vkn),
        "ornek_kopya_unvanlar": sorted(kopya_unvanlar.items(), key=lambda x: -x[1])[:5],
        "unvansiz_kayit": sum(1 for k in kayitlar if not k["unvan"]),
    }

    ham_skorlar = [kalite_skoru(k, kirlilik_dus=False) for k in kayitlar]
    temiz_skorlar = [kalite_skoru(k, kirlilik_dus=True) for k in kayitlar]
    kova = Counter(skor_kovasi(s) for s in temiz_skorlar)

    skor = {
        "ortalama_ham": round(sum(ham_skorlar) / toplam, 2),
        "ortalama_temiz": round(sum(temiz_skorlar) / toplam, 2),
        "sisme_farki": round((sum(ham_skorlar) - sum(temiz_skorlar)) / toplam, 2),
        "min": min(temiz_skorlar),
        "maks": max(temiz_skorlar),
        "medyan": sorted(temiz_skorlar)[toplam // 2],
        "dagilim": dict(sorted(kova.items(), reverse=True)),
    }

    return {
        "kaynak": kaynak,
        "dosya": str(yol.relative_to(ROOT)) if yol.is_relative_to(ROOT) else str(yol),
        "mevcut": True,
        "toplam_kayit": toplam,
        "doluluk": doluluk,
        "gecerlilik": gecerlilik,
        "kirlilik": kirlilik,
        "kopya": kopya,
        "skor": skor,
    }


def capraz_analiz(sonuclar: list[dict[str, Any]]) -> dict[str, Any]:
    """Kaynaklar arasi tamamlayicilik ozeti (hangi alan hangi kaynakta guclu)."""
    tablo: dict[str, dict[str, float]] = {}
    for s in sonuclar:
        if not s["toplam_kayit"]:
            continue
        for alan, deger in s["doluluk"].items():
            tablo.setdefault(alan, {})[s["kaynak"]] = deger["oran"]

    tamamlayici: list[str] = []
    for alan, oranlar in tablo.items():
        if len(oranlar) < 2:
            continue
        en_iyi = max(oranlar, key=lambda k: oranlar[k])
        en_kotu = min(oranlar, key=lambda k: oranlar[k])
        if oranlar[en_iyi] - oranlar[en_kotu] >= 50:
            tamamlayici.append(
                f"{alan}: {en_iyi} (%{oranlar[en_iyi]}) >> {en_kotu} (%{oranlar[en_kotu]})"
            )

    return {"alan_doluluk_matrisi": tablo, "tamamlayici_alanlar": tamamlayici}


# ---------------------------------------------------------------------------
# Raporlama
# ---------------------------------------------------------------------------


def markdown_rapor(sonuclar: list[dict[str, Any]], capraz: dict[str, Any]) -> str:
    """Insan okur Markdown raporu uretir (Turkce)."""
    zaman = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    sat: list[str] = []
    sat.append("# ASO ve OSTİM Veri Kalite Raporu (P7-24)")
    sat.append("")
    sat.append(f"**Üretim tarihi:** {zaman}  ")
    sat.append("**Üreten:** `scripts/quality_report.py`  ")
    sat.append(
        "**Skor formülü:** VKN 15 + adres 15 + telefon 15 + e-posta 15 + web 10 "
        "+ NACE 15 + parsel 10 + sektör/ticaret adı 5 (tavan 100) — "
        "`scripts/quality_recalc_fast.py` ile aynı ağırlıklar."
    )
    sat.append("")

    # Özet tablo
    sat.append("## 1. Özet")
    sat.append("")
    sat.append("| Kaynak | Kayıt | Ort. Skor (temiz) | Ort. Skor (ham) | Şişme | Kopya Ünvan Grubu |")
    sat.append("|---|---:|---:|---:|---:|---:|")
    for s in sonuclar:
        if not s["toplam_kayit"]:
            sat.append(f"| `{s['kaynak']}` | 0 | - | - | - | - | ")
            continue
        sat.append(
            f"| `{s['kaynak']}` | {s['toplam_kayit']} | {s['skor']['ortalama_temiz']} "
            f"| {s['skor']['ortalama_ham']} | +{s['skor']['sisme_farki']} "
            f"| {s['kopya']['kopya_unvan_grubu']} |"
        )
    sat.append("")

    # Kaynak detayları
    for s in sonuclar:
        sat.append(f"## 2. Kaynak: `{s['kaynak']}`")
        sat.append("")
        sat.append(f"- **Dosya:** `{s['dosya']}`")
        if not s["toplam_kayit"]:
            sat.append("- **Durum:** Dosya bulunamadı veya boş.")
            sat.append("")
            continue
        sat.append(f"- **Toplam kayıt:** {s['toplam_kayit']}")
        sat.append("")

        sat.append("### 2.1 Alan Doluluk")
        sat.append("")
        sat.append("| Alan | Dolu | Oran |")
        sat.append("|---|---:|---:|")
        for alan, d in s["doluluk"].items():
            sat.append(f"| {alan} | {d['dolu']} | %{d['oran']} |")
        sat.append("")

        sat.append("### 2.2 Format Geçerliliği")
        sat.append("")
        sat.append("| Alan | Dolu | Geçerli | Hatalı | Geçerlilik |")
        sat.append("|---|---:|---:|---:|---:|")
        for alan, g in s["gecerlilik"].items():
            sat.append(
                f"| {alan} | {g['dolu']} | {g['gecerli']} | {g['hatali']} "
                f"| %{g['gecerlilik_orani']} |"
            )
        sat.append("")

        k = s["kirlilik"]
        sat.append("### 2.3 Kirlilik (Portal Kaynaklı Sahte Zenginlik)")
        sat.append("")
        sat.append(f"- Web sitesi dolu: **{k['web_dolu']}**")
        sat.append(
            f"- Bunların portal kaynaklı olanı: **{k['web_portal_kaynakli']}** "
            f"(%{k['web_portal_orani']})"
        )
        sat.append(f"- Gerçek firma web sitesi: **{k['gercek_firma_web_sitesi']}**")
        sat.append(f"- Sosyal medyası portal hesabı olan kayıt: **{k['sosyal_medya_portal_kaynakli']}**")
        if k["en_sik_domainler"]:
            sat.append("- En sık domainler:")
            for d, adet in k["en_sik_domainler"]:
                isaret = " ⚠️ portal" if portal_mi(d) else ""
                sat.append(f"  - `{d}` → {adet}{isaret}")
        sat.append("")

        kp = s["kopya"]
        sat.append("### 2.4 Kopya / Tekillik")
        sat.append("")
        sat.append(f"- Benzersiz ünvan: **{kp['benzersiz_unvan']}**")
        sat.append(
            f"- Kopya ünvan grubu: **{kp['kopya_unvan_grubu']}** "
            f"(fazladan {kp['kopya_unvan_kayit']} kayıt)"
        )
        sat.append(f"- Kopya VKN grubu: **{kp['kopya_vkn_grubu']}**")
        sat.append(f"- Ünvansız kayıt: **{kp['unvansiz_kayit']}**")
        if kp["ornek_kopya_unvanlar"]:
            sat.append("- Örnek kopyalar:")
            for u, adet in kp["ornek_kopya_unvanlar"]:
                sat.append(f"  - `{u}` → {adet} kez")
        sat.append("")

        sk = s["skor"]
        sat.append("### 2.5 Kalite Skoru Dağılımı")
        sat.append("")
        sat.append(
            f"- Ortalama (temiz): **{sk['ortalama_temiz']}** | "
            f"Ortalama (ham): {sk['ortalama_ham']} | "
            f"Kirlilik şişmesi: **+{sk['sisme_farki']} puan**"
        )
        sat.append(f"- Min / Medyan / Maks: {sk['min']} / {sk['medyan']} / {sk['maks']}")
        sat.append("")
        sat.append("| Kova | Kayıt |")
        sat.append("|---|---:|")
        for kova, adet in sk["dagilim"].items():
            sat.append(f"| {kova} | {adet} |")
        sat.append("")

    # Çapraz analiz
    sat.append("## 3. Kaynaklar Arası Tamamlayıcılık")
    sat.append("")
    matris = capraz["alan_doluluk_matrisi"]
    if matris:
        kaynaklar = sorted({k for v in matris.values() for k in v})
        sat.append("| Alan | " + " | ".join(kaynaklar) + " |")
        sat.append("|---|" + "---:|" * len(kaynaklar))
        for alan, oranlar in matris.items():
            hucreler = [f"%{oranlar.get(k, 0)}" for k in kaynaklar]
            sat.append(f"| {alan} | " + " | ".join(hucreler) + " |")
        sat.append("")
    if capraz["tamamlayici_alanlar"]:
        sat.append("**Belirgin tamamlayıcılık (≥50 puan fark):**")
        sat.append("")
        for t in capraz["tamamlayici_alanlar"]:
            sat.append(f"- {t}")
        sat.append("")

    # Bulgular
    sat.append("## 4. Bulgular ve Öneriler")
    sat.append("")
    sat.append(
        "1. **Portal kaynaklı web/sosyal medya verisi skoru şişiriyor.** "
        "`ostimistihdam.com` gibi OSB portal adresleri firmanın kendi sitesi değildir; "
        "ETL aşamasında `website_domain` alanına yazılmadan önce elenmelidir."
    )
    sat.append(
        "2. **ASO ve OSTİM tamamlayıcıdır.** ASO NACE/adres/ticaret sicil tarafında güçlü, "
        "OSTİM ise parsel/sektör ve iletişim tarafında daha zengin. "
        "Birleştirme (dedup) ünvan normalizasyonu + VKN üzerinden yapılmalıdır."
    )
    sat.append(
        "3. **VKN doluluğu darboğaz.** VKN olmayan kayıtlar tekilleştirmede ünvan benzerliğine "
        "mahkûm kalıyor; VKN zenginleştirme (Ticaret Sicil Gazetesi / e-fatura mükellef listesi) "
        "öncelikli iş olmalı."
    )
    sat.append(
        "4. **Kopya ünvanlar dedup öncesi temizlenmeli.** Rapordaki kopya ünvan grupları, "
        "aynı firmanın farklı sayfalardan iki kez çekildiğine işaret ediyor."
    )
    sat.append("")

    return "\n".join(sat) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def rapor_uret(girdiler: dict[str, str] | None = None) -> dict[str, Any]:
    """Tum kaynaklari analiz edip JSON uyumlu sonuc sozlugu dondurur."""
    girdiler = girdiler or VARSAYILAN_GIRDILER
    sonuclar = [kaynak_analiz(ad, ROOT / yol) for ad, yol in girdiler.items()]
    capraz = capraz_analiz(sonuclar)
    return {
        "uretim_tarihi": datetime.now(timezone.utc).isoformat(),
        "gorev": "P7-24",
        "agirliklar": AGIRLIKLAR,
        "kaynaklar": sonuclar,
        "capraz_analiz": capraz,
    }


def main(argv: list[str] | None = None) -> int:
    ayrıstırıcı = argparse.ArgumentParser(
        description="P7-24 — ASO ve OSTİM veri kalite raporu üretici"
    )
    ayrıstırıcı.add_argument(
        "--json-out",
        default="data/quality/aso_ostim_kalite.json",
        help="JSON çıktı yolu (varsayılan: data/quality/aso_ostim_kalite.json)",
    )
    ayrıstırıcı.add_argument(
        "--md-out",
        default="data/quality/aso_ostim_kalite_raporu.md",
        help="Markdown çıktı yolu",
    )
    ayrıstırıcı.add_argument("--sessiz", action="store_true", help="Konsol özetini bastırma")
    args = ayrıstırıcı.parse_args(argv)

    sonuc = rapor_uret()
    md = markdown_rapor(sonuc["kaynaklar"], sonuc["capraz_analiz"])

    json_yol = ROOT / args.json_out
    md_yol = ROOT / args.md_out
    json_yol.parent.mkdir(parents=True, exist_ok=True)
    md_yol.parent.mkdir(parents=True, exist_ok=True)
    json_yol.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    md_yol.write_text(md, encoding="utf-8")

    if not args.sessiz:
        print("=== ASO / OSTİM Veri Kalite Özeti (P7-24) ===")
        for s in sonuc["kaynaklar"]:
            if not s["toplam_kayit"]:
                print(f"  {s['kaynak']:<16} kayıt yok ({s['dosya']})")
                continue
            sk = s["skor"]
            k = s["kirlilik"]
            print(
                f"  {s['kaynak']:<16} kayıt={s['toplam_kayit']:<6} "
                f"skor(temiz)={sk['ortalama_temiz']:<6} şişme=+{sk['sisme_farki']:<5} "
                f"portal_web={k['web_portal_kaynakli']}"
            )
        print(f"\nJSON: {json_yol}")
        print(f"MD  : {md_yol}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
