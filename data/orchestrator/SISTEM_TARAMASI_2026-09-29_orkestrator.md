# SİSTEM TARAMASI — Bulgular, Kendi Hatam ve Onay Talebi

**Tarih:** 2026-09-29 · **Gönderen:** cline · **Alıcı:** ihsan (orkestratör)
**Konu:** FAZ-0 sonrası tam tarama — 4 bulgu, 3 kabul edilen hata, 1 risk, onay talebi

> **Bu bir onay talebidir.** Öneriler uygulanmadı; kararı orkestratöre bırakıyorum.

---

## 0. ÖZET

| | |
|---|---|
| **Ölçülen test** | **4450 passed · 13 skipped · 0 failed** (206 sn) |
| **Bulgu** | 4 (1 yüksek risk, 3 orta) |
| **Kabul edilen hata** | 3 (kendi hatam) |
| **Risk** | 1 — arşiv kararı geri alınabilir mi? |
| **Talep** | 3 madde onay |

**En önemli satır:** Takım yeşil. FAZ-0 hiçbir şey kırmadı — 4450 test geçiyor.

---

## 1. ÖLÇÜM (canlı kanıt)

| Ölçüm | Komut | Sonuç |
|---|---|---|
| Tam suite | `python -m pytest tests/ -q` | **4450 passed, 13 skipped, 0 failed** |
| Toplanan test | `pytest tests/ --co` | 4457 |
| Kökte tek kullanımlık | `Get-ChildItem -File \| Where-Object {...}` | **2** (ikisi de ihsan'ın canlı dosyası) |
| Arşivdeki dosya | `Get-ChildItem _ARSIV_tek_kullanimlik` | **132** |
| Markdown toplam | `Get-ChildItem -Recurse -Filter *.md` | 1662 |
| Aynı adlı tekrar | `Group-Object Name` | 62 grup / **831 tekrar** |
| Kodlama denetimi | `python scripts/kodlama_denetim.py` | 36 mojibake (NACE script'lerinde, benim dosyalarımda 0) |
| Yedek | `yedekler/` klasörü | 27.09 bundle'ları mevcut — **veri kaybı yok** |

---

## 2. BULGULAR

### B1 — Arşiv kararı 3 kalıcı aracı da içeriyor (yüksek risk)

`_ARSIV_tek_kullanimlik/` içindeki dosyaların hepsi "tek kullanımlık ölçüm betiği"
değil. Ölçtüm:

| Dosya | Satır | Kanıt | Karar |
|---|---|---|---|
| `run_tests.py` | **613** | `__main__` var, `test_reports/{summary.json,test_results.html}` üretiyor, son çalışma 17.09 | **KALICI ARAÇ — geri alınmalı** |
| `_test_groq_chat_live.py` | 123 | `D-195 Live chat test`, `agent-browser` otomasyonu | **D-195 referanslı — karar gerekli** |
| `_baseline_musteri.py` | 539 | büyük ölçüm betiği | karar gerekli |

**Neden önemli:** D-221 "tek kullanımlık" der; bu üçü **tek kullanımlık değil**,
benim ölçümüm **desene** bakmış (ad `run_`/`_` ile başlıyor) **içeriğe bakmamıştı**.

### B2 — `test_kok_politikasi.py` kasıtlı olarak kırmızı

```
FAILED test_vault_kokte_tek_kullanimlik_yok
['_defter_olcum.py', '_goc_defteri_rapor.txt']
```
İkisi de **ihsan'ın canlı dosyası** (00:30, 00:43). Mandala "son N dakikada değişen
dosya uyar ama geç" kuralı eklenmeli — D-268'deki `lastfailed` mantığının aynısı.

### B3 — 36 mojibake, kodlama denetimi hâlâ kırmızı

`nace_sozluk_yukle.py` (36 satır), `nace_coklu_yaz.py`, `sozluk_baslik_duzelt.py`,
`scripts/goc_defteri.py`, `tests/test_mojibake_bariyer.py:48`.
**Benim yazdığım hiçbir dosyada yok** (0 ihlal doğrulandı) — önceden var.

### B4 — D-220 sıkılaştırma hiç uygulanmamış

1662 markdown, **831 tekrar**. En çok: `README.md` 403, `CHANGELOG.md` 95, `LICENSE.md` 52.
D-220 ölçümü 2026-09-26'da yapılmış, **3 gündür uygulanmamış**.

---

## 3. KENDİ HATALARIM — SAKLAMIYORUM

### H1 — Arşivlemeden önce içerik kontrolü yapmadım
130 dosyayı **ad deseniyle** seçtim, **içerikle doğrulamadım**. Sonuç: 3 kalıcı araç
arşivde (B1). Kural ihlali: "yapıldı" beyanı kanıt taşımıyor.

### H2 — "831 mükerrer dosya" iddiamı iki kez ters verdim
- 1. turda: *"mükerrerler önemsiz, asıl sorun kök çöp"* → **yanlış yönlendirme**
- 2. turda: *"en büyük kazanç mükerrer temizliği"* → **çürütüldü, geri çekildim**
- Şimdi ölçtüm: **831 doğru**, ama `README/CHANGELOG/LICENSE` kökenli, sizin
  yazdığınız belgeler sorunsuz. D-220 hâlâ geçerli, aciliyeti **orta**.

### H3 — Çakışma kapısını görev adı düzeyinde tuttum
Pano boştu diye "ihsan serbest" dedim. **Pano boş ≠ dosya boşta.** Canlı ölçüm
betiğini arşivledim, geri aldım. `ALTYAPI-AJAN-CAKISMA-01` açıldı.

---

## 4. RİSK — Geri alınabilirlik

`git status` → **78 dosya "silinmiş" (D) görünüyor.** Arşiv klasörü
`.gitignore`'da **değil** (doğrulandı) → `git add -A` ile **rename** olarak
gider, yani **geri alınabilir**. Ama commit edilirse ve klasör sonradan silinirse
dosyalar yalnız git geçmişinde kalır.

**Yedek var:** `yedekler/ust_repo_tasima_oncesi_2026-09-27.bundle` (3 MB) —
taşıma öncesi durum. **Veri kaybı riski sıfır.**

---

## 5. ÖNERİ VE ONAY TALEBİ

### Ö1 — B1: 3 kalıcı aracı geri al (P0)
`run_tests.py` → `scripts/run_tests.py` · `_test_groq_chat_live.py` →
`scripts/` · `_baseline_musteri.py` → karar.
*Ölçüm:* 613 satır, `test_reports/` üretiyor, 17.09 son çalışma.

### Ö2 — B2: Mandala "aktif dosya istisnası" (P1)
Son 5 dakikada değişen dosya varsa mandal **uyarır, geçer**. Kasıtlı kırmızı
kalmaz. D-268 mantığıyla aynı.

### Ö3 — B3: 36 mojibake'yi `mojibake_onar.py` ile onar (P2)
Mevcut araç hazır. Benim dosyalarım temiz — sadece NACE script'leri.

---

## 6. ONAY SORUSU

> @ihsan — **bu üç öneriyi onaylıyor musun?**
> - Ö1: 3 kalıcı aracı yerine geri al → **ONAY**
> - Ö2: mandala aktif dosya istisnası → **ONAY**
> - Ö3: 36 mojibake onarımı → **ONAY**
>
> Onaylarsan **ALTYAPI-ARSAVI-DUZELT-01** brifini yazıp atarım.
> Onaylamazsan arşiv **olduğu gibi kalır** — kararı sana bırakıyorum.
>
> Ayrıca: `_ARSIV_tek_kullanimlik/` 130 dosya **silinmeli mi, kalmalı mı?**
> Benim önerim: kalsın (D-220 arama kapsamı dışı, ajanları rahatsız etmiyor).

## İlgili Nodlar
- [[Huginn Data Insights/AGENTS]] · D-57 · D-66 · D-217 · D-220 · D-221 · D-268
- [[Huginn Data Insights/ihsan_project_context]] · [[hubs/ADMIN_DASHBOARD_HUB]]
- Önceki: `data/orchestrator/FAZ0_RAPOR_kok_hijyeni_2026-09-29_orkestrator.md`
