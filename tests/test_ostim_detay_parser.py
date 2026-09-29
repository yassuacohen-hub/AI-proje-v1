"""D-286 OSTIM detay parser fixture testleri (canli ag YOK).

Neden: D-283'te parser "duzeltildi" ama TEKRAR KOSULMADI. Tek canli
kosuda dogru sonuc verdi; kaynak kodda regresyon olup olmadigi
BILINMIYORDU. Bu testler sabit HTML parcalariyla calisir.

Kapsam:
  1. Firma bilgisi bloklari dogru ayiklaniyor
  2. Menu/footer/site bilgisi KOLONLARA KARIŞMIYOR (K-2, D-283)
  3. HTML entity'leri cozuluyor (D-283: `Demir ├çelik` hatasi)
  4. Maskeli alan kopyalanmiyor (P-10)
  5. P-8 imza fonksiyonu ayni/a farkli sayfayi ayirt ediyor

Kullanim: python -m pytest tests/test_ostim_detay_parser.py -v
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]
SP = KOK / "scripts" / "ostim_detay_tamamla.py"


def _mod():
    spec = importlib.util.spec_from_file_location("ostim_detay", SP)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def t():
    return _mod()


#: Gercek sayfa yapisindan olculerek hazirlanmis fixture (D-283).
#:
#: ONEMLI: Gercek yapi duz metin DEGIL, `bg-light` kutusunun ICINDE
#: `<strong>Etiket</strong>` + `<p class="m-0 fw-5">deger</p>` zinciri
#: kullanir. Ilk yazimda fixture yanlis yapiyi taklit ediyordu ve
#: adres/telefon testleri dustu — dogru sonuc: fixture hataliydi.
#:
#: Bloklar `bg-secondary` baslikli, icerikleri `bg-light` kutulu.
GERCEK_HTML = """
<html><body>
  <!-- MENU: K-2 karisikligi testi icin burada -->
  <nav><a href="/firmalar">Firmalar</a> <a href="/kurumsal">Kurumsal</a></nav>

  <div class="card">
    <h1>Demir Çelik Sanayi A.Ş.</h1>

    <p class="bg-secondary fw-bold small">Merkez</p>
    <div class="p-2 bg-light mb-2 small">
      <strong>Telefon</strong> <p class="m-0 fw-5">0312 385 40 00</p>
      <strong>Adres</strong>   <p class="m-0 fw-5">
        OST&#x130;M OSB, 100. Y&#x131;l Bulvar&#x131; No:5 Ankara</p>
      <strong>E-Posta</strong> <p class="m-0 fw-5">
        <a href="mailto:info@demircelik.com.tr">info@demircelik.com.tr</a></p>
    </div>

    <p class="bg-secondary fw-bold small">Web Site</p>
    <div class="p-2 bg-light mb-2 small">
      <p class="m-0 fw-5">https://www.demircelik.com.tr</p>
    </div>

    <p class="bg-secondary fw-bold small">Sektör</p>
    <div class="p-2 bg-light mb-2 small">
      <p class="m-0 fw-5">Metal ve Metal İşleme Çeşitli</p>
    </div>
  </div>

  <!-- FOOTER: K-2 karisikligi testi icin burada -->
  <footer>
    <a href="https://www.facebook.com/OstimOSB">Facebook</a>
    <a href="https://x.com/ostimosb">X</a>
    <a href="http://www.htk.org.tr">HTK</a>
    <a href="https://www.ostim.org.tr">OSTİM</a>
  </footer>
</body></html>
"""


# --- 1. DOGRU AYIKLAMA ---------------------------------------------

def test_unvan_ayiklanir(t):
    k = t.detay_ayikla(GERCEK_HTML, "demir-celik")
    assert k["unvan"] == "Demir Çelik Sanayi A.Ş."


def test_adres_ayiklanir(t):
    k = t.detay_ayikla(GERCEK_HTML, "demir-celik")
    assert "100" in (k["adres"] or "")
    assert "Ankara" in (k["adres"] or "")


def test_telefon_ve_eposta(t):
    k = t.detay_ayikla(GERCEK_HTML, "demir-celik")
    tel = " ".join(k["telefonler"] or [])
    assert "385" in tel
    ep = " ".join(k["emailler"] or [])
    assert "demircelik.com.tr" in ep


# --- 2. K-2 KOLON KARIŞMASI (D-283'ün asil hatasi) ----------------

def test_footer_sosyal_medya_karismaz(t):
    """OSTIM'in kendi hesaplari firma sosyal medyasi OLMAZ."""
    k = t.detay_ayikla(GERCEK_HTML, "demir-celik")
    sm = json_dumps(k["sosyal_medya"])
    assert "OstimOSB" not in sm
    assert "ostimosb" not in sm.lower()


def test_footer_htk_sitesi_karismaz(t):
    """`htk.org.tr` fuar sitesidir, firma web sitesi DEGILDIR."""
    k = t.detay_ayikla(GERCEK_HTML, "demir-celik")
    assert "htk.org.tr" not in (k["web_sitesi"] or "")


def test_menu_linkleri_alana_girmez(t):
    k = t.detay_ayikla(GERCEK_HTML, "demir-celik")
    web = (k["web_sitesi"] or "")
    assert "/kurumsal" not in web
    assert "ostim.org.tr" != web


# --- 3. HTML ENTITY (D-283: `Demir ├çelik`) -----------------------

def test_entity_cozulur(t):
    k = t.detay_ayikla(GERCEK_HTML, "demir-celik")
    # Ham HTML'de &#x130; vardi -> gercek metin "İ" olmali
    assert "├" not in (k["adres"] or "")
    assert "Çelik" in k["unvan"]


def test_duz_harfleri_temizler(t):
    assert t.duz("a &amp; b") == "a & b"
    assert t.duz("<p>x</p>") == "x"
    assert t.duz("<script>var x=1</p>y") .endswith("y")


# --- 4. P-10 MASKELEMI ALAN ---------------------------------------

def test_maskeli_deger_kirptili(t):
    assert t.maskeli_mi("0312 *** ** 00") is True
    assert t.maskeli_mi("0312 385 40 00") is False


# --- 5. P-8 IMZA AYIRIMI ------------------------------------------

def test_imza_ayni_sayfada_ayni(t):
    assert t.imza(GERCEK_HTML) == t.imza(GERCEK_HTML)


def test_imza_farkli_sayfada_farkli(t):
    diger = GERCEK_HTML.replace("Demir Çelik", "Başka Firma")
    assert t.imza(GERCEK_HTML) != t.imza(diger)


def test_imza_script_degisince_degisir(t):
    """Script icerigi degisse bile govde ayniysa imza ayni kalmali.

    Aksi halde her sayfa farkli sayilir ve P-8 guard ise yaramaz.
    """
    a = "<html><body><p>X</p><script>var a=1</script></body></html>"
    b = "<html><body><p>X</p><script>var a=2</script></body></html>"
    assert t.imza(a) == t.imza(b)


def test_gercek_hesap_mi_pilot_sahtesi(t):
    """D-286 pilot kirpi: `{"instagram": "accounts"}` uretilmemeli.

    Regex dogru olsa bile sayfadaki gecici-login linki
    (`/accounts/login/?next=`) sahte hesap uretir.
    """
    assert t._gercek_hesap_mi("accounts") is False
    assert t._gercek_hesap_mi("login") is False
    assert t._gercek_hesap_mi("sharer") is False
    assert t._gercek_hesap_mi("x") is False         # 1 harf
    assert t._gercek_hesap_mi("ostimosb") is False  # sitenin hesabi
    assert t._gercek_hesap_mi("ostim_osb") is False


def test_gercek_hesap_mi_gecerli_adlar(t):
    assert t._gercek_hesap_mi("333Reklam") is True
    assert t._gercek_hesap_mi("senkronplastik") is True
    assert t._gercek_hesap_mi("4n") is True          # 2 harf = gecerli


def test_pilot_sahtesi_kutuya_girmez(t):
    """Sahte deger kayda hic yazilmamali."""
    html = GERCEK_HTML.replace(
        "</footer>",
        '<a href="https://www.instagram.com/accounts/login/?next=%2Fx">i</a>'
        "</footer>")
    k = t.detay_ayikla(html, "demir-celik")
    assert k["sosyal_medya"] == {} or "accounts" not in str(
        k["sosyal_medya"])


# --- 6. KAYNAK KOLONLARI (K-2) -----------------------------------

def test_kaynak_kolonlari_dolu(t):
    k = t.detay_ayikla(GERCEK_HTML, "demir-celik")
    assert k["kaynak_adi"] == "ostim"
    assert k["kaynak_turu"] == "osb"
    assert k["slug"] == "demir-celik"


def test_vergi_no_hic_doldurulmaz(t):
    """D-282: OSTIM'de VKN YOKTUR; parser uydurmamalidir."""
    k = t.detay_ayikla(GERCEK_HTML, "demir-celik")
    assert k["vergi_no"] is None


def json_dumps(x) -> str:
    import json
    return json.dumps(x, ensure_ascii=False)
