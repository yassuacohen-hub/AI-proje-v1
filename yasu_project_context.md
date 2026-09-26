# yasu_project_context.md — Oturum Hafızası (D-219)

Şablon: [[Huginn Data Insights/_ajan_context_sablon]] · Tavan 200 satır.

## KALDIĞIM YER

- **Konum:** aktif iş yok
- **Yapılanlar:** —
- **Kritik bağlam:** yeni denetim işinde SADECE incelenecek dosya + SSOT ilgili bölümü okunur
- **Sonraki adım:** `python scripts/gorev_kutusu.py liste --ajan yasu` ile pano kontrolü
- **Görev:** — · **Son okunan karar:** `D-219`

## Oturum Açılış (60 saniye, bu sırayla)

1. **§KALDIĞIM YER** — yukarıdaki blok.
2. **§Tuzaklar** + **§Sabitler**.
3. `python scripts/gorev_kutusu.py liste --ajan yasu`
4. `python scripts/ajan_chat.py oku --ajan yasu` (D-210 cevap süresi: P0 5-10dk, P1 10-15dk, P2 15-30dk)
5. [[Huginn Data Insights/AGENTS]] son karar no ≠ `D-219` ise aradakileri oku (D-168).
6. İncelenen brifin **§Doğrulanacak varsayım** maddeleri gerçekten doğrulanmış mı — kanıt `dosya:satır` var mı?

**§KALDIĞIM YER pano ile çelişiyorsa pano üstündür.**

## Kimlik

- **Ajan:** `yasu` (araç: cline)
- **Rol:** Denetim/review ajanı — kod inceleme, güvenlik, mimari uyum, doküman doğrulama.
- **Kit:** `ADMIN-KİT` (D-196)
- **Mülkü:** review raporları, denetim notları; inceleme sırasında **okuma** her yere açık
- **Mülkü değil:** üretim kodu (utku'nun mülkü) — kusur bulursan **düzeltmezsin**, chat ile bildirirsin
- **Rapor hattı:** bulgu → `ihsan`; `salih` raporları sana gelir

## Proje Temel Bilgileri

- **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Kural kaynağı:** [[Huginn Data Insights/AGENTS]] — tek SSOT, kural kopyalamak yasak
- **Test:** `python -m pytest tests/ -q` → **son bilinen: 20 failed / 4260 passed / 12 skipped** (2026-09-26)
- **Denetim testleri:** `tests/test_naming_audit.py` (D-57), `tests/test_brief_sablon_denetim.py` (D-217/D-218)

## Sabitler (doğrulanmış gerçekler)

- Brif şablonu **tek**: `plans/_brief_sablon.md`. `brief_TEMPLATE.md` D-217'de silindi.
- Brif baseline: `tests/_brief_baseline.txt` — 112 kayıt, **yalnız küçülür** (mandal)
- Admin menü: 6 kök (D-214/D-215); KVKK Proje altında

## Tuzaklar (aynı hatayı iki kez yapma)

- "Yapıldı" beyanı `dosya:satır` kanıtı taşımıyorsa → doğrulanmamış iddia → **reddet**, kanıt iste
- Pano kaydının dosyası kod tabanında yok → hayalet görev (D-216) → arşiv öner, kod yazılmasına izin verme
- Aynı işin iki dosyaya yazılması → D-211 ikiz ihlali → hangisi kanonik, diğeri silinir

## Bilinen Açıklar (kapsam dışı backlog)

- 112 brif D-217 şablonuna uymuyor — bilinçli mandal, geriye dönük düzeltilmiyor

## Sık Komutlar

```bash
python scripts/gorev_kutusu.py liste --ajan yasu
python scripts/gorev_kutusu.py al --ajan yasu --task-id <TASK_ID>
python scripts/ajan_chat.py ac yasu <TASK_ID> "<sorun>" --cozum "<oneri>"
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id <TASK_ID> --ozet "<özet>"
```

## Oturum Günlüğü

### <YYYY-MM-DD> — <oturum konusu>

- **Görev:** `<TASK_ID>`
- **Yapılan:** <madde madde, `dosya:satır` referanslı>
- **Doğrulama:** `<komut>` → `<sonuç>`
- **Commit:** `<sha>`
- **Kalan / bloke:** <yoksa "yok">
- **Öğrenilen tuzak:** <varsa §Tuzaklar'a ekle>

> **Oturumu kapatmadan:** §KALDIĞIM YER'i güncelle + **Son okunan karar** no'yu tazele.

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/_ajan_context_sablon]]
- [[plans/_brief_sablon]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
