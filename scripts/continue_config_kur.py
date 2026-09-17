# -*- coding: utf-8 -*-
"""Continue config kurucu: sablondaki ${env:X} yer tutucularini .env ile doldurur.

Neden gerekli: Continue'nun JSON config'i ${env:...} genisletmesi YAPMAZ; anahtar
bos string olarak gider ve OpenRouter `401 Missing Authentication header` doner.
Bu script anahtarlari kurulum aninda dosyaya basar; repo kopyasi temiz kalir.

Kullanim:
    python scripts/continue_config_kur.py            # yaz
    python scripts/continue_config_kur.py --kontrol  # yazmadan ozet (self-check)
    python scripts/continue_config_kur.py --dogrula  # slug'lari canli /models ile karsilastir
    python scripts/continue_config_kur.py --tara     # yeni :free modelleri bul, rapor yaz

Rotate sonrasi tekrar kosulmasi ZORUNLU.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
SABLON = KOK / "docs" / "continue_config.json"
HEDEF = Path.home() / ".continue" / "config.json"
RAPOR_DIZIN = KOK / "docs" / "raporlar" / "continue"
OR_BASE = "https://openrouter.ai/api/v1"
DESEN = re.compile(r"\$\{env:([A-Z0-9_]+)\}")


def env_oku(yol: Path | None = None) -> dict[str, str]:
    """`.env` dosyasindan DOLU anahtarlari okur (bos degerler atlanir)."""
    yol = yol or KOK / ".env"
    sozluk: dict[str, str] = {}
    if not yol.exists():
        return sozluk
    for satir in yol.read_text(encoding="utf-8-sig").splitlines():
        satir = satir.strip()
        if not satir or satir.startswith("#") or "=" not in satir:
            continue
        ad, _, deger = satir.partition("=")
        deger = deger.strip().strip('"').strip("'")
        if deger:
            sozluk[ad.strip()] = deger
    return sozluk


def coz(nesne, env: dict[str, str], eksik: set[str]):
    """Nesne agacindaki ${env:X} yer tutucularini doldurur; bulunamayani `eksik`e yazar."""
    if isinstance(nesne, str):
        def _degistir(m: re.Match[str]) -> str:
            deger = env.get(m.group(1), "")
            if not deger:
                eksik.add(m.group(1))
            return deger
        return DESEN.sub(_degistir, nesne)
    if isinstance(nesne, dict):
        return {k: coz(v, env, eksik) for k, v in nesne.items()}
    if isinstance(nesne, list):
        return [coz(v, env, eksik) for v in nesne]
    return nesne


def yapilandirma_uret(sablon: dict, env: dict[str, str]) -> tuple[dict, list[str]]:
    """Sablonu cozer; anahtari eksik olan modelleri listeden DUSURUR."""
    atlanan: list[str] = []
    modeller = []
    for model in sablon.get("models", []):
        eksik: set[str] = set()
        cozulmus = coz(model, env, eksik)
        if eksik:
            atlanan.append(f"{model.get('title', '?')} -> eksik: {','.join(sorted(eksik))}")
        else:
            modeller.append(cozulmus)

    eksik_genel: set[str] = set()
    cfg = coz({k: v for k, v in sablon.items() if k != "models"}, env, eksik_genel)
    cfg["models"] = modeller

    tab = cfg.get("tabAutocompleteModel")
    if isinstance(tab, dict) and not tab.get("apiKey"):
        cfg.pop("tabAutocompleteModel")
        atlanan.append("tabAutocompleteModel -> anahtar bos")
    return cfg, atlanan


def model_listesi(api_base: str, api_key: str, timeout: int = 20) -> tuple[set[str], str | None]:
    """`{api_base}/models` cagirir -> (id kumesi, hata). Hata varsa kume bostur.

    OpenRouter'da ucretsiz olanlari ayirmak icin `:free` son eki id'de zaten var.
    """
    url = api_base.rstrip("/") + "/models"
    istek = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {api_key}", "User-Agent": UA}
    )
    try:
        with urllib.request.urlopen(istek, timeout=timeout) as yanit:  # noqa: S310
            veri = json.loads(yanit.read().decode("utf-8"))
    except urllib.error.HTTPError as hata:
        return set(), f"HTTP {hata.code}"
    except Exception as hata:  # ag/DNS/JSON — saglayici digerlerini kirmasin
        return set(), f"{type(hata).__name__}: {hata}"
    kayitlar = veri.get("data") if isinstance(veri, dict) else veri
    if not isinstance(kayitlar, list):
        return set(), "beklenmeyen yanit bicimi"
    return {str(k.get("id")) for k in kayitlar if isinstance(k, dict) and k.get("id")}, None


def _adaylar(slug: str, mevcut: set[str], limit: int = 5) -> list[str]:
    """Olu slug icin ad parcalarini paylasan mevcut id'leri onerir."""
    parcalar = {p for p in re.split(r"[/:\-_.]", slug.lower()) if len(p) > 2}
    puanli = [
        (sum(1 for p in parcalar if p in mid.lower()), mid)
        for mid in mevcut
    ]
    return [mid for puan, mid in sorted(puanli, reverse=True) if puan][:limit]


# Cloudflare 1010 = UA'siz istemciyi bot sayip banliyor (Groq/Together bu yuzden 403 veriyordu).
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) continue-config-kur/1.0"


def sohbet_testi(api_base: str, api_key: str, slug: str, timeout: int = 60) -> tuple[str, str]:
    """GERCEK cagri: POST {api_base}/chat/completions -> (etiket, aciklama).

    `/models` listesi yeterli DEGIL: slug listede olsa da cagri 429/404 donebilir.
    Etiketler: OK / KOTA / OLU / URL_HATALI / YETKI / HATA
    """
    url = api_base.rstrip("/") + "/chat/completions"
    govde = json.dumps({
        "model": slug,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
    }).encode("utf-8")
    istek = urllib.request.Request(
        url,
        data=govde,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(istek, timeout=timeout) as yanit:  # noqa: S310
            ham = yanit.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as hata:
        ham = hata.read().decode("utf-8", "replace")[:200].replace("\n", " ")
        if "<html" in ham.lower():
            return "URL_HATALI", f"HTTP {hata.code} + HTML sayfa -> apiBase API host degil"
        if hata.code in (401, 403):
            return "YETKI", f"HTTP {hata.code}: {ham}"
        if hata.code in (402, 429):
            return "KOTA", f"HTTP {hata.code}: {ham}"
        if hata.code == 404:
            return "OLU", f"HTTP 404: {ham}"
        return "HATA", f"HTTP {hata.code}: {ham}"
    except Exception as hata:  # ag/DNS — digerlerini kirmasin
        return "HATA", f"{type(hata).__name__}: {hata}"
    if "<html" in ham[:200].lower():
        return "URL_HATALI", "200 ama HTML govde -> apiBase API host degil"
    try:
        json.loads(ham)
    except ValueError:
        return "URL_HATALI", f"JSON degil: {ham[:120]}"
    return "OK", "cevap alindi"


def anthropic_testi(api_key: str, slug: str, timeout: int = 60) -> tuple[str, str]:
    """Anthropic ayri protokol: POST /v1/messages + x-api-key (OpenAI uyumlu DEGIL)."""
    govde = json.dumps({
        "model": slug,
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "ping"}],
    }).encode("utf-8")
    istek = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=govde,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
            "User-Agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(istek, timeout=timeout) as yanit:  # noqa: S310
            yanit.read()
    except urllib.error.HTTPError as hata:
        ham = hata.read().decode("utf-8", "replace")[:200].replace("\n", " ")
        if hata.code in (401, 403):
            return "YETKI", f"HTTP {hata.code}: {ham}"
        if hata.code in (402, 429):
            return "KOTA", f"HTTP {hata.code}: {ham}"
        if hata.code == 404:
            return "OLU", f"HTTP 404: {ham}"
        return "HATA", f"HTTP {hata.code}: {ham}"
    except Exception as hata:
        return "HATA", f"{type(hata).__name__}: {hata}"
    return "OK", "cevap alindi"


def dogrula(cfg: dict) -> int:
    """Her modeli GERCEK `POST /chat/completions` ile dener; sadece OK olan kullanilabilir."""
    hedefler = list(cfg.get("models", []))
    tab = cfg.get("tabAutocompleteModel")
    if isinstance(tab, dict):
        hedefler.append(tab)

    onbellek: dict[str, tuple[set[str], str | None]] = {}
    sorunlu = 0
    for model in hedefler:
        temel = model.get("apiBase", "")
        anahtar = model.get("apiKey", "")
        slug = model.get("model", "")
        if model.get("provider") == "anthropic":
            etiket, aciklama = anthropic_testi(anahtar, slug)
        else:
            etiket, aciklama = sohbet_testi(temel, anahtar, slug)
        print(f"  {etiket:9} {model.get('title')}: {slug}")
        if etiket == "OK":
            continue
        sorunlu += 1
        print(f"            {aciklama}")
        if etiket == "OLU":
            if temel not in onbellek:
                onbellek[temel] = model_listesi(temel, anahtar)
            mevcut, _ = onbellek[temel]
            for aday in _adaylar(slug, mevcut):
                print(f"            aday: {aday}")
    print(f"\nSorunlu model sayisi: {sorunlu}/{len(hedefler)}")
    return 3 if sorunlu else 0


def tara(env: dict[str, str], sablon: dict, limit: int = 25) -> int:
    """OpenRouter katalogundaki YENI `:free` modelleri gercek POST ile dener, rapor yazar.

    Haftalik rutin. Cikti: docs/raporlar/continue/tarama_<tarih>.md
    """
    anahtar = env.get("OPENROUTER_API_KEY", "")
    if not anahtar:
        print("HATA: OPENROUTER_API_KEY yok")
        return 2
    mevcut = {m.get("model", "") for m in sablon.get("models", [])}
    katalog, hata = model_listesi(OR_BASE, anahtar)
    if hata:
        print(f"HATA: katalog okunamadi: {hata}")
        return 3
    adaylar = sorted(s for s in katalog if s.endswith(":free") and s not in mevcut)[:limit]
    print(f"Katalog: {len(katalog)} · yeni :free aday: {len(adaylar)} (limit {limit})")

    satirlar = [
        f"# Continue ucretsiz model taramasi — {date.today().isoformat()}",
        "",
        f"- Katalog: {len(katalog)} slug · sablonda: {len(mevcut)} · denenen yeni `:free`: {len(adaylar)}",
        "- Test: GERCEK `POST /chat/completions` (`max_tokens: 1`). `/models` listesi tek basina yeterli degil.",
        "",
        "| slug | sonuc | aciklama |",
        "|---|---|---|",
    ]
    eklenebilir: list[str] = []
    for slug in adaylar:
        etiket, aciklama = sohbet_testi(OR_BASE, anahtar, slug)
        print(f"  {etiket:9} {slug}")
        if etiket == "OK":
            eklenebilir.append(slug)
        satirlar.append(f"| `{slug}` | {etiket} | {aciklama[:120].replace('|', '/')} |")

    satirlar += ["", "## Sablona eklenebilir (OK)", ""]
    satirlar += [f"- `{s}`" for s in eklenebilir] or ["- (yok)"]
    satirlar += ["", "Ekleme sonrasi: `python scripts/continue_config_kur.py --dogrula` + kurulum.", ""]

    RAPOR_DIZIN.mkdir(parents=True, exist_ok=True)
    rapor = RAPOR_DIZIN / f"tarama_{date.today().isoformat()}.md"
    rapor.write_text("\n".join(satirlar), encoding="utf-8")
    print(f"\nRapor: {rapor}  ·  eklenebilir: {len(eklenebilir)}")
    return 0


def main(argv: list[str]) -> int:
    kontrol = "--kontrol" in argv
    dogrulama = "--dogrula" in argv
    tarama = "--tara" in argv
    env = env_oku()
    if not SABLON.exists():
        print(f"HATA: sablon yok: {SABLON}")
        return 1
    sablon = json.loads(SABLON.read_text(encoding="utf-8"))
    if tarama:
        return tara(env, sablon)
    cfg, atlanan = yapilandirma_uret(sablon, env)

    if not cfg["models"]:
        print("HATA: hicbir modelin anahtari cozulemedi (.env kontrol et)")
        return 2

    print(f"Yazilacak model: {len(cfg['models'])}")
    for model in cfg["models"]:
        anahtar = model.get("apiKey", "")
        print(f"  + {model['title']}  (anahtar son4={anahtar[-4:]})")
    for satir in atlanan:
        print(f"  - ATLANDI {satir}")

    if dogrulama:
        print("\n--dogrula: GERCEK POST /chat/completions testi")
        return dogrula(cfg)

    if kontrol:
        print("--kontrol: dosya YAZILMADI")
        return 0

    HEDEF.parent.mkdir(parents=True, exist_ok=True)
    if HEDEF.exists():
        yedek = HEDEF.with_suffix(".json.bak")
        yedek.write_text(HEDEF.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Yedek: {yedek}")
    HEDEF.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Yazildi: {HEDEF}")
    print("UYARI: hedef dosya duz metin anahtar icerir; repo disinda, paylasilmaz.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
