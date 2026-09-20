# -*- coding: utf-8 -*-
"""TEST-AYARLAR-KAPSAM-01 — Kullanıcı Ayarları sayfası test iskeleti (ADMIN-UX-AYARLAR-SAYFA-01).

Kaynak sözleşme:
    ``docs/UX_AYARLAR_SAYFA_WIREFRAME_2026-09-18.md`` (KAHİN onaylı) — Bölüm 4.2
    kabul kriterleri (7 madde). Her test tek bir kriteri ölçer ve docstring'inde
    kriter numarasını taşır.

Hedef modül durumu:
    ``web_dashboard/tabs/admin_kullanici_ayarlari.py`` roo tarafından HENÜZ
    yazılmadı. Modül gelene kadar tüm kriter testleri ``pytest.skip`` ile
    ATLANIR (dosya varlık kontrolü — importorskip deseni, sys.path derdi yok).
    Modül geldiğinde testler otomatik devreye girer.

Yöntem:
    Kaynak dosyalar **AST ile** taranır; Streamlit çalıştırılmaz (hızlı ve yan
    etkisiz — ``tests/test_sayfa_iskeleti.py`` deseni).

Kural:
    ``web_dashboard/`` altına DOKUNULMAZ (roo üretiyor); bu dosya yalnız
    ``tests/`` altındaki kapsamı ölçer. İskelet statik kontroller içerir;
    hedef modül geldiğinde kriter 4 gibi davranışsal doğrulamalar
    derinleştirilmelidir (TEST-AYARLAR-KAPSAM-01 teslim özetinde notlu).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parent.parent
HEDEF_YOL = KOK / "web_dashboard" / "tabs" / "admin_kullanici_ayarlari.py"
HEDEF_MODUL = "web_dashboard.tabs.admin_kullanici_ayarlari"
ADMIN_PANEL_YOL = KOK / "web_dashboard" / "tabs" / "admin_panel.py"
NAV_YOL = KOK / "web_dashboard" / "tabs" / "__init__.py"

BEKLENEN_FONKSIYON = "render_kullanici_ayarlari_tab"
#: Wireframe §2.1: 3 bölüm — Hesap · Güvenlik · Tercihler (sıra sabit, §3.4).
BEKLENEN_BOLUMLER = ("Hesap", "Güvenlik", "Tercihler")


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------


def _hedef_kaynak() -> str:
    """Hedef modülü okur; yoksa tüm sınıfı tek noktadan atlatır."""
    if not HEDEF_YOL.exists():
        pytest.skip(
            "ADMIN-UX-AYARLAR-SAYFA-01 hedef modülü henüz yok (roo yazıyor) — "
            "kriter testleri modül geldiğinde devreye girer"
        )
    return HEDEF_YOL.read_text(encoding="utf-8")


def _hedef_agac() -> ast.Module:
    """Hedef modülü AST'ye ayrıştırır; bozuk kaynak doğrudan fail üretir."""
    return ast.parse(_hedef_kaynak())


def _fonksiyon_adlari(agac: ast.AST) -> list[str]:
    return [
        node.name
        for node in ast.walk(agac)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]



# ---------------------------------------------------------------------------
# Kritik 1 — "Sayfa 3 bölüm çizer (Hesap, Güvenlik, Tercihler)"
# ---------------------------------------------------------------------------


def test_kriter1_sayfa_uc_bolum_cizer() -> None:
    """4.2 #1: modül sözleşmesi + 3 bölüm (Hesap, Güvenlik, Tercihler) mevcut."""
    kaynak = _hedef_kaynak()
    agac = _hedef_agac()
    # Dosya sözleşmesi (wireframe §3.1): render_kullanici_ayarlari_tab tanımlı.
    assert BEKLENEN_FONKSIYON in _fonksiyon_adlari(agac), (
        f"{HEDEF_MODUL} içinde {BEKLENEN_FONKSIYON} tanımlı olmalı (wireframe §3.1)"
    )
    # Modül düzeyi BOLUMLER tanımı var (§3.1: BOLUMLER: tuple[Section, ...]).
    modul_tanimlari = {
        node.targets[0].id
        for node in agac.body
        if isinstance(node, ast.Assign)
        and node.targets
        and isinstance(node.targets[0], ast.Name)
    }
    assert "BOLUMLER" in modul_tanimlari, "modül düzeyinde BOLUMLER tanımı yok (§3.1)"
    # Üç bölüm etiketi kaynakta geçmeli (sıra §3.4'te sabittir).
    konum = [kaynak.find(b) for b in BEKLENEN_BOLUMLER]
    for ad, k in zip(BEKLENEN_BOLUMLER, konum):
        assert k != -1, f"'{ad}' bölüm etiketi kaynaktta geçmiyor"
    assert konum == sorted(konum), (
        "bölüm sırası sabit olmalı: Hesap → Güvenlik → Tercihler (wireframe §3.4)"
    )


# ---------------------------------------------------------------------------
# Kritik 2 — "Misafirde Hesap + Güvenlik çizilmez"
# ---------------------------------------------------------------------------


def test_kriter2_misafirde_hesap_guvenlik_cizilmez() -> None:
    """4.2 #2: misafir/anon kimlik için Hesap+Güvenlik bölümü çizilmez.

    Statik ölçüt: kaynakta misafir kimliğin ayrıştırıldığı bir kontrol
    (``misafir`` / ``anon`` / ``guest`` / ``ROL_ANON``) geçmeli. Davranışsal
    doğrulama hedef modül geldiğinde derinleştirilir.
    """
    kaynak = _hedef_kaynak()
    izler = ("misafir", "anon", "guest", "ROL_ANON")
    bulunan = [i for i in izler if i in kaynak]
    assert bulunan, (
        "misafir kimlik kontrolü kaynaktta görünmüyor "
        f"(beklenen izler: {', '.join(izler)}) — wireframe §3.5: misafirde "
        "Güvenlik bölümü hiç çizilmez (form bile oluşturulmaz)"
    )


# ---------------------------------------------------------------------------
# Kritik 3 — "Şifre değiştirme mevcut şifre ister"
# ---------------------------------------------------------------------------


def test_kriter3_sifre_degistirme_mevcut_sifre_ister() -> None:
    """4.2 #3: şifre değiştirme akışı mevcut şifre doğrulaması içerir.

    Sözleşme (§3.2): form ``admin_auth.render_sifre_degistir()``'den gelir.
    Statik ölçüt: ya bu çağrı ya da mevcut/yeni şifre alanları kaynakta
    bulunmalı. Güvenlik kısıtı (§3.5): mevcut şifre doğrulaması KALDIRILMAZ.
    """
    kaynak = _hedef_kaynak()
    izler = ("render_sifre_degistir", "old_password", "mevcut_sifre", "mevcut şifre")
    bulunan = [i for i in izler if i in kaynak]
    assert bulunan, (
        "mevcut şifre izi bulunamadı (render_sifre_degistir çağrısı veya "
        "old_password / mevcut_sifre alanı) — wireframe §3.5: mevcut şifre "
        "doğrulaması zorunlu kalır, kaldırılmaz"
    )


# ---------------------------------------------------------------------------
# Kritik 4 — "Ayar kaydetme hepsi-ya-hiç davranışı korunur"
# ---------------------------------------------------------------------------


def test_kriter4_ayar_kaydetme_hepsi_ya_hic() -> None:
    """4.2 #4: tercih kaydetme tek noktadan, tümüyle uygulanır.

    Statik iskelet ölçütü: ``Kaydet`` düğmesi (form_submit_button) modülde tek
    merkez noktada toplanmalı; tercihler ile güvenlik bölümü AYRI submit'lere
    bölünmemeli (tek Kaydet → hepsi-ya-hiç, wireframe §3.4). Hedef modül
    geldiğinde bu test, kaydet akışının gerçek transaction davranışını da
    ölçecek şekilde derinleştirilir.
    """
    agac = _hedef_agac()
    hedef_fn = next(
        (n for n in ast.walk(agac) if isinstance(n, ast.FunctionDef)
         and n.name == BEKLENEN_FONKSIYON),
        None,
    )
    assert hedef_fn is not None, f"{BEKLENEN_FONKSIYON} bulunamadı"
    submit_sayisi = sum(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "form_submit_button"
        for node in ast.walk(hedef_fn)
    )
    assert submit_sayisi <= 1, (
        f"tercih kaydetme {submit_sayisi} submit düğmesine bölünmüş — "
        "hepsi-ya-hiç davranışı tek Kaydet noktası ister (wireframe §3.4)"
    )


# ---------------------------------------------------------------------------
# Kritik 5 — "admin_panel.py'de render_ayarlar_tab kalmaz"
# ---------------------------------------------------------------------------


def test_kriter5_admin_panelde_render_ayarlar_tab_kalmaz() -> None:
    """4.2 #5: eski ``render_ayarlar_tab`` admin_panel.py'den kalkar.

    Wireframe §4.3 riski: ince sarmalayıcı bırakma ihtimali KAHİN'e sorulmalı;
    kriter metni "kalmaz" der — test kriteri uygular (FunctionDef yasağı).
    """
    _hedef_kaynak()  # hedef modül yoksa skip — kriter roo taşınmasından sonra doğrulanır
    kaynak = ADMIN_PANEL_YOL.read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    tanimlar = _fonksiyon_adlari(agac)
    assert "render_ayarlar_tab" not in tanimlar, (
        "admin_panel.py'de render_ayarlar_tab TANIMI hâlâ var — taşınma "
        "tamamlanmamış (wireframe §4.2 kriter 5). Sarmalayıcı bırakılması "
        "KAHİN onayı ister (§4.3 risk tablosu)."
    )


# ---------------------------------------------------------------------------
# Kritik 6 — "Navigasyon kaydı yeni modüle işaret eder"
# ---------------------------------------------------------------------------


def test_kriter6_navigasyon_yeni_module_isaret_eder() -> None:
    """4.2 #6: ``web_dashboard/tabs/__init__.py`` kaydı hedef modüle döner.

    Sözleşme (§3.1): ``modul`` → ``web_dashboard.tabs.admin_kullanici_ayarlari``,
    ``fonksiyon`` → ``render_kullanici_ayarlari_tab``.
    """
    _hedef_kaynak()  # hedef modül yoksa skip — kriter roo taşınmasından sonra doğrulanır
    kaynak = NAV_YOL.read_text(encoding="utf-8")
    assert HEDEF_MODUL in kaynak, (
        f"navigasyon kaydında '{HEDEF_MODUL}' yok — modül kaydı yeni modüle "
        "işaret etmeli (wireframe §3.1)"
    )
    assert BEKLENEN_FONKSIYON in kaynak, (
        f"navigasyon kaydında '{BEKLENEN_FONKSIYON}' yok (wireframe §3.1)"
    )


# ---------------------------------------------------------------------------
# Kritik 7 — "Mevcut ayar testleri geçmeye devam eder"
# ---------------------------------------------------------------------------


def test_kriter7_mevcut_ayar_testleri_canary() -> None:
    """4.2 #7: taşınma mevcut ayar testlerini KIRMAMALI.

    Iskelet canary (hızlı + bağımlılıksız):
      1. ``admin_panel.py`` AST ile derlenebilir (roo taşıması syntax kırmaz),
      2. mevcut ayar test dosyası (``tests/test_admin_panel_tab.py``) yerinde.
    Tam "geçme" kanıtı tam süit koşusuyla (pytest -q) doğrulanır; bu canary
    yalnız toplama hatası (collection error) korumasıdır.
    """
    kaynak = ADMIN_PANEL_YOL.read_text(encoding="utf-8")
    ast.parse(kaynak)  # syntax bozulmamalı
    mevcut_test = KOK / "tests" / "test_admin_panel_tab.py"
    assert mevcut_test.exists(), (
        "tests/test_admin_panel_tab.py yok — mevcut ayar testleri kaybolmuş "
        "(kriter 7)"
    )


# ---------------------------------------------------------------------------
# Dosya sözleşmesi ek denetimi (wireframe §3.1 imza)
# ---------------------------------------------------------------------------


def test_render_fonksiyonu_imzasi_sozlesmeye_uyumlu() -> None:
    """§3.1: ``render_kullanici_ayarlari_tab(kullanici_id: str | None = None)``.

    AST ile imza denetimi: fonksiyon en fazla 1 konumsal parametre alır; adı
    ``kullanici_id`` ise varsayılanı None olmalı (kimlik opsiyonel).
    """
    agac = _hedef_agac()
    fn = next(
        (n for n in ast.walk(agac) if isinstance(n, ast.FunctionDef)
         and n.name == BEKLENEN_FONKSIYON),
        None,
    )
    assert fn is not None, f"{BEKLENEN_FONKSIYON} tanımı yok (§3.1)"
    pos = fn.args.posonlyargs + fn.args.args
    assert len(pos) <= 1, (
        f"{BEKLENEN_FONKSIYON} beklenmedik konumsal parametreler taşıyor: "
        f"{[a.arg for a in pos]}"
    )
    if pos and pos[0].arg == "kullanici_id" and fn.args.defaults:
        varsayilan = fn.args.defaults[-1]
        assert isinstance(varsayilan, ast.Constant) and varsayilan.value is None, (
            "kullanici_id varsayılanı None olmalı (§3.1 imza sözleşmesi)"
        )

