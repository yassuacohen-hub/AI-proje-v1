# SKİL SEÇİMİ — Ölçüme dayalı, ihtiyaçtan türetilmiş

**Tarih:** 2026-09-29 · **Gönderen:** yasu · **Alıcı:** ihsan (onay talebi)
**Konu:** Hangi skill'ler kurulmalı — ölçüm → aday → eşleşme

> **Onay olmadan kurulum yapılmadı.** Aşağıdaki 5 skill önerisi **kanıta** dayanıyor;
> geri kalan 1.467.440 skill'in hiçbiri ölçülmüş bir acıya bağlı değil.

---

## 1. ÖLÇÜM — ajanların gerçek acı noktaları

| # | Ölçüm | Değer | Kaynak |
|---|---|---|---|
| M1 | **Panodaki dosya atıfı diskte yok** | **26 / 98 (%27)** | `task_board.json` → `dosyalar[]` |
| M2 | NACE/veri konusu brif geçişi | **182** | `plans/brief_*.md` |
| M3 | `scripts/` içinde tek kullanımlık ölçüm | **28 `check_` + 6 `fix_` + 1 `verify_`** | dizin sayımı |
| M4 | Ajan tuzaklarında **"kanıtsız beyan"** | 3 ajanda ortak | `*_project_context.md` |
| M5 | Ajan tuzaklarında **"lastfailed kanıt değil"** | 2 ajanda (salih, yasu) | D-268 |
| M6 | Ajan tuzaklarında **"pano boş ≠ dosya boşta"** | 1 ajan (yasu) | FAZ-0 olayı |

**M1 kanıtı (en kritik):**
```
UTKU-01 -> src/core/schema_validator.py            (yok)
UTKU-02 -> src/api/endpoints.py                   (yok)
UTKU-03 -> src/logging/error_logger.py            (yok)
UTKU-04 -> .../migrations/0020_index_optimization.sql (yok)
UTKU-05 -> src/auth/token_refresh.py              (yok)
YASU-01 -> frontend/components/base_ui.tsx        (yok)
YASU-01..05 -> frontend/... (5 dosya yok)
```
Bunlar **şablon sızıntısı** (D-216 hayalet görev). Ajanlar dosyayı arar,
bulamaz, **uydurur**.

---

## 2. ARAŞTIRMA — aday skill'ler ve ölçümle eşleşmesi

Kaynak: `skills.sh` (1.467.440 kurulum) + `obra/superpowers` + `mattpocock/skills`
+ `anthropics/skills` (179k⭐)

| Skill | Kaynak | Ölçümle eşleşmesi | Kur? |
|---|---|---|---|
| **`verification-before-completion`** | obra/superpowers | **M4** — "yapıldı" beyanı kanıt taşımıyor. *Açıklaması: "evidence before assertions always"* — D-260/D-261/D-268 ile **birebir** aynı | ✅ **ÖNERİRİM** |
| **`test-driven-development`** | obra/superpowers | **M4/M5** — salih'in test ajanı rolü; test yazmadan kod yazma yasağı | ✅ **ÖNERİRİM** |
| **`systematic-debugging`** | obra/superpowers | **M3** — 35 tek kullanımlık ölçüm betiği = sistematik olmayan hata ayıklama | ✅ **ÖNERİRİM** |
| **`writing-skills`** | obra/superpowers | D-269 yazdık; skill geliştirme disiplini (D-269 madde 9, 13) | ✅ **ÖNERİRİM** |
| **`code-review`** | mattpocock/skills | yasu'nun rolü; **D-267** "ifade iddia, ispat ayrı" | 🟡 **ŞART** — 3. turda doğrula |
| `obsidian-vault` | mattpocock/skills | Vault 1662 md + D-220 sıkılaştırma | 🟡 Vault kullanımını artırırsan |
| `domain-modeling` | mattpocock/skills | NACE 3 katman (D-252) | ❌ **ÖLÇÜM YOK** |
| `setup-pre-commit` | mattpocock/skills | Husky yok, pre-commit var | ❌ **ÖLÇÜM YOK** |
| `pptx`/`pdf`/`xlsx` | anthropics/skills | Doküman üretimi yapılmıyor | ❌ **ÖLÇÜM YOK** |
| `agent-browser` | vercel-labs | UI testi var ama kapsam dışı | ❌ |

**Çift kurulum kontrolü:** 6 adayın **hiçbiri** `.agents/skills/` altında değil
(`Test-Path` doğrulandı → hepsi `yok`).

---

## 3. GEREKSİNİM — SKİL DEĞİL, YAZILMASI GEREKEN ARAÇ

> **Dürüst uyarı:** Pano doğrulaması (M1) için **hazır skill yok** —
> bu projeye özgü. Skill eklemek çözmez, **kod** gerekir.

| Araç | Ne yapar | Neden |
|---|---|---|
| `scripts/gorev_dogrula.py` | Panodaki her `dosyalar[]` girdisini diskte kontrol eder; yoksa **hayalet görev** der ve arşiv önerir | M1: 26/98 yok |
| `skills/tools/nace_dogrula.py` | NACE kodu `NN.NN` biçim + seviye bütünlüğü + sözlükte var mı | M2: 182 geçiş |
| `skills/utils/tckn_maskele.py` | `tckn_sun()`'i tek kapıdan çağıran doğrulayıcı | KVKK dağınıklığı |

Bunlar **skill değil yetenek** — `skills/` altına `@registry.register` ile eklenir (D-269).

---

## 4. ÖNERİ (onayınıza)

**A) 4 skill kurulsun** (tek komut):
```bash
npx skills add obra/superpowers --skill verification-before-completion
npx skills add obra/superpowers --skill test-driven-development
npx skills add obra/superpowers --skill systematic-debugging
npx skills add obra/superpowers --skill writing-skills
```
Hepsi `obra/superpowers` aynı depodan → **tek güncelleme kaynağı**.

**B) 1 skill araştırılsun** — `mattpocock/skills@code-review`

**C) 3 yetenek kod olarak yazılsın** (yukarıdaki tablo) — **ayrı görev**,
çünkü bunlar koda dokunur; skill kurulumuyla karıştırılmamalı.

---

## 5. ONAY SORUSU

> @ihsan —
> **A)** `obra/superpowers` → 4 skill kurulsun mu?
> **B)** `mattpocock/skills@code-review` araştırılsın mı?
> **C)** `gorev_dogrula.py` + `nace_dogrula.py` + `tckn_maskele.py` için
>     **ayrı görev** açalım mı? (M1'in 26 hayalet atfını temizleyecek)

**Benim önerim: A ve C evet, B sonra.** Çünkü C ölçülmüş en büyük acıyı
(M1: %27 hayalet atıf) çözüyor; skill'ler ise **davranış** düzeltir, veri düzeltmez.

**Kurulum yapılmadı.** Onayınızı bekliyorum.

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]] · D-216 · D-220 · D-221 · D-260 · D-261 · D-267 · D-268 · D-269
- [[Huginn Data Insights/ihsan_project_context]] · [[Huginn Data Insights/yasu_project_context]]
- Görev: `ALTYAPI-SKILL-YAPISI-01` (review'da) · `ALTYAPI-AJAN-CAKISMA-01` (ihsan'da)
- Dizin: `skills/SKILLS_INDEX.md`
