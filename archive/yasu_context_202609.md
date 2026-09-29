## Oturum Günlüğü

### 2026-09-29 — ALTYAPI-SKILL-YAPISI-01: skill sistemi tek havuzda

- **Görev:** `ALTYAPI-SKILL-YAPISI-01` → **teslim (review)**
- **Yapılan (6 faz):**
  - **Faz A** — `skills/devops/__init__.py` + `skills/streamlit/__init__.py` sınıf
    bekliyordu (`NginxSkill`), modül fonksiyon tanımlıyordu → **ImportError**.
    Fonksiyon dışa aktarımına çevrildi (`skills/common/__init__.py` deseni).
  - **Faz B** — `agents/devops_agent.py:3` `import anthropic` → **ModuleNotFoundError**.
    `NineRouter` istemcisine geçirildi (`ninerouter_client.py`), model
    `NINEROUTER_MODEL` env'ine. **Sıfır yeni bağımlılık** (kural: ek bağımlılık yasak).
  - **Faz C** — `.kilo/skills` 6 ölü skill → `.agents/skills` (26→32); `.kilo/skills`
    **kaldırıldı**; `.claude/skills` 5 kopya → **junction**; `.continue/skills` 5
    **boş** klasör → silindi; `.roo/skills/sistemsel` kanonik havuza taşındı (32→33).
  - **Faz D** — `skills/common/` → `skills/{tools,services}/`; `devops`+`streamlit`
    → `skills/tools/`; `cline-sdk` → `prompts/system_prompt_cline.md`;
    `skills/SKILLS_INDEX.md` yazıldı (135 satır, iki dünyayı birlikte listeler).
  - **Faz E** — `tests/test_skill_havuzu.py` (kopya/boş/ölü yol/import kapıları).
  - **Faz F** — regresyon.
- **Doğrulama:**
  - `python -m pytest tests/ -q` → **4465 passed, 13 skipped, 0 failed** (223 sn)
    · başlangıç 4450 → **+15** (yeni mandal 13 + diğer 2)
  - `python -m pytest tests/test_skill_havuzu.py -q` → **13 passed**
  - `python -m pytest tests/test_dokuman_politikasi.py tests/test_kok_politikasi.py -q` → **geçti**
    (`test_kok_politikasi` artık **yeşil** — ihsan'ın canlı dosyaları kökten bitti)
  - `python scripts/kodlama_denetim.py` → benim dosyalarımda **0** ihlal
  - `python scripts/brief_denetim.py plans/brief_yasu_...md` → **UYUMLU**
  - `python scripts/gorev_kutusu.py teslim ...` → **review**
- **Mandal kanıt üretti:** Faz E ilk koşuda `.roo/skills/sistemsel` yakaladı
  (kanonik havuzda yoktu) → taşındı → 13 passed.
- **Kalan / bloke:** `.kilo/skills` yedeği `_ARSIV_tek_kullanimlik/kilo_skills_yedek/`
  (6 skill). `devops_agent` eski sürüm yedeği aynı klasörde.
- **Öğrenilen tuzak:** PowerShell `Set-Content` UTF-8 **BOM** ekliyor; Python
  betiklerde `# -*- coding: utf-8 -*-` satırı şart. Markdown'da backtick kaçışı
  `\x08` üretti — kod bloğu üretirken script dosyası kullan, `-c` ile değil.

> **Oturumu kapatmadan:** §KALDIĞIM YER'i güncelle + **Son okunan karar** no'yu tazele.

- **Görev:** `ALTYAPI-AJAN-CAKISMA-01` (atandı → ihsan, henüz alınmadı)
- **Yapılan:**
  - Kökten **130** tek kullanımlık dosya `_ARSIV_tek_kullanimlik/`'a taşındı
    (`_ajan_context_sablon.md` korundu — 3 referans okuyor)
  - `tests/test_kok_politikasi.py:104-124` → `test_vault_kokte_tek_kullanimlik_yok`
    + `test_ajan_sablonu_kokte_kalir` (D-221 kök yarısı)
  - `AGENTS.md:3943-3969` → **D-268** kararı (lastfailed kanıt değildir)
  - **İHLAL + ONARIM:** ihsan aktifken 130 dosya taşındı; canlı ölçüm betiği
    `_defter_olcum.py` arşive kaydı → **geri alındı**. Chat tetiği atıldı
    (`chat_gonder.py`, 00:40:46). Görev + brif açıldı.
  - D-57 ve D-217 kapılarına iki kez çarptım (ASCII `->`, Türkçe `İ`) — ikisi de
    düzeltildi, kapılar çalışıyor
- **Doğrulama:**
  - `python -m pytest tests/test_kok_politikasi.py -q` → **5 passed**
  - `python scripts/kodlama_denetim.py` → benim dosyalarımda **0 ihlal**
    (36 bildirim NACE script'lerinde, önceden var)
  - `python scripts/brief_denetim.py plans/brief_ihsan_ALTYAPI-AJAN-CAKISMA-01.md` → **UYUMLU**
  - `python scripts/gorev_at.py at ...` → **ATANDI → ihsan (P1, mod=code)**
  - `python -m pytest tests/ --co` → **4457 test toplandı**
- **Mandal kanıt üretti:** test yazıldıktan ~3 dk sonra doğan `_defter_olcum.py`
  (00:29:53) testi **kırmızıya düşürdü** → kapı gerçekten çalışıyor.
- **Kalan / bloke:** `_ARSIV_tek_kullanimlik/` 130 dosyanın akıbeti KAHİN kararı bekliyor.
- **Öğrenilen tuzak:** pano boş olmak dosyanın boşta olduğunu **kanıtlamaz**
  → §Tuzaklar'a eklendi.

> **Oturumu kapatmadan:** §KALDIĞIM YER'i güncelle + **Son okunan karar** no'yu tazele.

