# Orkestratör Ajan — İç Ajan Koordinasyon Merkezi

> **Durum:** Aktif · **Tarih:** 2026-09-03 · **Sahip:** Orkestratör (otomatik kurulum)

İlgili: [[01_koordinator_ajan]] · [[OSINT_Scraper_Motoru]] · [[project_state]] · [[00-Home]] · [[CHANGELOG]]

## Nedir?

Eski sistemde "herkes herkesin ne yaptığını sürekli bir listede takip ediyordu"
mekanizmasının **yeniden kurulumu**. Orkestratör (koordinatör yetkisi) iç ajanlara
görev atar, **dosya-lock** ile çakışma önler, **merkezi görev panosu** herkesin
ne yaptığını canlı gösterir.

## Mimarı

| Bileşen | Konum | Görev |
|---------|-------|-------|
| **İç Ajan Manifest** | `src/company_master/orchestrator/internal.py` | 6 iç ajan tanımı (koordinatör/mimar/araştırmacı/geliştirici/kalite/web_kazıma) |
| **Görev Panosu** | `src/company_master/orchestrator/task_board.py` | `data/orchestrator/task_board.json` — atama/durum/lock |
| **CLI** | `scripts/orchestrator_internal.py` | `ajanlar / gorev-ekle / gorev-guncelle / pano / lock / kilitle / birak / donem-raporu` |
| **İzleyici** | `scripts/watch_agent.py` | Dosya değişiklik + kritik dosya uyarısı + süreç izleme |

## İç Ajanlar

| ID | Rol | Yetki Alanı | Kısıtlar |
|----|-----|-------------|----------|
| `koordinatör` | Orkestratör | orkestrasyon, önceliklendirme, çakışma önleme | Doğrudan kod üretmez |
| `mimar` | Mimar | şema, mimari karalar, ETL tasarımı | Tasarım odaklı |
| `arastirmaci` | Araştırmacı | kaynak araştırma, API, KVKK/legal | Doğrulanabilir kaynak arar |
| `gelistirici` | Geliştirici | kod, scraper, ETL implementasyonu | Çalışan sistemi bozmadan |
| `kalite` | Kalite | test coverage, KPI, review, doğrulama | Gate görevi görür |
| `web_kazima` | Web Kazıma Uzmanı | scrape, robots.txt, KVKK kazıma | İzinli/kontrollü kazıma |

## Görev Akışı

```
[plan] → [aktif] → [review] → [done]
                          ↘ [blocked]
```

1. Orkestratör `gorev-ekle` ile görev oluşturur → dosya-lock otomatik
2. İç ajan görevi yürütür, dosyalara sahip (başka ajan aynı dosyaya dokunamaz)
3. `gorev-guncelle --durum` ile ilerleme kaydedilir
4. Bitince lock'lar otomatik bırakılır
5. `donem-raporu` ile dönemsel özet alınır

## Çakışma Önleme (Dosya-Lock)

- Bir görev dosya listesiyle oluşturulursa o dosyalar **kilitlenir**
- Başka ajan aynı dosyayı isterse `PermissionError` ile reddedilir
- Görev bitince veya sahip değişince lock'lar transfer edilir
- Kritik dosyalar: `engine/`, `permission_router`, `entity_resolution` değişirse **acil uyarı**

## Kullanım

```bash
# Ajan listesi
python scripts/orchestrator_internal.py ajanlar

# Görev ata (P0 öncelik + dosya kilidi)
python scripts/orchestrator_internal.py gorev-ekle T1 gelistirici "Ivedik scraper" --oncelik P0 --dosya src/company_master/etl/scrapers/ivedik_scraper.py

# Durum güncelle
python scripts/orchestrator_internal.py gorev-guncelle T1 --durum aktif

# Panoyu gör
python scripts/orchestrator_internal.py pano

# Dosya kimde?
python scripts/orchestrator_internal.py lock src/company_master/engine/osint_engine.py

# Dönem raporu
python scripts/orchestrator_internal.py donem-raporu
```

## İlgili Ajanlar

| Ajan | Rolü |
|------|------|
| [[01_koordinator_ajan]] | Bu node'un insan-rol karşılığı |
| [[02_mimar_ajan]] | Orkestrasyon mimarisi |
| [[04_gelistirici_ajan]] | task_board / lock implementasyonu |
| [[05_kalite_ajan]] | Görev tamamlama doğrulaması |

Teknik uygulama: `src/company_master/orchestrator/task_board.py` · Wiki: [[OSINT_Scraper_Motoru]] (veri toplama tarafı).

## İlişkiler

- [[01_koordinator_ajan]] — bu node koordinatörün teknik uygulamasıdır
- [[OSINT_Scraper_Motoru]] — OSINT motoru kaynakları yönetir, orkestratör iç ajanları yönetir
- [[project_state]] — proje durumu buradan beslenir
- [[06_web_kazima_uzmani]] — web_kazima ajanı Permission Router'ı kullanır
- [[CHANGELOG]] — değişiklikler orkestratör kayıtlarıyla senkron

## Yol Haritası

1. **Harici ajan entegrasyonu** — mevcut `orchestrator/cli.py` (cursor_grok/copilot) ile köprü
2. **Otomatik görev atama** — Kilo Code sonrası kalan görevleri panoya taşı
3. **Dönem raporu otomasyonu** — günlük özet [[project_state]]'e yazılır