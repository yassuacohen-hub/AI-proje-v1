"""D-298: Kalan kayitlari kisa timeout ile tamamla.

D-296 surucusu 3.303'te ASILDI: `httpx.Client(timeout=30)` tek
parametre oldugu icin connect/read/write AYRI ayrilmaz ve bir
baglanti server'a baglanip cevap vermeyince surekli bekleyebilir.
Sonuc: 15+ dakika ilerleme yok.

Burada her istek icin KISA (8 sn) timeout kullanilir; asili kalan
istek hata sayilir ve ATLANIR. Politika P-3 (2 sn bekleme) ve P-5
(403/401 turu keser) degismez; sadece asili kalmak engellenir.

Kullanim: python scripts/ostim_tamamla_kalan.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "scripts"))

import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "odt", KOK / "scripts" / "ostim_detay_tamamla.py")
odt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(odt)

import httpx  # noqa: E402

K = KOK / "data" / "ostim"
B = K / "tamamlama_2026-09-29"
BEKLEME = 2.0
ZAMAN_ASIMI = 8.0


def kalanlar() -> list[str]:
    liste = {json.loads(x)["slug"] for x in (K / "firmalar_full.jsonl")
             .read_text(encoding="utf-8").splitlines() if x.strip()}
    var = set()
    for x in (K / "firmalar_vkn_ekli.jsonl").read_text(
            encoding="utf-8").splitlines():
        if x.strip():
            var.add(json.loads(x)["slug"])
    cikti = B / "firmalar_tamamlanmis.jsonl"
    if cikti.is_file():
        for x in cikti.read_text(encoding="utf-8").splitlines():
            if x.strip():
                try:
                    var.add(json.loads(x)["slug"])
                except json.JSONDecodeError:
                    continue
    return sorted(liste - var)


def main() -> int:
    ihlal = odt.koruma_kontrolu()
    if ihlal:
        print(f"D-290: {ihlal}")
        return 1
    odt.robots_uyumlu_mu()

    kalan = kalanlar()
    print(f"Kalan kayit: {len(kalan)}")
    if not kalan:
        print("TAMAMLANDI.")
        return 0

    durum = json.loads((B / "durum.json").read_text(encoding="utf-8"))
    islenmis = durum.get("islenen", {})
    yeni: list[dict] = []
    atlanan: list[str] = []
    bas = time.time()

    with httpx.Client(
        headers={"User-Agent": odt.UA},
        timeout=httpx.Timeout(ZAMAN_ASIMI, connect=5.0),
        follow_redirects=True,
    ) as istek:
        for i, slug in enumerate(kalan, 1):
            if i > 1:
                time.sleep(BEKLEME)
            try:
                r = istek.get(f"{odt.DIZIN}/firmalar/{slug}")
                if r.status_code in (401, 403):
                    print(f"P-5 erisim reddi {r.status_code} - TUR BIRAKILDI")
                    break
                r.raise_for_status()
                kayit = odt.detay_ayikla(r.text, slug)
                dolu = sum(1 for k, v in kayit.items()
                           if v not in (None, "", [], {})
                           and k not in ("slug", "kaynak_adi", "kaynak_turu",
                                         "kaynak_url", "cekilme_tarihi"))
                if dolu < 2:
                    raise RuntimeError(f"P-6 bos cikarim ({dolu})")
                yeni.append(kayit)
                islenmis[slug] = kayit.get("cekilme_tarihi")
                print(f"  [{i}/{len(kalan)}] {slug[:46]} OK")
            except Exception as e:
                islenmis[slug] = f"HATA: {type(e).__name__}"
                atlanan.append(slug)
                print(f"  [{i}/{len(kalan)}] {slug[:46]} "
                      f"ATLANDI ({type(e).__name__})")

    durum["islenen"] = islenmis
    odt.durum_yaz(durum)
    m, e, t = odt._cikti_yaz(yeni)
    print(f"\nCikti: {m} mevcut + {e} yeni = {t}")
    print(f"Atlanan (asili/404): {len(atlanan)}")
    print(f"Sure: {time.time() - bas:.0f} sn")
    print(f"Kalan kayit: {len(kalanlar())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
