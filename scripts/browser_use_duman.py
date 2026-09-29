# -*- coding: utf-8 -*-
"""Browser-Use SDK duman testi (D-270).

Kurulum: `pip install browser-use-sdk`
Anahtar:  `.env` -> `BROWSER_USE_API_KEY` (cloud.browser-use.com/new-api-key)

D-269 kurali: bu bir DIS SERVIS cagrisidir -> `skills/services/` altinda olmali.
Su an tek kullanimlik duman testi olarak `scripts/` altinda durur; registry'ye
baglanmasi icin ayri bir gorev acilmasi gerekir.

D-268 kurali: "calisti" demek olcum demektir. Asagidaki komut + cikti kanittir.

Kullanim:
    python scripts/browser_use_duman.py
    python scripts/browser_use_duman.py "belirli bir gorev metni"
"""
from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path

_KOK = Path(__file__).resolve().parents[1]

# .env yukle (paket eklemadan; ninerouter_client.py ile ayni desen)
_ENV = _KOK / ".env"
if _ENV.is_file():
    for _satir in _ENV.read_text(encoding="utf-8").splitlines():
        _satir = _satir.strip()
        if not _satir or _satir.startswith("#") or "=" not in _satir:
            continue
        _k, _v = _satir.split("=", 1)
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

#: Anahtarin basilmamasi icin: yalnizca varlik kontrolu yapilir.
if not os.environ.get("BROWSER_USE_API_KEY"):
    sys.exit(
        "HATA: BROWSER_USE_API_KEY yok. `.env` icine ekle "
        "(cloud.browser-use.com/new-api-key)."
    )

from browser_use_sdk.v4 import AsyncBrowserUse  # noqa: E402

#: Bos gorev gonderilmez; API cagrisi bos kalir.
#: `MODEL = None` -> servis varsayilanini (ucretsiz plan) kullanir.
MODEL: str | None = None
VARSAYILAN_GOREV = (
    "Ankara'da B2B firma listesi arayan bir ETL pipeline icin,ornegin "
    "https://www.ostim.org.tr adresine git, sitenin uye/firma listesine "
    "ulasma seklini ve erisim durumunu (HTTP durum kodu ve sayfa basligi) "
    "raporla. Hicbir veri cekme."
)

#: API `sessionId` alanini UUID bekliyor (ajan adi degil) -> 422.
#: Ancak rastgele UUID de 404 verir: SDK'da `sessions.create` yok, oturumlar
#: cloud arayuzunden acilir. Bu yuzden varsayilan olarak hic gonderilmez.
_OTURUM_DOSYA = _KOK / ".browser_use_session"


def _oturum_arg() -> dict:
    """`runs.create` icin `session_id` argumanini uretir.

    Onceki kosul: API UUID bekliyor (422). Ikinci kosul: UUID var olmali (404).
    Bu yuzden deger ancak dosyada KAYITLI ve UUID bicimli ise gonderilir.
    """
    if not _OTURUM_DOSYA.is_file():
        return {}
    deger = _OTURUM_DOSYA.read_text(encoding="utf-8").strip()
    try:
        uuid.UUID(deger)
    except (ValueError, AttributeError):
        return {}
    return {"session_id": deger}


async def main(task: str) -> None:
    async with AsyncBrowserUse(
        api_key=os.environ["BROWSER_USE_API_KEY"]
    ) as client:
        run = await client.runs.create(
            task=task,
            # `model` BILINCLI verilmez. Hesap "free plan" (403:
            # "Model 'gpt-6-luna' is not available on the free plan"), bu
            # planda varsayilan model kullanilir. Gerekirse `MODEL` degiskeni.
            model=MODEL,
            model_params=(
                {
                    "reasoning": {"effort": "low"},
                    "service_tier": "default",
                }
                if MODEL
                else None
            ),
            # `session_id` OPSIYONEL. UUID zorunlu ama rastgele UUID de 404 verir
            # ("session not found") cunku SDK'da `sessions.create` YOK; oturumlar
            # cloud arayuzunden acilir. Hesapta 0 oturum oldugu icin burada
            # hic gonderilmiyor. Gerekirse `scripts/... --oturum <UUID>`.
            **_oturum_arg(),
            browser_settings={
                "proxy_country_code": "tr",
                "record": False,
            },
            # Guvenlik siniri: bulut ucretlidir, bir hatanin maliyeti sinirsiz
            # olmasin. Asil fiyat hesabina gore belirlenir.
            max_cost_usd=0.50,
        )
        print(f"run_id = {run.id}", flush=True)
        result = await client.runs.wait_for_completion(run.id)
        print(result)


if __name__ == "__main__":
    gorev = " ".join(sys.argv[1:]).strip() or VARSAYILAN_GOREV
    print(f"gorev uzunlugu = {len(gorev)} karakter", flush=True)
    asyncio.run(main(gorev))
