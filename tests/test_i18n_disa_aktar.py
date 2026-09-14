# -*- coding: utf-8 -*-
"""MRK-02H bekçisi: Huginn (8000) JS sözlüğü üreticiyle senkron mu?

Sözleşme:
- `web_dashboard/js/messages.js` her zaman `disa_aktar.js_uret()` çıktısıyla birebir aynıdır.
- Yalnızca Huginn önekli anahtarlar + Odin ortak anahtarları dışa aktarılır (Muninn sızmaz).
- Dosya "OTOMATIK URETILDI" başlığı taşır; elle düzenlenmez.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from company_master.i18n import disa_aktar

KOK = Path(__file__).resolve().parents[1]
MESSAGES_JS = KOK / "web_dashboard" / "js" / "messages.js"


def test_messages_js_ureticiyle_senkron() -> None:
    """Elle düzenleme veya eski üretim varsa kırmızı yanar."""
    assert MESSAGES_JS.exists(), "messages.js yok; `python -m company_master.i18n.disa_aktar` çalıştır"
    assert disa_aktar.kontrol(MESSAGES_JS), (
        "messages.js üreticiyle uyumsuz; `python -m company_master.i18n.disa_aktar` ile yenile"
    )


def test_huginn_anahtarlari_yalnizca_izinli_onekler() -> None:
    anahtarlar = disa_aktar.huginn_anahtarlari()
    assert len(anahtarlar) >= 60
    for anahtar in anahtarlar:
        izinli = anahtar.startswith(disa_aktar.HUGINN_ONEKLERI) or anahtar in disa_aktar.ODIN_ORTAK
        assert izinli, f"Huginn paketine izinsiz anahtar sızdı: {anahtar}"


def test_muninn_anahtarlari_disa_aktarilmaz() -> None:
    """`ODIN_ORTAK` listesinde açıkça beyan edilmemiş hiçbir muninn_/menu_m_ anahtarı sızmaz."""
    sizanlar = [
        a
        for a in disa_aktar.huginn_anahtarlari()
        if a.startswith(("muninn_", "menu_m_")) and a not in disa_aktar.ODIN_ORTAK
    ]
    assert not sizanlar, f"Muninn anahtarları müşteri yüzeyine sızdı: {sizanlar}"


def test_odin_ortak_anahtarlar_dahil() -> None:
    anahtarlar = set(disa_aktar.huginn_anahtarlari())
    eksik = [a for a in disa_aktar.ODIN_ORTAK if a not in anahtarlar]
    assert not eksik, f"Odin ortak anahtarları eksik: {eksik}"


@pytest.mark.parametrize(
    "parca",
    ["OTOMATIK URETILDI", "export const MESSAGES", "export function dilAyarla", "export function t("],
)
def test_js_ciktisi_beklenen_sozlesmeyi_icerir(parca: str) -> None:
    assert parca in disa_aktar.js_uret()
