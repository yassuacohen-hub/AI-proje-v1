"""ALTYAPI-SKILL-YAPISI-01 Faz E: SKILL.md havuzu ve Python registry kapisi.

Iki ayri "skill" dunyasi vardi (SKILL.md belgeleri + Python @registry yetenekleri)
ve SKILL.md havuzu 4 klasore daginmisti. Bu test tek kaynak ilkesini mandalla
sikilastirir: kopya olmayacak, olu klasor geri gelmeyecek, paketler import
edilebilir olacak.

D-221 kok mandalinin SKILL.md havuzu karsiligi — o mandal yazildigi gun canli
bir dosyayi yakalayip kirmiziya dusurdu; bu da ayni isi yapar.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]

#: Kanonik SKILL.md havuzu. Bu ajanlar dogrudan okur.
KANONIK = KOK / ".agents" / "skills"

#: Ajan dizinleri -> kanonik havuza junction kurar. Kural: kopya degil.
AJAN_DIZINLERI = (".claude", ".continue", ".roo")


# ---------------------------------------------------------------------------
# 1) Kopya yasagi
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not KANONIK.is_dir(), reason="kanonik skill havuzu yok")
@pytest.mark.parametrize("ajan_dizini", AJAN_DIZINLERI)
def test_ajan_dizininde_kopya_skill_yok(ajan_dizini: str) -> None:
    """Ajan dizinindeki her skill kanonik havuzda da olmali."""
    dizin = KOK / ajan_dizini / "skills"
    if not dizin.is_dir():
        return
    kanonik = {p.name for p in KANONIK.iterdir() if p.is_dir()}
    yabancilar = sorted(
        p.name for p in dizin.iterdir() if p.is_dir() and p.name not in kanonik
    )
    assert not yabancilar, (
        f"{ajan_dizini}/skills icinde kanonik havuzda olmayan skill: {yabancilar}\n"
        "Cozum: skill .agents/skills altinda olmali. SKILL.md havuzu tek "
        "kaynaktir; ajan dizini yalnizca junction ile gosterir."
    )


@pytest.mark.skipif(not KANONIK.is_dir(), reason="kanonik skill havuzu yok")
@pytest.mark.parametrize("ajan_dizini", AJAN_DIZINLERI)
def test_ajan_dizini_bos_klasor_almaz(ajan_dizini: str) -> None:
    """BOS klasor, junction olmayan skill ajani yaniltir.

    Continue'da 5 adet bos klasor birikisti; ajan skill var saniyordu.
    """
    dizin = KOK / ajan_dizini / "skills"
    if not dizin.is_dir():
        return
    boslar = sorted(
        p.name
        for p in dizin.iterdir()
        if p.is_dir() and p.is_junction() is False and not any(p.iterdir())
    )
    assert not boslar, (
        f"{ajan_dizini}/skills icinde bos klasor: {boslar}\n"
        "Cozum: ya junction yap ya da sil. Bos klasor skill varmis izlenimi "
        "uretir ve ajani yanlis yonlendirir."
    )


# ---------------------------------------------------------------------------
# 2) Olu yol / olu klasor yasagi
# ---------------------------------------------------------------------------


def test_kilo_skills_klasoru_yok() -> None:
    """.kilo/skills olusmamali — Kilo Code .agents/skills okur."""
    assert not (KOK / ".kilo" / "skills").is_dir(), (
        ".kilo/skills yeniden olustu. Kilo Code proje dizini .agents/skills "
        "olarak tanimli; ikinci bir havuz carpisma ve olu kod yaratir."
    )


def test_skills_common_klasoru_yok() -> None:
    """skills/common/ toplandi; iki yol birden yasak (D-220 Kural 1)."""
    assert not (KOK / "skills" / "common").is_dir(), (
        "skills/common/ yeniden olustu. Faz D'de tools/ + services/ altina "
        "toplandi. Iki yol birden yasak: ajan hangisini okuyacagini bilmez."
    )


# ---------------------------------------------------------------------------
# 3) Python registry yapi kapisi
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("paket", ["tools", "services", "utils"])
def test_skills_alt_paketleri_import_edilebilir(paket: str) -> None:
    """skills/{tools,services,utils} import edilebilmeli (Faz A regresyonu).

    Faz A oncesi skills.devops ve skills.streamlit sinif bekliyordu, modul
    fonksiyon tanimliyordu -> ImportError. Bu kapı o sessiz kırılmayı yakalar.
    """
    sonuc = subprocess.run(
        [sys.executable, "-c", f"import skills.{paket}; print('OK')"],
        cwd=KOK,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert sonuc.returncode == 0, (
        f"skills.{paket} import edilemedi:\n{sonuc.stderr[-500:]}\n"
        "Cozum: __init__.py disa aktarimlari modul imzalariyla eslesmeli."
    )


def test_registry_yetenekleri_yukleniyor() -> None:
    """Tum alt paketler yuklenince registry bos kalmamali."""
    sonuc = subprocess.run(
        [
            sys.executable,
            "-c",
            "import skills.tools, skills.services, skills.tools.devops, "
            "skills.tools.streamlit; from skills.base import registry; "
            "print(len(registry._skills))",
        ],
        cwd=KOK,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert sonuc.returncode == 0, sonuc.stderr[-500:]
    sayi = int(sonuc.stdout.strip().splitlines()[-1])
    assert sayi >= 30, (
        f"Registry yalniz {sayi} yetenek kaydi. import'lar bir yuklenmiyor "
        "demektir (eski deger: 51)."
    )


# ---------------------------------------------------------------------------
# 4) Birlestirilmis dizin
# ---------------------------------------------------------------------------


def test_skills_index_dosyasi_var() -> None:
    """skills/SKILLS_INDEX.md iki dunyayi birlikte listelemeli."""
    yol = KOK / "skills" / "SKILLS_INDEX.md"
    assert yol.is_file(), (
        "skills/SKILLS_INDEX.md yok. Iki skill dunyasi (Python + SKILL.md) "
        "tek dizinde gorunmezse ajan hangisini arayacagini bilemez."
    )
    metin = yol.read_text(encoding="utf-8")
    assert "Python" in metin and "SKILL.md" in metin
