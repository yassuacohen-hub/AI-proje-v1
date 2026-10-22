# -*- coding: utf-8 -*-
"""7 strateji gorevini task_board.json'a ekler (BOM korunur, idempotent)."""
import json
from pathlib import Path

P = Path("Huginn Data Insights/data/orchestrator/task_board.json")
raw = P.read_bytes()
bom = raw.startswith(b"\xef\xbb\xbf")
board = json.loads(raw.decode("utf-8-sig"))
mevcut = {t.get("task_id") for t in board}

T = "2026-10-10T23:25:00"
def g(tid, baslik, sahip, onc, dosyalar, bagimlilik=None):
    d = {
        "task_id": tid, "id": tid, "baslik": baslik, "sahip": sahip, "oncelik": onc,
        "durum": "aktif", "baslangic": T, "bitis": None, "dosyalar": dosyalar,
        "not": "Strateji seti (docs/strateji) turevi; PO 2026-10-10: 'apiler hemen yapilabilir'.",
        "source": "ic", "from_agent": "ihsan", "mod": "code",
        "brief": f"plans/brief_{sahip}_{tid}.md",
        "talimat": f"Brif: plans/brief_{sahip}_{tid}.md; Faz A olcum once (D-224/D-238)",
    }
    if bagimlilik:
        d["dependencies"] = bagimlilik
    return d

yeni = [
    g("API-PAKET-SCOPE-01", "[API] Paket -> scope dict + scope_gerekli() Depends + kredi 402 + paket rate-limit -> tests/test_api_scope.py (4s)", "utku", "P0",
      ["src/company_master/paketler.py", "src/company_master/api/scope.py", "src/company_master/api/rate_limiter.py", "tests/test_api_scope.py"]),
    g("API-V1-COMPANY-FRAUD-01", "[API] GET /v1/companies/{vkn} (1 kredi) + POST /v1/fraud-check (3 kredi) -> sunum.py, kimlik_tamligi+tavan zorunlu (6s)", "utku", "P0",
      ["src/company_master/api/routers/v1.py", "web_app.py", "tests/test_api_v1_company.py"], ["API-PAKET-SCOPE-01"]),
    g("VERI-OZELLIK-MATRISI-SIM-01", "[VERI] OZELLIK_MATRISI + PAKET_V2 + RAPOR_KREDI tek kaynak -> fiyat_katalogu(surum) + scripts/paket_simulasyon.py + 4 assert (5s)", "utku", "P1",
      ["src/company_master/paketler.py", "scripts/paket_simulasyon.py", "tests/test_ozellik_matrisi.py"], ["API-PAKET-SCOPE-01"]),
    g("UI-PAKET-ROZET-01", "[UI] Paket sayfasi ozellik rozeti -> var duz / yakinda 'Yakinda aktif - Faz N' / plan gri (2s)", "utku", "P2",
      ["web_dashboard/tabs/paketler.py", "tests/test_paket_rozet.py"], ["VERI-OZELLIK-MATRISI-SIM-01"]),
    g("WEB-SSR-JINJA-KUNYE-01", "[WEB] Halka acik firma kunyesi SSR -> FastAPI + Jinja2 GET /firma/{vkn} HTML + JSON-LD sunucuda, kilitli alan 'Ornek gorunum' (6s)", "utku", "P1",
      ["src/company_master/web/templates/firma.html", "src/company_master/web/public.py", "web_app.py", "tests/test_web_firma_ssr.py"], ["API-V1-COMPANY-FRAUD-01"]),
    g("VERI-OSB-MASTER-LISTE-01", "[VERI] Ankara OSB master 9 -> 15 (OSBUK) -> goc 0060 + uc kopya tek kaynak + osbuk kayit + tests/test_osb_master.py (4s)", "yasu", "P1",
      ["src/company_master/schema/migrations/0060_osb_master_15.sql", "src/company_master/schema/companies.sql", "src/company_master/seed/seed_ankara_osb.py", "src/company_master/engine/source_registry.py", "tests/test_osb_master.py"]),
    g("API-V1-NETWORK-REPORT-01", "[API] GET /v1/companies/{vkn}/network (5 kredi, entity_graph) + /full-report (10 kredi) -> Profesyonel scope (6s)", "yasu", "P1",
      ["src/company_master/api/routers/v1_network.py", "web_app.py", "tests/test_api_v1_network.py"], ["API-PAKET-SCOPE-01", "API-V1-COMPANY-FRAUD-01"]),
]

eklenen = [t for t in yeni if t["task_id"] not in mevcut]
assert all(Path("Huginn Data Insights", t["brief"]).exists() for t in eklenen), "brif eksik (D-66)"
board.extend(eklenen)
out = json.dumps(board, ensure_ascii=False, indent=2) + "\n"
P.write_bytes((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
print("eklendi:", [t["task_id"] for t in eklenen], "toplam:", len(board), "bom:", bom)
