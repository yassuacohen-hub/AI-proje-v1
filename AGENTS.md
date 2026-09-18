# Çalışma Alanı Kuralları (Kök AGENTS.md) — Çekirdek

> Ayrıntılar `docs/AJAN_DETAY.md`'de (§ numaralı bölümler). Bu çekirdek ihlal edilmez.

## Çoklu Ajan Koordinasyonu
- İşe başlamadan önce V9 ana bağlamı ve `AGENT_SYNC.md`'yi oku; başkasının aktif işi olan dosyaya dokunma.
- V9 = teknik SSOT; V10 = yönetim. Çakışmada V9 kazanır. Ayrıntı: AJAN_DETAY §9.
- Görev panosu + dosya kilidi ZORUNLU: `gorev_ekle(..., dosyalar=[...])` ile kilitle, bitince `lock_birak`. Ayrıntı: AJAN_DETAY §14.

## Görev Yaşam Döngüsü (ORCH-08, ZORUNLU)
- Posta: `bak` → `al` → brif → iş → `teslim` (görev `review`'a geçer; onaysız `done` GEÇERSİZ). Sessizlik onay değildir. Ayrıntı: AJAN_DETAY §15.
- Otomatik onay (S-07, KAHİN kararı 2026-09-16): `oto-nobetci` / `hepsini-tamamla` yalnız **P2 ve altı** görevleri onaylar; **P0/P1 roo elle onaylar** (`trigger.otomatik_onaylanabilir`). Tekrar ihlalde oto-nobetci kapatılır.
- Başlangıç protokolü: oturum açınca veya tek kelimelik tetik (başla/go/devam/tamam = tam yetki) ile önce posta kutusunu kontrol et.
- Teslim kontrol listesi: brif maddeleri + diskte dosya + test sayısı + UTF-8 temizlik + kilit disiplini. Ayrıntı: AJAN_DETAY §17.
- **TESLİM SONRASI DOĞRULAMA (KESIN KURAL):** Her görev teslim edilmeden önce şıklar doğrulanır:
  1. Rapor dosyası mevcut: `data/orchestrator/<TASK>_rapor_<tarih>_<ajan>.md`
  2. Bilinen test failure'ları (kilitle kaynaklı bile) raporda açıkça belirtilmiş mi?
  3. Task board (`data/orchestrator/task_board.json`) entryi güncellenmiş mi (durum, not, bitis)?
  4. `python scripts/gorev_kutusu.py onay-bekleyen` ile teslim kaydındaki görev görünüyor mu?
  5. Test sonuçları tekrarlanabilir (tam süit veya ilgili test seti yeşil)?
  Bu 5 madde eksik herhangi biri = teslim YOK.
- Kodlama guard: `python scripts/kodlama_denetim.py` temiz çıkmadan teslim yok (BOM/NUL/mojibake/sozdizimi; pre-commit'te de bağlı).
- BULGU NOTU (cline): kapsam dışı bulguyu DÜZELTME; `data/orchestrator/<TASK>_bulgular_<tarih>_cline.md`'ye yaz, roo'ya tetik düş. Ayrıntı: AJAN_DETAY §7.

## Ajan Adları (D-33) ve Roller
- Kanonik adlar yalnız: `kilo`, `cline`, `roo`. Normalizasyon: `trigger.ajan_normalize()`. Ayrıntı: AJAN_DETAY §16.
- Roller: kilo = üretim/hacim, cline = denetim/review, roo = orkestratör (son söz roo'da). Ayrıntı: AJAN_DETAY §7.
- **Merve** 👩‍💻 (Continue IDE, D-49): danışman — dosya yazmaz, görev almaz, komut çalıştırmaz. Panoya girmez. Prompt: `docs/continue_system_prompt.md`.
- Rotasyon yalnız KAHİN'in `abrakadabra` ritüeliyle; subagent orkestratör olamaz, panoya görev ekleyemez. Ayrıntı: AJAN_DETAY §1-4.

## Adlandırma (Demir Kural, D-55 — KAHİN kararı 2026-09-18)
- Hiçbir ajan **kendi adını** dosya adına, dizine, branch'e, commit mesajına, rapor başlığına veya görev kimliğine yazmaz.
- Ajan adı yalnız **o ajanın kendi kişisel dosyasında** geçebilir.
- Rol bazlı son ek kullanılır: `_orkestrator` · `_uretim` · `_denetim`.
  Örnek: `data/orchestrator/<TASK>_rapor_<tarih>_orkestrator.md`
- **Kapsam dışı (makine kimliği, dosya adı değil):** `task_board.json` `sahip` alanı, CLI `--ajan` parametresi, `triggers/{ajan}.jsonl` kuyruk dosyaları, `ajan_normalize()`.
- Kural **yeni çıktılar** için derhal yürürlükte. Geriye dönük 55 dosya: `ADLANDIRMA-GERIYE-01` (iş yükü azalınca).

## Ürün Sahibi Raporlama Formatı (D-55)
- KAHİN'e giden her özet: **kısa cümleler**, teknik olmayan dil, tablo.
- Bulgular 4 sınıfta renklendirilir: 🔴 kırmızı (acil/blokaj) · 🟡 sarı (dikkat) · 🟢 yeşil (tamam) · 🔵 mavi (bilgi/öneri).
- Mümkün olan her yerde **oran ve yüzde** verilir.

## Hitap (Demir Kural, D-49 — KAHİN kararı 2026-09-18)
- Ürün Sahibi'nin adı **KAHİN**. Tüm ajanlar (kilo, cline, roo, Merve) ona **`KAHİN (Ürün Sahibi)`** diye hitap eder — büyük harfle.
- **"sahip", "kullanıcı", "efendim" kelimeleri YASAK.** Eski dokümanlardaki "sahip kararı" ifadeleri geçmiş kayıt; yeni metinlerde `KAHİN kararı` yazılır.

## Dil (Demir Kural)
- Kullanıcı iletişimi ve akıl yürütme %100 TÜRKÇE, kısa maddeler. Kod/teknik terimler İngilizce olabilir.

## Token Verimliliği — Demir Kural (D-48, KAHİN kararı 2026-09-17)
- Token tasarrufu için modelin **düşünme/akıl yürütme gücüne müdahale YASAK**: reasoning/thinking budget düşürme, `max_tokens` daraltma, iş kalitesini düşüren zayıf model seçimi.
- Hedef dörtlü: **temiz kod yazımı · kaliteli iş · verimlilik planlaması · maliyet avantajı**.
- İzin verilen tasarruf: bağlam seçimi, görev brief'i, gereksiz keşif/okuma eleme, çıktı tekrarını azaltma (K1-K6).
- Takip: `docs/raporlar/roo_code/TAKIP.md` (sürekli güncellenir).

## Genel Kod/Dosya Kuralları
- Gizli bilgiler `.env`'de; hardcoded secret yok. Tüm dosyalar UTF-8 (BOM yasak; PS `Out-File -Encoding utf8` kullanma).
- Silme/taşıma kullanıcı onayıyla; mevcut temel üzerine geliştir. Ayrıntı: AJAN_DETAY §18.
- PEP 8, tip notları, birim test; test edilmemiş iş teslim edilmez.

## Proje Sınırı (ZORUNLU)
- Her şey yalnız repo kökü içinde; üst dizine yaz/taşı/kopyala YASAK. Geçici: `data/_tmp/` veya `_trash/`, iş bitince sil.
- Dışarıdaki proje öğesini SİLME, içeri TAŞI. Ürün Sahibi notu (aynen): "Dizinin dışında projeye ait hiçbir şey görmek istemiyorum." Ayrıntı: AJAN_DETAY §19.

## Servis Kuralları
- **Streamlit restart:** UI dosyasına dokunan ajan teslimden ÖNCE `python scripts/streamlit_restart.py` çalıştırır (fileWatcherType=none). Ayrıntı: AJAN_DETAY §20.
- **FastAPI 8000 Docker'da:** API değişince `docker compose up -d --build api` + curl doğrulama. Ayrıntı: AJAN_DETAY §12.
- **VPN:** ağ hatalarında VPN notu düş; kritik işlemlerde kapatmadan önce sor. Ayrıntı: AJAN_DETAY §13.

## Marka Terminolojisi (öz)
- Huginn 🦅 = müşteri (8000, `huginn_`) · Muninn 🛡️ = iç ekip (8501, `muninn_`) · Odin ⚡ = çekirdek (`odin_`).
- İsimler çevrilmez/bölünmez; teknik kimliklerde (`huginn` db/repo) değişmez. Yasak: Huggin, Hugginn, Hugin, Munin, Muginn, Munnin, Odinn, Odın. Ayrıntı: AJAN_DETAY §11.
- Marka kiti (pazarlama/web/logo/marka metni üretimi): `docs/brand/` — D-44/D-45 kapsam ayrımı için AJAN_DETAY §11.
- Harici ajan etkileşimi orkestratör + `workspace/external/{agent_id}/` üzerinden; kök erişim yok. Ayrıntı: AJAN_DETAY §8.

## Sözlük (Lexicon) — D-29/D-30/D-47
> Bu bölüm proje genelinde kullanılan terimlerin, kısaltmaların ve ajan rollerinin tek kaynaklı tanımını tutar. D-29/D-30 kural satırı + D-47 karar dayanağıyla eklendi.

### Ajanlar ve Roller
| Terim | Tanım |
|-------|-------|
| **kilo** | Üretim/hacim ajanı — kod yazma, refactoring, test, CI/CD. Kilitli dosyalarda çalışır. |
| **cline** | Denetim/review ajanı — kod inceleme, güvenlik, mimari uyum, doküman doğrulama. |
| **roo** | Orkestratör — görev dağıtımı, onay, commit, push, karar kaydı, ajan koordinasyonu. Son söz roo'da. |
| **orkestrator** | `roo` ile eşanlamlı; görev panosu yönetimi, tetik kuyruğu, kilit takibi. |
| **oto-nobetci** | Otomatik onay/teslim işleyen arka plan süreci (`scripts/oto_nobetci.py`). P2 ve altı görevleri onaylar; P0/P1 elle onay (D-46). |

### Görev Yaşam Döngüsü Terimleri
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

### Teknik Kısaltmalar ve Terimler
| Terim | Tanım |
|-------|-------|
| **SSOT** | Single Source of Truth — tek doğruluk kaynağı (V9 = teknik SSOT, V10 = yönetim). |
| **MVP** | Minimum Viable Product — şu anki hedef kapsam. |
| **P0/P1/P2** | Öncelik seviyeleri: P0=kritik (blokaj), P1=yüksek (güvenlik/çekirdek), P2=orta, P3=düşük. |
| **BOM** | Byte Order Mark — UTF-8 dosyalarda yasak (kodlama denetimi). |
| **mojibake** | Karakter kodlama bozulması (Türkçe karakterler bozulmuş). |
| **NUL** | Null byte (dosya içinde yasak). |
| **AST** | Abstract Syntax Tree — statik analiz/testlerde kullanılır. |
| **monkeypatch** | `pytest` fixture'i; elle `MonkeyPatch()` oluşturulmaz (D-47). |
| **fileWatcherType=none** | Streamlit dosya izleme kapalı (restart script'inde). |
| **rate-limit** | API isteği sınırlaması (IP bazlı, dakikada N istek). |
| **SSE** | Server-Sent Events — canlı veri akışı (admin_realtime). |
| **DLQ** | Dead Letter Queue — işlenemeyen mesaj kuyruğu. |
| **MRR/ARR** | Monthly/Annual Recurring Revenue — executive dashboard metrikleri. |
| **churn** | Müşteri kaybı oranı. |
| **tenant** | Çoklu müşteri (multi-tenant) yapısındaki bir müşteri/kurum. |

### Dosya ve Dizin Kısaltmaları
| Yol | Anlamı |
|-----|--------|
| `data/orchestrator/` | Görev panosu, tetikler, handoff, karar defteri, raporlar. |
| `data/orchestrator/task_board.json` | Merkezi görev panosu (tek kaynak). |
| `data/orchestrator/triggers/{ajan}.jsonl` | Ajanın tetik kuyruğu (bekleyen/alınan/teslim/done). |
| `data/orchestrator/handoff.jsonl` | Teslim kayıtları (ajan, task_id, özet, çıktılar, tarih). |
| `data/orchestrator/decision_log.jsonl` | Karar kayıtları (D-XX numaralı). |
| `scripts/gorev_kutusu.py` | Ajan posta kutusu + kontrolör onay CLI. |
| `scripts/oto_nobetci.py` | Otomatik onay/zincir devam süreci. |
| `scripts/kodlama_denetim.py` | BOM/NUL/mojibake/sozdizimi denetimi. |
| `scripts/streamlit_restart.py` | UI değişince Streamlit güvenli restart. |
| `src/company_master/` | Çekirdek Python paketi (odın). |
| `web_dashboard/` | Streamlit admin paneli (muninn, port 8501). |
| `web_app.py` | FastAPI müşteri API'si (huginn, port 8000, Docker). |
| `docs/brand/` | Marka kiti (pazarlama/web/logo SSOT). |
| `src/company_master/ui/tokens.py` | Ürün UI tasarım tokenları (Indigo #6366f1 SSOT, D-45). |

### Marka ve Ürün Kimliği
| Terim | Tanım |
|-------|-------|
| **Huginn** 🦅 | Müşteri tarafı (port 8000, `huginn_` öneki, DB `huginn`). |
| **Muninn** 🛡️ | İç ekip/admin paneli (port 8501, `muninn_` öneki). |
| **Odin** ⚡ | Çekirdek/kütüphane (`odin_` öneki). |
| **Yasak yazımlar** | Huggin, Hugginn, Hugin, Munin, Muginn, Munnin, Odinn, Odın. |

### Süreç Kuralları (Hızlı Referans)
- **ORCH-08**: Görev yaşam döngüsü — `bak` → `al` → brif → iş → `teslim` → `review` → `onay` → `done`.
- **S-07 (D-46)**: Otomatik onay yalnız P2 ve altı; P0/P1 roo elle onaylar.
- **D-47**: `pytest.MonkeyPatch` elle oluşturulmaz; her zaman `monkeypatch` fixture.
- **Kilit disiplini**: `gorev_ekle(..., dosyalar=[...])` ile kilitle, bitince `lock_birak`.
- **Commit**: Sabah roo/KAHİN; ajanlar commit ATMAZ.
- **UI restart**: `python scripts/streamlit_restart.py` (fileWatcherType=none).
- **API restart**: `docker compose up -d --build api` + curl doğrulama.
