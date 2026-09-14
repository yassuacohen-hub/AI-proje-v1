# -*- coding: utf-8 -*-
"""ADMIN-UI-09/10: Sayfa iskeleti sözleşmesi.

Amaç:
    Admin panelindeki her sekmenin **aynı dokümantasyon kalıbını** kullanmasını
    garanti etmek: ``PageHeader`` (üst etiket → H1 → giriş paragrafı) +
    ``Section`` (H2 + açıklama) blokları. Böylece "derme çatma, tutarsız"
    başlık kullanımı (``st.subheader`` / elle ``st.markdown("### ...")``)
    sessizce geri dönemez.

Yaklaşım:
    Kaynak dosyalar **AST ile** taranır; Streamlit çalıştırılmaz (hızlı ve
    yan etkisiz).

    ADIM 10 tamamlandığında geçici ``TASINMIS`` / ``BEKLEYEN`` listeleri
    kaldırıldı. Artık sözleşme **türetilmiş** bir listeye uygulanır:

        EKRANLAR = tabs/ altındaki tüm modüller − MUAF

    Bunun sonucu: ``tabs/`` altına eklenen **her yeni ekran otomatik olarak
    sözleşmeye tabidir**. Bir modül ekran değilse (yardımcı parça, alt sekme
    gövdesi vb.) bilinçli olarak ``MUAF`` sözlüğüne **gerekçesiyle** eklenmeli;
    aksi halde testler kırılır.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent
TABS_DIZIN = KOK / "web_dashboard" / "tabs"

# ---------------------------------------------------------------------------
# Kapsam
# ---------------------------------------------------------------------------

#: Sözleşme dışı tutulan modüller (dağıtıcı değil, yardımcı parça).
#: Yeni bir muafiyet eklemek **bilinçli bir karardır**; gerekçe zorunludur.
MUAF: dict[str, str] = {
    "__init__": "Navigasyon kaydı; ekran çizmez",
    "admin_auth": "Giriş formu; tam sayfa başlığı taşımaz",
    "admin_auto_refresh": "Gömülü kontrol şeridi; bağımsız ekran değil",
    "admin_errors": "Hata sayfası bileşeni; kendi başlık kalıbı var",
    "admin_loading": "Yükleme durumu vitrini; öksüz (sahip kararı bekliyor)",
    "admin_extras": "Yardımcı parçalar; bağımsız ekran değil",
    "admin_export": "Dışa aktarma yardımcıları; bağımsız ekran değil",
    "admin_search": "Arama yardımcıları; bağımsız ekran değil",
    "webhook_monitor": "Alt sekme gövdesi; sistem dağıtıcısı altında çizilir",
    "admin_api_analytics": "Alt sekme gövdesi",
    "admin_cost": "Alt sekme gövdesi",
    "admin_dlq": "Alt sekme gövdesi",
    "admin_kpi": "Alt sekme gövdesi",
    "admin_performance": "Alt sekme gövdesi",
    "admin_quality": "Alt sekme gövdesi",
    "admin_audit": "Alt sekme gövdesi",
}


def _ekranlar() -> tuple[str, ...]:
    """Sözleşmeye tabi ekran modüllerini dosya sisteminden türetir."""
    mevcut = {p.stem for p in TABS_DIZIN.glob("*.py")}
    return tuple(sorted(mevcut - set(MUAF)))


#: Sözleşmeye uymak **zorunda** olan ekranlar (türetilmiş — elle bakım yok).
EKRANLAR: tuple[str, ...] = _ekranlar()


# ---------------------------------------------------------------------------
# AST yardımcıları
# ---------------------------------------------------------------------------


def _agac(modul: str) -> ast.Module:
    """Modül kaynağını AST'ye çevirir."""
    kaynak = (TABS_DIZIN / f"{modul}.py").read_text(encoding="utf-8")
    return ast.parse(kaynak)


def _kullanilan_isimler(agac: ast.Module) -> set[str]:
    """Kaynakta geçen tüm `Name` düğümlerini toplar."""
    return {d.id for d in ast.walk(agac) if isinstance(d, ast.Name)}


def _st_cagrilari(agac: ast.Module, ad: str) -> list[ast.Call]:
    """`st.<ad>(...)` biçimindeki çağrıları döndürür."""
    sonuc: list[ast.Call] = []
    for dugum in ast.walk(agac):
        if not isinstance(dugum, ast.Call):
            continue
        f = dugum.func
        if isinstance(f, ast.Attribute) and f.attr == ad:
            if isinstance(f.value, ast.Name) and f.value.id == "st":
                sonuc.append(dugum)
    return sonuc


def _markdown_basliklari(agac: ast.Module) -> list[str]:
    """`st.markdown("### ...")` gibi elle yazılmış başlıkları bulur."""
    bulunan: list[str] = []
    for cagri in _st_cagrilari(agac, "markdown"):
        if not cagri.args:
            continue
        ilk = cagri.args[0]
        if isinstance(ilk, ast.Constant) and isinstance(ilk.value, str):
            metin = ilk.value.lstrip()
            if metin.startswith("#"):
                bulunan.append(metin.splitlines()[0][:60])
    return bulunan


# ---------------------------------------------------------------------------
# Sözleşme testleri — tüm ekranlar
# ---------------------------------------------------------------------------

#: Sözleşme ihlalinde gösterilecek ortak yönlendirme.
_IPUCU = (
    "Modül bir ekran değilse MUAF sözlüğüne gerekçesiyle ekleyin; "
    "ekransa ADMIN-UI-10 kalıbına taşıyın."
)


@pytest.mark.parametrize("modul", EKRANLAR)
def test_ekran_page_header_kullanir(modul: str) -> None:
    """Her ekran `PageHeader` ile tek bir H1 kurar."""
    isimler = _kullanilan_isimler(_agac(modul))
    assert "PageHeader" in isimler, (
        f"{modul}: sayfa `PageHeader` ile başlamalı. "
        f"Playground kalıbı: üst etiket → H1 → giriş paragrafı. {_IPUCU}"
    )


@pytest.mark.parametrize("modul", EKRANLAR)
def test_ekran_section_kullanir(modul: str) -> None:
    """Her ekran gövdeyi `Section` bloklarına ayırır."""
    isimler = _kullanilan_isimler(_agac(modul))
    assert "Section" in isimler, (
        f"{modul}: içerik `Section` blokları ile gruplanmalı "
        f"(H2 + açıklama + ayraç). {_IPUCU}"
    )


@pytest.mark.parametrize("modul", EKRANLAR)
def test_ekranda_subheader_kalmaz(modul: str) -> None:
    """`st.subheader` sayfa iskeletiyle çakışan eski kalıptır."""
    kalanlar = _st_cagrilari(_agac(modul), "subheader")
    assert not kalanlar, (
        f"{modul}: {len(kalanlar)} adet `st.subheader` kaldı. "
        "Bunlar `PageHeader` veya `Section` ile değiştirilmeli."
    )


@pytest.mark.parametrize("modul", EKRANLAR)
def test_ekranda_elle_markdown_baslik_kalmaz(modul: str) -> None:
    """`st.markdown("### ...")` tipografi ölçeğini atlar; yasak."""
    kalanlar = _markdown_basliklari(_agac(modul))
    assert not kalanlar, (
        f"{modul}: elle yazılmış markdown başlığı kaldı: {kalanlar}. "
        "Başlıklar `Section` üzerinden kurulmalı ki tipografi ölçeği "
        "ve anchor kimlikleri tutarlı kalsın."
    )


# ---------------------------------------------------------------------------
# Bekçi testleri — kapsamın bütünlüğü
# ---------------------------------------------------------------------------


def test_ekran_listesi_bos_degil() -> None:
    """Glob bozulursa sözleşme sessizce hiçbir şeyi test etmez; bunu yakala."""
    assert EKRANLAR, (
        "Sözleşmeye tabi ekran bulunamadı. `TABS_DIZIN` yolu bozulmuş olabilir "
        f"({TABS_DIZIN}) veya tüm modüller yanlışlıkla MUAF'a alınmış."
    )


def test_bilinen_ekranlar_kapsamda() -> None:
    """Çekirdek ekranlar kapsam dışına kaydırılamaz (regresyon kilidi)."""
    cekirdek = {"ana_kontrol", "admin_sistem", "admin_yonetim", "admin_panel"}
    eksik = sorted(cekirdek - set(EKRANLAR))
    assert not eksik, (
        f"Çekirdek ekranlar sözleşme kapsamı dışında: {eksik}. "
        "MUAF listesine alınmış olabilirler; bu kabul edilemez."
    )


def test_muaf_moduller_gercekten_var() -> None:
    """MUAF listesi var olmayan dosyaya işaret etmemeli (ölü kayıt)."""
    eksik = [ad for ad in MUAF if not (TABS_DIZIN / f"{ad}.py").exists()]
    assert not eksik, (
        f"MUAF listesinde olup dosyası bulunmayan modüller: {eksik}. "
        "Dosya silindiyse kaydı da kaldırın."
    )


def test_muaf_kayitlarin_gerekcesi_var() -> None:
    """Gerekçesiz muafiyet kalıcı borç üretir."""
    bos = sorted(ad for ad, gerekce in MUAF.items() if not gerekce.strip())
    assert not bos, f"Gerekçesiz muafiyet kayıtları: {bos}"


@pytest.mark.parametrize(
    "modul", sorted(p.stem for p in TABS_DIZIN.glob("*.py"))
)
def test_kaynak_dosya_bom_icermez(modul: str) -> None:
    """UTF-8 BOM yasak: ``ast.parse`` ve bazı araçlar U+FEFF ile kırılır.

    ADIM 10 sırasında üç dosyada (``admin_panel``, ``admin_auth``,
    ``__init__``) BOM bulundu. ``py_compile`` bunu tolere ettiği için hata
    yıllarca sessiz kalabiliyordu; bu bekçi onu görünür tutar.
    """
    ham = (TABS_DIZIN / f"{modul}.py").read_bytes()
    assert not ham.startswith(b"\xef\xbb\xbf"), (
        f"{modul}.py UTF-8 BOM ile başlıyor (U+FEFF). Dosyayı BOM'suz "
        "UTF-8 olarak kaydedin; aksi halde AST tabanlı araçlar kırılır."
    )
