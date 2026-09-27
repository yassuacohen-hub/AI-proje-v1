# -*- coding: utf-8 -*-
"""D-163 karar kaydi: D-66 Kanit Zorunlulugu Orkestrator Muafiyeti."""
from __future__ import annotations

from decision_log import log_decision


def main() -> None:
    entry = log_decision(
        title="D-163 D-66 Kanit Zorunlulugu: Orkestrator ve Urun Sahibi Muaf",
        decision="accepted",
        decider="orkestrator",
        reason=(
            "D-66 kanit zorunlulugu metni yanlis yazilmisti (orkestrator muaf degil). "
            "Duzeltildi: orkestrator (D-77 pano yetkisi) ve urun sahibi D-66'dan muaftir, "
            "ajanlar icin zorunlu kalir. gorev_at.py cmd_at() icinde aktif orkestratorun "
            "kendine atadigi gorevlerde brief/talimat kontrolu atlanir."
        ),
        tags=["D-66", "D-77", "D-58", "muafiyet", "kanit", "orkestrasyon"],
    )
    print(f"[OK] D-163 kaydedildi: {entry['ts']}")


if __name__ == "__main__":
    main()
