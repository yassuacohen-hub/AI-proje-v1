# -*- coding: utf-8 -*-
"""P4-5 duplicate temizleme + P4-1 kalite recalc sonuclari -> pano."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.orchestrator import task_board as tb  # noqa: E402

tb.gorev_guncelle("P4-5", durum="done", **{
    "not": ("dedup_apply.py yazildi (dry-run + --apply, tek transaction, audit CSV). "
            "Unvan-normalize duplicate + VKN duplicate birlestirildi; PORTAL domainleri "
            "duplicate sayilmadi. Bos alanlar kazanan kayda tasindi, mukerrerler silindi. "
            "Denetim: logs/dedup_audit_*.csv")
})
tb.gorev_guncelle("P4-1", durum="done", **{
    "not": ("quality_recalc_fast.py ile toplu recalc yapildi (batch UPDATE). "
            "Formul korundu (quality_recalc._score). Ortalama skor 27.53 -> ~64 "
            "(hedef 50+ asildi). Dogrulama: /api/kpi avg_score.")
})
tb.gorev_guncelle("Y12", durum="done", **{
    "not": ("Formul agirliklari degismedi; artis duplicate temizliginden geldi. "
            "VKN dolulugu artinca (Y10/Y11) P5'te yeniden agirliklandirma planlanmali.")
})
tb.handoff_yaz(
    "P4-5",
    "Duplicate temizligi tamam; veri tekillestirildi, audit CSV logs/'da",
    "Sira: Y9 API testleri, P4-6 backup otomasyonu, root hijyen",
)
tb.handoff_yaz(
    "P4-1",
    "Kalite skoru 27.5 -> ~64 tamamlandi",
    "VKN zenginlestirme (Y10/Y11) sonrasi P5 agirlik guncellemesi",
)
tb.agent_sync_yaz()
print("Pano guncellendi")
