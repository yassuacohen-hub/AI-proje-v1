# Kilo Brief — TEN-01 · GAM-01 · AI-RAG-01

> Hazırlayan: roo · Tarih: 2026-09-14 · Kaynak plan: `plans/MRK_marka_ve_dil_paketi_plani.md` (satır 233-248)

## 0. Ortak bağlam

| Yüzey | Port | Marka | Teknik önek |
|---|---|---|---|
| Müşteri (HTML) | 8000 | 🦅 Huginn | `huginn_` |
| İç ekip (Streamlit) | 8501 | 🛡️ Muninn | `muninn_` |
| Çekirdek | — | ⚡ Odin | `odin_` |

- **Tarihsel Çatı Adı kuralı:** `huginn` DB/repo/`HuginnMCPServer`/`admin@huginn.local` gibi teknik kimlikler **değişmez**, sıfır migration.
- **Demir kural:** kullanıcıya açıklama Türkçe; kod/API İngilizce olabilir. Dosyalar UTF-8, BOM yok.
- **Roo'nun alanı — DOKUNMA:** `app.py`, `web_dashboard/tabs/__init__.py`, `web_dashboard/tabs/admin_yonetim.py`, `web_dashboard/tabs/admin_sistem.py`, `src/company_master/auth/*`, `src/company_master/ui/components/topbar.py`, `tests/test_dashboard_nav.py`.
- **Cline'ın alanı — DOKUNMA:** `src/company_master/ui/charts/__init__.py`, `requirements-app.txt` (CHART-01 kilitli).
- Üç görev de **motor/iskelet** işidir; ekran entegrasyonu Roo'da (U-11 sonrası). Streamlit import etme.

### Teslim öncesi kontrol listesi — ŞART (eksikse teslim reddedilir)

- [ ] Brifteki **her madde** karşılandı (yarım iş "tamamlandı" sayılmaz)
- [ ] Yeni/değişen dosyaların hepsi **gerçekten diskte var** (`dir` ile yol yol doğrula)
- [ ] Hedefli testler yeşil **ve** `python -X utf8 -m pytest tests/ -q` çalıştırıldı, sayı özete yazıldı
- [ ] Dosyalar UTF-8, BOM yok, Türkçe karakterler bozulmamış
- [ ] Kilitli dosya dışına dokunulmadı; dokunulduysa özette belirtildi
- [ ] `--ozet` içinde: değişen dosya listesi + test sayısı + eksik/erteleme açıkça yazıldı
- Teslim: `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id <ID> --ozet "..."` (asla doğrudan `done` yapma)

---

## 1. TEN-01 — Multi-tenant hazırlığı (P1)

**Amaç:** İleride `tenant_id` + KVKK ayrımı + faturalama gelecek. Bu turda **şema değişikliği yok**; yalnızca "multi-tenant'ı imkânsız kılan varsayım üretilmesin" bekçisi ve bağlam iskeleti.

**Yapılacaklar**
1. `src/company_master/tenant/__init__.py` + `model.py`:
   - `@dataclass(frozen=True) TenantContext(tenant_id: str, ad: str, plan: str = "standart")`
   - `VARSAYILAN_TENANT = TenantContext("huginn", "Huginn Data", "kurumsal")` (Tarihsel Çatı Adı)
   - `tenant_coz(kaynak: dict | None) -> TenantContext` — `tenant_id` yoksa varsayılanı döndür, boş/None güvenli.
   - `tenant_dogrula(tenant_id: str) -> str` — `^[a-z0-9_-]{2,32}$`, aksi `ValueError`.
2. **AST bekçisi** `tests/test_tenant_bekci.py`: `src/company_master/` altında modül seviyesinde `global` tek örnek ayar tutan yeni kalıp taramasına gerek yok; yalnızca **`tenant` paketinin `streamlit`/`auth` import etmediğini** ve `TenantContext`'in `frozen=True` olduğunu doğrula.
3. `tests/test_tenant.py`: en az 8 test (çözümleme, doğrulama, varsayılan, hatalı id, frozen).
4. `docs/TENANT_HAZIRLIK.md` (≤40 satır): ne yapıldı, ne **yapılmadı** (şema, faturalama, KVKK ayrımı iş modeli netleşince), ileride hangi tablolara `tenant_id` eklenecek (yalnızca liste).

**Kilitli dosyalar:** `src/company_master/tenant/__init__.py`, `src/company_master/tenant/model.py`, `tests/test_tenant.py`, `tests/test_tenant_bekci.py`, `docs/TENANT_HAZIRLIK.md`

---

## 2. GAM-01 — Rozet / Keşif sistemi (P2)

**Amaç:** Rozet = "henüz keşfedilmemiş özellik" haritası; puan değil. Bu turda yalnızca **motor + JSON saklama**.

**Rozetler (sabit, 3 adet)**

| Kimlik | Görünen ad | Tetik olayı |
|---|---|---|
| `huginn_gozu` | 👁️ Huginn'in Gözü | `canli_akis_izlendi` |
| `muninn_hafizasi` | 🧠 Muninn'in Hafızası | `ilk_denetim_kaydi` |
| `odin_tahti` | ⚡ Odin'in Tahtı | `ilk_kok_ayar` |

**Yapılacaklar**
1. `src/company_master/rozet/__init__.py`:
   - `ROZETLER: tuple[Rozet, ...]` (frozen dataclass: `kimlik`, `ad`, `aciklama`, `tetik`)
   - `olay_isle(kullanici_id: str, olay: str, yol: Path | None = None) -> Rozet | None` — yeni açılan rozeti döndürür, zaten açıksa `None`.
   - `ilerleme_oku(kullanici_id, yol=None) -> dict` / `kilitli_rozetler(kullanici_id, yol=None) -> list[Rozet]`
   - Saklama: `data/kullanici_ilerleme.json` → `{"<kullanici_id>": {"<rozet_kimlik>": "<ISO tarih>"}}`; atomik yazım (`tmp` + `replace`), dosya yoksa oluştur. **DB gelince taşınacak** — docstring'e yaz.
2. `tests/test_rozet.py`: en az 8 test (`tmp_path` ile izole; ilk açılış, tekrar, bilinmeyen olay, kilitli liste, bozuk JSON toleransı).
3. `data/kullanici_ilerleme.json` **repoya boş `{}` olarak** ekle.

**Kilitli dosyalar:** `src/company_master/rozet/__init__.py`, `tests/test_rozet.py`, `data/kullanici_ilerleme.json`

---

## 3. AI-RAG-01 — Odin AI / RAG iskeleti (P2)

> Not: `AI-CHAT-01` panoda **done** (senin önceki teslimin: `src/company_master/ai_chat.py` + `web_dashboard/tabs/abrakadabra.py`). Bu görev onun **üstüne** bağlam katmanı ekler; **`ai_chat.py` ve `abrakadabra.py`'ye dokunma**, entegrasyon ayrı görev.

**Amaç:** Huginn canlı veri + Muninn denetim logu → asistan bağlamı. Bu turda **model çağrısı yok**; yalnızca kaynak toplayıcı + bağlam derleyici iskeleti. Görünen ad **S11 kararına kadar "Abrakadabra"** (topbar.py'deki mevcut ad; dokunma).

**Yapılacaklar**
1. `src/company_master/odin_ai/__init__.py` + `rag.py`:
   - `Kaynak` protokolü: `ad: str`, `getir(sorgu: str, limit: int) -> list[Parca]`; `Parca(kaynak, metin, skor, meta)`.
   - `AuditLogKaynak(yol: Path)` — `data/orchestrator/trigger_log.jsonl` benzeri JSONL okur, basit anahtar-kelime skoru.
   - `HuginnCanliKaynak(veri: Callable[[], dict])` — sözlük döndüren callable'ı sarar (SSE'ye bağlanma, sadece arayüz).
   - `baglam_derle(sorgu: str, kaynaklar: list[Kaynak], limit_parca: int = 8, limit_karakter: int = 4000) -> str` — skorla sırala, karakter sınırını aşma.
   - `.env`/anahtar okuma **yok**; `9router` çağrısı **yok** (ayrı görev).
2. `tests/test_odin_ai.py`: en az 8 test (boş kaynak, sıralama, karakter sınırı, bozuk JSONL toleransı, callable hata sınırı).
3. `docs/ODIN_AI_ISKELET.md` (≤30 satır): mimari şeması + "sonraki adım: 9router chat sağlayıcısı bağlama".

**Kilitli dosyalar:** `src/company_master/odin_ai/__init__.py`, `src/company_master/odin_ai/rag.py`, `tests/test_odin_ai.py`, `docs/ODIN_AI_ISKELET.md`

---

## 4. Sıra ve teslim

1. TEN-01 → teslim → 2. GAM-01 → teslim → 3. AI-RAG-01 → teslim (her biri ayrı `teslim`).
2. Her teslimde tam regresyon sayısı yaz (mevcut taban: **2787 passed, 2 skipped**).
3. Sorun/engel: görevi `blocked` + `not` ile işaretle, `AGENT_SYNC.md` sonuna kısa not ekle.
