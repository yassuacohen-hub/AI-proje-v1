#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
"""
ADIM 8 — 15-20 Acil Görev Üretimi & Dağıtım
Kaynaklar: ADIM4 (Hub kriterleri), ADIM6 (Admin panel), ADIM7 (Menu ağacı), Arşiv
Çıktı: tasks_generated.json + dağıtım dosyaları
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Başlangıç tarihi: Bugün 2026-09-25 (UTC+3)
NOW = datetime(2026, 9, 25, 11, 30, 0)  # UTC+3: 08:31 → 11:31
SPRINT_DAYS = 8  # 2026-09-25 ~ 2026-10-02 (5 iş günü + 3 gün tampon)

def deadline_for_days(days: int) -> str:
    """n gün sonraki deadline (ISO 8601)"""
    return (NOW + timedelta(days=days)).isoformat() + "Z"

# ============================================================================
# GÖREV DEFİNİSYONLARI (15-20 görev)
# ============================================================================

TASKS = [
    # === UTKU GÖREVLERI (5 adet: UTKU-01 ~ UTKU-05) ===
    {
        "task_id": "UTKU-01",
        "baslik": "[HUB] ADIM4 kriterleri — 10 görevde önem alanı ekle (task_board.json)",
        "aciklama": "ADIM4 denetiminde bulunan 10 görevde (UTKU-11, UTKU-12, UTKU-13, UTKU-14, UTKU-15, UTKU-16, UTKU-17, UTKU-18, UTKU-19, UTKU-20/21) onem alanı (P0/P1/P2) ekle. SSOT: Huginn Data Insights/ADIM4_HUB_KRITERLER_KONTROL.md:69-72 (kritik bulgu). Proof: task_board.json güncellemesi + sanity check script.",
        "oncelik": "P0",
        "durum": "yapilacak",
        "sahip": "utku",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(1),
        "bagimliliklar": [],
        "brief": "plans/brief_utku_ADIM4-ONEM-EKSIK.md",
        "talimat": "task_board.json'da kritik 10 görevde onem alanı (P0/P1) ekle. Sanity check: jq '.[] | select(.onem == null) | .task_id' — boş dönmeli.",
    },
    {
        "task_id": "UTKU-02",
        "baslik": "[TEST] TEST sınıfı görevler için brief dosyaları yaz (UTKU-11, UTKU-14)",
        "aciklama": "ADIM4:75-78'de bulunandan: task_id UTKU-11 (TEST-ADMIN-K2-AGIRLIK-23) ve UTKU-14 (TEST-BLOKE-FAKTOR-ARASTIRMA-01) brief dosyası yok. plans/brief_utku_TEST-K2-AGIRLIK.md + plans/brief_utku_TEST-BLOKE-FAKTOR.md yaz. SSOT: ADIM4_HUB_KRITERLER_KONTROL.md + ADMIN-KIT §7 (brief şablonu).",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "utku",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(2),
        "bagimliliklar": ["UTKU-01"],
        "brief": "plans/brief_utku_TEST-BRIEF-EKSIK.md",
        "talimat": "Brief şablonu: [Görev adı] → [SSOT kaynağı] → [Teknik detay] → [Test adımları] → [Başarı kriteri]. Dosyalara plan/brief_utku_*.md olarak kaydet.",
    },
    {
        "task_id": "UTKU-03",
        "baslik": "[UI] Admin Panel 33 modülü Streamlit ile test et (app.py başlatma)",
        "aciklama": "ADIM6:23'te MANUAL TEST GEREKLI olarak işaretlendi. `streamlit run app.py` ile dashboard başlat, tüm 33 tab modülünün render süresi ölç, network hataları kayıt et. SSOT: Huginn Data Insights/ADIM6_ADMIN_PANEL_KONTROL.md:115-129. Proof: test_report_dashboard_render_UTKU-03.json (render times + errors).",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "utku",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(2),
        "bagimliliklar": [],
        "brief": "plans/brief_utku_ADIM6-DASHBOARD-TEST.md",
        "talimat": "1. Terminal: streamlit run app.py. 2. Her tab tıkla, render süresini ölç (ms). 3. Network tab -> hata kontrol. 4. Rapor: test_report_dashboard_render_UTKU-03.json (tab: str, render_ms: float, errors: list[str]).",
    },
    {
        "task_id": "UTKU-04",
        "baslik": "[UI] Admin Panel UI/UX kontrol — Button, sidebar, modal responsiveness",
        "aciklama": "ADIM6:120-124'de UX denetimi tanımlandı ama yapılmadı. Dashboard'da button responsiveness, sidebar navigasyon akıcılığı, modal/form işlevselliği, veri yükleme göstergesi test et. SSOT: ADIM6_ADMIN_PANEL_KONTROL.md:120-124 (öneriler). Proof: ux_audit_UTKU-04.json (test sonuçları + screenshots).",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "utku",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(3),
        "bagimliliklar": ["UTKU-03"],
        "brief": "plans/brief_utku_ADIM6-UX-AUDIT.md",
        "talimat": "Kontrol listesi: [Button click → state change (0.5s içinde)] [Sidebar expand/collapse smooth] [Modal close button + ESC key] [Loading indicator görünür]. JSON: {checkbox: bool, note: str}. Sorun varsa issue açıkla.",
    },
    {
        "task_id": "UTKU-05",
        "baslik": "[ALTYAPI] Admin Panel — API entegrasyon doğrulaması (web_app.py endpoint'leri)",
        "aciklama": "ADIM6:126-129'da API entegrasyonu doğrulanmadı. web_app.py endpoint'leriyle (GET/POST), authentication flow'u, rate limiting test et. SSOT: ADIM6_ADMIN_PANEL_KONTROL.md:126-129 + web_app.py source. Proof: api_integration_test_UTKU-05.json (200 OK, auth headers, rate limit headers).",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "utku",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(3),
        "bagimliliklar": ["UTKU-03"],
        "brief": "plans/brief_utku_ADIM6-API-INTEGRATION.md",
        "talimat": "curl/Python requests: GET /api/admin/kpi → 200 + JSON. POST /api/admin/log → auth header check + 201. Rate limit test: 100 req/s → 429 kontrol. JSON: {endpoint: str, status: int, latency_ms: float, auth_required: bool}.",
    },
    
    # === YASU GÖREVLERI (5 adet: YASU-01 ~ YASU-05) ===
    {
        "task_id": "YASU-01",
        "baslik": "[UI] ADIM7 menü ağacı — Sistem grubu 9 sekmeden 6'ya küçült",
        "aciklama": "ADIM7:144-150'de Sistem grubu aşırı yüklü (9 sekme). Wireframe hedefi: 6 sekme (Teknik, Performans, API, Webhook, Canlı Veri, Hatalar & DLQ). yenileme, ayarlar, yukleme sekmelerini kaldır (profil popover'a taşın). SSOT: Huginn Data Insights/ADIM7_MENU_AGACI_DUZELTME.md:128-136 + UX_MENU_AGACI_WIREFRAME_2026-09-18.md. Proof: web_dashboard/tabs/__init__.py + app.py güncellemesi.",
        "oncelik": "P0",
        "durum": "yapilacak",
        "sahip": "yasu",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(1),
        "bagimliliklar": [],
        "brief": "plans/brief_yasu_ADIM7-SISTEM-ONEM-KIS.md",
        "talimat": "web_dashboard/tabs/__init__.py: SECTIONS'te sistem.yenileme/ayarlar/yukleme'yi yorum yap. app.py: render_sidebar'dan 3 TabTanimi'ni çıkar. Test: sidebar 6 sekme göstersin. Wireframe kontrolü: 6/6 match.",
    },
    {
        "task_id": "YASU-02",
        "baslik": "[UI] ADIM7 menü ağacı — Ayarlar sekmesini profil popover'a taşı",
        "aciklama": "ADIM7:133-134'de ayarlar Sistem menüsünde (yanlış yer). Wireframe hedefi: profil popover (sağ-alt) → Ayarlar link. app.py:_hesap_karti_popover() içine 'Ayarlar' link ekle, ayarlar tab'ı menüden çıkar. SSOT: ADIM7_MENU_AGACI_DUZELTME.md:125-138 + UX_MENU_AGACI_WIREFRAME_2026-09-18.md (§3.4: profil popover). Proof: app.py + UX audit.",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "yasu",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(2),
        "bagimliliklar": ["YASU-01"],
        "brief": "plans/brief_yasu_ADIM7-AYARLAR-PROFIL.md",
        "talimat": "app.py:_hesap_karti_popover() (satır ~500): popover içine st.divider() + st.link_button('⚙️ Ayarlar', '?bolum=ayarlar') ekle. SECTIONS'ten ayarlar tab'ı kaldır. Test: profil tıkla → Ayarlar link görünür.",
    },
    {
        "task_id": "YASU-03",
        "baslik": "[UI] ADIM7 menü ağacı — Gelir & Paketler grubu oluştur (musteri_onizleme → 4 sekme)",
        "aciklama": "ADIM7:136'da Gelir & Paketler grubu eksik/yanlış yerde. Wireframe hedefi: yeni grup 'Gelir & Paketler' = Paketler + Pazarlama + Executive + Maliyet (4 sekme). musteri_onizleme grubu altında paketler/pazarlama var ama Executive + Maliyet yok. web_dashboard/tabs/__init__.py: 4 tab'ı yeniden gruplayıp 'gelir_paketler' üst grubu ekle. SSOT: ADIM7_MENU_AGACI_DUZELTME.md:136 + UX_MENU_AGACI_WIREFRAME (§2.3: Paketler grubu).",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "yasu",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(2),
        "bagimliliklar": ["YASU-01"],
        "brief": "plans/brief_yasu_ADIM7-GELIR-PAKETLER.md",
        "talimat": "SECTIONS'te yeni TabTanimi grubu: ust='gelir_paketler' (paketler, pazarlama, executive, maliyet). app.py render_sidebar'a grup başlığı ekle. Test: sidebar'da '💰 Gelir & Paketler' grubu (4 sekme).",
    },
    {
        "task_id": "YASU-04",
        "baslik": "[DOC] ADIM7 menü ağacı — Wireframe düzeltme tamamlama raporu yaz",
        "aciklama": "ADIM7 tamamlandıktan sonra: 6 sorun + 6 düzeltme planı (ADIM7:142-237) kontrol et, tamamlanmış görevleri kaydederek ADIM7-COMPLETION-REPORT.md yaz. SSOT: ADIM7_MENU_AGACI_DUZELTME.md (§2-3) + UX_MENU_AGACI_WIREFRAME_2026-09-18.md. Proof: ADIM7-COMPLETION-REPORT.md (✅/❌ grid).",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "yasu",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(4),
        "bagimliliklar": ["YASU-01", "YASU-02", "YASU-03"],
        "brief": "plans/brief_yasu_ADIM7-COMPLETION.md",
        "talimat": "Tablo: [Sorun | Hedef | Yapılan | Proof | Durum]. 6 sorun satırı (sistem, ayarlar, gelir_paketler, etc.). Sonunda: 'Wireframe onaylı, kod uygulama tamamlandı' sonucu. Dosya: Huginn Data Insights/ADIM7-COMPLETION-REPORT.md.",
    },
    {
        "task_id": "YASU-05",
        "baslik": "[TEST] ADIM7 menü ağacı — Menü render test + screenshot (visual regression)",
        "aciklama": "Menü değişiklikleri (YASU-01~04) tamamlandıktan sonra: Streamlit dashboard başlat, sidebar screenshot al (wireframe'deki 6 grup görünür mü?), visual regression check yap. SSOT: ADIM7_MENU_AGACI_DUZELTME.md + UX_MENU_AGACI_WIREFRAME_2026-09-18.md (hedef wireframe). Proof: screenshots/ dizini (sidebar_after_YASU.png vs wireframe_target.png).",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "yasu",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(5),
        "bagimliliklar": ["YASU-01", "YASU-02", "YASU-03"],
        "brief": "plans/brief_yasu_ADIM7-MENU-TEST.md",
        "talimat": "1. streamlit run app.py. 2. Screenshot sidebar. 3. wireframe_target.png'ye karşı kontrol et (6 grup, 4 sekme sayıları). 4. Diff → test_menu_regression_YASU-05.json (passed: bool, diffs: list[str]).",
    },
    
    # === ORKESTRATOR GÖREVLERI (5 adet: ORCH-01 ~ ORCH-05) ===
    {
        "task_id": "ORCH-01",
        "baslik": "[ORKESTRA] ADIM4-ADIM7 görevleri koordine et — Utku & Yasu görevleri sırasını tuttur",
        "aciklama": "UTKU-01~05 + YASU-01~05 görevleri paralel/sıralı çalışmak için: UTKU-01 ilk (kritik P0), YASU-01 paralel, UTKU-03/04/05 → YASU-05'ten sonra. Bağımlılık grafi oluştur, daily standuplar koordine et (2x/gün: 10:00 + 14:00 UTC+3). SSOT: task_board.json dependencies alan + bu görev brief'i. Proof: coordination_plan_ORCH-01.md (Gantt-style timeline).",
        "oncelik": "P0",
        "durum": "yapilacak",
        "sahip": "orkestrator",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(1),
        "bagimliliklar": [],
        "brief": "plans/brief_orch_KOORDINASYON.md",
        "talimat": "Gantt oluştur: [Görev | Day 1 | Day 2 | Day 3 | Day 4 | Day 5] formatında. Critical path: UTKU-01 (P0, 1d) → YASU-01 (P0, 1d). Slack görevleri paralel. Daily sync: 10:00 + 14:00 (Istanbul). Dosya: Huginn Data Insights/coordination_plan_ORCH-01.md",
    },
    {
        "task_id": "ORCH-02",
        "baslik": "[ALTYAPI] Archive belgelerini indir & tasnif et — Arşiv görevleri (Eski AGENTS, CHANGELOG, Roadmap)",
        "aciklama": "Arşiv klasöründe (_ARSIV_geçici_2026-09-21/): AIprojev1_AGENTS.md, AIprojev1_CHANGELOG.md, AIprojev1_PROJECT_ROADMAP.md, AIprojev1_AGENT_SYNC.md eski görev tanımları taşıyor. Bu belgeleri tasnif et: [Yapılan] [Yapılacak] [Deprecate edilmeli]. SSOT: _ARSIV_geçici_2026-09-21/ dosyaları + Huginn Data Insights/AGENTS.md (yeni kaynak). Proof: archive_triage_ORCH-02.md (tasnif tablosu).",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "orkestrator",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(2),
        "bagimliliklar": [],
        "brief": "plans/brief_orch_ARSIV-TASNIF.md",
        "talimat": "Arşiv belgeleri oku: Eski rules, ajan rolleri, açık görevler not et. Tablo: [Task | Eski durum | Yeni durum | SSOT | Action]. Ayrı dosya: archive_triage_ORCH-02.md. Deprecate edilecek kuralları işaretle.",
    },
    {
        "task_id": "ORCH-03",
        "baslik": "[DOC] ADIM 8 sonuç raporu yaz — 15-20 görev üretim + dağıtım özeti",
        "aciklama": "ADIM 8 tamamlandığında: görev üretim başarısı (15-20 görev ✅), dağıtım planı (Utku 5, Yasu 5, Orkestrator 5), timeline (2026-09-25 ~ 2026-10-02), kritik path (UTKU-01 + YASU-01), risk alanları (parallel testler). SSOT: Bu görev + task_board.json (üretilen görevler) + coordination_plan_ORCH-01.md. Proof: ADIM8-RESULT-REPORT.md.",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "orkestrator",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(8),
        "bagimliliklar": ["ORCH-01", "UTKU-01", "UTKU-02", "UTKU-03", "UTKU-04", "UTKU-05", "YASU-01", "YASU-02", "YASU-03", "YASU-04", "YASU-05"],
        "brief": "plans/brief_orch_ADIM8-REPORT.md",
        "talimat": "Bölümler: 1) Hedef (15-20 görev) ✅ 2) Üretilen (list + count) 3) Dağıtım (Utku/Yasu/Orch) 4) Timeline (Gantt) 5) Risks 6) Success. Dosya: Huginn Data Insights/ADIM8-RESULT-REPORT.md",
    },
    {
        "task_id": "ORCH-04",
        "baslik": "[ALTYAPI] task_board.json 20 görev validation — schema check + dependencies audit",
        "aciklama": "Üretilen 20 görev task_board.json'a eklendikten sonra: JSON schema validation (task_id, baslik, sahip, oncelik, durum, brief, talimat), circular dependencies kontrol, missing field audit. SSOT: task_board.json (mevcut yapı) + task_board_schema.json (hedef şema). Proof: validation_report_ORCH-04.json (errors: list[str], warnings: list[str], passed: bool).",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "orkestrator",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(3),
        "bagimliliklar": [],
        "brief": "plans/brief_orch_TASK-VALIDATION.md",
        "talimat": "Python script validate_tasks.py: 1) jq '.[] | select(.task_id == null)' → error. 2) Circular dependency check (dependencies -> task_id cycle). 3) brief dosyası var mı? 4) oncelik in ['P0','P1','P2']? JSON: {field_errors: [], circular: bool, missing_briefs: [], valid: bool}.",
    },
    {
        "task_id": "ORCH-05",
        "baslik": "[REPORT] ADIM 8 Görev Dashboard — Utku/Yasu/Orkestrator görev listeleri (.md + .json)",
        "aciklama": "Üretim tamamlandıktan sonra: 3 görev dosyası (utku_tasks.json, yasu_tasks.json, orchestrator_tasks.json) + summary dashboard (TASKS_DISTRIBUTION.md). SSOT: tasks_generated.json (tüm 20 görev) + bu görev brief'i. Proof: Huginn Data Insights/ dizininde 5 dosya (tasks_generated.json, utku_tasks.json, yasu_tasks.json, orchestrator_tasks.json, TASKS_DISTRIBUTION.md).",
        "oncelik": "P1",
        "durum": "yapilacak",
        "sahip": "orkestrator",
        "baslangic": NOW.isoformat() + "Z",
        "bitis": deadline_for_days(1),
        "bagimliliklar": ["ORCH-01"],
        "brief": "plans/brief_orch_TASK-DISTRIBUTION.md",
        "talimat": "1) tasks_generated.json tümü. 2) .jq filter: .[] | select(.sahip == \"utku\") > utku_tasks.json. Aynı yasu/orch. 3) TASKS_DISTRIBUTION.md: tablo (Adı | Count | P0 | P1 | P2 | Bağımlılık sayısı). 4) Timeline: start + deadline.",
    },
]

# ============================================================================
# MAIN
# ============================================================================

def main():
    print(f"Görev üretimi başlıyor — {len(TASKS)} görev")
    print(f"Now: {NOW.isoformat()}")
    print(f"Sprint deadline: {deadline_for_days(SPRINT_DAYS)}")
    print()
    
    # Görevleri task_id'ye göre sırala
    TASKS_SORTED = sorted(TASKS, key=lambda x: x["task_id"])
    
    # ===== ÇIKTI 1: tasks_generated.json (TÜM GÖREVLER) =====
    output_all = TASKS_SORTED
    with open("Huginn Data Insights/data/tasks_generated.json", "w", encoding="utf-8") as f:
        json.dump(output_all, f, ensure_ascii=False, indent=2)
    print(f"✅ Üretilen: Huginn Data Insights/data/tasks_generated.json ({len(output_all)} görev)")
    
    # ===== ÇIKTI 2: Dağıtım dosyaları =====
    for owner in ["utku", "yasu", "orkestrator"]:
        owner_tasks = [t for t in TASKS_SORTED if t["sahip"] == owner]
        filename = f"Huginn Data Insights/data/{owner}_tasks.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(owner_tasks, f, ensure_ascii=False, indent=2)
        print(f"✅ Dağıtım: {filename} ({len(owner_tasks)} görev)")
    
    # ===== ÇIKTI 3: Özet rapor (Markdown) =====
    summary_lines = [
        "# ADIM 8 — Görev Üretim Özeti",
        "",
        f"**Tarih:** {NOW.isoformat()}",
        f"**Sprint:** 2026-09-25 ~ 2026-10-02 (8 gün)",
        "",
        "## Dağıtım",
        "",
        "| Kişi | Görev Sayısı | P0 | P1 | P2 | Bağımlılık Sayısı |",
        "|------|--------------|----|----|----|--------------------|",
    ]
    
    for owner in ["utku", "yasu", "orkestrator"]:
        owner_tasks = [t for t in TASKS_SORTED if t["sahip"] == owner]
        p0_count = len([t for t in owner_tasks if t["oncelik"] == "P0"])
        p1_count = len([t for t in owner_tasks if t["oncelik"] == "P1"])
        p2_count = len([t for t in owner_tasks if t["oncelik"] == "P2"])
        dep_count = sum(len(t.get("bagimliliklar", [])) for t in owner_tasks)
        summary_lines.append(f"| {owner.capitalize()} | {len(owner_tasks)} | {p0_count} | {p1_count} | {p2_count} | {dep_count} |")
    
    summary_lines.extend([
        "",
        "## Görevler",
        "",
        "### Utku Görevleri (UTKU-01 ~ UTKU-05)",
        "- **UTKU-01:** [HUB] Önem alanı ekle (P0, 1d) ← kritik",
        "- **UTKU-02:** [TEST] Brief dosyaları yaz (P1, 2d) ← UTKU-01 sonrası",
        "- **UTKU-03:** [UI] Dashboard render test (P1, 2d)",
        "- **UTKU-04:** [UI] UX audit (P1, 3d) ← UTKU-03 sonrası",
        "- **UTKU-05:** [ALTYAPI] API entegrasyon test (P1, 3d) ← UTKU-03 sonrası",
        "",
        "### Yasu Görevleri (YASU-01 ~ YASU-05)",
        "- **YASU-01:** [UI] Sistem grubu küçült (P0, 1d) ← kritik",
        "- **YASU-02:** [UI] Ayarlar profil'e taşı (P1, 2d) ← YASU-01 sonrası",
        "- **YASU-03:** [UI] Gelir & Paketler grubu (P1, 2d) ← YASU-01 sonrası",
        "- **YASU-04:** [DOC] Wireframe raporu (P1, 4d) ← YASU-01/02/03 sonrası",
        "- **YASU-05:** [TEST] Menu visual test (P1, 5d) ← YASU-01/02/03 sonrası",
        "",
        "### Orkestrator Görevleri (ORCH-01 ~ ORCH-05)",
        "- **ORCH-01:** [ORKESTRA] Koordinasyon planı (P0, 1d) ← kritik",
        "- **ORCH-02:** [ALTYAPI] Arşiv tasnifi (P1, 2d)",
        "- **ORCH-03:** [DOC] ADIM 8 raporu (P1, 8d) ← tüm görevler sonrası",
        "- **ORCH-04:** [ALTYAPI] Task validation (P1, 3d)",
        "- **ORCH-05:** [REPORT] Görev dağıtım dashboard (P1, 1d) ← ORCH-01 sonrası",
        "",
        "## Kritik Path",
        "",
        "1. **UTKU-01** (P0, 1d) → UTKU-02 (1d) → UTKU-03 (1d) → UTKU-04 + UTKU-05 (1d paralel) = **5 günlük yol**",
        "2. **YASU-01** (P0, 1d) → YASU-02 + YASU-03 (1d paralel) → YASU-04 + YASU-05 (2d paralel) = **5 günlük yol**",
        "3. **ORCH-01** (P0, 1d) + **ORCH-02** (2d) + **ORCH-04** (3d) + **ORCH-03** (8d) = **8 günlük yol**",
        "",
        "**Toplam Sprint:** 8 gün (2026-09-25 ~ 2026-10-02)",
        "**Tamamlanma Tarihi:** 2026-10-02 (perşembe 11:30 UTC+3)",
        "",
        "---",
        "",
        "**Oluşturdu:** ADIM 8 Görev Üretim Motoru",
        f"**Zaman:** {NOW.isoformat()}",
    ])
    
    summary_text = "\n".join(summary_lines)
    with open("Huginn Data Insights/TASKS_DISTRIBUTION.md", "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"✅ Özet: Huginn Data Insights/TASKS_DISTRIBUTION.md")
    
    print()
    print("=" * 70)
    print("ADIM 8 ÖZET")
    print("=" * 70)
    print(f"Üretilen görevler: {len(TASKS)}")
    print(f"Dağıtım: Utku {len([t for t in TASKS if t['sahip'] == 'utku'])} | Yasu {len([t for t in TASKS if t['sahip'] == 'yasu'])} | Orkestrator {len([t for t in TASKS if t['sahip'] == 'orkestrator'])}")
    print(f"P0: {len([t for t in TASKS if t['oncelik'] == 'P0'])} | P1: {len([t for t in TASKS if t['oncelik'] == 'P1'])} | P2: {len([t for t in TASKS if t['oncelik'] == 'P2'])}")
    print(f"Sprint: 2026-09-25 ~ 2026-10-02")
    print()
    print("Çıktılar:")
    print("  1. Huginn Data Insights/data/tasks_generated.json (tüm görevler)")
    print("  2. Huginn Data Insights/data/utku_tasks.json (5 görev)")
    print("  3. Huginn Data Insights/data/yasu_tasks.json (5 görev)")
    print("  4. Huginn Data Insights/data/orchestrator_tasks.json (5 görev)")
    print("  5. Huginn Data Insights/TASKS_DISTRIBUTION.md (özet)")
    print()

if __name__ == "__main__":
    main()
