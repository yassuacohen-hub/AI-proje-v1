# Bulgu Defteri — 2026-09-20

| Tarih | Task ID | Rol | 🔴/🟡/🟢/🔵 | Özet | Karar |
|-------|---------|-----|----------|------|-------|
| 2026-09-20 | ALTYAPI-BILGI-TABANI-03 | denetim | 🟡 | D-57 eski görevler standart dışı | BASLIK-GERIYE-01 (P3, backlog) |
| 2026-09-20 | ALTYAPI-BILGI-TABANI-03 | denetim | 🟡 | 7 aktif görev kilit disiplini dikkat (2 orkestratörde) | İzlenmeli, ORCH-08 bakım |
| 2026-09-20 | ALTYAPI-BILGI-TABANI-03 | denetim | 🔵 | `AI proje v1/` arşiv kodlama denetiminden çıkarılmalı | ATLANAN_DIZINLER güncelle (P3) |
| 2026-09-20 | ORKESTRA-KARAR-DEFTERI-AUDIT-01 | denetim | 🔴 | decision_log.jsonl: 97/98 kayıt `decision_id` null/boş | ORKESTRA-KARAR-DEFTERI-FIX-01 (P1) |
| 2026-09-20 | ORKESTRA-KARAR-DEFTERI-AUDIT-01 | denetim | 🔴 | decision_log tüm kayıtları zorunlu alanlar eksik (kahin_onayi/tarih/ozet) | ORKESTRA-KARAR-DEFTERI-FIX-01 (P1) |
| 2026-09-20 | ORKESTRA-KARAR-DEFTERI-AUDIT-01 | denetim | 🟡 | ADMIN-UX-MENUTREE-01, ADMIN-UX-PROFILMENU-01 için decision_log kaydı yok | Karar kayıtları eklenecek (P2) |
| 2026-09-20 | ALTYAPI-BENCHMARK-02 | orkestrator | 🔴 | Rapor `done` işaretli ama 3× `(doldur)` boş şablon içeriyordu (D-67 ihlali) | Pano `plan`'a çekildi, düzeltme brifi + tetik SALİH'e atıldı |
| 2026-09-20 | ORKESTRA-BACKLOG-KANIT-01 | orkestrator | 🟡 | Backlog 2 yanlış madde kaydedildi — kanıt satırı (dosya:satır) enforseı eksik | Görev açıldı (P2), AGENTS.md D-66 + komut doğrulaması yazılacak |
| 2026-09-20 | ALTYAPI-DECISION-LOG-ENCODE-01 | orkestrator | 🔵 | decision_log.jsonl UTF-8 mojibake (~46494 pos) — test_doc_audit hatasının root cause | Görev açıldı (P2), dosya temizleme + kodlama denetim yazılacak |
| 2026-09-20 | TEST-D77-01 | orkestrator | 🔵 | Pano işleri D-77 kuralı test — kilit disiplini, tetik-pano tutarlılığı, zincir yönetimi | Görev açıldı (P2), brif + pano kaydı + tetik talimatı tamam |
| 2026-09-20 | ORKESTRA-STALE-TEMIZLIK-01 | denetim | 🔴 | Dosya kilitleri tamamlanmış görevlerde: V10-HIJYEN-01/02 (engine.py, fulltext.py, test_search_engine_where.py) 2+ gündür kilitli | ALTYAPI-KILIT-TEMIZLIK-V10-01 (P2), kilit bırak |
| 2026-09-20 | ORKESTRA-STALE-TEMIZLIK-01 | denetim | 🟡 | Decision log satır 86: UTF-8 bozulması (0x87 baytı) — test_doc_audit hatası root cause ile uyumlu | ORKESTRA-DECISION-LOG-FORMAT-01 (P1), UTF-8 fix + reformatı |
| 2026-09-20 | ORKESTRA-STALE-TEMIZLIK-01 | denetim | 🟡 | Decision log: 2 duplicate karar (orkestrator_rotasyonu x2, AI-CI-01 x2) — veri bütünlüğü sorunu | ORKESTRA-DECISION-LOG-FORMAT-01 (P1), tekilleştir |
| 2026-09-20 | ORKESTRA-STALE-TEMIZLIK-01 | denetim | 🔵 | Kendine yönelik orkestratör rotasyonu (cline → cline) — olası yanlış veri girişi | İncelenmeli, AGENTS.md orkestrator devralma protokolü teyid |
| 2026-09-20 | ORKESTRA-BRIEF-KALITE-01 | denetim | 🔴 | Brif başlık D-57 formatı ihlali: 11/12 brif; D-66 uyumu tamam (100%) | ORKESTRA-BASLIK-D57-FIX-01 (P1), 11 başlığı formatına uydur |
| 2026-09-20 | ORKESTRA-BRIEF-KALITE-01 | denetim | 🟡 | Brif talimat eksikliği: 4/12 brif talimat alanı boş veya dosya yok | D-66 enforcement yazılmalı, görev aç |
| 2026-09-20 | ORKESTRA-DUPLIK-KAPAYANIM-01 | denetim | 🟢 | Çakışan görevler çözüldü: UI-MENUTREE-02 (done) tamamlandı, ADMIN-UX-MENUTREE-01 iptal edildi | Karar kaydı D-XX numarasıyla eklenecek (ORKESTRA-DECISION-LOG-FORMAT-01) |
| 2026-09-20 | ORKESTRA-KARAR-DEFTERI-AUDIT-01 | denetim | 🔴 | Karar defteri audit: 98 kayıt, 97/98 `decision_id` null/boş, 96 tekrar, format uyusuz | ORKESTRA-DECISION-LOG-FORMAT-01 (P1), D-XX numaralandırması + zorunlu alanlar doldur |
