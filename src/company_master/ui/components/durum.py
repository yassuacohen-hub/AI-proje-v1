# -*- coding: utf-8 -*-
"""ADMIN-ROO-01: Durum bileşenleri (hata kutusu, boş durum, yükleniyor, api_cagir).

Admin sekmelerinde tekrar eden ``try/except: pass`` ve çıplak ``requests``
kalıplarını tek bir sözleşmeye bağlar:

- :func:`hata_kutusu`  — başlık + kısa hata metni + isteğe bağlı ipucu.
- :func:`bos_durum`    — veri yokken ikon + mesaj (+ isteğe bağlı aksiyon etiketi).
- :func:`yukleniyor`   — yükleniyor iskeleti (metin).
- :func:`api_cagir`    — çağrıyı sarmalar; hata olursa ``hata_kutusu`` çizer ve
  ``None`` döndürür. Sekme çökmez, kullanıcı ne olduğunu görür.

Tasarım kuralları (``company_master.ui.base`` ile hizalı):
- Bileşenler **saf HTML string** üretir (``*_html`` fonksiyonları); Streamlit
  yalnızca ``render`` tarafında **yerel import** ile çağrılır.
- Kullanıcı verisi ``guvenli_metin`` ile kaçışlanır (XSS).
- Ham hex renk yok; tüm renkler ``tokens.py`` CSS değişkenleri üzerinden.
- CSS sınıf ön eki ``hg-``.
"""
from __future__ import annotations

import logging
from typing import Any, Callable, TypeVar

from company_master.ui.base import etiket, guvenli_metin, sinif, sinif_listesi
from company_master.ui.tokens import ONEK, token

log = logging.getLogger(__name__)

T = TypeVar("T")

#: Hata metni bu uzunluğu aşarsa kırpılır (stack trace/HTML gövdesi sızmasın).
HATA_METIN_LIMIT: int = 240

#: Durum bileşenlerinin stil kuralları (oturum başına bir kez enjekte edilir).
#: Tüm değerler ``tokens.py`` CSS değişkenleridir; sabit renk içermez.
DURUM_CSS: str = f"""
<style>
.{ONEK}-durum {{
  border: 1px solid {token("color", "border")};
  border-radius: {token("radius", "card")};
  padding: {token("space", "3")} {token("space", "4")};
  margin: {token("space", "2")} 0;
  font-family: {token("font", "font-family")};
  font-size: {token("font", "size-body")};
  line-height: {token("font", "line-normal")};
  color: {token("color", "text")};
  background: {token("color", "surface")};
}}
.{ONEK}-durum-hata {{
  border-color: {token("color", "danger")};
  background: {token("color", "danger-soft")};
}}
.{ONEK}-durum-hata .{ONEK}-durum-baslik {{ color: {token("color", "danger-text")}; }}
.{ONEK}-durum-bos {{
  text-align: center;
  color: {token("color", "text-muted")};
  border-style: dashed;
}}
.{ONEK}-durum-yukleniyor {{
  color: {token("color", "text-muted")};
  border-color: {token("color", "info")};
  background: {token("color", "info-soft")};
}}
.{ONEK}-durum-baslik {{ font-weight: {token("font", "weight-semibold")}; margin-bottom: {token("space", "1")}; }}
.{ONEK}-durum-metin {{ word-break: break-word; }}
.{ONEK}-durum-ipucu {{ color: {token("color", "text-muted")}; font-size: {token("font", "size-help")}; margin-top: {token("space", "1")}; }}
.{ONEK}-durum-ikon {{ font-size: {token("font", "size-2xl")}; display: block; margin-bottom: {token("space", "1")}; }}
.{ONEK}-durum-aksiyon {{ color: {token("color", "primary-text")}; margin-top: {token("space", "1")}; }}
</style>
"""

_CSS_SESSION_ANAHTARI = f"_{ONEK}_durum_css_yuklendi"


def hata_metni_kisalt(hata: Any, limit: int = HATA_METIN_LIMIT) -> str:
    """İstisna/metni kullanıcıya gösterilebilir tek satıra indirir.

    - ``Exception`` → ``"TürAdı: mesaj"`` (mesaj boşsa yalnız tür adı).
    - Satır sonları boşluğa çevrilir; ``limit`` aşılırsa ``…`` ile kırpılır.
    - ``None``/boş → ``"Bilinmeyen hata"``.
    """
    if isinstance(hata, BaseException):
        mesaj = str(hata).strip()
        metin = f"{type(hata).__name__}: {mesaj}" if mesaj else type(hata).__name__
    else:
        metin = str(hata or "").strip()
    if not metin:
        return "Bilinmeyen hata"
    metin = " ".join(metin.split())
    if len(metin) > limit:
        return metin[: limit - 1].rstrip() + "…"
    return metin


def hata_kutusu_html(baslik: str, hata: Any, ipucu: str | None = None) -> str:
    """Hata kutusunun HTML'i (yan etkisiz, Streamlit gerektirmez)."""
    icerik = etiket("div", "⚠️ " + guvenli_metin(baslik), **{"class": sinif("durum", "baslik")})
    icerik += etiket("div", guvenli_metin(hata_metni_kisalt(hata)), **{"class": sinif("durum", "metin")})
    if ipucu:
        icerik += etiket("div", "💡 " + guvenli_metin(ipucu), **{"class": sinif("durum", "ipucu")})
    siniflar = sinif_listesi(sinif("durum"), sinif("durum", "hata"))
    return etiket("div", icerik, **{"class": siniflar, "role": "alert"})


def bos_durum_html(mesaj: str, ikon: str = "📭", aksiyon: str | None = None) -> str:
    """Boş durum HTML'i (yan etkisiz)."""
    icerik = etiket("span", guvenli_metin(ikon), **{"class": sinif("durum", "ikon"), "aria-hidden": "true"})
    icerik += etiket("div", guvenli_metin(mesaj), **{"class": sinif("durum", "metin")})
    if aksiyon:
        icerik += etiket("div", "→ " + guvenli_metin(aksiyon), **{"class": sinif("durum", "aksiyon")})
    siniflar = sinif_listesi(sinif("durum"), sinif("durum", "bos"))
    return etiket("div", icerik, **{"class": siniflar, "role": "status"})


def yukleniyor_html(mesaj: str = "Yükleniyor…") -> str:
    """Yükleniyor iskeleti HTML'i (yan etkisiz)."""
    icerik = etiket("div", "⏳ " + guvenli_metin(mesaj), **{"class": sinif("durum", "metin")})
    siniflar = sinif_listesi(sinif("durum"), sinif("durum", "yukleniyor"))
    return etiket("div", icerik, **{"class": siniflar, "role": "status", "aria-live": "polite"})


def _st():
    """Streamlit modülünü yerel import ile döndürür (test ortamı Streamlit istemez)."""
    import streamlit as st  # yerel import: base.py kalıbı

    return st


def _css_enjekte(st: Any) -> None:
    """Durum CSS'ini oturum başına bir kez enjekte eder (ilk render'da)."""
    try:
        durum = st.session_state
        if durum.get(_CSS_SESSION_ANAHTARI):
            return
        durum[_CSS_SESSION_ANAHTARI] = True
    except Exception:  # pragma: no cover - session_state yoksa (test stub) yine de yaz
        pass
    st.markdown(DURUM_CSS, unsafe_allow_html=True)


def _yaz(html: str, container: Any | None = None) -> str:
    st = _st()
    hedef = container if container is not None else st
    _css_enjekte(st)
    hedef.markdown(html, unsafe_allow_html=True)
    return html


def hata_kutusu(baslik: str, hata: Any, ipucu: str | None = None, container: Any | None = None) -> str:
    """Hata kutusunu Streamlit'e çizer; üretilen HTML'i döndürür.

    Args:
        baslik: Kısa bağlam ("KPI verisi alınamadı").
        hata: İstisna ya da metin; :func:`hata_metni_kisalt` ile sadeleşir.
        ipucu: Kullanıcıya yol gösteren isteğe bağlı satır ("API 8000 ayakta mı?").
        container: Streamlit kapsayıcısı (``st.columns`` vb.); ``None`` → ``st``.
    """
    return _yaz(hata_kutusu_html(baslik, hata, ipucu), container)


def bos_durum(mesaj: str, ikon: str = "📭", aksiyon: str | None = None, container: Any | None = None) -> str:
    """Boş durum kutusunu çizer; üretilen HTML'i döndürür."""
    return _yaz(bos_durum_html(mesaj, ikon, aksiyon), container)


def yukleniyor(mesaj: str = "Yükleniyor…", container: Any | None = None) -> str:
    """Yükleniyor iskeletini çizer; üretilen HTML'i döndürür."""
    return _yaz(yukleniyor_html(mesaj), container)


def api_cagir(
    fn: Callable[..., T],
    *args: Any,
    baslik: str,
    ipucu: str | None = "API (8000) ayakta mı? `docker compose ps api` ile kontrol edin.",
    container: Any | None = None,
    **kwargs: Any,
) -> T | None:
    """``fn(*args, **kwargs)`` çağırır; istisna olursa ``hata_kutusu`` çizip ``None`` döner.

    Çıplak ``requests.get(...)`` ve ``except Exception: pass`` kalıplarının yerine
    kullanılır. Hata ayrıca ``logging`` ile kaydedilir (sessiz yutma yok).

    Örnek::

        veri = api_cagir(load_kpi_data, baslik="KPI verisi alınamadı")
        if veri is None:
            return
    """
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - UI sınırı: her hata kullanıcıya gösterilir
        log.warning("api_cagir: %s -> %s", baslik, hata_metni_kisalt(exc))
        hata_kutusu(baslik, exc, ipucu, container=container)
        return None


__all__ = [
    "DURUM_CSS",
    "HATA_METIN_LIMIT",
    "api_cagir",
    "bos_durum",
    "bos_durum_html",
    "hata_kutusu",
    "hata_kutusu_html",
    "hata_metni_kisalt",
    "yukleniyor",
    "yukleniyor_html",
]
