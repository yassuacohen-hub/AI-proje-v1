"""Görev panosu yeniden inşa scripti (veri kurtarma).

Kapsam (kullanıcı onayı 2026-09-11):
- 12 mevcut görev (git HEAD'den kurtarılan): task_board.json'da duruyor, dokunulmaz
- 9 aktif/plan görev (AGENT_SYNC.md 20:50:11 kanıtı)
- 10 tamamlanan görev (AGENT_SYNC.md + plans bitiş kanıtı)
- 9R-01 -> done olarak kaydedilir
- İşlem öncesi task_board.json yedeği alınır

Güvenlik: gorev_ekle'ye dosyalar parametresi VERİLMEZ -> yeni dosya kilidi alınmaz,
mevcut file_locks.json (P7-14 -> kariyer_net.py) korunur.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import shutil

from src.company_master.orchestrator.task_board import (
    TASK_BOARD,
    agent_sync_yaz,
    gorev_ekle,
    gorev_getir,
    gorev_guncelle,
    gorev_listesi,
)

# ---- 1) Yedek ----
bak = ROOT / "data" / "orchestrator" / "task_board_backup_20260911_2106.json"
shutil.copy2(TASK_BOARD, bak)
print(f"[1/5] Yedek alindi: {bak}")

# ---- 2) Aktif / Plan görevler (AGENT_SYNC.md 20:50:11) ----
# (task_id, baslik, sahip, oncelik, durum, not)
aktif_plan = [
    ("P7-14", "E2E Pipeline Test — Webhook -> ingest -> kalite",
     "kilo", "P1", "aktif",
     "file_locks.json: kariyer_net.py kilitli (kazi_scraper/P7-14). Pano kurtarmasinda korundu."),
    ("P7-15", "Signal Dashboard / Aggregation — company sinyalleri",
     "kilo", "P2", "plan", ""),
    ("REFACTOR-01", "gorev_guncelle() not keyword argumanini temizle",
     "mimar", "P2", "plan",
     "task_board.py:116. not= yerine **{'not': ...} kullanildi (9R-01 sirasinda dogrulandi)."),
    ("TEST-01", "Review basarisiz senaryo testi ekle",
     "mimar", "P1", "plan", "tests/orchestrator/test_dispatch_review.py"),
    ("VALIDATE-01", "quick_task.py uctan uca validasyonu",
     "external_agent", "P1", "plan", ""),
    ("DOCS-04", "Brief.package() ile brief.py package_brief birlesimi",
     "mimar", "P3", "plan", "models.py:158 + brief.py"),
    ("QT-001", "Test research task",
     "claude_code", "P1", "aktif", ""),
    ("DOCS-05", "Dosya Kilitleme Protokolu Dokumani",
     "mimar", "P2", "plan", ""),
    ("DOCS-06", "Gorev Panosu Kullanim Kilavuzu",
     "mimar", "P3", "plan", ""),
]

# ---- 3) Tamamlanan görevler (AGENT_SYNC.md 20:50:11 + plans bitis) ----
# (task_id, baslik, sahip, oncelik, bitis, not)
tamamlanan = [
    ("P7-12", "Apify Webhook Prod Hardening — Rate limit + retry",
     "kilo", "P1", "2026-09-11",
     "Hardening tamamlandi; lock_birak cagrilmamisti (plans S-04), yeni panoda done."),
    ("P7-13", "MCP -> OSINT Motoru Bridge — ApifyAdapter",
     "kilo", "P1", "2026-09-11", ""),
    ("QTK-01", "Quick Task Wrapper + Harici Ajan Gorev Sarmalayici",
     "mimar", "P1", "2026-09-11", ""),
    ("DOCS-01", "Orchestrator README yaz",
     "mimar", "P1", "2026-09-11T16:28:04", ""),
    ("DOCS-02", "07_harici_ajan_protokolu.md guncelle",
     "mimar", "P1", "2026-09-11T16:29:36", ""),
    ("DOCS-03", "AGENTS.md guncelle (V9/V10 hiyerarsi kurali)",
     "mimar", "P1", "2026-09-11T16:33:50", ""),
    ("RO-02", "Dispatch + Review otomatik test",
     "cursor_grok", "P2", "2026-09-11", ""),
    ("LIVE-01", "Canli Test: Dispatch + Review Akisi",
     "cursor_grok", "P1", "2026-09-11", ""),
    ("ROO-01", "Roo Code - Kod Incelemesi ve Refactoring",
     "roo_code", "P2", "2026-09-11", ""),
    ("9R-01", "9Router AI Gateway entegrasyonu (env + istemci + smoke test)",
     "roo_code", "P1", "2026-09-11",
     "env kuruldu, gateway/ninerouter_client.py olusturuldu, health/chat/embed dogrulandi."),
]

# ---- 4) Kayit ----
eklenen, atlanan, hatali = 0, 0, 0
for tid, baslik, sahip, oncelik, durum, notlar in aktif_plan:
    if gorev_getir(tid):
        print(f"  MEVCUT (atlandi): {tid}")
        atlanan += 1
        continue
    try:
        gorev_ekle(tid, baslik, sahip, oncelik=oncelik, from_agent="roo_code")
        gorev_guncelle(tid, durum=durum, **{"not": notlar} if notlar else {})
        eklenen += 1
        print(f"  EKLENDI: {tid} [{durum}]")
    except Exception as e:  # noqa: BLE001
        print(f"  HATA {tid}: {e}")
        hatali += 1

for tid, baslik, sahip, oncelik, bitis, notlar in tamamlanan:
    if gorev_getir(tid):
        print(f"  MEVCUT (atlandi): {tid}")
        atlanan += 1
        continue
    try:
        gorev_ekle(tid, baslik, sahip, oncelik=oncelik, from_agent="roo_code")
        gorev_guncelle(tid, durum="done", **{"not": notlar} if notlar else {})
        gorev_guncelle(tid, bitis=bitis)
        eklenen += 1
        print(f"  EKLENDI: {tid} [done, bitis={bitis}]")
    except Exception as e:  # noqa: BLE001
        print(f"  HATA {tid}: {e}")
        hatali += 1

# ---- 5) Senkron + dogrulama ----
agent_sync_yaz()
gorevler = gorev_listesi()
du = {"plan": 0, "aktif": 0, "done": 0, "review": 0, "blocked": 0}
for t in gorevler:
    du[t["durum"]] = du.get(t["durum"], 0) + 1

print()  # noqa: T201
print("[5/5] OZET")
print(f"  Eklenen: {eklenen}, Mevcut/atlanan: {atlanan}, Hatali: {hatali}")
print(f"  TOPLAM GOREV: {len(gorevler)}")
print(f"  Dagilim: {du}")
r9 = gorev_getir("9R-01")
print(f"  9R-01 durumu: {r9['durum'] if r9 else 'YOK'} | bitis: {r9.get('bitis') if r9 else '-'}")
kritik = ["P7-14", "REFACTOR-01", "DOCS-04", "QT-001", "9R-01"]
eksik = [k for k in kritik if not gorev_getir(k)]
print(f"  Kritik kontroller: {'TAMAM' if not eksik else 'EKSIK: ' + ','.join(eksik)}")