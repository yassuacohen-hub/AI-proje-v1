# -*- coding: utf-8 -*-
"""D-165 karar kaydi: onay kuyrugu temizligi + Utku/Ihsan 5'er gorev gece zinciri atamasi."""
from __future__ import annotations

from decision_log import log_decision


def main() -> None:
    entry = log_decision(
        title="D-165 Onay Kuyrugu Temizligi + Gece Zinciri Atamasi (Utku/Ihsan)",
        decision="accepted",
        decider="orkestrator",
        reason=(
            "Onay kuyrugunda 5 kayittan sadece 1'i (DASH-UX-02a) gercek bekleyen "
            "teslimdi (digerleri eski reddedildi kayitlari); onaylandi. Kullanici "
            "talebiyle Utku'ya 5 (TEST-AYARLAR-KAPSAM-01, TEST-MERVE-KAPSAM-01, "
            "ORKESTRA-BASLIK-GERIYE-01, SEC-BANDIT-01, DASH-UX-02a-SECTIONS) ve "
            "Ihsan'a 5 (COP-26, BRIF-03, V10-BELGE-01, ORKESTRA-ONAY-KUYRUGU-02, "
            "ADLANDIRMA-GERIYE-01) gorev gece zinciri olarak atandi. Ayrica once "
            "V10-BELGE-01 kanitsiz 'done' yapilmisti (D-66 ihlali), geri 'plan'a "
            "alindi ve sonra kanitla atandi. Pano: 12 acik gorevden 10'u atandi "
            "(doing), 1 plan (DASH-UX-02a), 1 blocked (DASH-UX-02b)."
        ),
        tags=["D-165", "onay-kuyrugu", "gece-zinciri", "utku", "ihsan", "D-66"],
    )
    print(f"[OK] D-165 kaydedildi: {entry['ts']}")


if __name__ == "__main__":
    main()
