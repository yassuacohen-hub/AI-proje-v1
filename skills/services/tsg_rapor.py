# -*- coding: utf-8 -*-
"""TSG rapor şablonu (TSG-06, D-306).

Saf metin üreteci: girdi kanıt sözlükleri (`data/kanit/*.json` biçimi),
çıktı Markdown. **DB yok, ağ yok, posta gönderimi yok.**

Posta kapısı ZATEN VAR — ölçüldü (2026-09-29):
`web_app.py::_send_email(to, subject, html_body) -> bool` (smtplib, satır 2181).
İkinci bir SMTP kapısı yazılmadı (K-1). Ancak o kapı **modül düzeyinde**
`app = FastAPI(...)` kuran bir dosyanın içinde; `from web_app import _send_email`
tüm API'yi + DB motorunu yükler (ölçüldü: `fastapi` 5 kez, `flask` 0). Bu yüzden
bu modül yalnızca gövdeyi üretir (`posta_govdesi`), göndermeyi çağırana bırakır.
Rapor üretmek için web sunucusunu ayağa kaldırmak gerekmez.

ponytail: `_send_email` paylaşılan bir modüle taşınmadı — TSG-06'nın tek
ihtiyacı gövde biçimi, gönderim değil. Rapor postasını ZAMANLAYICI (cron/
orchestrator) gönderecekse `_send_email` o zaman taşınır; şimdi taşımak
web_app.py'de gerekçesiz bir diff olur.

D-216: eksik alan sessizce düşmez, "bilinmiyor" yazılır.
D-268: ölçülmeyen şey uydurulmaz — kapsam beyanı taranmayanı da yazar.
"""
from __future__ import annotations

import html
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from skills.services.ticaret_sicili_kanit import (
    ILAN_GOSTER_URL,
    ILAN_TURU_ESLEME,
    KAYNAK_URL,
    IlanKaniti,
    olay_esle,
)

#: Ürün sahibi kararı (2026-09-29): tam kapsam penceresi **1 gün**.
KAPSAM_PENCERE_GUN = 1

_MASKE = "***"
_YOK = "bilinmiyor"


def kisi_maskele(ad: str | None) -> str:
    """Kişi adını sunum için maskeler: `Ahmet Yılmaz` -> `A*** Y***`.

    Ürün sahibi kararı: kişi adı DB'ye AÇIK yazılır, **sunumda** maskelenir.
    Ölçüldü (2026-09-29): projede kişi adı maskeleyen kapı YOKTU
    (`ai_chat.kilit_maskele` sır maskeler, `telegram_bot.masked_token` jeton
    maskeler, `user_settings.kvkk_maske_acik` yalnızca bayrak okur). Bu yüzden
    tek kapı burada açıldı; ikinci kullanıcı çıkarsa buraya delege edilir (K-1).

    Maske sabit 3 yıldız: ad uzunluğu bilerek sızdırılmaz.

    ponytail: unvan maskelenmez (tüzel kişi KVKK dışı). Şahıs işletmesi
    unvanı kişi adı İÇEREBİLİR ama hangi kayıtların şahıs olduğu bu girdide
    ölçülü değil — `tuzel_tip` alanı kanıt şemasında yok. Şahıs unvanı
    maskesi, `tuzel_tip` kanıda taşındığında eklenir.
    """
    if not ad or not ad.strip():
        return _YOK
    return " ".join(f"{parca[0]}{_MASKE}" for parca in ad.split() if parca)


def kanit_anahtari(kanit: Mapping[str, Any]) -> str:
    """Kanıt JSON'undan üçlü referansı okur; yoksa kanıttan yeniden üretir."""
    turetilen = (kanit.get("dogrulama") or {}).get("turetilen") or {}
    mevcut = turetilen.get("anahtar")
    if mevcut:
        return str(mevcut)
    # Doğrulama koşulmamış kanıt da rapora girer (D-216): anahtarı tek
    # kapıdan üretiriz, burada ikinci bir biçimlendirme yazmayız (K-1).
    return IlanKaniti(
        ilan_sira_no=str(kanit.get("ilan_sira_no") or ""),
        icerik_no=str(kanit.get("icerik_no") or ""),
        gazete_sayi=kanit.get("gazete_sayi"),
        gazete_sayfa=kanit.get("gazete_sayfa"),
    ).kanit_anahtari()


def kalici_adres(kanit: Mapping[str, Any]) -> str | None:
    """Kanıtın kalıcı ilan adresi (GUID varsa). Katman 0'da GUID yoktur."""
    guid = (kanit.get("guid") or "").strip() if kanit.get("guid") else ""
    return ILAN_GOSTER_URL.format(guid=guid) if guid else None


def son_teyit(kanitlar: Sequence[Mapping[str, Any]]) -> str:
    """Kanıtların en son alınma zamanı (ISO-8601 UTC).

    `kanit_kaydet()` bu alanı daima `datetime.now(timezone.utc).isoformat()`
    ile yazar; tek biçim olduğu için sözlük sıralaması kronolojiktir.
    Hiç kanıt yoksa "bilinmiyor" — bugünün tarihi UYDURULMAZ (D-268).
    """
    zamanlar = sorted(
        str(k.get("alinma_zamani")) for k in kanitlar if k.get("alinma_zamani")
    )
    return zamanlar[-1] if zamanlar else _YOK


def zaman_cizelgesi(kanitlar: Iterable[Mapping[str, Any]]) -> list[dict]:
    """Kanıtları tarihe göre sıralı çizelge satırlarına çevirir.

    Tarihi ayrıştırılamayan kayıt **atılmaz** (D-216): `tarih=None` ile en
    sona alınır ve ham değeri raporda görünür.
    """
    satirlar = []
    for kanit in kanitlar:
        ham = kanit.get("yayin_tarihi") or kanit.get("tescil_tarihi") or ""
        cozulen = IlanKaniti._tarih(ham)
        ilan_turu = (kanit.get("il_turu") or "").strip()
        _, yon = olay_esle(ilan_turu)
        satirlar.append(
            {
                "tarih": cozulen.date().isoformat() if cozulen else None,
                "tarih_ham": str(ham),
                "ilan_turu": ilan_turu,
                "yon": yon,
                "anahtar": kanit_anahtari(kanit),
                "kalici_adres": kalici_adres(kanit),
            }
        )
    return sorted(satirlar, key=lambda s: (s["tarih"] is None, s["tarih"] or ""))


def olumsuz_ilanlar(kanitlar: Sequence[Mapping[str, Any]]) -> dict:
    """Olumsuz (`direction='negative'`) ilanları ayıklar.

    Satır bazında ölçülür (D-216): `ILAN_TURU_ESLEME`'de olmayan (yön=
    'unknown') bir etiket varsa, o kanıt sessizce "negatif değil" sayılmaz —
    `etiketsiz` listesine düşer ve `olculebilir=False` olur. Aksi hâlde rapor
    "olumsuz ilan yok" diye yanlış bir güvence verirdi. Sözlük TSG-04 ile
    dolduruldu (D-307); bu kapı yine de yeni/bilinmeyen etiketler için açık
    kalır.
    """
    cizelge = zaman_cizelgesi(kanitlar)
    etiketsiz = [s for s in cizelge if s["yon"] == "unknown"]
    if etiketsiz:
        return {
            "olculebilir": False,
            "sebep": (
                f"{len(etiketsiz)} kanitin ilan turu ILAN_TURU_ESLEME'de yok: "
                "'olumsuz ilan yok' denemez."
            ),
            "satirlar": [s for s in cizelge if s["yon"] == "negative"],
            "etiketsiz": etiketsiz,
        }
    satirlar = [s for s in cizelge if s["yon"] == "negative"]
    return {"olculebilir": True, "sebep": "", "satirlar": satirlar, "etiketsiz": []}


def _tablo(basliklar: Sequence[str], satirlar: Sequence[Sequence[str]]) -> list[str]:
    """Markdown tablosu. Satır yoksa tek bir '(kayıt yok)' satırı yazar."""
    ciz = ["| " + " | ".join(basliklar) + " |",
           "|" + "|".join("---" for _ in basliklar) + "|"]
    if not satirlar:
        ciz.append("| " + " | ".join(["(kayit yok)"] + [""] * (len(basliklar) - 1)) + " |")
    for satir in satirlar:
        ciz.append("| " + " | ".join(str(h or "") for h in satir) + " |")
    return ciz


def rapor_uret(
    unvan: str,
    kanitlar: Sequence[Mapping[str, Any]],
    kapsam: Mapping[str, str] | None = None,
    kisiler: Sequence[str] = (),
    pencere_gun: int = KAPSAM_PENCERE_GUN,
    uretim_zamani: datetime | None = None,
) -> str:
    """TSG raporunu Markdown olarak üretir.

    `kapsam`: `{kaynak_adi: durum_metni}` — hangi kaynağın tarandığı.
    **Ölçülmemişse `None` verilir** ve rapor bunu açıkça yazar; "tam kapsam"
    iddiası kanıtsız edilmez (D-268).
    """
    simdi = uretim_zamani or datetime.now(timezone.utc)
    cizelge = zaman_cizelgesi(kanitlar)
    olumsuz = olumsuz_ilanlar(kanitlar)

    s: list[str] = [
        f"# Ticaret Sicili Raporu - {unvan or _YOK}",
        "",
        f"- **Uretim:** {simdi.isoformat(timespec='seconds')}",
        f"- **Son teyit:** {son_teyit(kanitlar)}",
        f"- **Kanit sayisi:** {len(kanitlar)}",
        f"- **Kaynak:** {KAYNAK_URL}",
        "",
        "## Zaman cizelgesi",
        "",
    ]
    s += _tablo(
        ["Tarih", "Ilan turu", "Yon", "Kanit anahtari", "Kalici adres (GUID)"],
        [
            [
                r["tarih"] or f"cozulemedi: {r['tarih_ham'] or _YOK}",
                r["ilan_turu"] or _YOK,
                r["yon"],
                r["anahtar"],
                r["kalici_adres"] or "yok (Katman 0)",
            ]
            for r in cizelge
        ],
    )

    s += ["", "## Olumsuz ilanlar", ""]
    if not olumsuz["olculebilir"]:
        s += [f"**OLCULEMEZ.** {olumsuz['sebep']}", ""]
    else:
        s += _tablo(
            ["Tarih", "Ilan turu", "Kanit anahtari"],
            [[r["tarih"] or _YOK, r["ilan_turu"], r["anahtar"]]
             for r in olumsuz["satirlar"]],
        )

    s += ["", f"## Kapsam (son {pencere_gun} gun)", ""]
    if kapsam:
        s += _tablo(["Kaynak", "Durum"], [[k, v] for k, v in sorted(kapsam.items())])
    else:
        s += [
            "**OLCULMEDI.** Hangi kaynagin tarandigi bu rapora gecirilmedi; "
            "'tam kapsam' iddiasi edilemez (D-268).",
        ]

    s += ["", "## Kisiler (maskeli)", ""]
    s += _tablo(
        ["Ad (maskeli)"],
        [[kisi_maskele(k)] for k in kisiler],
    )

    return "\n".join(s) + "\n"


def rapor_konusu(unvan: str) -> str:
    """Posta konusu — tek yerden, rapor ile aynı dili konuşur."""
    return f"Ticaret Sicili Raporu: {unvan or _YOK}"


def posta_govdesi(markdown: str) -> str:
    """Markdown'i `web_app._send_email(html_body=...)` icin HTML'e sarar.

    ponytail: Markdown -> HTML cevirici YOK; govde `<pre>` icinde kacisli
    duz metin. Yeni bagimlilik (markdown paketi) eklemek icin tek gerekce
    "tablolar daha guzel gorunur" olurdu — yetersiz. Musteriye giden HTML
    rapor istenirse o zaman cevirici eklenir.
    """
    return f"<pre>{html.escape(markdown)}</pre>"
