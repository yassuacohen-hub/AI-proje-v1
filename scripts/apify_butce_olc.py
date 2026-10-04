# -*- coding: utf-8 -*-
"""Apify aylık kullanım (USD) ölçümü + tavan kapısı.

Görev: VERI-APIFY-BUTCE-01 · Kilitli dosya (brief'e göre yeni)
Kural: D-66 (brif varsayımı ölçülür) · D-86 (stdio utf-8) · D-243 (prova diske yazmaz)
       D-245/D-249/D-260 (beyan değil ölçüm; bilinmeyen 0 yazılmaz)

Ölçülen alan adları (2026-10-03 canlı ölçüm, tahmin **yok**):
  `/v2/users/me/limits`        -> data.current.monthlyUsageUsd   (aylık harcanan)
                               -> data.limits.maxMonthlyUsageUsd (konsolda ayarlı tavan)
                               -> data.monthlyUsageCycle.{startAt,endAt}
  `/v2/users/me/usage/monthly` -> data.totalUsageCreditsUsdAfterVolumeDiscount (yedek)
Kullanım:
    python scripts/apify_butce_olc.py --tavan 10
    python scripts/apify_butce_olc.py --tavan 10 --json
Çıkış kodu:
    0  ölçüldü, tavan içinde **ve** platform tavanı yerel tavanı aşmıyor
    2  ölçüldü ama tavan aşıldı **veya** platform tavanı yerel tavanı aşıyor
    3  ölçülemedi (token yok / ağ / 401 / alan bulunamadı) -> 0 uydurulmaz
Token hiçbir koşulda stdout'a girmez.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from decimal import Decimal
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
ENV_DOSYA = ROOT / ".env"
VARSAYILAN_BASE = "https://api.apify.com"
TIMEOUT_SN = 25
LC = "\n"


# ---------------------------------------------------------------- yardimcilar
def env_oku() -> dict:
    """`.env` dosyasını basit ayrıştırıcıyla okur (python-dotenv bağımlılığı yok)."""
    if not ENV_DOSYA.exists():
        return {}
    metin = ENV_DOSYA.read_text(encoding="utf-8", errors="replace")
    out = {}
    for anahtar, deger in re.findall(r"(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$", metin):
        v = deger.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
            v = v[1:-1]
        out[anahtar] = v
    return out


def api_kok(base: str) -> str:
    """`APIFY_API_BASE_URL` iki biçimde yazılabilir: kök ya da `/v2` sonlu.

    Ölçüldü (2026-10-03): `.env` değeri `.../v2` ile bitiyor. Kök varsayılırsa
    istek `/v2/v2/...` olur, Apify **404** döner — "ölçülemedi" görünür ama
    sebep yanlıştır. Tek kural: son segment `/v2` ise atılır, sonra bir kez eklenir.
    """
    kok = base.rstrip("/")
    if kok.endswith("/v2"):
        kok = kok[: -len("/v2")]
    return kok + "/v2"


def yol_birle(base: str, yol: str) -> str:
    return api_kok(base) + yol


def _iste(kok: str, yol: str, token: str) -> dict:
    istek = urllib.request.Request(
        yol_birle(kok, yol),
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "AnkaraB2B-Budget/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(istek, timeout=TIMEOUT_SN) as yanit:
            return {"http": yanit.status, "gövde": json.loads(yanit.read().decode("utf-8", "replace"))}
    except urllib.error.HTTPError as e:
        return {"http": e.code, "hata": f"HTTPError {e.code} {e.reason}"}
    except urllib.error.URLError as e:
        return {"http": None, "hata": f"URLError {e.reason}"}
    except (TimeoutError, OSError) as e:
        return {"http": None, "hata": f"{type(e).__name__}: {e}"}
    except json.JSONDecodeError as e:
        return {"http": None, "hata": f"govde JSON degil: {e}"}


def limits_getir(kok: str, token: str) -> dict:
    """Aylık harcanan USD + konsolda ayarlı tavan + fatura döngüsü."""
    s = _iste(kok, "/users/me/limits", token)
    if s.get("http") != 200:
        return {"http": s.get("http"), "hata": s.get("hata", "HTTP 200 degil")}
    d = s["gövde"].get("data", s["gövde"])
    cur = d.get("current", {}) if isinstance(d.get("current"), dict) else {}
    lim = d.get("limits", {}) if isinstance(d.get("limits"), dict) else {}
    dongu = d.get("monthlyUsageCycle", {}) if isinstance(d.get("monthlyUsageCycle"), dict) else {}
    return {
        "http": 200,
        "aylik_usd": cur.get("monthlyUsageUsd"),
        "platform_tavan_usd": lim.get("maxMonthlyUsageUsd"),
        "dongu_baslangic": dongu.get("startAt"),
        "dongu_bitis": dongu.get("endAt"),
        "bilesenler": {k: v for k, v in cur.items() if k != "monthlyUsageUsd"},
    }


def kullanim_getir(kok: str, token: str) -> dict:
    """Yedek ölçüm (limits erişilemezse). Alan adı canlıdan ölçülmüştür."""
    s = _iste(kok, "/users/me/usage/monthly", token)
    if s.get("http") != 200:
        return {"http": s.get("http"), "hata": s.get("hata", "HTTP 200 degil")}
    d = s["gövde"].get("data", s["gövde"])
    return {
        "http": 200,
        "aylik_usd": d.get("totalUsageCreditsUsdAfterVolumeDiscount"),
        "dongu_baslangic": (d.get("usageCycle") or {}).get("startAt"),
        "dongu_bitis": (d.get("usageCycle") or {}).get("endAt"),
    }


# ---------------------------------------------------------------------- main
def olc(token: str, base: str, tavan: float) -> dict:
    """Ölçüm + kapı kararı. Saf fonksiyon → test edilebilir (dosya yazmaz)."""
    kok = base.rstrip("/")
    rapor = {
        "tarih": date.today().isoformat(),
        "tavan_usd": tavan,
        "kaynak": yol_birle(kok, "/users/me/limits"),
        "token_yerel_mi": bool(token),
        "olculdu": False,
        "asildi": False,
        "platform_tavan_asildi": False,
    }
    if not token:
        rapor["neden"] = "APIFY_TOKEN yok (.env'de bulunamadi)"
        return rapor

    sonuc = limits_getir(kok, token)
    rapor["http"] = sonuc.get("http")
    if sonuc.get("http") != 200:
        yedek = kullanim_getir(kok, token)
        if yedek.get("http") == 200:
            rapor.update(kaynak=yedek_yol(kok), http=200, _kaynak_rozet="usage/monthly (yedek)")
            usd = yedek.get("aylik_usd")
            rapor["platform_tavan_usd"] = None
            rapor["dongu_baslangic"] = yedek.get("dongu_baslangic")
            rapor["dongu_bitis"] = yedek.get("dongu_bitis")
        else:
            rapor["neden"] = yedek.get("hata") or sonuc.get("hata")
            return rapor
    else:
        usd = sonuc.get("aylik_usd")
        rapor["platform_tavan_usd"] = sonuc.get("platform_tavan_usd")
        rapor["dongu_baslangic"] = sonuc.get("dongu_baslangic")
        rapor["dongu_bitis"] = sonuc.get("dongu_bitis")
        rapor["bilesenler"] = sonuc.get("bilesenler")

    if not isinstance(usd, (int, float)):
        # D-249: "veri yok" 0 degildir. Alan bulunamadiysa 0 yazilmayaz.
        rapor["neden"] = ("HTTP 200 dondu ama aylik USD sayisi bulunamadi "
                          "(beyan degil, olcum yok — 0 yazilmadi)")
        return rapor

    rapor.update(olculdu=True, aylik_usd=round(float(usd), 10))
    rapor["oran"] = f"{float(usd) / tavan * 100:.4f}%" if tavan else "n/a"
    rapor["asildi"] = float(usd) > tavan
    plat = rapor.get("platform_tavan_usd")
    rapor["platform_tavan_asildi"] = isinstance(plat, (int, float)) and float(plat) > tavan
    return rapor


def yedek_yol(kok: str) -> str:
    return yol_birle(kok, "/users/me/usage/monthly")


def _usd_fmt(deger) -> str:
    """USD'yi bilimsel gösterimsiz yazar: 1.41192e-05 -> 0.0000141192.

    Ölçülen (2026-10-03) gerçek değer 1.4e-05 mertebesinde; float repr
    `1.41192e-05` verir ve bütçe belgesinde okunmaz. Decimal ile sabit nokta.
    """
    d = Decimal(str(deger))
    s = f"{d:,.10f}".rstrip("0").rstrip(".")
    return s or "0"


def _yaz(rapor: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(rapor, ensure_ascii=False, indent=2, default=str))
        return
    print(f"[TARIH]  {rapor['tarih']}")
    print(f"[KAYNAK] {rapor['kaynak']}")
    if not rapor["olculdu"]:
        print(f"[DURUM]  OLCULMEDI - {rapor.get('neden', 'bilinmiyor')}")
        print("[SONUC]  Fatura limiti bilinmiyor; 0 varsayilmadi (D-249).")
        return
    plat = rapor.get("platform_tavan_usd")
    print(f"[KULLANIM] {_usd_fmt(rapor['aylik_usd'])} USD / tavan "
          f"{_usd_fmt(rapor['tavan_usd'])} USD = {rapor['oran']}")
    print(f"[PLATFORM TAVANI] {_usd_fmt(plat) if isinstance(plat, (int, float)) else 'okunamadi'}")
    if rapor.get("dongu_baslangic"):
        print(f"[FATURA DONGUSU] {rapor['dongu_baslangic']} -> {rapor['dongu_bitis']}")
    sorunlar = []
    if rapor["asildi"]:
        sorunlar.append("aylik kullanim tarani asitti")
    if rapor["platform_tavan_asildi"]:
        sorunlar.append("platform tavani yerel tavandan yuksek — butce korunmuyor")
    if sorunlar:
        print("[SONUC]  FAIL - " + "; ".join(sorunlar)
              + " (Apify konsolu: docs/APIFY_BUTCE.md)")
    else:
        print("[SONUC]  OK - butce tavani icinde ve platformda da esit")


def main() -> int:
    ap = argparse.ArgumentParser(description="Apify aylık kullanimini olc + tavan kapisi")
    ap.add_argument("--tavan", type=float, default=10.0,
                    help="USD tavan (varsayilan 10)")
    ap.add_argument("--json", action="store_true", help="makine-okunur cikti")
    ap.add_argument("--base", default=None, help="API taban adresi (varsayilan .env)")
    ap.add_argument("--token", default=None, help="token (verilmezse .env)")
    a = ap.parse_args()

    env = env_oku()
    rapor = olc(a.token or env.get("APIFY_TOKEN", ""),
                a.base or env.get("APIFY_API_BASE_URL") or VARSAYILAN_BASE,
                a.tavan)
    _yaz(rapor, a.json)
    if not rapor["olculdu"]:
        return 3
    return 2 if (rapor["asildi"] or rapor["platform_tavan_asildi"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
