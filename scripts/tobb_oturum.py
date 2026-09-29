# -*- coding: utf-8 -*-
"""TOBB Ticaret Sicili Gazetesi - guvenli oturum + kazi yici (D-276).

KAHIN yetkilendirmesi (2026-09-29): 14.000 isletmenin detayli kaydi
(Ticaret Sicili Gazetesi uyesi ile, e-Devlet kullanmadan) alinacak.

TASARIM KURALLARI (KAHIN'in "ban riski" uyarisi uzerine):
  1. Sifre SOHBETTEN okunmaz; `.env` dosyasindan okunur (`.gitignore`'da).
  2. Sifre HICBIR ZAMAN loglanmaz/ekrana basilmaz.
  3. Sorgular arasinda `ARALIK` sn beklenir (varsayilan 3 sn).
  4. Her istek sonrasi hiz sinirina uyulur; 429 gelirse bekleme artar.
  5. Oturum dusunce yeniden kurulur (cok fazla giris yapmamak icin).

Yasal: TOBB uyeligi ucretsizdir. e-Devlet KULLANILMAZ - boylece
KAHIN'in kişisel e-Devlet kayitlari olusmaz (D-276 karari).
"""
from __future__ import annotations

import os
import random
import re
import time
from pathlib import Path
from typing import Optional

import httpx

_KOK = Path(__file__).resolve().parents[1]

#: Sifre buradan okunur. Sohbette/temiz kodda BULUNMAZ.
_ENV = _KOK / ".env"
if _ENV.is_file():
    for _s in _ENV.read_text(encoding="utf-8").splitlines():
        _s = _s.strip()
        if _s and not _s.startswith("#") and "=" in _s:
            _k, _v = _s.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

TABBAN = "https://www.ticaretsicil.gov.tr"
GIRIS_URL = TABBAN + "/view/hizlierisim/ilangoruntuleme.php"
AJAX_GIRIS = TABBAN + "/view/modal/uyegirisi_ok.php"

#: Sorgular arası bekleme (sn). KAHIN: "yavas yavas, ban riski olmasin".
ARALIK = 3.0
#: Agirlastirilmis bekleme: her N istekte bir karesel pay eklendir.
N_ISTEK = 25
EK_BEKLEME = 2.0

#: Bir kullanici/oturum icin izin verilen azami istek (ban korumasi).
AZAMI_ISTEK = 400


def _ua() -> str:
    """Sabit User-Agent. SIK SIK DEGISMESI 'garip davranis' olur."""
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class TobbOturum:
    """TOBB oturumu. CAPTCHA elle verilir (otomatik COZME YAPILMAZ)."""

    def __init__(self, bekleme: float = ARALIK) -> None:
        self.bekleme = bekleme
        self.istek_sayaci = 0
        self.client = httpx.Client(
            headers={"User-Agent": _ua(), "Referer": GIRIS_URL},
            timeout=40,
            follow_redirects=True,
        )

    # ------------------------------------------------------------------
    def _bekle(self) -> None:
        """Hiz siniri: sabit aralik + karesel agirlastirma (D-276)."""
        self.istek_sayaci += 1
        bekle = self.bekleme + random.uniform(0, 0.8)
        if self.istek_sayaci % N_ISTEK == 0:
            bekle += EK_BEKLEME
        time.sleep(bekle)

    def _istek(self, method: str, url: str, **kw) -> httpx.Response:
        """Her istekten once BEKLER. 429 gelirse ustel bekler."""
        if self.istek_sayaci >= AZAMI_ISTEK:
            raise RuntimeError(
                f"Azami istek siniri ({AZAMI_ISTEK}) asildi - oturum kapatilir. "
                "Ban korumasi: devam etmek icin yeni oturum ac."
            )
        self._bekle()
        r = self.client.request(method, url, **kw)
        if r.status_code == 429:
            # Sunucu yavaslatma istiyor: geri cekil.
            bekleme_suresi = int(
                r.headers.get("Retry-After", "60")
            )
            print(f"  [429] {bekleme_suresi} sn bekleniyor", flush=True)
            time.sleep(bekleme_suresi)
            r = self.client.request(method, url, **kw)
        return r

    # ------------------------------------------------------------------
    def giris_sayfasini_al(self) -> Optional[bytes]:
        """CAPTCHA gorselini indirir, dosyaya yazar. Elle cozulecek."""
        r = self.client.get(GIRIS_URL)
        m = re.search(r'src="(/captcha/captcha\.php\?\d+)"', r.text)
        if not m:
            return None
        img = self._istek("GET", TABBAN + m.group(1))
        yol = _KOK / "data" / "captcha_tobb.png"
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_bytes(img.content)
        return yol

    def giris_yap(self, captcha: str) -> bool:
        """Girisi dener. `captcha` ELLE verilir (gorselden okunur).

        D-276 KOK NEDEN: Form `enctype="multipart/form-data"` ve JS
        `new FormData(this)` ile POST ediyor. URL-encoded gonderilirse
        sunucu cevabi `0` doner ve giris YAPILMAZ. Bu yuzden `files=`.
        """
        e_posta = os.environ.get("TOBB_KULLANICI", "")
        sifre = os.environ.get("TOBB_SIFRE", "")
        if not e_posta or not sifre:
            raise RuntimeError(
                "TOBB_KULLANICI/TOBB_SIFRE yok -> `.env` icine ekle"
            )
        veri = {
            "LoginEmail": (None, e_posta),
            "LoginSifre": (None, sifre),
            "Captcha": (None, captcha),
        }
        r = self._istek("POST", AJAX_GIRIS, files=veri)
        cevap = r.text.strip()
        if cevap != "1":
            # Sifre ASLA yazdirilmaz.
            raise RuntimeError(
                f"Giris basarisiz (sunucu cevabi={cevap!r}); yalniz '1' kabul edilir"
            )
        return True


    def kapat(self) -> None:
        self.client.close()

    # ------------------------------------------------------------------
    # Oturum kaliciligi: CAPTCHA oturuma baglidir. Goruntuyu indirdikten
    # sonra process kapanirsa (KAHIN'in okumasi icin beklerken) session
    # kaybolur. Bu yuzden cookie'ler diske yazilir/geri yuklenir.
    # ------------------------------------------------------------------
    COOKIE_DOSYA = _KOK / "data" / "tobb_cookie.json"

    def cookie_kaydet(self) -> str:
        """Oturum cookie'lerini diske yazar. SIFRE YAZILMAZ."""
        veri = {c.name: c.value for c in self.client.cookies.jar}
        self.COOKIE_DOSYA.parent.mkdir(parents=True, exist_ok=True)
        self.COOKIE_DOSYA.write_text(
            __import__("json").dumps(veri, ensure_ascii=False),
            encoding="utf-8",
        )
        return str(self.COOKIE_DOSYA)

    def cookie_yukle(self) -> bool:
        """Kaydedilmis cookie'leri yukler. True ise basarili."""
        import json

        if not self.COOKIE_DOSYA.is_file():
            return False
        veri = json.loads(self.COOKIE_DOSYA.read_text(encoding="utf-8"))
        for ad, deger in veri.items():
            self.client.cookies.set(ad, deger, domain="www.ticaretsicil.gov.tr")
        return True

    def oturum_gecerli_mi(self) -> bool:
        """Girili session canli mi? (Sorgu formu geliyor mu?)"""
        r = self.client.get(GIRIS_URL)
        return "LoginEmail" not in r.text

