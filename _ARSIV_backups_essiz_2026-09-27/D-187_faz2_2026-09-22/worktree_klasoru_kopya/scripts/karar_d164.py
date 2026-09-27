# -*- coding: utf-8 -*-
"""D-164 karar kaydi: marka denetimi arsiv klasorlerini atlar."""
from __future__ import annotations

from decision_log import log_decision


def main() -> None:
    entry = log_decision(
        title="D-164 Marka Denetimi: Arsiv Klasorleri Tarama Disi",
        decision="accepted",
        decider="orkestrator",
        reason=(
            "test_kok_denetimi_temiz kirildi: _ARSIV_ikiz_2026-09-21 icindeki eski "
            "rapor yasak yazim iceriyordu. ATLANAN_DIZINLER tam-isim eslesmesi "
            "yaptigi icin tarihli arsiv klasorleri (_ARSIV_*) yakalanmiyordu. "
            "marka_denetim.py'ye ATLANAN_ONEKLER=('_ARSIV',) onek kontrolu eklendi. "
            "Arsiv icerigi canli kural denetimine girmez."
        ),
        tags=["D-164", "marka", "denetim", "arsiv", "test"],
    )
    print(f"[OK] D-164 kaydedildi: {entry['ts']}")


if __name__ == "__main__":
    main()
