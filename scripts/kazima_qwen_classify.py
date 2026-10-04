# -*- coding: utf-8 -*-
"""SCRAPE-004: Qwen (9Router) ile yapi bilinmeyen sayfalari siniflandirma.

NEDEN
    SCRAPE-003 dogrudan/Jina ile ham icerigi getirir. Ancak `kart_tipi=None`
    oldugunda **ne tur kart oldugu bilinmez** (D-245). Burada LLM o boslugu
    doldurur: metinden NACE sektoru + unvan cikarir.

LLM'E DOGRULANAMAZ IDDIA YAZILMAZ (D-245 / D-287)
    1. Cevap JSON olmazsa hata kuyruguna yazilir, **uydurma etiket yazilmaz**.
    2. `etiket_bos` ayri bir durumdur: LLM "bilmiyorum" derse `None` yazilir.
    3. Ham ham metin degil, **kirpilmis** metin gonderilir (maliyet + KVKK).

    python -X utf8 scripts/kazima_qwen_classify.py --kuru <url> [<url> ...]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import requests  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

from company_master.etl.scrape_kayit import KazimaYazici  # noqa: E402

TASK_ID = "SCRAPE-004-QWEN-SINIFLANDIRMA"
KAYNAK_ADI = "9router/qwen-classify"
VARSAYILAN_MODEL = "clinepass/cline-pass/mimo-v2.5"
#: EVREN bir 9Router saglayicisi DEGIL, **kendi kredisi olan ayri bir
#: gecittir** (olcum 2026-10-04: 1040 CR, embedding 0 kredi). Onceden
#: sadece 9Router deneniyordu; 9Router'daki MiMo tek bir saglayiciya
#: bagliyken EVREN'de `mimo-v2.6-pro` **kendi kredisiyle** duruyor.
#: Siralama: EVREN once (bagimsiz, ucuz), 9Router yedek.
EVREN_BASE_URL = os.environ.get(
    "EVREN_BASE_URL", "https://evren-llmapi.ssyz.org.tr")
EVREN_MODELLER = ("mimo-v2.6-pro", "auto")
#: Saglayici anahtarlari gecici olarak bitebilir (olcum 2026-10-04: Qwen ve
#: MiMo'nun 8/8 9Router modeli 503 dondu, /v1/models ise 200 veriyordu). Bu yuzden
#: tek model DENEmez; sirayla deneyip calisan ilk sonucu kullanir.
MODEL_ZINCIRI = (
    "clinepass/cline-pass/mimo-v2.5",
    "bzl/mimo-v2.5",
    "cl/xiaomi/mimo-v2.6-flash",
    "cl/qwen/qwen3.7-flash",
    "cl/xiaomi/mimo-v2.5",
)
TIMEOUT = 60
#: Maliyet + KVKK: LLM'e gonderilen metin siniri (karakter).
METIN_TAVAN = 3000

SISTEM = (
    "Sen NACE siniflandirmaci sin. Verilen firma metninden SADECE JSON dondur: "
    '{"nace_kodu": "XX.XX", "sektor_adi": "...", "unvan": "...", '
    '"etiket_bos": false}. Bilmiyorsan etiket_bos=true dondur ve alanlari bos birak. '
    "Aciklama yazma, JSON disinda hicbir sey yazma."
)


def _env_oku(ad: str) -> str:
    deger = os.environ.get(ad, "").strip()
    if deger:
        return deger
    env = ROOT / ".env"
    if not env.is_file():
        return ""
    on = ad + "="
    for ln in env.read_text(encoding="utf-8-sig").splitlines():
        if ln.strip().startswith(on):
            return ln.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def metni_kirp(html: str, tavan: int = METIN_TAVAN) -> str:
    """Sayfadan gorunur metni cikarir ve kirpar (JS/ozelik atilir)."""
    soup = BeautifulSoup(html, "html.parser")
    for et in soup(["script", "style", "noscript", "svg"]):
        et.decompose()
    metin = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    return metin[:tavan]


def _evren_anahtari() -> str:
    """`.env` icindeki `evren_llm_` anahtari.

    Ayni kural `vector/embedder.py::_evren_anahtari` ile ayni olmali;
    anahtarin `X-API-Key:evren_llm_...` **satiri** olarak saklandigi
    varsayiliyor (olcum 2026-10-04).
    """
    dogrudan = os.environ.get("EVREN_API_KEY", "").strip()
    if dogrudan:
        return dogrudan
    env = ROOT / ".env"
    if not env.is_file():
        return ""
    for ln in env.read_text(encoding="utf-8-sig").splitlines():
        if "evren_llm_" in ln:
            return "evren_llm_" + ln.split("evren_llm_", 1)[1].split()[0].strip()
    return ""


def _evren_bir_model_dene(html: str, model: str) -> tuple:
    """EVREN uzerinden tek modele sorar. Doner: (ham_cevap, hata)."""
    anahtar = _evren_anahtari()
    if not anahtar:
        return "", "EVREN_ANAHTAR_YOK"
    govde = {
        "model": model,
        "messages": [{"role": "system", "content": SISTEM},
                     {"role": "user", "content": metni_kirp(html)}],
        "stream": False,
        "temperature": 0,
    }
    try:
        r = requests.post(EVREN_BASE_URL + "/v1/chat/completions",
                          json=govde, timeout=TIMEOUT,
                          headers={"Content-Type": "application/json",
                                   "Authorization": "Bearer " + anahtar})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"], ""
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        return "", f"{type(exc).__name__}: {exc}"[:160]


def _bir_model_dene(html: str, model: str) -> tuple:
    """Tek modele sorar. Doner: (ham_cevap, hata)."""
    taban = _env_oku("NINEROUTER_URL").rstrip("/")
    if not taban:
        return "", "NINEROUTER_URL_YOK"
    basliklar = {"Content-Type": "application/json"}
    anahtar = _env_oku("NINEROUTER_KEY")
    if anahtar:
        basliklar["Authorization"] = "Bearer " + anahtar
    govde = {
        "model": model,
        "messages": [{"role": "system", "content": SISTEM},
                     {"role": "user", "content": metni_kirp(html)}],
        "stream": False,
        "temperature": 0,
    }
    try:
        r = requests.post(taban + "/chat/completions", json=govde,
                          headers=basliklar, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"], ""
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        return "", f"{type(exc).__name__}: {exc}"[:160]


_ANAHTAR_ONBELLEK: dict[str, str] = {}


def _anahtar_bir(ad: str) -> str:
    """Anahtari ilk seferde keyring/env'den okur, sonra onbellekten verir.

    SCRAPE-004 madde 5 (p95 < 2 sn) icin: keyring her sinifla_etiket() cagrisinda
    soruluyordu; olcumde p95 2.5-4.4 s idi. Onbellekle keyring yalnizca ilk
    cagrida sorulur.
    """
    if ad in _ANAHTAR_ONBELLEK:
        return _ANAHTAR_ONBELLEK[ad]
    deger = ""
    if KEYRING is not None:
        try:
            deger = (_anahtar_bir(ad)).strip()
        except Exception:
            deger = ""
    if not deger:
        deger = _env_oku(ad)
    _ANAHTAR_ONBELLEK[ad] = deger
    return deger


def qwen_siniflandir(html: str, model: str = "") -> dict:
    """Metni LLM'e sorar; model zinciri sirayla denenir.

    Doner: {etiket_bos, nace_kodu, sektor_adi, unvan, hata, model}
    Hicbir model calismazsa **uydurma etiket yazilmaz** (D-245).
    """
    secili = model or _env_oku("SINIFLANDIRMA_MODEL")
    hatalar = []
    # 1) EVREN once: kendi kredisi var, 9Router'a bagli degil.
    if not secili:
        for ad in EVREN_MODELLER:
            cevap, hata = _evren_bir_model_dene(html, ad)
            if hata:
                hatalar.append("evren/" + ad + ": " + hata)
                continue
            veri = _json_ayikla(cevap)
            if veri is None:
                hatalar.append("evren/" + ad + ": JSON_COZULEMEDI")
                continue
            return _etiketle(veri, "evren/" + ad)
        # EVREN calismadiysa yine de 9Router'a dusulur.
    zincir = (secili,) if secili else MODEL_ZINCIRI
    for ad in zincir:
        cevap, hata = _bir_model_dene(html, ad)
        if hata:
            hatalar.append(ad + ": " + hata)
            continue
        veri = _json_ayikla(cevap)
        if veri is None:
            # JSON gelmezse etiket sayilmaz; siradaki modele gecilir.
            hatalar.append(ad + ": JSON_COZULEMEDI")
            continue
        return _etiketle(veri, ad)
    return {"etiket_bos": True, "nace_kodu": None, "sektor_adi": None,
            "unvan": None, "hata": " | ".join(hatalar)[:300],
            "model": "", "denenen": len(EVREN_MODELLER) + len(zincir)}


def _etiketle(veri: dict, model_adi: str) -> dict:
    """Cozulmus JSON -> standart sonuc. Sema her yolda AYNI (D-245)."""
    if veri.get("etiket_bos"):
        return {"etiket_bos": True, "nace_kodu": None, "sektor_adi": None,
                "unvan": veri.get("unvan") or None, "hata": "", "model": model_adi}
    return {"etiket_bos": False, "nace_kodu": veri.get("nace_kodu") or None,
            "sektor_adi": veri.get("sektor_adi") or None,
            "unvan": veri.get("unvan") or None, "hata": "", "model": model_adi}
def _json_ayikla(cevap) -> dict | None:
    """LLM cevabindan JSON nesnesini cikarir; cozulemezse None.

    LLM bazen ```json ... ``` sarar ya da metne gorev ekler. Bu
    normalizasyon **zorunlu**: cozulemeyen cevap etiket sayilmaz.
    """
    metin = str(cevap).strip()
    if metin.startswith("```"):
        metin = re.sub(r"^```[a-zA-Z]*\s*", "", metin)
        metin = re.sub(r"```\s*$", "", metin).strip()
    try:
        veri = json.loads(metin)
    except ValueError:
        bas = metin.find("{")
        son = metin.rfind("}")
        if bas == -1 or son <= bas:
            return None
        try:
            veri = json.loads(metin[bas:son + 1])
        except ValueError:
            return None
    return veri if isinstance(veri, dict) else None


def siniflandir(html: str, model: str = "") -> dict:
    """Metin -> Qwen -> sonuc. Yazma burada yapilmaz."""
    return qwen_siniflandir(html, model)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Qwen ile yapi bilinmeyen sayfalari siniflandir")
    p.add_argument("hedef", nargs="+", help="siniflandirilacak URL'ler")
    p.add_argument("--model", default="", help="9Router model adi")
    p.add_argument("--kuru", action="store_true", help="DB'ye yazmaz")
    a = p.parse_args()

    yazici = KazimaYazici(KAYNAK_ADI, task_id=TASK_ID)

    sonuclar = []
    for url in a.hedef:
        izin, sebep = KazimaYazici.izin_var(url)
        if not izin:
            sonuclar.append({"url": url, "neden": "izin yok: " + sebep,
                             "etiket_bos": True})
            continue
        try:
            r = requests.get(url, timeout=20, headers={
                "User-Agent": "OSINT-Scraper-Motoru/1.0 (+Ankara B2B)"})
            r.raise_for_status()
            html = r.text
        except requests.RequestException as exc:
            sonuclar.append({"url": url, "neden": type(exc).__name__,
                             "etiket_bos": True})
            continue

        s = siniflandir(html, a.model)
        s["url"] = url
        if s.get("hata"):
            sonuclar.append(s)
            continue
        if not a.kuru:
            yazici.audit_kaydet(url, action="classify", status="success",
                                bayt=len(metni_kirp(html)), ms=0)
            yazici.sayfa_kaydet(url, html, {
                "nace_kodu": s.get("nace_kodu"),
                "sektor_adi": s.get("sektor_adi"),
                "unvan": s.get("unvan"),
                "etiket_bos": bool(s.get("etiket_bos")),
                "model": s.get("model") or a.model or _env_oku("QWEN_MODEL") or VARSAYILAN_MODEL,
            })
        sonuclar.append(s)

    print(json.dumps({
        "hedef": len(sonuclar),
        "siniflandirilan": sum(1 for s in sonuclar if not s.get("etiket_bos")),
        "etiket_bos": sum(1 for s in sonuclar if s.get("etiket_bos")),
        "kuru": bool(a.kuru),
        "sonuclar": sonuclar,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())