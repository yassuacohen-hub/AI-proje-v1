# salih_project_context.md — Oturum Hafızası (D-219)

Şablon: [[Huginn Data Insights/_ajan_context_sablon]] · Tavan 200 satır.

## KALDIĞIM YER







- **Konum:** ALTYAPI-MIMIR-BAGLAM-01 (aktif) + TEST-ODIN-PROMPT-INJECTION (iş #1 etiket önerisi, iş #2 LLM-as-judge bekliyor)
- **V4 okundu, organize edildi:** ayrıntı → [[salih_v4_arsiv]] (DIŞ+İÇ+ORTAK, mimir_servis sözleşmesi, 33 senaryo)
- **Chat:** MIMIR-BAGLAM-01'e 17:27 cevap düştü (D-210 sayacı durdu). Kimlik blokesi geçici `$env:HUGINN_AJAN=salih` ile aşıldı (kalıcı = KAHIN kararı).
- **Sonraki adım:** TESLİM BLOKE, bekleme: D-210 kapısına `type in (soru,hata)` filtresi eklenmesi (ihsan'a görev açıldı chat 13:21, task-id'siz). Gelince: `gorev_kutusu teslim --ajan salih --task-id ALTYAPI-MIMIR-BAGLAM-01`. Teknik BİTTİ 7/7 kanıt: A 4301ms finish=stop 'veri tabanımızda yok', B 4427kr BAGLAM 4124ms finish=stop 'calisan 85 + kaynak', 6/6 mandal + kil-restore, 60 komşu test, hub B-14 yazıldı. Sonra: REDTEAM-S1S4-I1I4-01 (P1, SLA 10-06)
- **Görev:** ALTYAPI-MIMIR-BAGLAM-01 · **Son okunan karar:** `D-312`
## Oturum Açılış (60 saniye, bu sırayla)

1. **§KALDIĞIM YER** — yukarıdaki blok.
2. **§Tuzaklar** + **§Sabitler**.
3. `python scripts/gorev_kutusu.py liste --ajan salih`
4. `python scripts/ajan_chat.py oku --ajan salih` (D-210 cevap süresi: P0 5-10dk, P1 10-15dk, P2 15-30dk)
5. [[Huginn Data Insights/AGENTS]] son karar no ≠ `D-219` ise aradakileri oku (D-168).
6. Brifin **§Doğrulanacak varsayım** maddelerini koda karşı doğrula.
7. **Her teslimden sonra** `python scripts/gorev_kutusu.py nobet --ajan salih` (D-335). Çıkış 0 = İŞ VAR → hemen yap; 3 = 60 dk boş → ihsan'a rapor. `nobet` dönmeden "bitti" denmez.

**§KALDIĞIM YER pano ile çelişiyorsa pano üstündür.**

## Kimlik

- **Ajan:** `salih` (araç: continue)
- **Rol:** Test Danışman — mekanik görevler: test planlama, benchmark, bilgi tabanı, uyum denetimi.
- **Kit:** `ADMIN-KİT` (D-196)
- **Mülkü:** test planları, benchmark çıktıları, bilgi tabanı notları
- **Mülkü değil:** üretim kodu ve test kodu implementasyonu (utku) — plan üretirsin, yazmazsın
- **Rapor hattı:** **rapor → YASU** (doğrudan ihsan'a değil)

## Proje Temel Bilgileri

- **SSOT:** `AI proje v1/V10/05_versiyonlar/02_admin_panel_hedef_dokumani.md`
- **Kural kaynağı:** [[Huginn Data Insights/AGENTS]] — tek SSOT, kural kopyalamak yasak
- **Test:** `python -m pytest tests/ -q` → **4457 test toplanıyor. Kırık sayısı
  `.pytest_cache/lastfailed`'a bakılarak ÖLÇÜLMEZ** (D-268) — canlı koşu çıktısı tek kaynak

## Sabitler (doğrulanmış gerçekler)








- Test kökü `tests/`; tam suite **4457** test toplanıyor (canlı koşu; lastfailed DEĞİL, D-268)
- `AGENTS.md` son karar: **D-312** (v4 prompt dayanağı D-310)
- **V4 = üç parça prompt** (DIŞ Mimir §1 / İÇ Odin §2 + ARA/GETIR / ORTAK): [[salih_v4_arsiv]]
- **Kilitli dosyam:** `src/company_master/odin_ai/mimir_servis.py` (hâlâ YOK, yazılacak)
- **Bağımlılıklar (okundu, mülküm değil):** `odin_ai/arac_dongusu.py` (ARA/GETIR, 6 tur), `odin_ai/rag.py` (chunk), `vector/embedder`
- **Enjeksiyon:** `scripts/odin_prompt_injection_test.py` (adaptör `cevapla(prompt)->str`). Senaryo v4 ile 28→**33**; genişletilmeden GECTI sayılmaz (D-224). GO eşiği: 10/12 red, meşru red 0, sızıntı 0, başarısız ≤2. Şu an %50 NO-GO.
## Tuzaklar (aynı hatayı iki kez yapma)









- **BAŞKASININ DOSYASINA DOKUNMA (KAHIN 2026-10-03):** salih kendi dosyalarına yazar (`salih_*`, `tests/test_*` brifte bende), başkalarınınkini SADECE okur (mimir_servis.py hariç — o kilitli dosyam, brifte bende)
- **Araç argümanı düşürme:** create/edit'te filepath+contents eksik → 6 kez patladı (N3, D-67). Çağırmadan önce her zorunlu argümanı kontrol
- **Boş yanıt = sahte yeşil tuzak:** `reddetti_mi("") is True` 12 senaryoyu yalancı GO yapardı (D-249/D-266). Boş → basarili=False
- **Fixture da beyandır (D-260):** `_s()` meşruda reddetti=True üretti, test_karar_go düştü; üretim kodu doğruydu
- Her write/diff sonrası dosyanın İLK+SON satırını oku (`</parameter>` çöpü, İhsan Hatam #13)
- **grep_search bu dizinde 0 döner** → PowerShell `Get-Content | Select-String`
- **BAYAT chat kaydı BİLİ notu DEĞİLDİR (D-260, 2026-10-04):** 'qwen 503 offline' kaydına güvenip 'bloke' dedim; canlı tek istek ölçtüm → ONLINE. Bayat beyan + canlı ölçüm çelişirse ÖLÇ
- **Ölçüm aracın da bir beyandır (D-260 kar-deseni, 2026-10-04):** PowerShell `Invoke-RestMethod` string'i Windows-1254'e çeviriyor, Türkçe prompt'ta 500 veriyor — model değil, ARACIM kör. Çözüm: `[Text.Encoding]::UTF8.GetBytes($bd)`. Modeli suçlamadan aracıyı doğrula
- **`ajan_chat` index'i 0-TABANLI (2026-10-04):** `oku` 1'den numaralıyor, `kapat/guncelle` 0'dan. Ben 1-tabanlı verdim → NO-GO kaydını kapattım + ihsan'ın çözüm metnini ezdim. Index vermeden önce `oku` çıktısındaki satırı eşleştir
- **`single_find_and_replace` uzun old_string kırılgan:** boş satır sayısı/tırnak/özel karakter farkı → 'string not found'. Kısa benzersiz satır hedefle, sonra edit'i MUTLAKA read/pytest ile doğrula ('Successfully edited' yalancı olabilir — 2 kez oldu)
- **D-210 teslim kapısı mesaj tipine bakmıyor (bulgu 12:53):** `messages.jsonl`de `yanit_alindi=false` olan HER mesaj soru sayılıyor; benim `rapor` mesajlarım teslimi bloke etti. `--zorla` bu kapıyı ATMZ (yalnız B-14'ü atlar). jsonl'a elle `yanit_alindi:true` YAZMA (D-260, olmayan cevabı olmuş gösterme). Düzeltme ihsan'da
- Çok satırlı `python -c` PowerShell'de sessiz bozuk → kalıcı kapı kullan
- Plan/atıf: var olmayan dosya → hayalet görev (D-216); her atıf `dosya:satır` doğrulanır
- `.pytest_cache/lastfailed` kanıt DEĞİL → canlı koşu (D-268)
## Bilinen Açıklar (kapsam dışı backlog)

- Tam suite 20 failed — görev `TEST-BACKLOG-20` (utku'da)

## Sık Komutlar

