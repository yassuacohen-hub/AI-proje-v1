# -*- coding: utf-8 -*-
"""ADMIN-ROO-01 Aşama E: kapsam sekmelerinde durum/hata disiplini regresyon testi.

Kontroller (brief D + E):
    * ``except ...: pass`` sessiz yutma kalıbı YOK (regex, yorum satırları hariç).
    * ``st.metric(`` kullanımı YOK — KPI'lar ``kpi_karti`` ile çizilir.
    * Çıplak ``requests.get/post`` yok (``api_cagir`` / ``get_api`` sarmalı zorunlu);
      istisna: ``admin_realtime`` SSE okuyucu (try/except + ``(veri, hata)`` sözleşmesi).
    * ``import ... text`` — ham SQL ``sqlalchemy.text()`` ile sarılı (``.execute("...``
      dizgesi doğrudan geçmiyor).
    * Her modül import edilebilir; ``render_*`` giriş noktaları çağrıldığında
      API/DB hatası fırlatmaz (``api_cagir`` → ``hata_kutusu`` yolu).
"""
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TABS = ROOT / "web_dashboard" / "tabs"

#: ADMIN-ROO-01 kapsamındaki sekmeler (brief Aşama B + C + D).
KAPSAM: tuple[str, ...] = (
    "admin_realtime",
    "admin_sistem",
    "admin_musteriler",
    "admin_yonetim",
    "admin_extras",
    "admin_destek",
    "admin_export",
    "admin_loading",
    "teknik_altyapi",
    "proje_yonetimi",
    "pazarlama",
    "paketler",
)

#: Aşama D — kpi_karti zorunlu olan sekmeler.
KPI_KARTI_ZORUNLU: tuple[str, ...] = ("admin_realtime", "pazarlama", "paketler")

_SESSIZ_YUTMA = re.compile(r"except[^\n]*:\s*(#[^\n]*)?\n\s+pass\b")
_ST_METRIC = re.compile(r"\bst\.metric\(")
_CIPLAK_REQUESTS = re.compile(r"\brequests\.(get|post|put|delete)\(")
_HAM_SQL_EXECUTE = re.compile(r"\.execute\(\s*[\"']")


def _kaynak(modul: str) -> str:
    return (TABS / f"{modul}.py").read_text(encoding="utf-8")


def _yorumsuz(kaynak: str) -> str:
    """Satır yorumlarını ve docstring başlıklarını kabaca ayıklar."""
    satirlar = []
    for satir in kaynak.splitlines():
        gövde = satir.split("#", 1)[0] if not satir.lstrip().startswith("#") else ""
        satirlar.append(gövde)
    return "\n".join(satirlar)


@pytest.mark.parametrize("modul", KAPSAM)
def test_dosya_var_ve_utf8(modul: str) -> None:
    yol = TABS / f"{modul}.py"
    assert yol.exists(), f"{yol} bulunamadı"
    ham = yol.read_bytes()
    assert not ham.startswith(b"\xef\xbb\xbf"), f"{modul}.py BOM içeriyor"
    assert b"\x00" not in ham, f"{modul}.py NUL byte içeriyor"


@pytest.mark.parametrize("modul", KAPSAM)
def test_sessiz_yutma_yok(modul: str) -> None:
    """``except ...: pass`` kalıbı kapsam sekmelerinde bulunmamalı."""
    eslesmeler = _SESSIZ_YUTMA.findall(_yorumsuz(_kaynak(modul)))
    assert not eslesmeler, f"{modul}.py içinde sessiz `except: pass` var ({len(eslesmeler)})"


@pytest.mark.parametrize("modul", KAPSAM)
def test_st_metric_yok(modul: str) -> None:
    """KPI tek dil: ``st.metric`` yerine ``kpi_karti``."""
    assert not _ST_METRIC.search(_yorumsuz(_kaynak(modul))), f"{modul}.py hâlâ st.metric kullanıyor"


@pytest.mark.parametrize("modul", KPI_KARTI_ZORUNLU)
def test_kpi_karti_import_edilmis(modul: str) -> None:
    kaynak = _kaynak(modul)
    assert "from web_dashboard.charts import" in kaynak and "kpi_karti" in kaynak, (
        f"{modul}.py kpi_karti import etmiyor"
    )
    assert "kpi_karti(" in kaynak, f"{modul}.py kpi_karti çağırmıyor"


@pytest.mark.parametrize("modul", [m for m in KAPSAM if m != "admin_realtime"])
def test_ciplak_requests_yok(modul: str) -> None:
    """Sekmeler HTTP'yi ``get_api``/``post_api`` + ``api_cagir`` üzerinden yapar."""
    assert not _CIPLAK_REQUESTS.search(_yorumsuz(_kaynak(modul))), (
        f"{modul}.py çıplak requests.* çağrısı içeriyor"
    )


def test_admin_realtime_sse_sarmali_ve_text() -> None:
    """SSE okuyucu try/except + (veri, hata) sözleşmesinde; ham SQL text() ile sarılı."""
    kaynak = _kaynak("admin_realtime")
    assert "def _sse_oku" in kaynak
    assert "hata_kutusu" in kaynak or "api_cagir" in kaynak
    assert "text(" in kaynak, "admin_realtime ham SQL'i sqlalchemy.text() ile sarmalı"
    assert not _HAM_SQL_EXECUTE.search(_yorumsuz(kaynak)), "admin_realtime .execute(\"...\") ham SQL içeriyor"


@pytest.mark.parametrize("modul", KAPSAM)
def test_modul_import_edilebilir(modul: str) -> None:
    mod = importlib.import_module(f"web_dashboard.tabs.{modul}")
    assert mod is not None


# ---------------------------------------------------------------------------
# Render duman testleri — API/DB patlasa bile exception fırlatmamalı
# ---------------------------------------------------------------------------


def _st_mock() -> MagicMock:
    """Bağlam yöneticileri ve kolon döndüren çağrılar için güvenli Streamlit taklidi."""
    st_mock = MagicMock()
    kolon = MagicMock()
    kolon.__enter__ = lambda s: s
    kolon.__exit__ = lambda s, *a: False
    st_mock.columns.side_effect = lambda spec, **kw: [kolon] * (spec if isinstance(spec, int) else len(spec))
    st_mock.tabs.side_effect = lambda etiketler, **kw: [kolon] * len(etiketler)
    st_mock.expander.return_value = kolon
    st_mock.form.return_value = kolon
    st_mock.container.return_value = kolon
    st_mock.session_state = {}
    st_mock.button.return_value = False
    st_mock.form_submit_button.return_value = False
    st_mock.selectbox.side_effect = lambda label, options=(), **kw: (list(options) or [None])[0]
    st_mock.radio.side_effect = lambda label, options=(), **kw: (list(options) or [None])[0]
    st_mock.text_input.return_value = ""
    st_mock.number_input.return_value = 0
    st_mock.checkbox.return_value = False
    return st_mock


def _patla(*_a, **_k):
    raise RuntimeError("API/DB erişilemez (test)")


def test_admin_extras_api_hatasi_exception_firlatmaz(monkeypatch) -> None:
    import web_dashboard.tabs.admin_extras as m

    st_mock = _st_mock()
    monkeypatch.setattr(m, "st", st_mock)
    monkeypatch.setattr(m, "get_api", _patla)
    m.render_api_management(token="t")
    m.render_user_management(token="t")
    assert st_mock.dataframe.call_count == 0  # veri gelmedi, tablo çizilmedi


def test_admin_export_db_hatasi_exception_firlatmaz(monkeypatch) -> None:
    import web_dashboard.tabs.admin_export as m

    st_mock = _st_mock()
    monkeypatch.setattr(m, "st", st_mock)
    monkeypatch.setattr(m, "_export_verisi_oku", lambda q: (None, "DB yok (test)"))
    m.render_export_tab()
    assert st_mock.download_button.call_count == 0


def test_pazarlama_ozet_kpi_karti_ile_cizilir(monkeypatch) -> None:
    import web_dashboard.tabs.pazarlama as m

    st_mock = _st_mock()
    monkeypatch.setattr(m, "st", st_mock)
    cagrilar: list[tuple] = []
    monkeypatch.setattr(m, "kpi_karti", lambda *a, **k: cagrilar.append((a, k)))
    m._render_ozet({"kampanya_sayisi": 3, "aktif_kampanyalar": 1, "segment_sayisi": 2, "aktif_segmentler": 2})
    assert [c[0][0] for c in cagrilar] == ["Kampanya Sayısı", "Aktif Kampanya", "Segment Sayısı", "Aktif Segment"]
    assert all("aciklama" in c[1] for c in cagrilar)
    assert st_mock.metric.call_count == 0


def test_pazarlama_performans_none_maliyet(monkeypatch) -> None:
    """Dönüşüm yoksa maliyet None → kpi_karti '—' basar (string '-' yok)."""
    import web_dashboard.tabs.pazarlama as m

    st_mock = _st_mock()
    monkeypatch.setattr(m, "st", st_mock)
    cagrilar: list[tuple] = []
    monkeypatch.setattr(m, "kpi_karti", lambda *a, **k: cagrilar.append((a, k)))
    kampanyalar = [{"budget": 1000, "impressions": 100, "clicks": 10, "conversions": 0}]
    m._render_performans(kampanyalar)
    basliklar = {c[0][0]: c for c in cagrilar}
    assert "Dönüşüm Başı Maliyet" in basliklar
    assert basliklar["Dönüşüm Başı Maliyet"][0][1] is None
    assert basliklar["Toplam Bütçe"][1].get("birim") == "₺"
    assert basliklar["Tıklama Oranı (CTR)"][1].get("birim") == "%"


def test_paketler_ozet_bos_liste(monkeypatch) -> None:
    """Paket yokken ortalama/aralık None → kpi_karti '—' gösterir; ZeroDivision yok."""
    import web_dashboard.tabs.paketler as m

    st_mock = _st_mock()
    monkeypatch.setattr(m, "st", st_mock)
    cagrilar: list[tuple] = []
    monkeypatch.setattr(m, "kpi_karti", lambda *a, **k: cagrilar.append((a, k)))
    m._render_ozet([])
    degerler = {c[0][0]: c[0][1] for c in cagrilar}
    assert degerler == {"Paket Sayısı": 0, "Ortalama Fiyat": None, "Fiyat Aralığı": None}


def test_paketler_ozet_fiyat_araligi_turkce_binlik(monkeypatch) -> None:
    import web_dashboard.tabs.paketler as m

    st_mock = _st_mock()
    monkeypatch.setattr(m, "st", st_mock)
    cagrilar: list[tuple] = []
    monkeypatch.setattr(m, "kpi_karti", lambda *a, **k: cagrilar.append((a, k)))
    m._render_ozet([{"price": 1000}, {"price": 25000}])
    degerler = {c[0][0]: c[0][1] for c in cagrilar}
    assert degerler["Fiyat Aralığı"] == "1.000 – 25.000 ₺"
    assert degerler["Ortalama Fiyat"] == 13000.0


def test_sayi_formatla_none_ve_string_gecisi() -> None:
    """kpi_karti'ye geçen None → '—'; hazır string olduğu gibi kalır (Aşama D varsayımı)."""
    from web_dashboard.charts import sayi_formatla

    assert sayi_formatla(None, 0, "₺") == "—"
    assert sayi_formatla("1.000 – 25.000 ₺") == "1.000 – 25.000 ₺"
    assert sayi_formatla(12.345, 2, "%") == "%12,35"
    assert sayi_formatla(12345, 0, "₺") == "12.345 ₺"


# ADMIN-NAV-HAZIR-01: Pano okunamazsa kullanılacak asgari "bitmiş görev" listesi.
# Bu görevler tamamlandığı hâlde SECTIONS'ta `bekleyen_gorev` olarak duruyordu.
BITMIS_GOREVLER: frozenset[str] = frozenset({"NAV-IA-01", "NAV-IA-02"})


def _pano_gorevleri() -> list[dict]:
    """Görev panosunu okur; dosya yoksa/bozuksa boş liste döndürür (skip yok)."""
    import json
    from pathlib import Path

    yol = Path(__file__).resolve().parents[1] / "data" / "orchestrator" / "task_board.json"
    if not yol.exists():
        return []
    try:
        veri = json.loads(yol.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return []
    if isinstance(veri, dict):
        veri = veri.get("tasks") or veri.get("gorevler") or []
    if not isinstance(veri, list):
        return []
    return [g for g in veri if isinstance(g, dict)]


def _bitmis_gorev_kumesi() -> set[str]:
    """Panoda ``done``/``review`` olan görev kimlikleri + sabit fallback listesi."""
    bitmis = set(BITMIS_GOREVLER)
    for gorev in _pano_gorevleri():
        if gorev.get("durum") in {"done", "review"}:
            kimlik = gorev.get("task_id") or gorev.get("id")
            if kimlik:
                bitmis.add(str(kimlik))
    return bitmis


def test_tabs_init_bekleyen_gorev_panoda_done() -> None:
    """ADMIN-NAV-HAZIR-01: Bitmiş göreve referans veren `bekleyen_gorev` kalmamalı.

    Pano (`data/orchestrator/task_board.json`) okunabiliyorsa `done`/`review` görevler
    kullanılır; okunamazsa sabit ``BITMIS_GOREVLER`` listesiyle devam edilir (skip yok).
    """
    from web_dashboard.tabs import SECTIONS

    bitmis = _bitmis_gorev_kumesi()
    for tanim in SECTIONS:
        bekleyen = tanim.bekleyen_gorev
        if bekleyen:
            assert bekleyen not in bitmis, (
                f"{tanim.anahtar}: bekleyen_gorev={bekleyen} görevi bitmiş olduğu hâlde "
                "hâlâ tanımda duruyor (hazir=True yapılmalı)"
            )
