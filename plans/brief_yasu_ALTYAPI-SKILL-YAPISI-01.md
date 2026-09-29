# ALTYAPI-SKILL-YAPISI-01 — Brief (yasu)

**Başlık:** [ALTYAPI] Kırık skill paketlerini düzelt + SKILL.md havuzunu tekilleştir -> test_skill_havuzu.py (6s)
**Öncelik:** P1 · **Kit:** `ALTYAPI-KİT` (D-196)
**Kilitli dosya:** `skills/devops/__init__.py`, `skills/streamlit/__init__.py`, `tests/test_skill_havuzu.py`
**Bağımlılık:** yok
**Hub:** `hubs/ADMIN_DASHBOARD_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bir görev = bir brif. Toplu iş birden çok brife bölünmez;
> tek brifte `## Faz A/B/C...` başlıklarıyla anlatılır. Faz başına ayrı dosya açmak yasak.

## Neden

2026-09-29 taraması iki ayrı "skill" dünyası buldu. Kafa karışıklığının sebebi
**aynı adın iki mekanizmayı göstermesi**:

**Dünya A — Markdown `SKILL.md`** (ajan *okur*) → 4 klasör, 42 dosya
**Dünya B — Python `@registry.register`** (ajan *çalıştırır*) → `skills/`, 37 yetenek

Hedef: `.agents/skills/` **tek kanonik SKILL.md havuzu** olsun.

## Kanıt (ölçülmüş, 2026-09-29)

| # | Bulgu | Kanıt |
|---|---|---|
| 1 | `skills.devops` **ImportError** | `cannot import name 'NginxSkill' from 'skills.devops.nginx'` — `__init__.py:3` sınıf bekliyor, `nginx.py:10,20,31` düz fonksiyon tanımlıyor |
| 2 | `skills.streamlit` **ImportError** | `cannot import name 'DebugSkill' from 'skills.streamlit.debug'` — aynı imza uyuşmazlığı |
| 3 | `agents/devops_agent.py` **çalışmıyor** | `ModuleNotFoundError: No module named 'anthropic'` (satır 3) + yukarıdaki 2 ImportError |
| 4 | `.kilo/skills` **ölü** | `.kilo/` içinde config yok; Kilo Code `skillsDir: .agents/skills` okuyor. 6 skill (adbc, airflow…) okunmuyor |
| 5 | `.claude/skills` + `.continue/skills` **kopya** | `cuopt`, `data-designer`, `supabase` → 3 ayrı yerde **farklı kopya** (junction değil) |
| 6 | `skills/cline-sdk` **prompt dosyası** | `.py` değil — 5567 bayt sistem prompt metni, paket içinde adı `cline-sdk` |
| 7 | `skills/` paketini kullanan tek yer | `agents/devops_agent.py:4-11` (8 import). `src/`, `web_dashboard/`, `app.py`, `web_app.py`, `tests/` → **0 referans** |

**Menşe:** Hepsi `214d857` (2026-09-23, Yasua, "chore: onay kuyrugu denetimi (D-77)")
commitinde `Skill_README.md` ile birlikte gelmiş. README yapıyı "standardized
skill system" diye tanımlıyor ama **çalıştırılmamış**.

**D-220 uyumu:** `tests/test_dokuman_politikasi.py:17-31` `GURULTU` listesinde
`.agents`, `.kilo`, `.claude`, `_ARSIV` **zaten** var → tekilleştirme bu kuralı
bozmaz. Test şu an **5 passed**.

## Doğrulanacak varsayım

> Zorunlu bölüm (D-66 brif sözleşmesi). Sabitlenen tablo adı, kolon adı,
> fonksiyon imzası, satır numarası ve eşik değeri buraya geçer.

- `skills/devops/__init__.py:3-5` → `NginxSkill`, `DockerSkill`, `MonitorSkill`
  bekleniyor. `nginx.py:10,20,31`, `docker.py:10,21`, `monitor.py:10,20` düz
  fonksiyon tanımlıyor. Farklıysa **dur**, panoya sorun aç.
- `skills/streamlit/__init__.py:3-4` → `DebugSkill`, `UXSkill` bekleniyor.
  `debug.py:10,21` ve `ux_ui.py:10..69` düz fonksiyon tanımlıyor.
- `skills/common/__init__.py` **çalışıyor** (37 kayıt) — `__all__` listesini
  bozmadan değiştirilmemeli. Doğrulandı: `import skills.common` → OK.
- `agents/devops_agent.py:3` → `import anthropic`. Proje kuralı yeni bağımlılık
  eklemeyi yasaklar; `ninerouter_chat_anthropic` (`skills/common/ninerouter.py:73`)
  aynı işi ek bağımlılıksız yapar. Farklıysa **dur**, KAHİN'e sor.
- `.kilo/skills/` 6 skill adı: `adbc`, `agent-md-refactor`, `airflow`,
  `changelog-generator`, `database-observability`, `dd-logs`. Değiştiyse **dur**.

## Adımlar

> Toplu işte `## Faz A/B/C` başlıkları kullan; her fazda kök neden + etkilenen dosya
> + doğrulama komutu yazılı olsun. Fazlar sırayla yapılır, **en riskli faz ilk sırada**.

### Faz A — Kırık paket imzaları düzeltilir (en riskli, ilk)

1. **Kök neden:** `__init__.py` sınıf (`NginxSkill`) bekliyor, modül düz
   fonksiyon (`analyze_nginx_websocket`) tanımlıyor. Sınıf hiç yazılmamış.
2. **Çözüm:** `__init__.py` fonksiyonları **dışa aktarsın**; `skills/common`
   desenine uygun olsun:
   ```python
   from skills.devops.nginx import (
       analyze_nginx_websocket, fix_nginx_proxy, generate_nginx_config,
   )
   __all__ = ["analyze_nginx_websocket", "fix_nginx_proxy", "generate_nginx_config"]
   ```
   `streamlit/__init__.py` için de aynı desen.
3. **Etkilenen dosya:** `skills/devops/__init__.py`, `skills/streamlit/__init__.py`
4. **Doğrulama:**
   ```bash
   python -c "import sys; sys.path.insert(0,'.'); import skills.devops, skills.streamlit; print('OK')"
   ```
   → `OK` (şu an `ImportError`)

### Faz B — `agents/devops_agent.py` çalışır hale getirilir

1. **Kök neden:** `import anthropic` kurulu değil + Faz A'daki 2 ImportError.
   Dosya **hiç çalışmamış**; testi yok.
2. **Çözüm seçenekleri (biri seç, gerekçe yaz):**
   - **(a)** `anthropic` SDK kur → yeni bağımlılık, kurala aykırı
   - **(b)** `NineRouter`'a geçir → `ninerouter_chat_anthropic` mevcut,
     **sıfır yeni bağımlılık** ← *tercih edilen*
   - **(c)** Dosyayı sil → zaten çalışmıyor; ama `registry` tek kullanıcısı
     olur ve `SkillRegistry` de ölür
3. **Etkilenen dosya:** `agents/devops_agent.py`
4. **Doğrulama:**
   ```bash
   python -c "import sys; sys.path.insert(0,'.'); import agents.devops_agent; print('OK')"
   ```

### Faz C — SKILL.md havuzu tekilleştirilir

1. **Kök neden:** `npx skills` her ajanın **sabit** dizinine junction atıyor
   (Kilo/Cline/Copilot → `.agents/skills`; Claude → `.claude/skills`;
   Continue → `.continue/skills`; Roo → `.roo/skills`). **Eski skill'ler elle
   kopyalanmış** → 3-4 ayrı kopya oluşmuş.
2. **Çözüm:**
   - `.kilo/skills/` (6 ölü skill) → `.agents/skills/`'e **taşı**
   - `.kilo/skills/` → **kaldır** (Kilo zaten `.agents/skills` okuyor)
   - `.claude/skills/*`, `.continue/skills/*` kopyaları → `.agents/skills`'e
     **junction** yap (`typesafe-ai` örneği: `.continue/skills/typesafe-ai`
     Junction ✅ — yeni kurulum `npx skills` zaten böyle yapıyor)
3. **Etkilenen dosya:** `.kilo/skills/*`, `.claude/skills/*`, `.continue/skills/*`
4. **Doğrulama:**
   ```bash
   python -c "import pathlib; a={p.name for p in pathlib.Path('.agents/skills').iterdir() if p.is_dir()}; b={p.name for p in pathlib.Path('.claude/skills').iterdir() if p.is_dir()}; c={p.name for p in pathlib.Path('.continue/skills').iterdir() if p.is_dir()}; print('claude fark:', b-a); print('continue fark:', c-a)"
   ```
   → her iki liste **boş** olmalı

### Faz D — Python tarafı da TEK havuza katılır (tam birleşme)

> **Kullanıcı kararı (2026-09-29):** "Tüm sistemi skill reyonunda birleştir, orayı da atma."
> Yani `SKILL.md` havuzu birleşecek, **Python registry tarafı da** bırakılmayacak.

1. **Kök neden:** Aynı ad iki mekanizma gösteriyor —
   `skills/` (Python, 37 yetenek) vs `.agents/skills/` (SKILL.md, 26).
   Ajan "skill" dediğinde hangisini kastettiği belirsiz.
2. **Çözüm — `skills/` tek çatı altında toplanır:**
   ```
   skills/                    ← TEK YER
   ├── base.py               SkillRegistry (DEĞİŞMEZ)
   ├── tools/                file_ops, llm_helper, osint, orchestrator, admin_panel
   ├── services/             ninerouter (307 satır tek dosya)
   ├── utils/                validators (yeni veya mevcut)
   ├── prompts/              cline-sdk → system_prompt_cline.md
   ├── docs/                 SKILL.md havuzu (junction kaynağı)
   └── SKILLS_INDEX.md       TEK DİZİN — iki dünyayı birlikte listeler
   ```
   `skills/common/` → `tools/` + `services/` olarak dağıtılır.
3. **Etkilenen dosya:** `skills/**`, `agents/devops_agent.py` (import güncellemesi)
4. **Doğrulama:**
   ```bash
   python -c "import sys; sys.path.insert(0,'.'); import skills.tools, skills.services, skills.utils; print('OK')"
   python -c "import sys; sys.path.insert(0,'.'); import agents.devops_agent; print('OK')"
   ```

### Faz E — Havuz denetimi testi yazılır (kalıcı kapı)

1. **Kök neden:** D-221 kök mandalı yazıldı, **çalıştı** (canlı dosyayı yakaladı).
   Aynı disiplin SKILL.md havuzu için de geçerli.
2. **Yeni dosya:** `tests/test_skill_havuzu.py` — denetler:
   - Her ajan dizinindeki skill `.agents/skills/`'te var mı (kopya yok)
   - Ajan dizinindeki skill **junction** mi (kopya değil)
   - `.kilo/skills` **yok** (ölü klasör geri gelmesin)
   - `skills/` alt paketleri (`tools`, `services`, `utils`) **import edilebilir**
   - `skills/common/` **yok** (eski yol geri gelmesin)
3. **Doğrulama:** `python -m pytest tests/test_skill_havuzu.py -q`

### Faz F — Regresyon kapısı

1. **Kök neden:** 4450 test yeşildi; Faz A-D dokunduğu için **yeniden kanıt** şart.
2. **Doğrulama:**
   ```bash
   python -m pytest tests/ -q
   python scripts/kodlama_denetim.py
   python -m pytest tests/test_dokuman_politikasi.py -q
   ```

## Kabul kriteri

- [ ] `python -c "import skills.devops, skills.streamlit"` → `OK`
- [ ] `python -c "import agents.devops_agent"` → `OK` (veya dosya gerekçeyle kaldırıldı)
- [ ] `.claude/skills` ve `.continue/skills` fark listesi **boş**
- [ ] `.kilo/skills` **yok**; 6 skill `.agents/skills` altında
- [ ] `skills/tools/`, `skills/services/`, `skills/utils/` **import edilebilir**
- [ ] `skills/common/` **yok** (eski yol toplandı)
- [ ] `skills/SKILLS_INDEX.md` **iki dünyayı birlikte** listeliyor (Python + SKILL.md)
- [ ] `skills/prompts/system_prompt_cline.md` taşındı (eskiden `skills/cline-sdk`)
- [ ] `tests/test_skill_havuzu.py` yazıldı ve **geçiyor**
- [ ] `python -m pytest tests/ -q` → **0 failed** (başlangıç: 4450 passed / 13 skipped)
- [ ] `python scripts/kodlama_denetim.py` → temiz
- [ ] `tests/test_dokuman_politikasi.py` → **5 passed** (başlangıç korundu)
- [ ] **Yeni bağımlılık eklenmedi** (`requirements.txt` değişmedi)

## Kurallar (ALTYAPI-KİT · D-196)
- **Görev başında** SSOT oku: `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedufmani.md`
- **Görev sonunda** ilerlemeyi SSOT §7 (İzlenebilirlik Matrisi) satırına işle.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- Yeni bağımlılık ekleme; mevcut şema/araç ile çöz.
- **Dosya kilidi:** Faz A'dan önce `gorev_kutusu.py bak` ile kilit kontrolü yap.
  Pano boş olmak dosyanın boşta olduğunu **kanıtlamaz** (D-268).
- **Teslimden önce** `**Hub:**` dosyasının "Kapanan işler" bölümüne
  `ALTYAPI-SKILL-YAPISI-01` satırı yaz (B-14 kapısı).

## Ajan chat zorunlu (D-210 · D-217)
Sessiz çalışma yasak. Aşağıdaki durumlarda **chat'e yazmak zorunludur**:

- Brifteki bir varsayım kodda tutmuyorsa → `ac` ile sorun aç, **uydurma, durma**.
- Bir faz tıkandıysa → sorun aç, **sonraki faza geç**, zinciri durdurma.
- @mention aldıysan → P0 5-10 dk, P1 10-15 dk, P2 15-30 dk içinde cevap **zorunlu**.

```bash
python scripts/ajan_chat.py ac yasu ALTYAPI-SKILL-YAPISI-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id ALTYAPI-SKILL-YAPISI-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id ALTYAPI-SKILL-YAPISI-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id ALTYAPI-SKILL-YAPISI-01 --ozet "<ozet>"
```

Teslim öncesi zorunlu kapılar:
1. `python -m pytest tests/ -q` → 0 failed
2. `python scripts/kodlama_denetim.py` → temiz
3. `hubs/ADMIN_DASHBOARD_HUB.md` "Kapanan işler" bölümüne görev satırı (B-14)
4. `yasu_project_context.md` §KALDIĞIM YER + §Oturum Günlüğü güncellendi (D-219)
5. **ihsan'a review tetiği** atıldı

## Ilgili Nodlar
> **Zorunlu (D-218).** Obsidyen proje hafızasıdır. **En az 2 wikilink.**

- [[AI proje v1/V10/05_versiyonlar/02_admin_panel_hedufmani]]
- [[Huginn Data Insights/AGENTS]] · D-57 · D-66 · D-217 · D-218 · D-219 · D-220 · D-221 · D-268
- [[Huginn Data Insights/yasu_project_context]] · [[plans/_brief_sablon]]
- Menşe commit: `214d857` (23.09.2026) — `Skill_README.md` ile birlikte
- Tarama: `data/orchestrator/SISTEM_TARAMASI_2026-09-29_orkestrator.md`
- Mandal: `tests/test_dokuman_politikasi.py:17-31` (GURULTU listesi)

