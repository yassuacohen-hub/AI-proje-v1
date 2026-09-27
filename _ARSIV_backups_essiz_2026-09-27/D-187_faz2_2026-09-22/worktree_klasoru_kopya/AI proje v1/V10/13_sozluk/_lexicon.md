---
aliases:
  - Lexicon
  - Teknik Sözlük
  - Terminoloji
title: V10 Kapsamlı Sözlük
---

# V10 Kapsamlı Sözlük

Proje genelinde kullanılan terimlerin, kısaltmaların, ajan rollerinin ve veri modelinin tek kaynak tanımı.

## Ajan Rolü Tanımları

| Kanonik Ad | Başlık | Görev Ön Eki | Tanım |
|-----------|--------|--------------|-------|
| **ihsan** | Orkestratör | ORKESTRA- | Görev dağıtımı, onay, karar kaydı, ajan koordinasyonu. Son söz ihsan'da. |
| **utku** | Üretim/Hacim | UI-, API-, VERI- | Kod yazma, refactoring, test, CI/CD. Hacim ve hız odaklı. |
| **salih** | Test Danışman | TEST-, ALTYAPI- | Bağımsız, mekanik görevler: test planlama, benchmark, bilgi tabanı, uyum denetimi. |
| **yasu** | Denetim/Review | ORKESTRA- | Kod inceleme, güvenlik, mimari uyum, doküman doğrulama, raporlama, teslim işleri. |

## Görev Yaşam Döngüsü Terimleri

| Terim | Tanım |
|-------|-------|
| **bekliyor** | Tetik kuyruğunda, henüz ajan tarafından alınmamış görev. |
| **alindi** / **aktif** | Ajan `gorev_kutusu.py al` ile görevi üstlendi; kilitler verildi. |
| **teslim** | Ajan `gorev_kutusu.py teslim` ile işi bitirdi; `review` durumuna geçer, onay bekler. |
| **review** | Kontrolör (roo) incelemesi bekleyen görev. |
| **done** | Onaylandı; kilitler bırakıldı, tetik `done`, zincir varsa sonraki tetiklendi. |
| **iptal_stale** | Bayat/çalışılmayan görev/tetik; bakım ile temizlenir. |
| **zincir_bekleme** | Zincirdeki önceki görev bitmeden bekleyen sonraki görev. |
| **handoff** | Teslim kaydı: `data/orchestrator/handoff.jsonl` — kim ne zaman ne teslim etti. |

## Teknik Kısaltmalar ve Terimler

| Terim | Tanım |
|-------|-------|
| **SSOT** | Single Source of Truth — tek doğruluk kaynağı (V9 = teknik SSOT, V10 = yönetim). |
| **MVP** | Minimum Viable Product — şu anki hedef kapsam. |
| **P0/P1/P2** | Öncelik seviyeleri: P0=kritik (blokaj), P1=yüksek (güvenlik/çekirdek), P2=orta, P3=düşük. |
| **BOM** | Byte Order Mark — UTF-8 dosyalarda yasak (kodlama denetimi). |
| **mojibake** | Karakter kodlama bozulması (Türkçe karakterler bozulmuş). |
| **NUL** | Null byte (dosya içinde yasak). |
| **AST** | Abstract Syntax Tree — statik analiz/testlerde kullanılır. |
| **monkeypatch** | `pytest` fixture'i; elle `MonkeyPatch()` oluşturulmaz. |
| **fileWatcherType=none** | Streamlit dosya izleme kapalı (restart script'inde). |
| **rate-limit** | API isteği sınırlaması (IP bazlı, dakikada N istek). |
| **SSE** | Server-Sent Events — canlı veri akışı (admin_realtime). |
| **DLQ** | Dead Letter Queue — işlenemeyen mesaj kuyruğu. |
| **MRR/ARR** | Monthly/Annual Recurring Revenue — executive dashboard metrikleri. |
| **churn** | Müşteri kaybı oranı. |
| **tenant** | Çoklu müşteri (multi-tenant) yapısındaki bir müşteri/kurum. |

## Marka ve Ürün Kimliği

| Terim | Tanım |
|-------|-------|
| **Huginn** 🦅 | Müşteri tarafı (port 8000, `huginn_` öneki, DB `huginn`). |
| **Muninn** 🛡️ | İç ekip/admin paneli (port 8501, `muninn_` öneki). |
| **Odin** ⚡ | Çekirdek/kütüphane (`odin_` öneki). |

## Dosya ve Dizin Kısaltmaları

| Yol | Anlamı |
|-----|--------|
| `data/orchestrator/` | Görev panosu, tetikler, handoff, karar defteri, raporlar. |
| `data/orchestrator/task_board.json` | Merkezi görev panosu (tek kaynak). |
| `data/orchestrator/triggers/{ajan}.jsonl` | Ajanın tetik kuyruğu (bekleyen/alınan/teslim/done). |
| `data/orchestrator/handoff.jsonl` | Teslim kayıtları (ajan, task_id, özet, çıktılar, tarih). |
| `data/orchestrator/decision_log.jsonl` | Karar kayıtları (D-XX numaralı). |
| `scripts/gorev_kutusu.py` | Ajan posta kutusu + kontrolör onay CLI. |
| `src/company_master/` | Çekirdek Python paketi (odin). |
| `web_dashboard/` | Streamlit admin paneli (muninn, port 8501). |
| `web_app.py` | FastAPI müşteri API'si (huginn, port 8000, Docker). |

## Not

Bu sözlük, yeni terimlerin eklenmesiyle dinamik olarak güncellenir. Değişiklikler [[_changelog]]'da kaydedilir.

**Bağlantılar:** [[13_sozluk/README]] · [[14_yardim_ve_ogrenme/_usage_guide]] · [[_home]]
