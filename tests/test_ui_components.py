# -*- coding: utf-8 -*-
"""UX-01: UI bileşen kütüphanesi regresyon testleri.

Kapsam:
  - Her bileşenin HTML çıktısının beklenen sınıf/nitelikleri taşıması
  - Geçersiz girdilerde `BilesenHatasi`
  - XSS kaçışlama (kullanıcı verisi asla ham gömülmez)
  - Erişilebilirlik nitelikleri (aria-*, role, scope, for/id eşleşmesi)
  - **Ölü CSS / stilsiz sınıf regresyonu** (scripts/_ux01_sinif_dok.py yerine geçer)

Not: Streamlit bağımlılığı yoktur; tüm testler saf HTML üretimi üzerinden çalışır.
"""
from __future__ import annotations

import re

import pytest

from company_master.ui import (
    RENKLER,
    ROLLER,
    SOHBET_ROLLERI,
    TEMA_SUNUMU,
    YARICAPLAR,
    Badge,
    Bilesen,
    BilesenHatasi,
    Button,
    ButtonGroup,
    Card,
    ChatBubble,
    Dropdown,
    Input,
    MetricCard,
    Modal,
    PageHeader,
    Section,
    SectionNav,
    Table,
    ThemeToggle,
    Tooltip,
    TopBar,
    bilesen_css,
    kimlik_uret,
    kok_css,
    stil_etiketi,
    tum_css,
    tema_dogrula,
    tema_karsiti,
)

XSS = "<script>alert('x')</script>"


# --------------------------------------------------------------------------
# Button
# --------------------------------------------------------------------------
def test_button_temel_html():
    cikti = Button("Kaydet").html()
    assert cikti.startswith("<button")
    assert 'class="hg-btn hg-btn-primary hg-btn-md"' in cikti
    assert 'type="button"' in cikti
    assert "Kaydet" in cikti


def test_button_href_ile_link_olur():
    cikti = Button("Git", href="/panel").html()
    assert cikti.startswith("<a")
    assert 'role="button"' in cikti
    assert 'href="/panel"' in cikti
    assert "type=" not in cikti


def test_button_yukleniyor_pasiflestirir_ve_spinner_ekler():
    cikti = Button("Kaydet", yukleniyor=True).html()
    assert "hg-spinner" in cikti
    assert "hg-btn-loading" in cikti
    assert "disabled" in cikti
    assert 'aria-busy="true"' in cikti


def test_button_pasif_href_ile_link_olmaz():
    """Pasif buton link'e dönüşmemeli; yoksa tıklanabilir kalır (erişilebilirlik hatası)."""
    cikti = Button("Git", href="/panel", pasif=True).html()
    assert cikti.startswith("<button")
    assert 'aria-disabled="true"' in cikti


def test_button_bos_metin_hata():
    with pytest.raises(BilesenHatasi):
        Button("   ")


def test_button_gecersiz_varyant_hata():
    with pytest.raises(BilesenHatasi):
        Button("X", varyant="mor")


def test_button_gecersiz_boyut_hata():
    with pytest.raises(BilesenHatasi):
        Button("X", boyut="xxl")


def test_button_xss_kacislar():
    cikti = Button(XSS).html()
    assert "<script>" not in cikti
    assert "&lt;script&gt;" in cikti


# --------------------------------------------------------------------------
# Input
# --------------------------------------------------------------------------
def test_input_label_ve_alan_id_eslesir():
    bilesen = Input("E-posta")
    cikti = bilesen.html()
    assert f'for="{bilesen.alan_id}"' in cikti
    assert f'id="{bilesen.alan_id}"' in cikti


def test_input_hata_durumu_aria_ve_role_yazar():
    bilesen = Input("E-posta", hata="Geçersiz adres")
    cikti = bilesen.html()
    assert 'aria-invalid="true"' in cikti
    assert 'role="alert"' in cikti
    assert "hg-input-message-error" in cikti
    assert f'aria-describedby="{bilesen.alan_id}-yardim"' in cikti


def test_input_yardim_metni_hata_yoksa_gosterilir():
    cikti = Input("Ad", yardim="Kısa yazın").html()
    assert "hg-input-message" in cikti
    assert "hg-input-message-error" not in cikti


def test_input_textarea_tipi():
    cikti = Input("Not", tip="textarea").html()
    assert "<textarea" in cikti
    assert 'rows="4"' in cikti


def test_input_gecersiz_tip_hata():
    with pytest.raises(BilesenHatasi):
        Input("X", tip="renk")


def test_input_bos_etiket_hata():
    with pytest.raises(BilesenHatasi):
        Input("")


def test_input_xss_kacislar():
    cikti = Input("Ad", deger=XSS, yardim=XSS).html()
    assert "<script>" not in cikti


# --------------------------------------------------------------------------
# Dropdown
# --------------------------------------------------------------------------
def test_dropdown_duz_liste_secenekleri():
    cikti = Dropdown("İl", ["Ankara", "İstanbul"]).html()
    assert '<option value="Ankara"' in cikti
    assert "hg-select-field" in cikti


def test_dropdown_cift_liste_ve_secili():
    cikti = Dropdown("İl", [("06", "Ankara"), ("34", "İstanbul")], secili="34").html()
    assert '<option value="34" selected' in cikti


def test_dropdown_coklu_secim():
    cikti = Dropdown("İl", ["a", "b"], secili=["a", "b"], coklu=True).html()
    assert "multiple" in cikti


def test_dropdown_bilinmeyen_secili_deger_hata():
    with pytest.raises(BilesenHatasi):
        Dropdown("İl", ["a"], secili="z")


def test_dropdown_tekli_secimde_coklu_deger_hata():
    with pytest.raises(BilesenHatasi):
        Dropdown("İl", ["a", "b"], secili=["a", "b"])


def test_dropdown_bozuk_secenek_cifti_hata():
    with pytest.raises(BilesenHatasi):
        Dropdown("İl", [("a", "b", "c")])


# --------------------------------------------------------------------------
# Badge
# --------------------------------------------------------------------------
def test_badge_temel():
    cikti = Badge("aktif", varyant="info").html()
    assert 'class="hg-badge hg-badge-info hg-badge-sm"' in cikti


def test_badge_durumdan_bilinen_durum():
    assert Badge.durumdan("done").varyant == "success"
    assert Badge.durumdan("blocked").varyant == "danger"
    assert Badge.durumdan("review").varyant == "warning"


def test_badge_durumdan_bilinmeyen_durum_cokmez():
    """Panoda yeni bir durum çıkarsa arayüz çökmemeli, secondary'ye düşmeli."""
    rozet = Badge.durumdan("yeni_bir_durum")
    assert rozet.varyant == "secondary"
    assert "hg-badge-dot" in rozet.html()


def test_badge_bos_metin_hata():
    with pytest.raises(BilesenHatasi):
        Badge("  ")


# --------------------------------------------------------------------------
# Card / MetricCard
# --------------------------------------------------------------------------
def test_card_bolumleri():
    cikti = Card(baslik="B", icerik="I", altbilgi="A", ikon="*").html()
    assert "hg-card-header" in cikti
    assert "hg-card-body" in cikti
    assert "hg-card-footer" in cikti
    assert "hg-card-icon" in cikti


def test_card_tamamen_bos_hata():
    with pytest.raises(BilesenHatasi):
        Card()


def test_card_ham_html_bayragi():
    guvensiz = Card(icerik="<b>x</b>", ham_html=True).html()
    guvenli = Card(icerik="<b>x</b>").html()
    assert "<b>x</b>" in guvensiz
    assert "&lt;b&gt;" in guvenli


def test_metric_card_turkce_sayi_bicimi():
    cikti = MetricCard("Toplam Firma", 8313, kategori="customer").html()
    assert "8.313" in cikti
    assert "hg-metric-customer" in cikti


def test_metric_card_ondalik_turkce_bicim():
    cikti = MetricCard("Ortalama", 12.5).html()
    assert "12,5" in cikti


def test_metric_card_delta_oklari():
    assert "▲" in MetricCard("m", 1, delta="+12", delta_yonu="yukari").html()
    assert "▼" in MetricCard("m", 1, delta="-3", delta_yonu="asagi").html()


def test_metric_card_gecersiz_kategori_hata():
    with pytest.raises(BilesenHatasi):
        MetricCard("m", 1, kategori="yesil")


def test_metric_card_gecersiz_delta_yonu_hata():
    with pytest.raises(BilesenHatasi):
        MetricCard("m", 1, delta="1", delta_yonu="sag")


# --------------------------------------------------------------------------
# Table
# --------------------------------------------------------------------------
def test_table_bos_durum_mesaji():
    cikti = Table([]).html()
    assert "hg-table-empty" in cikti
    assert "<table" not in cikti


def test_table_basliklar_ve_scope():
    cikti = Table([{"ad": "A", "skor": 1}]).html()
    assert 'scope="col"' in cikti
    assert "hg-table-th" in cikti
    assert "hg-table-td" in cikti


def test_table_sayi_binlik_ayraci():
    assert "8.313" in Table([{"n": 8313}]).html()


def test_table_none_ve_bool_hucreleri():
    cikti = Table([{"a": None, "b": True, "c": False}]).html()
    assert "—" in cikti
    assert "Evet" in cikti
    assert "Hayır" in cikti


def test_table_max_satir_uyarisi():
    cikti = Table([{"a": i} for i in range(5)], max_satir=2).html()
    assert "hg-table-more" in cikti
    assert "3 satır daha var" in cikti


def test_table_gecersiz_hizalama_hata():
    with pytest.raises(BilesenHatasi):
        Table([{"a": 1}], hizalama={"a": "ortala"})


def test_table_sozluk_olmayan_satir_hata():
    with pytest.raises(BilesenHatasi):
        Table([1, 2, 3])


def test_table_max_satir_sifir_hata():
    with pytest.raises(BilesenHatasi):
        Table([{"a": 1}], max_satir=0)


def test_table_dataframe_benzeri_girdi():
    class SahteDF:
        def to_dict(self, orient="records"):
            return [{"a": 1}, {"a": 2}]

    cikti = Table(SahteDF()).html()
    assert "<table" in cikti


def test_table_xss_kacislar():
    cikti = Table([{"ad": XSS}]).html()
    assert "<script>" not in cikti


# --------------------------------------------------------------------------
# Modal
# --------------------------------------------------------------------------
def test_modal_erisilebilirlik_nitelikleri():
    modal = Modal("Onay", "Emin misiniz?")
    cikti = modal.html()
    assert 'role="dialog"' in cikti
    assert 'aria-modal="true"' in cikti
    assert f'aria-labelledby="{modal.baslik_id}"' in cikti


def test_modal_aciklama_describedby_ekler():
    modal = Modal("Onay", "gövde", aciklama="Alt açıklama")
    assert f'aria-describedby="{modal.aciklama_id}"' in modal.html()


def test_modal_baslik_zorunlu():
    with pytest.raises(BilesenHatasi):
        Modal("  ")


def test_modal_gecersiz_boyut_hata():
    with pytest.raises(BilesenHatasi):
        Modal("B", boyut="xl")


def test_modal_aksiyon_bilesen_kabul_eder():
    cikti = Modal("B", "i", aksiyonlar=[Button("Tamam")]).html()
    assert "hg-btn" in cikti


def test_modal_gecersiz_aksiyon_hata():
    with pytest.raises(BilesenHatasi):
        Modal("B", "i", aksiyonlar=[42]).html()


# --------------------------------------------------------------------------
# Tooltip
# --------------------------------------------------------------------------
def test_tooltip_temel_nitelikler():
    ipucu = Tooltip("?", "Açıklama")
    cikti = ipucu.html()
    assert 'role="tooltip"' in cikti
    assert 'tabindex="0"' in cikti
    assert f'aria-describedby="{ipucu.tooltip_id}"' in cikti


def test_tooltip_id_benzersiz():
    assert Tooltip("a", "m").tooltip_id != Tooltip("b", "m").tooltip_id


def test_tooltip_gecersiz_konum_hata():
    with pytest.raises(BilesenHatasi):
        Tooltip("a", "m", konum="ortala")


def test_tooltip_bos_metin_hata():
    with pytest.raises(BilesenHatasi):
        Tooltip("a", "   ")


def test_tooltip_ikon_kisayolu():
    cikti = Tooltip.ikon("Bilgi").html()
    assert "hg-tooltip" in cikti


def test_tooltip_bilesen_tetikleyici_kabul_eder():
    cikti = Tooltip(Badge("aktif"), "Durum").html()
    assert "hg-badge" in cikti


def test_tooltip_xss_kacislar():
    cikti = Tooltip(XSS, XSS).html()
    assert "<script>" not in cikti


# --------------------------------------------------------------------------
# Token / stil katmanı
# --------------------------------------------------------------------------
def test_kok_css_degiskenleri_uretir():
    css = kok_css()
    assert css.startswith(":root")
    assert "--hg-color-primary" in css


def test_stil_etiketi_style_bloguna_sarar():
    assert stil_etiketi().startswith("<style>")


def test_bilesenlerde_hardcoded_renk_yok():
    """Tema değiştirilebilirliği (UX-03) için CSS yalnız token kullanmalı."""
    hex_rx = re.compile(r"#[0-9a-fA-F]{3,8}\b")
    assert not hex_rx.findall(bilesen_css())


def test_tum_css_token_ve_bilesen_birlesimi():
    css = tum_css()
    assert "--hg-color-primary" in css
    assert ".hg-btn" in css


# --------------------------------------------------------------------------
# ADMIN-UI-01: sayfa iskeleti sözleşmeleri
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "metin,beklenen",
    [
        ("Veri Sağlığı Özeti", "veri-sagligi-ozeti"),
        ("İŞ AKIŞI", "is-akisi"),
        ("Çağrı & Şikâyet", "cagri-sikayet"),
        ("   ", "bolum"),
        ("2026 Güncel", "2026-guncel"),
    ],
)
def test_kimlik_uret_turkce_karakter_guvenli(metin, beklenen):
    """Anchor kimliği Türkçe harflerde bozulmamalı (ı/İ NFKD ile düşmez)."""
    assert kimlik_uret(metin) == beklenen


def test_page_header_tek_birincil_aksiyon_zorunlu():
    """Sahip kuralı: aynı ekranda birden fazla birincil buton olamaz."""
    with pytest.raises(ValueError):
        PageHeader(
            "B",
            aksiyonlar=[Button("a"), Button("b")],
        )


def test_page_header_h1_uretir_ve_kacis_yapar():
    html = PageHeader(XSS, XSS, ust_etiket=XSS).html()
    assert "<h1" in html
    assert "<script>" not in html


def test_section_gecersiz_seviye_reddedilir():
    with pytest.raises(ValueError):
        Section("B", seviye=4)


def test_section_kimlik_otomatik_uretilir():
    html = Section("Veri Sağlığı").html()
    assert 'id="veri-sagligi"' in html


def test_section_nav_bos_liste_reddedilir():
    with pytest.raises(ValueError):
        SectionNav([])


def test_section_nav_yinelenen_kimlik_reddedilir():
    with pytest.raises(ValueError):
        SectionNav([("a", "A"), ("a", "B")])


def test_section_nav_anchor_section_kimligiyle_eslesir():
    """Gezinme bağlantısı gerçek bölüm kimliğine gitmeli (kırık anchor yok)."""
    bolum = Section("Veri Sağlığı")
    nav = SectionNav([bolum]).html()
    assert f'href="#{bolum.kimlik}"' in nav
    assert f'id="{bolum.kimlik}"' in bolum.html()


# --------------------------------------------------------------------------
# ADMIN-UI-02: tek buton sistemi sözleşmeleri
# --------------------------------------------------------------------------
@pytest.mark.parametrize("rol,varyant", sorted(ROLLER.items()))
def test_rol_dogru_varyanta_cevrilir(rol, varyant):
    """Semantik rol, tasarım sisteminin varyantına birebir eşlenmeli."""
    assert Button("a", rol=rol).varyant == varyant
    assert f"hg-btn-{varyant}" in Button("a", rol=rol).html()


def test_gecersiz_rol_turkce_hata_verir():
    with pytest.raises(BilesenHatasi):
        Button("a", rol="kirmizi")


def test_rol_varyanti_ezer():
    """Rol verildiğinde `varyant` parametresi yok sayılır (tek kaynak: rol)."""
    assert Button("a", rol="tehlikeli", varyant="success").varyant == "danger"


def test_button_group_tek_birincil_kurali():
    """Sahip kuralı kod seviyesinde zorlanmalı: ekranda tek birincil buton."""
    with pytest.raises(ValueError):
        ButtonGroup([Button("Kaydet", rol="birincil"), Button("Uygula", rol="birincil")])


def test_button_group_bos_liste_reddedilir():
    with pytest.raises(ValueError):
        ButtonGroup([])


def test_button_group_gecersiz_hizalama_reddedilir():
    with pytest.raises(BilesenHatasi):
        ButtonGroup([Button("a", rol="sessiz")], hizalama="orta")


def test_button_group_erisilebilir_grup_rolu_yazar():
    html = ButtonGroup(
        [Button("Kaydet", rol="birincil"), Button("Vazgeç", rol="ikincil")]
    ).html()
    assert 'role="group"' in html
    assert html.count("hg-btn-primary") == 1


# --------------------------------------------------------------------------
# Regresyon: ölü CSS / stilsiz sınıf denetimi
# --------------------------------------------------------------------------
_CLASS_RX = re.compile(r'class="([^"]+)"')
_SELECTOR_RX = re.compile(r"\.(hg-[a-z0-9-]+)")


def _tum_ornekler() -> list[str]:
    """Tüm bileşenlerin anlamlı varyasyonlarını kapsayan HTML örnekleri."""
    ornekler = [
        Button("a", ikon="x", yukleniyor=True).html(),
        Button("a", href="#", tam_genislik=True, varyant="ghost", boyut="lg").html(),
        Button("a", pasif=True, varyant="danger", boyut="sm").html(),
        Input("E", yardim="y", zorunlu=True, tip="textarea").html(),
        Input("E", hata="h", pasif=True, boyut="lg").html(),
        Input("E", boyut="sm", yer_tutucu="p").html(),
        Dropdown("S", ["a", "b"], coklu=True, yardim="y", pasif=True, boyut="lg").html(),
        Dropdown("S", ["a", "b"], secili="a", boyut="sm").html(),
        Badge("x", nokta=True, yumusak=False, boyut="lg").html(),
        Badge("x", varyant="info", boyut="md").html(),
        Card(baslik="b", icerik="i", altbilgi="f", ikon="*", vurgulu=True).html(),
        MetricCard("m", 1, delta="1", delta_yonu="asagi", kategori="system").html(),
        MetricCard("m", 1, delta="1", delta_yonu="notr", aciklama="a", soru="s").html(),
        Table([{"a": 1}] * 3, hizalama={"a": "right"}, yogun=True, zebra=False, max_satir=2).html(),
        Table([{"a": 1}], hizalama={"a": "center"}).html(),
        Table([]).html(),
        Modal("M", "i", aciklama="d", boyut="full", acik=False, kapatilabilir=False).html(),
        Modal("M", "i", boyut="sm", aksiyonlar=[Button("o")]).html(),
        Modal("M", "i", boyut="lg").html(),
        Tooltip("t", "m", konum="right", genis=True).html(),
        Tooltip("t", "m", konum="bottom").html(),
        Tooltip("t", "m", konum="left").html(),
        # ADMIN-UI-01 sayfa iskeleti — tüm opsiyonel parçalar açık
        PageHeader(
            "Başlık",
            "Giriş paragrafı",
            ust_etiket="Grup",
            ikon="🏠",
            aksiyonlar=[Button("Kaydet"), Button("Vazgeç", varyant="ghost")],
        ).html(),
        PageHeader("Yalın başlık").html(),
        Section("Bölüm", "Açıklama", ikon="📊").html(),
        Section("Alt bölüm", seviye=3).html(),
        Section("Ayraçsız", ayrac=False).html(),
        SectionNav([("a", "A"), ("b", "B", 3)]).html(),
        SectionNav([("a", "A"), ("b", "B", 3)], yatay=True).html(),
        SectionNav([Section("Canlı bölüm")]).html(),
        # ADMIN-UI-02 aksiyon kümesi — üç hizalama da kapsanır
        ButtonGroup(
            [Button("Kaydet", rol="birincil"), Button("Vazgeç", rol="ikincil")]
        ).html(),
        ButtonGroup([Button("Sil", rol="tehlikeli")], hizalama="sag").html(),
        ButtonGroup([Button("Yenile", rol="sessiz")], hizalama="arali").html(),
        # ADMIN-UI-03 üst şerit ve tema/sohbet kontrolleri
        TopBar(
            "Sayfa Başlığı",
            ust_etiket="Grup",
            sag=[ThemeToggle(tema="karanlik"), ThemeToggle(tema="aydinlik")],
        ).html(),
        TopBar("Yalın başlık").html(),
        ThemeToggle(tema="karanlik").html(),
        ThemeToggle(tema="aydinlik").html(),
        ChatBubble(acik=False).html(),
        ChatBubble(acik=True, mesajlar=[]).html(),
        ChatBubble(
            acik=True,
            mesajlar=[
                ("ai", "Merhaba! Nasıl yardımcı olabilirim?"),
                ("kullanici", "Sistem hakkında bilgi verir misin?"),
                ("ai", "Tabii, sistem mimari ve teknoloji hakkında her şeyi açıklayabilirim."),
            ],
        ).html(),
        ChatBubble(
            acik=True,
            mesajlar=[{"rol": "ai", "metin": "Sözlük formatı da desteklenir."}],
        ).html(),
    ]
    # Tüm varyant ve boyut kombinasyonları (ölü CSS avı için)
    for varyant in ("primary", "secondary", "success", "warning", "danger", "info", "ghost"):
        ornekler.append(Button("a", varyant=varyant).html())
        ornekler.append(Badge("a", varyant=varyant, boyut="md").html())
    for boyut in ("sm", "md", "lg"):
        ornekler.append(Input("E", boyut=boyut).html())
        ornekler.append(Dropdown("S", ["a"], boyut=boyut).html())
        ornekler.append(Badge("a", boyut=boyut).html())
    for boyut in ("sm", "md", "lg", "full"):
        ornekler.append(Modal("M", "i", boyut=boyut).html())
    for konum in ("top", "bottom", "left", "right"):
        ornekler.append(Tooltip("t", "m", konum=konum).html())
    for kategori in ("customer", "system", "neutral"):
        ornekler.append(MetricCard("m", 1, kategori=kategori).html())
    for yon in ("yukari", "asagi", "notr"):
        ornekler.append(MetricCard("m", 1, delta="d", delta_yonu=yon).html())
    return ornekler


def _uretilen_siniflar() -> set[str]:
    uretilen: set[str] = set()
    for parca in _tum_ornekler():
        for grup in _CLASS_RX.findall(parca):
            uretilen.update(grup.split())
    return uretilen


def test_her_uretilen_sinifin_css_karsiligi_var():
    """HTML'de üretilen her `hg-*` sınıfı CSS'te tanımlı olmalı (stilsiz sınıf yok)."""
    stilsiz = sorted(_uretilen_siniflar() - set(_SELECTOR_RX.findall(bilesen_css())))
    assert not stilsiz, f"CSS karşılığı olmayan sınıflar: {stilsiz}"


def test_olu_css_secici_yok():
    """CSS'te tanımlı her `hg-*` seçicisi bir bileşen tarafından üretilmeli.

    (M-03 eleştirisinin regresyonu: `metric-blue`/`metric-orange` gibi ölü sınıflar.)
    """
    olu = sorted(set(_SELECTOR_RX.findall(bilesen_css())) - _uretilen_siniflar())
    assert not olu, f"Hiçbir bileşenin üretmediği ölü CSS seçicileri: {olu}"


# --------------------------------------------------------------------------
# ADMIN-UI-03: Üst şerit (topbar) ve tema/sohbet kontrolleri
# --------------------------------------------------------------------------


def test_theme_toggle_tema_dogrulama():
    """Geçersiz tema → BilesenHatasi."""
    with pytest.raises(BilesenHatasi):
        ThemeToggle(tema="kirmizi")


def test_theme_toggle_tema_karsiti():
    """Tema karşıtı doğru hesaplanmalı."""
    assert tema_karsiti("karanlik") == "aydinlik"
    assert tema_karsiti("aydinlik") == "karanlik"


def test_theme_toggle_html_role_button_var():
    """Düğme erişilebilirliği: role ve aria-label."""
    html = ThemeToggle(tema="karanlik").html()
    assert 'role="button"' in html
    assert "aria-label" in html


def test_theme_toggle_aria_label_aksiyon_aciklar():
    """`aria-label` tıklamanın **ne yapacağını** söylemeli (statü değil)."""
    html = ThemeToggle(tema="karanlik").html()
    assert "Gündüz moduna geç" in html


def test_theme_toggle_data_tema_niteligi():
    """Tema bilgisi `data-tema` niteliğinde saklanmalı (Streamlit doğrulama için)."""
    html = ThemeToggle(tema="karanlik").html()
    assert 'data-tema="karanlik"' in html
    html = ThemeToggle(tema="aydinlik").html()
    assert 'data-tema="aydinlik"' in html


def test_topbar_bos_baslik_reddedilir():
    """TopBar başlığı zorunludur."""
    with pytest.raises(ValueError):
        TopBar("")
    with pytest.raises(ValueError):
        TopBar("   ")


def test_topbar_bilesenleri_html_cinesi():
    """TopBar `sag` parametresi hem Bilesen nesnelerini hem hazır HTML'i kabul eder."""
    tema = ThemeToggle(tema="karanlik")
    html_str = "<button>Test</button>"
    topbar = TopBar("Başlık", sag=[tema, html_str])
    html = topbar.html()
    assert "hg-topbar" in html
    assert "hg-theme-toggle" in html
    assert "Test" in html


def test_topbar_baslik_kacis_yapar():
    """TopBar başlığı XSS korumalı olmalı."""
    topbar = TopBar(XSS)
    html = topbar.html()
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_chat_bubble_kapalı_fab_olustur():
    """Kapalı ChatBubble yalnız FAB (yüzen buton) çizer."""
    html = ChatBubble(acik=False).html()
    assert "hg-chat-fab" in html
    assert "hg-chat-panel" not in html


def test_chat_bubble_acık_panel_olustur():
    """Açık ChatBubble panel ve başlık/govde/not çizer."""
    html = ChatBubble(acik=True, mesajlar=[]).html()
    assert "hg-chat-panel" in html
    assert "hg-chat-bas" in html
    assert "hg-chat-govde" in html
    assert "hg-chat-not" in html


def test_chat_bubble_geçersiz_rol_reddedilir():
    """Sohbet rolü doğrulanmalı."""
    with pytest.raises(BilesenHatasi):
        ChatBubble(acik=True, mesajlar=[("oto", "Merhaba")])


def test_chat_bubble_mesaj_normalizasyonu():
    """Mesajlar (rol, metin) ikilileri veya sözlükler olabilir."""
    # İkili format
    html1 = ChatBubble(
        acik=True, mesajlar=[("ai", "Selam"), ("kullanici", "Merhaba")]
    ).html()
    # Sözlük format
    html2 = ChatBubble(
        acik=True,
        mesajlar=[
            {"rol": "ai", "metin": "Selam"},
            {"rol": "kullanici", "metin": "Merhaba"},
        ],
    ).html()
    assert "hg-chat-mesaj-ai" in html1
    assert "hg-chat-mesaj-kullanici" in html1
    assert "hg-chat-mesaj-ai" in html2
    assert "hg-chat-mesaj-kullanici" in html2


def test_chat_bubble_bos_govde():
    """Mesaj yoksa bölüm boş mesajı gösterilir."""
    html = ChatBubble(acik=True, mesajlar=[]).html()
    assert "hg-chat-bos" in html
    assert "Henüz mesaj yok" in html


def test_chat_bubble_dialog_role():
    """Açık panel `role="dialog"` olmalı (erişilebilirlik)."""
    html = ChatBubble(acik=True).html()
    assert 'role="dialog"' in html


def test_chat_bubble_varsayilan_not():
    """Not metni verilmezse varsayılan metin gösterilir."""
    html = ChatBubble(acik=True, not_metni=None).html()
    assert ChatBubble.VARSAYILAN_NOT in html


def test_chat_bubble_ozel_not():
    """Özel not metni verilirse onu gösterir."""
    ozel = "Motor bağlandı — tamamen hazır!"
    html = ChatBubble(acik=True, not_metni=ozel).html()
    assert ozel in html
    assert ChatBubble.VARSAYILAN_NOT not in html


def test_chat_bubble_varsayilan_yakinda_rozeti():
    """Motor bağlı olmadığı sürece başlıkta "Yakında" rozeti görünür."""
    html = ChatBubble(acik=True).html()
    assert "hg-chat-rozet" in html
    assert ChatBubble.VARSAYILAN_ROZET in html


def test_chat_bubble_rozet_gizlenebilir():
    """Motor bağlandığında `rozet_metni=""` ile rozet kaldırılabilir."""
    html = ChatBubble(acik=True, rozet_metni="").html()
    assert "hg-chat-rozet" not in html
    assert ChatBubble.VARSAYILAN_ROZET not in html


def test_chat_bubble_rozet_kacis_yapar():
    """Rozet metni HTML kaçışından geçer (XSS regresyonu)."""
    html = ChatBubble(acik=True, rozet_metni="<script>x</script>").html()
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_chat_bubble_fab_rozet_cizmez():
    """Kapalı balon yalnız FAB çizer; rozet panel başlığına aittir."""
    html = ChatBubble(acik=False).html()
    assert "hg-chat-rozet" not in html


def test_chat_bubble_ozel_rozet_metni():
    """Özel rozet metni varsayılanın yerine geçer (motor bağlanınca 'Beta' vb.)."""
    html = ChatBubble(acik=True, rozet_metni="Beta").html()
    assert "Beta" in html
    assert ChatBubble.VARSAYILAN_ROZET not in html


# --------------------------------------------------------------------------
# Ortak sözleşme
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "bilesen",
    [
        Button("a"),
        Input("E"),
        Dropdown("S", ["a"]),
        Badge("b"),
        Card(icerik="i"),
        MetricCard("m", 1),
        Table([{"a": 1}]),
        Modal("M", "i"),
        Tooltip("t", "m"),
        PageHeader("B"),
        Section("S"),
        SectionNav([("a", "A")]),
    ],
)
def test_tum_bilesenler_sozlesmeye_uyar(bilesen):
    """Her bileşen `Bilesen` alt sınıfıdır, str() == html() ve boş çıktı vermez."""
    assert isinstance(bilesen, Bilesen)
    cikti = bilesen.html()
    assert cikti and cikti.startswith("<")
    assert str(bilesen) == cikti


# --------------------------------------------------------------------------
# Copilot UX denetimi sözleşmesi
# (docs/UX_ADMIN_PANEL_REVIEW_2026-09-14.md)
# --------------------------------------------------------------------------
#: Denetim raporunun zorunlu kıldığı semantik renk değerleri.
_ZORUNLU_RENKLER: dict[str, str] = {
    "accent": "#6366f1",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
}

#: Denetim raporunun yarıçap bandı: (alt_sinir_px, ust_sinir_px).
_YARICAP_BANTLARI: dict[str, tuple[int, int]] = {
    "button": (8, 10),
    "card": (12, 16),
    "modal": (16, 20),
}


@pytest.mark.parametrize("anahtar,deger", sorted(_ZORUNLU_RENKLER.items()))
def test_semantik_renk_sozlesmesi(anahtar, deger):
    """UX denetimi paleti (Indigo accent + success/warning/danger) korunmalı."""
    assert RENKLER[anahtar].lower() == deger, (
        f"'{anahtar}' rengi denetim sözleşmesinden saptı: "
        f"{RENKLER[anahtar]} != {deger}"
    )


def test_accent_primary_ile_ayni():
    """`accent` semantik takma adı `primary` ile aynı değeri taşımalı."""
    assert RENKLER["accent"].lower() == RENKLER["primary"].lower()


@pytest.mark.parametrize("anahtar,bant", sorted(_YARICAP_BANTLARI.items()))
def test_yaricap_bandi_sozlesmesi(anahtar, bant):
    """Buton 8-10px, kart 12-16px, modal/drawer 16-20px bandında kalmalı."""
    ham = YARICAPLAR[anahtar]
    assert ham.endswith("px"), f"'{anahtar}' yarıçapı px cinsinden olmalı: {ham}"
    deger = int(ham.removesuffix("px"))
    alt, ust = bant
    assert alt <= deger <= ust, (
        f"'{anahtar}' yarıçapı {deger}px, izinli bant {alt}-{ust}px dışında"
    )


@pytest.mark.parametrize("anahtar", sorted(_YARICAP_BANTLARI))
def test_semantik_yaricap_css_te_kullaniliyor(anahtar):
    """Bileşen CSS'i ham ölçek yerine semantik yarıçap token'ına bağlanmalı."""
    assert f"var(--hg-radius-{anahtar})" in bilesen_css()
