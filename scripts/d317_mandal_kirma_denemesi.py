"""D-317 mandalının KIRILDIĞINI kanıtlar (D-256/4).

Gerçek kuyruk dosyasına geçici olarak kapanmış bir görev için `bekliyor`
tetiki yazar, mandalın kırmızıya döndüğünü ölçer, dosyayı **bit düzeyinde**
geri alır. `finally` bloğu dosyayı her koşulda eski haline döndürür.

Kullanım: python scripts/d317_mandal_kirma_denemesi.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TETIK = os.path.join(KOK, "data", "orchestrator", "triggers", "utku.jsonl")
TEST = os.path.join("tests", "test_tetik_pano_tutarlilik.py")

#: Panoda `done` olan ve tabanda OLMAYAN bir görev — yeni bayat tetik üretir.
SAHTE_GOREV = "DOC-ADMIN-V9-KUTUCUK-24"


def pytest_kos() -> int:
    return subprocess.call(
        [sys.executable, "-X", "utf8", "-m", "pytest", TEST, "-q", "-p", "no:randomly"],
        cwd=KOK,
    )


def main() -> int:
    yedek = os.path.join(tempfile.gettempdir(), "utku.jsonl.d317.yedek")
    shutil.copy2(TETIK, yedek)
    try:
        with open(TETIK, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {"task_id": SAHTE_GOREV, "durum": "bekliyor", "ajan": "utku"},
                    ensure_ascii=False,
                )
                + "\n"
            )
        kod = pytest_kos()
        if kod == 0:
            print("[KIRILMA YOK] mandal sahte bayat tetigi YAKALAMADI - mandal ise yaramaz")
            return 1
        print("[DOGRULANDI] mandal sahte bayat tetigi yakaladi (kirmizi)")
        return 0
    finally:
        shutil.copy2(yedek, TETIK)
        kod2 = pytest_kos()
        print(f"[GERI ALINDI] tetik dosyasi eski haline dondu; mandal kodu={kod2}")
        if kod2 != 0:
            print("[UYARI] geri alma sonrasi mandal yine kirmizi - dosya bozuldu")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
