# REVIEW-PO-BACK-06 — Destek Merkezi Çapraz İnceleme

- **İnceleyen:** cline (tarih: 2026-09-15)
- **İncelenen teslim (kilo):** `src/company_master/destek.py` (Ticket frozen dataclass + durum makinesi), `data/destek/tickets.json` (JSON depo), `web_dashboard/tabs/admin_destek.py`, `tests/test_destek.py`
- **Karar önerisi:** **ONAY** (kritik bulgu yok; 2 orta bulgu için takip görevi önerilir — bkz. tablo)

## 1. Doğrulama Koşuları (kanıt)

| Kontrol | Sonuç |
|---|---|
| `python -m pytest tests/test_destek.py -q` | **10 passed** (0.34s) — tam yeşil |
| `python -m pytest tests/test_sayfa_iskeleti.py -q` | **76 passed** (0.61s) |
| `python scripts/kodlama_denetim.py` | EXIT 0 — destek dosyalarında BOM/UTF-16/NUL **yok** (BUG-DESTEK-UTF8 sonrası temiz) |

Not: Talimatta modül yolu `src/company_master/destek/` (paket) geçiyor; fiilen **tek dosya** `src/company_master/destek.py` (3884 bayt). İşlevsel fark yok, rapora not düştüm.

## 2. Kontrol Maddeleri

1. **Durum makinesi:** `GECERLI_GECISLER` doğru (`acik→inceleniyor`, `inceleniyor→cozuldu|acik`, `cozuldu→kapali`, `kapali` terminal). Geçersiz geçiş `ValueError` fırlatıyor; testi de mevcut (`test_durum_gecis_gecersiz_hata`). ✔
2. **Immutability:** `Ticket` `@dataclass(frozen=True)`; `__post_init__` içindeki `object.__setattr__` yalnızca kurulum anında varsayılan damga için — frozen sözleşmesi korunuyor. ✔
3. **JSON depo:** UTF-8 okuma/yazma (`encoding="utf-8"`) ✔; **atomik yazma YOK** ve **eşzamanlılık kilidi YOK** → bkz. orta bulgu B-1. `durum_gecis_depo` oku→geçiş→yaz penceresinde lost-update riski aynı başlıkta.
4. **UI kalıbı:** `admin_destek.py` `PageHeader` + `Section`(kimlik/anchor) + `SectionNav` kalibine uyuyor; `BOLUMLER` tek yerde tanımlı. ✔ (`test_sayfa_iskeleti.py` 76 passed)
5. **Secret/KVKK:** Hardcoded secret yok. KVKK notu: ticket başlık/açıklama serbest metin olarak `data/destek/tickets.json`'a düz yazı saklanıyor (bkz. düşük bulgu D-3).

## 3. Bulgu Tablosu

| ID | Seviye | Dosya | Bulgu |
|---|---|---|---|
| B-1 | **Orta** | `destek.py` (`_kaydet`, `durum_gecis_depo`) | Yazma atomik değil (`write_text` doğrudan) ve depo kilidi yok: eşzamanlı istekte yarım dosya veya lost-update olasılığı. Öneri: tmp dosya + `os.replace` + `task_board._lock_alan` benzeri dosya kilidi. |
| B-2 | **Orta** | `destek.py` (`_yukle`) | Bozuk JSON okunduğunda sessizce `{}` dönüyor; ardından ilk yazma **mevcut tüm ticketları ezer** (veri kaybı). Öneri: corrupt dosyada `.corrupt-<ts>` yedeğine taşı + uyarı. |
| D-1 | Düşük | `destek.py` (satır 57) | `durum_gecis` içindeki `time.sleep(0.003)` timestamp ayrımı için hard-coded bekleme; mimari koku + gereksiz yavaşlatma. Öneri: `guncelleme` karşılaştırmasını testte ms yerine `>=` yapın ya da monotonik sayaç ekleyin. |
| D-2 | Düşük | `tests/test_destek.py` | Testler **gerçek depoyu** (`data/destek/tickets.json`) kullanıp setup/teardown'da sıfırlıyor; `tmp_path` + monkeypatch ile izole edilmeli (pytest-xdist paralel koşumda flaky riski). |
| D-3 | Düşük | `destek.py`, `admin_destek.py` | KVKK: kullanıcı girişli serbest metin şifresiz düz dosyada saklanıyor; ayrıca `st.markdown(f"...{t.baslik}...")` ile kullanıcı metni markdown olarak basılıyor (enjeksiyon yüzeyi düşük ama mevcut). |
| D-4 | Düşük | `admin_destek.py` (satır 81) | `ticket_olustur("kilo", ...)` — tenant sabit; MVP için kabul edilebilir, gerçek tenant bağlamı geldiğinde değişmeli. |

## 4. Onay Önerisi

**ONAY** — işlevsel kabul kriterleri karşılanıyor (testler yeşil, durum makinesi/immutability doğru, UI kalibine uyumlu, secret yok). B-1 ve B-2 için (atomik yazım + kilit + corrupt-güvenli yükleme) takip görevi açılmasını öneririm; tek dosyalık MVP'de bloke edici değil.

## BULGU NOTU (kapsam dışı)

Kapsam dışı düzeltme yapılmadı. Gözlemler: (a) `scripts/check_email_dist.py` + `scripts/test_growth.py` compile-bozuk ve `scripts/scripts/` mükerrer klasör sorunu — ayrı **BUG-SCRIPTS-COMPILE-01** görevinde ele alınıyor (cline aktif). (b) `tests/test_destek.py` ilk versiyondaki 2 kırmızı test kilo tarafından yeşile çekilmiş; oturum ortasında önce 1 failed görüldü, nihai koşuda 10 passed.
