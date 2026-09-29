# -*- coding: utf-8 -*-
"""PANEL-DURUSTLUK-01 mandallari: panel gercekten oldugundan iyi gorunemez.

Cerceve yok, assert yeter. pre-commit kancasindan gecer.
Kapsam:
  1. Ulasilabilir tavan agirlik setinden TURETILIR (sabit yazilirsa kirilir).
  2. Tavan asla azami puani asamaz.
  3. Kanit kaynagi olmayan NACE etiketsiz sunulamaz.
  4. D-249: "veri yok" 0 gibi gosterilmez.
  5. Panel kaynaklari terk edilmis data_quality_score'u gostermez.
  6. Hicbir test dosyasi olu import yuzunden sessizce toplanamaz olmaz.
"""
import ast
import re
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "src"))

from company_master import sunum  # noqa: E402
from company_master.etl import quality_recalc as qr  # noqa: E402


# --- 1. Tavan turetilmis mi -------------------------------------------------

def test_tavan_agirlik_setinden_turetilir():
    """Agirlik seti degisince tavan da degisir. Sabit yazilirsa bu kirilir."""
    kilitli = {"mersis_number", "trade_registry_number", "nace_code", "tax_office"}
    assert qr.ulasilabilir_tavan(kilitli) == 6.5

    asil = dict(qr.AGIRLIKLAR)
    try:
        # v2 provasi: D-250/3 tax_number 1.5 -> 3.0
        qr.AGIRLIKLAR["tax_number"] = 3.0
        assert qr.ulasilabilir_tavan(kilitli) == 8.0, \
            "tavan agirlik setini izlemiyor -> sabit yazilmis"
        # Kilit kalkinca tavan yukselir: gercek ilerleme bu.
        assert qr.ulasilabilir_tavan(kilitli - {"mersis_number"}) == 9.0
    finally:
        qr.AGIRLIKLAR.clear()
        qr.AGIRLIKLAR.update(asil)

    assert qr.ulasilabilir_tavan(kilitli) == 6.5, "geri alma basarisiz"


def test_azami_de_turetilir():
    assert qr.AZAMI == round(sum(qr.AGIRLIKLAR.values()), 1) == 10.0


def test_tavan_azamiyi_asamaz():
    assert qr.ulasilabilir_tavan(set()) == qr.AZAMI
    for kilitli in (set(), {"tax_office"}, {"nace_code", "address"},
                    set(qr.AGIRLIKLAR)):
        t = qr.ulasilabilir_tavan(kilitli)
        assert 0.0 <= t <= qr.AZAMI, f"tavan aralik disi: {t}"
    assert qr.ulasilabilir_tavan(set(qr.AGIRLIKLAR)) == 0.0


def test_bilinmeyen_alan_sessizce_yutulmaz():
    try:
        qr.ulasilabilir_tavan({"uydurma_alan"})
    except ValueError:
        return
    raise AssertionError("agirlik setinde olmayan alan sessizce kabul edildi")


def test_kilitli_alanin_gerekcesi_yazili():
    """D-257: kilit gerekcesi okunabilir olacak."""
    kilitli = {"mersis_number": 1.0, "nace_code": 1.0}
    satirlar = sunum.kilit_satirlari(kilitli)
    assert len(satirlar) == 2
    for s in satirlar:
        assert s["gerekce"].strip(), f"gerekce bos: {s['alan']}"
        assert s["kayip_puan"] > 0


# --- 2. Puan sunumu --------------------------------------------------------

def test_puan_tavansiz_sunulamaz():
    """D-250/7: panelde puan tek basina cikamaz."""
    metin = sunum.puan_metni(3.71, 6.5)
    assert "3.71" in metin and "6.50" in metin and "ulaşılabilir" in metin
    assert "10" not in metin, "puan azami 10 olcegiyle sunuluyor"


def test_bayat_puan_etiketlenir():
    assert "bayat" in sunum.puan_metni(3.71, 6.5, "v0")
    assert "bayat" not in sunum.puan_metni(3.71, 6.5, qr.SURUM)


def test_veri_yok_sifir_gibi_gosterilmez():
    """D-249: NULL -> 0 donusumu yasak."""
    assert sunum.puan_metni(None, 6.5) == sunum.BOS
    assert sunum.bos_veya(None) == sunum.BOS
    assert sunum.bos_veya("  ") == sunum.BOS
    assert sunum.bos_veya(0) == "0", "gercek 0 bos sayilmamali"
    assert sunum.BOS != "0"


# --- 3. NACE etiketi -------------------------------------------------------

def test_tahmin_nace_etiketsiz_sunulamaz():
    """D-252/2: kanit kaynagi olmayan kod 'tahmini sektör' etiketi alir."""
    for kaynak in ("sector_default", "unknown", "fallback", "title_default",
                   "invalid_cleared", "predicted", None, ""):
        metin = sunum.nace_metni("29.10", kaynak)
        assert sunum.TAHMIN_ETIKETI in metin, f"etiketsiz sunuldu: {kaynak!r}"
    for kaynak in qr.NACE_KANIT_KAYNAKLARI:
        assert sunum.nace_metni("29.10", kaynak) == "29.10"


def test_kodsuz_nace_bos_gosterilir():
    assert sunum.nace_metni(None, "mersis") == sunum.BOS
    assert sunum.nace_metni("", "sector_default") == sunum.BOS


def test_tahmin_kutlesi_sektor_sayacina_girmez():
    """D-252/5: 29.10 kutlesi sektor dagilimini sismanlatamaz."""
    satirlar = ([("29.10", "sector_default")] * 1876
                + [("62.09", "fallback")] * 654
                + [("25.11", "mersis")] * 2
                + [(None, "mersis")])
    s = sunum.sektor_sayaci(satirlar)
    assert s["kanitli"] == {"25.11": 2}
    assert s["tahmin_haric"] == 1876 + 654
    assert "29.10" not in s["kanitli"], "tahmin kutlesi sayaca sizdi"
    assert s["kanitli_toplam"] == 2


def test_tahmin_kutlesi_ekranda_ilan_edilir():
    """Sayactan cikarmak yetmez: kullanici NICIN dustugunu gormeli.

    Parametreyi alip gostermemek yalanin devamidir --- kapsam orani sebepsiz
    dusuk gorunur. ``tahmin_haric`` bir ``st.*`` cagrisinin icinde gecmeli.
    """
    kaynak = (KOK / "web_dashboard/tabs/pazarlama.py").read_text("utf-8")
    kart = next(
        d for d in ast.walk(ast.parse(kaynak))
        if isinstance(d, ast.FunctionDef) and d.name == "_render_kapsam_karti"
    )
    assert "tahmin_haric" in {a.arg for a in kart.args.args}, "parametre kayboldu"
    ilan = [
        c for c in ast.walk(kart)
        if isinstance(c, ast.Call)
        and isinstance(c.func, ast.Attribute)
        and isinstance(c.func.value, ast.Name)
        and c.func.value.id == "st"
        and any(isinstance(n, ast.Name) and n.id == "tahmin_haric"
                for a in c.args for n in ast.walk(a))
    ]
    assert ilan, "tahmin_haric hesaplaniyor ama ekrana basilmiyor"


# --- 4. Panel kaynaklari ---------------------------------------------------

# Terk edilmis kolon: 0-100 olcekli, tek kapinin yazmadigi puan.
_TERK = "data_quality_score"
_PANEL_KOKLERI = ("web_dashboard", "scripts/dashboard.py", "web_app.py")


# D-259: mandal yalniz *.py tarariyordu; panel yalani (app.js'in olu kolonu
# okumasi) tam bu delikten gecti. Kullaniciya ekran basan her uzanti taranir.
_PANEL_UZANTILARI = ("*.py", "*.js", "*.html")


def _panel_dosyalari():
    for kok in _PANEL_KOKLERI:
        p = KOK / kok
        if p.is_file():
            yield p
        elif p.is_dir():
            for desen in _PANEL_UZANTILARI:
                yield from p.rglob(desen)


def test_tek_kapi_terk_edilmis_kolona_yazmaz():
    kaynak = (KOK / "src/company_master/etl/quality_recalc.py").read_text("utf-8")
    assert _TERK not in kaynak
    assert "identity_completeness = v.s" in kaynak


def test_panel_terk_edilmis_kolonu_gostermez():
    """Panel tek kapinin yazdigi kolonu gosterir; 0-100'luk bayat kolonu degil."""
    suclular = [str(p.relative_to(KOK)) for p in _panel_dosyalari()
                if _TERK in p.read_text("utf-8", errors="replace")]
    assert not suclular, (
        f"{len(suclular)} panel dosyasi hala '{_TERK}' (0-100, bayat) gosteriyor: "
        + ", ".join(sorted(suclular))
    )


def _ekran_metinleri(kaynak: str):
    """Kullaniciya GIDEN dize sabitlerini verir: ``(satir_no, metin)``.

    Metin taramasi yerine AST: ``pct / 100`` yuzde normalizasyonudur, yorum
    satiri aciklamadir; ikisi de yalan degil. Yalan yalniz ekrana basilan
    dizede durur. Docstring'ler de dislanir (kendi duzeltme notumuzu
    suclamasin).
    """
    agac = ast.parse(kaynak)
    docstringler = set()
    for d in ast.walk(agac):
        gövde = getattr(d, "body", None)
        if isinstance(gövde, list) and gövde and isinstance(gövde[0], ast.Expr):
            ilk = gövde[0].value
            if isinstance(ilk, ast.Constant) and isinstance(ilk.value, str):
                docstringler.add(id(ilk))
    for d in ast.walk(agac):
        if (
            isinstance(d, ast.Constant)
            and isinstance(d.value, str)
            and id(d) not in docstringler
        ):
            yield d.lineno, d.value


def _metin_satirlari(kaynak: str):
    """JS/HTML icin AST yok; yorum satirlari disinda ham satirlar taranir."""
    for no, satir in enumerate(kaynak.splitlines(), 1):
        if not satir.lstrip().startswith(("//", "<!--", "*")):
            yield no, satir


def test_panelde_bolu_yuz_olcegi_yazmaz():
    """'/100' metni kimlik tamligi (0-10) icin yalandir."""
    desen = re.compile(r"/\s*100\b")
    suclular = []
    for p in _panel_dosyalari():
        kaynak = p.read_text("utf-8", errors="replace")
        # D-259: AST yalniz Python'da calisir; JS/HTML satir bazli taranir.
        uret = _ekran_metinleri if p.suffix == ".py" else _metin_satirlari
        for no, metin in uret(kaynak):
            if desen.search(metin) and "width_bucket" not in metin:
                suclular.append(f"{p.relative_to(KOK)}:{no}")
    assert not suclular, "panelde '/100' olcegi: " + ", ".join(sorted(set(suclular)))


# D-266: mandal yalniz panel koklerini tariyordu; perf_monitor.py src/ icinde
# olduğu icin 0-100 esigini iki yil tasidi. Olcek yalani nerede olursa olsun
# yakalanir: 0-10 kolonuna 10'dan buyuk sabit esik uygulayan her satir.
_OLCEK_ESIK = re.compile(r"identity_completeness\s*(?:>=|<=|>|<)\s*(\d+(?:\.\d+)?)")
_OLCEK_KOKLERI = ("src", "scripts", "web_dashboard", "web_app.py")


def test_kimlik_tamligina_yuz_olcekli_esik_uygulanmaz():
    """identity_completeness 0-10'dur; 10'u asan sabit esik olcek yalanidir.

    Esik TAVANDAN turetilmeli (D-258). Sabit 20/40/60/80 yazildiginda butun
    firmalar en dusuk banda duser: olculen 9409/9409 kayit tek bant.
    Turetilen esik ({...} ya da :param) sayi olmadigi icin bu mandaldan gecer.
    """
    suclular = []
    for kok in _OLCEK_KOKLERI:
        p = KOK / kok
        yollar = [p] if p.is_file() else [
            y for d in ("*.py", "*.sql", "*.js", "*.html") for y in p.rglob(d)
        ]
        for y in yollar:
            for no, satir in enumerate(y.read_text("utf-8", errors="replace").splitlines(), 1):
                for sayi in _OLCEK_ESIK.findall(satir):
                    if float(sayi) > 10:
                        suclular.append(f"{y.relative_to(KOK)}:{no} -> {sayi}")
    assert not suclular, (
        "kimlik tamligina (0-10) 100'luk olcek esigi: " + ", ".join(sorted(suclular))
    )


# --- 5b. NACE: sozluk uyeligi kanit degildir (D-287) ------------------------

# Olculdu (2026-09-29): nace_codes sozlugu 3319 satir VAR, ama yetim kod = 0 —
# 8289 kodun TAMAMI sozlukte. Yani "sozlukte mi?" sorusu hicbir seyi ayirt
# etmez; puana baglanirsa 8289 TAHMIN koda 1.0 dagitir = puan uydurmak.
# nace_validity ise src'de hic OKUNMUYOR ve nace_source'un aynasidir
# (sector_default->medium 5679, fallback->fallback 654, invalid_cleared->
# unknown 554); 'verified' degeri hic uretilmez. Kanit yalniz nace_source.
_NACE_YASAK = re.compile(r"\bnace_codes\b|\bnace_validity\b|\bnace_level\b")


def test_nace_puani_sozluge_veya_validity_kolonuna_bakmaz():
    """Bicim/sozluk dogrulamasi kanit degildir: kaynak dogrular, sekil dogrulamaz."""
    kaynak = (KOK / "src" / "company_master" / "etl" / "quality_recalc.py").read_text("utf-8")
    bulgu = sorted(set(_NACE_YASAK.findall(kaynak)))
    assert not bulgu, (
        "puan kapisi NACE'yi sekil/sozluk ile dogruluyor: " + ", ".join(bulgu)
        + " — olculdu: yetim kod 0, sozluk hicbir seyi ayirt etmiyor (D-287)"
    )


def test_nace_kanit_kaynaklari_tahmin_etiketi_tasimaz():
    """Tahmin kaynagi kanit setine sizarsa 8289 tahmin koda puan akar (D-287)."""
    tahminler = {"sector_default", "title_default", "fallback",
                 "invalid_cleared", "unknown", "predicted"}
    sizan = tahminler & set(qr.NACE_KANIT_KAYNAKLARI)
    assert not sizan, f"tahmin kaynagi kanit sayildi: {sorted(sizan)}"


# --- 6. Olu import sessizce dosya oldurmesin --------------------------------

def test_hicbir_test_dosyasi_olu_import_tasimaz():
    """Tek bayat ``from ... import X`` tum dosyayi toplanamaz yapar.

    Bu hata pytest'te ``error`` sayilir, ``failed`` degil; ozet satirina bakan
    CI yesil gorunebilir. Bu oturumda iki dosya (218 + 384 satir) boyle
    sessizce oluydu. Dogru olcut cikis kodudur, ozet metni degil.
    """
    sonuc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider"],
        cwd=KOK, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=600,
    )
    assert sonuc.returncode == 0, (
        "test toplama hata verdi (olu import olabilir):\n"
        + (sonuc.stdout or "")[-3000:]
    )


if __name__ == "__main__":
    for ad, fn in sorted(globals().items()):
        if ad.startswith("test_"):
            fn()
            print(f"  OK {ad}")
    print("PANEL-DURUSTLUK-01 mandallari gecti")
