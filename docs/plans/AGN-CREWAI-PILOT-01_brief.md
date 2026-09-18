# AGN-CREWAI-PILOT-01 — crewAI Hibrit Worker Pilotu

**Sahip onayı:** 2026-09-18 ("açalım") · **Kaynak:** AGN-STACK-01_rapor_roo.md §5 · **Ajan:** roo
**Kural:** Deney üretim yolunda DEĞİL; pano/tetik/onay akışına DOKUNULMAZ; `requirements.txt` değişmez.

## Kapsam
- Tek dosya: `scripts/deney/crewai_arastirma_deneyi.py` (dizin yeni oluşturulacak)
- Tek iş: verilen konuda 3 alt-ajan (arayıcı / okuyucu / özetleyici) crewAI Crew ile **sıralı** çalışır, çıktı `data/_tmp/` altına markdown
- Script başında `try: import crewai / except ImportError: "kurulu değil, atlanıyor"` (crewai venv'de kurulu: 1.15.22)
- Model: TAKIP.md zincirinden ücretsiz katman (OR `:free` / Groq) — anahtarlar yalnız env'den
- **Kod yazan görevlerde KULLANILMAZ** (roo raporu §4-B) — yalnız metin-üretimi

## Kabul kriterleri (5)
| # | Kriter | Eşik |
|---|---|---|
| 1 | Çıktı kalitesi | Tek-ajan çıktısıyla eşdeğer (sahip gözüyle) |
| 2 | Token maliyeti | Tek-ajan yoluna göre ≤ +%50 |
| 3 | Süre | ≤ 2× |
| 4 | Determinizm | 3 koşuda çıktı yapısı (başlıklar) aynı |
| 5 | Geri alma | Tek dosya silinince sistem etkilenmez (tam süit yeşil kanıt) |

**Başarısızlık eşiği:** 2 kriter düşerse pilot kapanır, `scripts/deney/` silinir, karar defterine "denendi, tutmadı".
**Zaman kutusu:** 1 oturum — uzarsa iptal.

## Teslim
- Rapor: `data/orchestrator/AGN-CREWAI-PILOT-01_rapor_roo.md` (5 kriter sonuç tablosu + koşu çıktıları + token ölçümü)
- Tam süit yeşil + `kodlama_denetim.py` temiz + commit YOK
