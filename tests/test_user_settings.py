# -*- coding: utf-8 -*-
"""P7-46: Kullanıcı ayarları servisi ve panel sözleşmesi testleri.

Streamlit gerektirmez: panel katmanı yalnızca kaynak metin üzerinden
sözleşme açısından denetlenir; iş mantığı saf Python servisinde test edilir.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_KOK = Path(__file__).resolve().parents[1]
if str(_KOK / "src") not in sys.path:
    sys.path.insert(0, str(_KOK / "src"))

from company_master.settings import (  # noqa: E402
    AYAR_SEMASI,
    AyarHatasi,
    ayar_kaydet,
    ayarlari_getir,
    ayarlari_sifirla,
    ayarlari_yaz,
    dogrula,
    gruplar,
    varsayilanlar,
)

PANEL_PY = _KOK / "web_dashboard" / "tabs" / "admin_panel.py"
SERVIS_PY = _KOK / "src" / "company_master" / "settings" / "user_settings.py"


@pytest.fixture()
def dizin(tmp_path: Path) -> Path:
    """İzole ayar dizini (gerçek data/ dizinine dokunulmaz)."""
    return tmp_path / "user_settings"


# ---------------------------------------------------------------------------
# Şema
# ---------------------------------------------------------------------------


def test_sema_bos_degil():
    assert len(AYAR_SEMASI) >= 10


def test_sema_anahtarlari_benzersiz():
    anahtarlar = [t.anahtar for t in AYAR_SEMASI]
    assert len(anahtarlar) == len(set(anahtarlar))


@pytest.mark.parametrize("tanim", AYAR_SEMASI, ids=lambda t: t.anahtar)
def test_sema_tanimlari_tutarli(tanim):
    assert tanim.tip in {"secim", "bool", "sayi", "metin"}
    assert tanim.etiket.strip()
    assert tanim.grup.strip()
    if tanim.tip == "secim":
        assert tanim.secenekler, f"{tanim.anahtar}: secim tipi secenek gerektirir"
        assert tanim.varsayilan in tanim.secenekler
    if tanim.tip == "sayi":
        assert tanim.alt_sinir is not None and tanim.ust_sinir is not None
        assert tanim.alt_sinir <= tanim.varsayilan <= tanim.ust_sinir
    if tanim.tip == "bool":
        assert isinstance(tanim.varsayilan, bool)


@pytest.mark.parametrize("tanim", AYAR_SEMASI, ids=lambda t: t.anahtar)
def test_her_ayarin_aciklamasi_var(tanim):
    """Panelde yardım metni boş kalmasın (UX gereksinimi)."""
    assert len(tanim.aciklama) >= 10


def test_varsayilanlar_semayla_ortusur():
    assert set(varsayilanlar()) == {t.anahtar for t in AYAR_SEMASI}


def test_gruplar_tum_ayarlari_kapsar():
    toplam = sum(len(v) for v in gruplar().values())
    assert toplam == len(AYAR_SEMASI)
    assert set(gruplar()) == {t.grup for t in AYAR_SEMASI}


def test_tema_secenekleri_theme_js_ile_uyumlu():
    """UX-03 theme.js 'dark'/'light' bekler; panelde ek olarak 'sistem' olur."""
    tema = next(t for t in AYAR_SEMASI if t.anahtar == "tema")
    assert set(tema.secenekler) == {"sistem", "dark", "light"}


# ---------------------------------------------------------------------------
# Doğrulama
# ---------------------------------------------------------------------------


def test_dogrula_bilinmeyen_anahtar_reddeder():
    with pytest.raises(AyarHatasi):
        dogrula("olmayan_ayar", 1)


def test_dogrula_gecerli_secim():
    assert dogrula("tema", "light") == "light"


def test_dogrula_gecersiz_secim_reddeder():
    with pytest.raises(AyarHatasi):
        dogrula("tema", "mor")


def test_dogrula_bool_tipi_zorunlu():
    assert dogrula("yogun_mod", True) is True
    with pytest.raises(AyarHatasi):
        dogrula("yogun_mod", "evet")


def test_dogrula_sayi_alt_sinir():
    with pytest.raises(AyarHatasi):
        dogrula("sayfa_boyutu", 5)


def test_dogrula_sayi_ust_sinir():
    with pytest.raises(AyarHatasi):
        dogrula("sayfa_boyutu", 5000)


def test_dogrula_sayi_sinir_degerleri_kabul():
    assert dogrula("sayfa_boyutu", 10) == 10
    assert dogrula("sayfa_boyutu", 500) == 500


def test_dogrula_sayiya_bool_sizmaz():
    """bool, int alt sınıfıdır; sessizce 1/0'a dönüşmemeli."""
    with pytest.raises(AyarHatasi):
        dogrula("sayfa_boyutu", True)


def test_dogrula_boola_sayi_sizmaz():
    with pytest.raises(AyarHatasi):
        dogrula("yogun_mod", 1)


# ---------------------------------------------------------------------------
# Okuma / yazma
# ---------------------------------------------------------------------------


def test_dosya_yokken_varsayilan_doner(dizin):
    assert ayarlari_getir("ali", dizin) == varsayilanlar()


def test_kaydet_ve_geri_oku(dizin):
    ayar_kaydet("ali", "tema", "light", dizin)
    assert ayarlari_getir("ali", dizin)["tema"] == "light"


def test_kaydedilmeyen_alanlar_varsayilanda_kalir(dizin):
    ayar_kaydet("ali", "tema", "dark", dizin)
    ayarlar = ayarlari_getir("ali", dizin)
    assert ayarlar["sayfa_boyutu"] == varsayilanlar()["sayfa_boyutu"]


def test_toplu_yazma(dizin):
    sonuc = ayarlari_yaz(
        "ali", {"tema": "light", "sayfa_boyutu": 100, "yogun_mod": True}, dizin
    )
    assert sonuc["tema"] == "light"
    assert sonuc["sayfa_boyutu"] == 100
    assert sonuc["yogun_mod"] is True


def test_toplu_yazma_hepsi_ya_hic(dizin):
    """Bir değer geçersizse hiçbiri yazılmamalı."""
    ayar_kaydet("ali", "tema", "dark", dizin)
    with pytest.raises(AyarHatasi):
        ayarlari_yaz("ali", {"tema": "light", "sayfa_boyutu": 99999}, dizin)
    assert ayarlari_getir("ali", dizin)["tema"] == "dark"


def test_kullanicilar_izole(dizin):
    ayar_kaydet("ali", "tema", "light", dizin)
    ayar_kaydet("veli", "tema", "dark", dizin)
    assert ayarlari_getir("ali", dizin)["tema"] == "light"
    assert ayarlari_getir("veli", dizin)["tema"] == "dark"


def test_sifirla_varsayilana_doner(dizin):
    ayar_kaydet("ali", "tema", "light", dizin)
    ayarlari_sifirla("ali", dizin)
    assert ayarlari_getir("ali", dizin) == varsayilanlar()


def test_sifirla_dosya_yokken_cokmez(dizin):
    assert ayarlari_sifirla("hic_yok", dizin) == varsayilanlar()


def test_bozuk_json_cokmez(dizin):
    dizin.mkdir(parents=True, exist_ok=True)
    (dizin / "ali.json").write_text("{bozuk json", encoding="utf-8")
    assert ayarlari_getir("ali", dizin) == varsayilanlar()


def test_json_liste_ise_cokmez(dizin):
    dizin.mkdir(parents=True, exist_ok=True)
    (dizin / "ali.json").write_text("[1, 2, 3]", encoding="utf-8")
    assert ayarlari_getir("ali", dizin) == varsayilanlar()


def test_eski_bilinmeyen_anahtar_atilir(dizin):
    dizin.mkdir(parents=True, exist_ok=True)
    (dizin / "ali.json").write_text(
        json.dumps({"tema": "light", "kaldirilmis_ayar": 42}), encoding="utf-8"
    )
    ayarlar = ayarlari_getir("ali", dizin)
    assert ayarlar["tema"] == "light"
    assert "kaldirilmis_ayar" not in ayarlar


def test_bozuk_deger_varsayilana_duser(dizin):
    dizin.mkdir(parents=True, exist_ok=True)
    (dizin / "ali.json").write_text(
        json.dumps({"tema": "mor", "sayfa_boyutu": 100}), encoding="utf-8"
    )
    ayarlar = ayarlari_getir("ali", dizin)
    assert ayarlar["tema"] == varsayilanlar()["tema"]
    assert ayarlar["sayfa_boyutu"] == 100


def test_dosya_utf8_ve_turkce_korunur(dizin):
    ayar_kaydet("ali", "saat_dilimi", "Europe/Istanbul", dizin)
    ham = (dizin / "ali.json").read_text(encoding="utf-8")
    assert "Europe/Istanbul" in ham
    json.loads(ham)  # geçerli JSON


def test_gecici_dosya_birakilmaz(dizin):
    ayar_kaydet("ali", "tema", "light", dizin)
    artiklar = [p.name for p in dizin.iterdir() if p.name.endswith(".tmp")]
    assert artiklar == []


# ---------------------------------------------------------------------------
# Güvenlik: kullanıcı kimliği
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "kimlik",
    ["../gizli", "a/b", "a\\b", "", "  ", "x" * 65, "a:b", "nul\x00"],
)
def test_gecersiz_kimlik_reddedilir(kimlik, dizin):
    with pytest.raises(AyarHatasi):
        ayarlari_getir(kimlik, dizin)


@pytest.mark.parametrize("kimlik", ["ali", "ali.veli", "a-b_c", "admin@huginn.co"])
def test_gecerli_kimlik_kabul(kimlik, dizin):
    assert ayarlari_getir(kimlik, dizin) == varsayilanlar()


def test_kimlik_dogrulamasi_yazmada_da_calisir(dizin):
    with pytest.raises(AyarHatasi):
        ayar_kaydet("../kotu", "tema", "light", dizin)


# ---------------------------------------------------------------------------
# Panel sözleşmesi (kaynak metin denetimi — Streamlit çalıştırılmaz)
# ---------------------------------------------------------------------------


def _panel_kaynak() -> str:
    return PANEL_PY.read_text(encoding="utf-8")


def test_panel_dosyasi_var_ve_utf8():
    assert PANEL_PY.exists()
    assert SERVIS_PY.exists()
    _panel_kaynak()


def test_panel_ayarlar_fonksiyonu_var():
    assert "def render_ayarlar_tab(" in _panel_kaynak()


def test_panel_mevcut_karar_defterini_bozmaz():
    assert "def render_decision_tab(" in _panel_kaynak()


def test_panel_servisi_kullanir():
    kaynak = _panel_kaynak()
    assert "from company_master.settings import" in kaynak
    for ad in ("ayarlari_getir", "ayarlari_yaz", "ayarlari_sifirla", "gruplar"):
        assert ad in kaynak


def test_panel_kendi_dogrulamasini_yapmaz():
    """İş kuralları servis katmanında kalmalı; panelde sabit liste olmamalı."""
    kaynak = _panel_kaynak()
    assert "AYAR_SEMASI = " not in kaynak
    assert re.search(r'\["sistem",\s*"dark",\s*"light"\]', kaynak) is None


def test_panel_ayar_hatasini_yakalar():
    kaynak = _panel_kaynak()
    assert "except AyarHatasi" in kaynak


def test_panel_formu_sema_uzerinden_uretir():
    """Elle yazılmış selectbox/checkbox yığını yerine döngü kullanılmalı.

    Sayım yalnızca ayarlar bölgesiyle (``_form_degeri`` → dosya sonu) sınırlıdır;
    Karar Defteri filtreleri (MVP-KD-01) aynı dosyada meşru selectbox kullanır.
    """
    kaynak = _panel_kaynak()
    bolge = kaynak[kaynak.index("def _form_degeri("):]
    assert "for tanim in grup_haritasi[" in bolge
    assert bolge.count("st.selectbox(") <= 1
    assert bolge.count("st.checkbox(") <= 1


def test_panel_misafir_kimligi_tanimli():
    assert "MISAFIR_KIMLIK" in _panel_kaynak()


def test_panel_kacis_karakteri_sizmasi_yok():
    """UX-03'te görülen kaçış karakteri nüksüne karşı bekçi."""
    kaynak = _panel_kaynak()
    assert "\\ " not in kaynak
    assert "\\(" not in kaynak


def test_servis_streamlitten_bagimsiz():
    """Servis katmanı UI'a bağımlı olmamalı (test edilebilirlik)."""
    kaynak = SERVIS_PY.read_text(encoding="utf-8")
    assert "import streamlit" not in kaynak


def test_servis_atomik_yazma_kullanir():
    kaynak = SERVIS_PY.read_text(encoding="utf-8")
    assert "os.replace" in kaynak
