#!/usr/bin/env python3
"""VERI-ENTITY-GRAPH-01: Faz 3 Entity Graph mandal testleri.

SSOT: `yedekler/Huginn Data Insights (HUGIns).txt:756-774`, :779, :837-839, :859-861.
Şema: `migrations/0047_entity_graph.sql`.

Kapsam: üretici mantığı + şema metni. CANLI DB'ye kenar yazılmaz (D-238) —
`kenarlari_yaz()` idempotensligi sahte engine ile denenir.

Kural izleri:
- D-249: ölçülemeyen `strength` → None, 0 değil; şemada DEFAULT 0 yok.
- D-260: boş `evidence` ile kenar yazılamaz.
- D-256/2: tek yazma kapısı — grep'te ikinci INSERT yok.
- D-256/4: mandal kırılarak doğrulanır (teslim özetine yazılır).

KÖPRÜ (D-184 — karar ↔ kod ↔ test):
  Kod   : src/company_master/graph/kenarlar.py
  Şema  : src/company_master/schema/migrations/0047_entity_graph.sql
  SSOT  : yedekler/Huginn Data Insights (HUGIns).txt:756-774, :779, :837-839, :859-861
  Görev : plans/brief_yasu_VERI-ENTITY-GRAPH-01.md
  Hub   : hubs/OSINT_VERI_TOPLAMA_HUB.md
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from company_master.graph.kenarlar import (  # noqa: E402
    EDGE_TYPES_SSOT,
    EDGE_TYPES_V0,
    KANONIK_EDGE_TYPES,
    KENAR,
    KenarHatasi,
    dogrula,
    kenarlari_yaz,
    nace_tamamlayici,
    normalize,
    osb_komsulari,
)

MIGRATIONS = PROJECT_ROOT / "src" / "company_master" / "schema" / "migrations"
SQL_0047 = MIGRATIONS / "0047_entity_graph.sql"
DOWN_0047 = MIGRATIONS / "down" / "0047_entity_graph.down.sql"

A_ID = "11111111-1111-1111-1111-111111111111"
B_ID = "22222222-2222-2222-2222-222222222222"


# --- 1) Yön normalize: (b,a) verilirse (a,b) olur ----------------------------
def test_normalize_yonu():
    a, b = normalize(A_ID, B_ID)
    assert a == A_ID and b == B_ID, f"ters sirada normalize edilmedi: {a}, {b}"
    # ters yön verilirse AYNI sonuç — kenar yönsüzdür
    assert normalize(B_ID, A_ID) == (a, b), "yonsuz kenar iki yonlu degil"
    try:
        normalize("x", "x")
    except KenarHatasi:
        pass
    else:
        raise AssertionError("self-loop reddedilmedi")


# --- 2) Boş evidence reddedilir (D-260) --------------------------------------
def test_bos_evidence_reddedilir():
    for bos in ("", "   ", None):
        try:
            dogrula(KENAR("a", "b", "same_osb", bos, None, "test"))
        except KenarHatasi:
            continue
        raise AssertionError(f"bos evidence kabul edildi: {bos!r}")
    gecerli = KENAR("a", "b", "same_osb", "ayni OSB: Baskent OSB", None, "test")
    assert dogrula(gecerli).evidence == "ayni OSB: Baskent OSB"


# --- 3) Ölçülemeyen strength -> None, 0 değil (D-249) -------------------------
def test_strength_none_degil_sifir():
    sirketler = [
        {"company_id": "c1", "osb_id": "osb-1"},
        {"company_id": "c2", "osb_id": "osb-1"},
    ]
    kenarlar = osb_komsulari(sirketler, osb_adlari={"osb-1": "Baskent OSB"})
    assert len(kenarlar) == 1, f"beklenen 1 kenar, {len(kenarlar)}"
    k = kenarlar[0]
    assert k.strength is None, f"strength None olmali, {k.strength!r} geldi"
    assert k.strength != 0, "strength 0 olmamali (D-249)"
    assert k.evidence == "ayni OSB: Baskent OSB", k.evidence


# --- 4) Kanonik liste dışı edge_type reddedilir -------------------------------
def test_kanonik_disi_edge_type_reddedilir():
    try:
        dogrula(KENAR("a", "b", "ortaklik", "kanit metni", None, "test"))
    except KenarHatasi as exc:
        assert "kanonik liste disi" in str(exc), str(exc)
    else:
        raise AssertionError("kanonik liste disi edge_type kabul edildi")

    assert len(EDGE_TYPES_V0) == 2, "v0'da yalniz 2 tur uretilmeli"
    for t in EDGE_TYPES_V0 + EDGE_TYPES_SSOT:
        assert t in KANONIK_EDGE_TYPES, f"{t} kanonik listede degil"


# --- 5) Aynı kenar iki kez yazılırsa tablo tek satır tutar --------------------
class _SahteSonuc:
    def __init__(self, rowcount):
        self.rowcount = rowcount


class _SahteEngine:
    """`ON CONFLICT DO NOTHING` davranışını taklit eder: aynı anahtar 1 kez."""

    def __init__(self):
        self.satirlar = []
        self._bagli = {}

    def connect(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params):
        anahtar = (params["company_a_id"], params["company_b_id"], params["edge_type"])
        if anahtar in self._bagli:                 # conflict -> hiç yazılmaz
            return _SahteSonuc(0)
        self._bagli[anahtar] = params
        self.satirlar.append(params)
        return _SahteSonuc(1)

    def commit(self):
        pass


def test_idempotent_ayni_kenar_iki_kez():
    kenar = KENAR("a", "b", "same_osb", "ayni OSB: Baskent OSB", None, "test")
    eng = _SahteEngine()
    ilk = kenarlari_yaz([kenar], engine=eng)
    ikinci = kenarlari_yaz([kenar], engine=eng)
    assert ilk == 1, f"ilk yazimda 1 satir bekleniyordu, {ilk}"
    assert ikinci == 0, f"ikinci yazim 0 satir olmali (idempotent), {ikinci}"
    assert len(eng.satirlar) == 1, f"tablo tek satir tutmali, {len(eng.satirlar)}"


# --- 6) OSB üyesi olmayan firma kenar üretmez --------------------------------
def test_osb_uyesiz_kenar_uretmez():
    sirketler = [
        {"company_id": "c1", "osb_id": None},     # OSB üyesi değil
        {"company_id": "c2", "osb_id": "osb-1"},
        {"company_id": "c3", "osb_id": "osb-2"},  # başka OSB
    ]
    assert osb_komsulari(sirketler) == [], "OSB'siz/tekil firma kenari uretilmemeli"
    uc = [{"company_id": f"c{i}", "osb_id": "osb-1"} for i in range(1, 4)]
    assert len(osb_komsulari(uc)) == 3, "3 uyeli 1 OSB -> 3 kenar beklenir"


# --- 7) NACE tamamlayıcılık: üst kod haritası yoksa kenar üretilmez ---------
def test_nace_ust_kodu_yoksa_bos():
    sirketler = [{"company_id": "c1", "nace_code": "25.11"}]
    assert nace_tamamlayici(sirketler) == [], "ust kod haritasi yoksa kenar uretilmemeli"

    sirketler = [
        {"company_id": "c1", "nace_code": "25.11"},
        {"company_id": "c2", "nace_code": "25.62"},
    ]
    kenarlar = nace_tamamlayici(sirketler, nace_ust={"25.11": "C25", "25.62": "C25"})
    assert len(kenarlar) == 1, f"ayni ust kodda 1 kenar beklenir, {len(kenarlar)}"
    assert kenarlar[0].edge_type == "nace_complementary"
    assert kenarlar[0].strength is None, "strength None olmali"
    assert "C25" in kenarlar[0].evidence, kenarlar[0].evidence
    # farklı üst kod -> kenar yok
    assert nace_tamamlayici(
        sirketler, nace_ust={"25.11": "C25", "25.62": "C28"}
    ) == []


# --- 8) Şema metni kuralları (düz metin denetimi, canlı DB gerekmez) --------
def test_sema_kurallari():
    sql = SQL_0047.read_text(encoding="utf-8")
    low = sql.lower()

    assert "companies(company_id)" in low, "FK companies(company_id) olmali (D-245)"
    # YANLI PK yazımı olmamali: yorum satirlarinda "companies(id)" gecebilir,
    # ancak REFERENCES taniminda gecmemeli.
    referanslar = [ln for ln in sql.splitlines()
                   if "references" in ln.lower() and not ln.strip().startswith("--")]
    assert referanslar, "REFERENCES tanimi yok"
    for ln in referanslar:
        assert "companies(company_id)" in ln, f"YANLIS FK: {ln.strip()}"
        assert "companies(id)" not in ln, f"YANLIS PK companies(id): {ln.strip()}"
    # D-249: DEFAULT 0 yasak — yalnizca yorum/COMMENT satirlarinda yazabilir,
    # CREATE TABLE taniminda olamaz. Blok, girintili kolon satirlaridir
    # ( satir satir parse edilir; ")" ile bolmek FK'de kesilirdi ).
    bas = sql.index("CREATE TABLE IF NOT EXISTS company_edges")
    blok = [ln for ln in sql[bas:].splitlines()[1:]
            if ln.startswith("    ") and not ln.strip().startswith("--")]
    blok_sql = "\n".join(blok).lower()
    assert "strength" in blok_sql, "strength kolonu tanimli degil"
    assert "numeric(5,2)" in blok_sql, "strength NUMERIC(5,2) olmali"
    # MANDAL KIRILDI ve GERI ALINDI (D-256/4): strength'a DEFAULT 0 eklendi ->
    # test kirmizi -> DEFAULT 0 kaldirildi -> yesil. Kanit teslim ozetinde.
    assert "default 0" not in blok_sql, "strength DEFAULT 0 yasak (D-249)"
    assert "company_a_id < company_b_id" in sql, "yonsuz kenar CHECK eksik"
    assert "btrim(evidence) <> ''" in sql, "evidence CHECK eksik"
    assert "ck_company_edges_edge_type" in sql, "edge_type CHECK eksik"
    assert "primary key (company_a_id, company_b_id, edge_type)" in low

    for t in KANONIK_EDGE_TYPES:
        assert f"'{t}'" in sql, f"kanonik listede {t} yok"

    down = DOWN_0047.read_text(encoding="utf-8")
    assert "drop table if exists company_edges" in down.lower(), "down DROP eksik"

    # D-256/2: tek yazma kapisi
    kaynak = (PROJECT_ROOT / "src" / "company_master" / "graph" / "kenarlar.py") \
        .read_text(encoding="utf-8").lower()
    assert kaynak.count("insert into company_edges") == 1, \
        "company_edges INSERT'i tek yerde olmali (D-256/2)"
    assert "on conflict do nothing" in kaynak, "idempotenslik (ON CONFLICT) eksik"


# D-265: schema_versions.json yazma kapisi KAPALI, "tarihi kayit"tir (bkz. migrate.py
# TEK_KAPI). Gercek defter `public.schema_migrations` tablosudur; onun mandali
# test_goc_defteri.py::test_defter_semayla_uyusuyor'dadir. Bu dosyadan 0047 bekleyen
# eski test D-265'ten once yazilmisti, bu yuzden kaldirildi.


if __name__ == "__main__":
    testler = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in testler:
        t()
        print(f"[PASS] {t.__name__}")
    print(f"\n[TUM TESTLER GECTI] {len(testler)} test")
