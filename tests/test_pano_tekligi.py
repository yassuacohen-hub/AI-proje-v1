"""D-222 mandali: gorev panosu tek olacak, kayit kaybolmayacak.

Hastalik: 2026-09-22 ile 2026-09-26 arasinda iki ayri gorev_panosu.md yasadi.
Eskisi 16 gorev tasiyordu, kimse okumuyordu; icindeki WK-02/WK-03 gercek
backlog kayitlari arsive gomulup kaybolmak uzereydi.

Bu test tekrarini engeller.
"""
import json
import pathlib

VAULT = pathlib.Path(__file__).resolve().parents[1]
SSOT = VAULT / "data/orchestrator/task_board.json"
PANO = VAULT / "data/orchestrator/gorev_panosu.md"

# Uretilen/kopya alanlar: worktree, ikiz klasor, yedek. Canli govde disidir.
YOKSAY = {".git", ".kilo", "AI proje v1", "backups", "data_worktree",
          "node_modules", "archive", "worktree klasoru"}


def _canli(p: pathlib.Path) -> bool:
    return not any(k in p.parts for k in YOKSAY)


def test_canli_govdede_tek_pano_var():
    """Ikinci bir gorev_panosu.md = ajanlarin yanlis panoyu okumasi."""
    panolar = [p for p in VAULT.rglob("gorev_panosu.md") if _canli(p)]
    assert panolar == [PANO], (
        f"Canli govdede {len(panolar)} pano var, 1 olmali. "
        f"Bulunan: {[str(p.relative_to(VAULT)) for p in panolar]}"
    )


def test_ssot_duplike_id_tasimaz():
    board = json.loads(SSOT.read_text(encoding="utf-8"))
    ids = [t["task_id"] for t in board]
    dup = {i for i in ids if ids.count(i) > 1}
    assert not dup, f"Duplike gorev ID: {dup}"


def test_arsivlenen_panodaki_kayitlar_ssotta_duruyor():
    """Arsive tasinan pano ID'leri SSOT'ta olmali; yoksa kayit kaybi var."""
    import re
    arsiv = VAULT / "data/orchestrator/archive/gorev_panosu_ESKI_2026-09-22.md"
    if not arsiv.exists():
        return  # arsiv silindiyse kontrol edilecek sey yok
    metin = arsiv.read_text(encoding="utf-8", errors="replace")
    ids = {m.group(1) for m in re.finditer(r"^\|\s*([A-Z][A-Z0-9-]{4,})\s*\|", metin, re.M)}
    ssot = {t["task_id"] for t in json.loads(SSOT.read_text(encoding="utf-8"))}
    kayip = ids - ssot
    assert not kayip, f"Arsivde olup SSOT'ta olmayan gorev: {sorted(kayip)}"


def test_backlog_gorevleri_panoda_gorunur():
    """plan durumundaki gorev Markdown panoda da yazili olmali (Obsidian okumasi)."""
    board = json.loads(SSOT.read_text(encoding="utf-8"))
    plan = [t["task_id"] for t in board if t["durum"] == "plan"]
    metin = PANO.read_text(encoding="utf-8", errors="replace")
    eksik = [i for i in plan if i not in metin]
    assert not eksik, f"SSOT'ta plan olup panoda yazmayan gorev: {eksik}"


if __name__ == "__main__":
    test_canli_govdede_tek_pano_var()
    test_ssot_duplike_id_tasimaz()
    test_arsivlenen_panodaki_kayitlar_ssotta_duruyor()
    test_backlog_gorevleri_panoda_gorunur()
    print("OK  4 mandal gecti")
