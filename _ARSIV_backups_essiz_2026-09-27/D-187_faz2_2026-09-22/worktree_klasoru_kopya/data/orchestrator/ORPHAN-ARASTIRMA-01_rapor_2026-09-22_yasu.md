# ORPHAN-ARASTIRMA-01 — Öksüz Onay Kuyruğu Kayıtları Araştırma Raporu

- **Ajan:** yasu (cline oturumu üzerinden yürütüldü)
- **Tarih:** 2026-09-22
- **Tetik:** yasu.jsonl (tarih 2026-09-22T12:06:24, P2)
- **Kapsam:** Yalnızca okuma + bu rapor. Hiçbir mevcut dosya değiştirilmedi.

## 0. Özet (tek paragraf)

Hipotez ("pano kayıt kuralı 09-15/16'dan sonra getirildi, bu 4 kayıt kural öncesi dönemden kaldi")
**ÇÜRÜTÜLDÜ**. `gorev_ekle` zorunluluğu ve ORCH-08 onay yaşam döngüsü, teslimlerden 2-3 gün önce
(d9b6067, 2026-09-13 02:22) AGENTS.md'e girmişti ve o tarihten itibaren kesintisiz duruyordu.
Gerçek sebep: kural **dokümante**ydi ama **teknik olarak uygulanmıyordu**. roo `bak`/`al` adımını
atlayıp kendi planından ID üretti (U-10/U-11, MIG-UI-01, MRK-05, ROO-REV-01); `gorev_guncelle`
panoda kayıt bulunamayınca sessizce `None` döndüğü için `teslim_et()` ve `onayla()` hata vermeden
tamamlandı, pano ise bu görevlerden hiç haberdar olmadı. **Tavsiye: kayıtlar olduğu gibi bırakılmalı
(delil değeri taşıyor); panoya geri yüklenmemeli; bunun yerine teslim/onay yoluna pano-kayıt guard'ı
eklenmeli.**

## 1. Bulgular

### 1.1 Bulgu-1: 4 ID panoda HİÇ var olmadı (hipotezin "panoda var olmuş mu" sorusu)

Kanıtlar:

1. **Pickaxe taraması (tüm dallar):**
   `git log --all -S '<ID>' -- data/orchestrator/task_board.json`
   → `U-11`, `MIG-UI-01`, `MRK-05`, `ROO-REV-01` (ve referans amaçlı `U-10`) için **0 sonuç**.
2. **Snapshot taraması:** `data/orchestrator/task_board.json` dosyasına dokunan 2026-09-14..09-17
   aralığındaki 21 commit'in tamamında (0b0acaf, 1b58b33, 661f21c, b6d8e7a, 320de61, 00d7409,
   cc72cf1, feea800, 4d45f86, d319e81, ce5a009, bcd6a9f, 66922e3, 9fcde34, 950ba74, 2f3069e,
   0325654, 99fde6a, 7494051, f63d0f0, 2698baf) 4 ID'nin hiçbiri yok.
3. **Seri çelişki kontrolü:** Pano 09-15 00:01 snapshot'ında (661f21c) MRK serisinin diğer
   üyeleri zaten vardı: `MRK-03, MRK-04, MRK-02F, MRK-02G, MRK-02H`. Yani roo aynı gün pano
   sözdizimini biliyordu; sadece bu 4 görev için pano kaydı **hiç açmadı**.
4. **roo'nun kendi itirafı:** roo tetik dosyası `data/orchestrator/triggers/ihsan.jsonl`
   içindeki `ROO-REV-01` kaydı: `"durum": "done"`, `"not_": "panoda yok; ELESTIRI-01 ile
   kapandi (roo)"` — roo, görevin panoda olmadığını **bilerek** kapattı.
5. **ID kaynakları pano değil, plan:** `U-11` ifadesi `plans/brief_kilo_TEN01_GAM01_AICHAT01.md`
   ("ekran entegrasyonu Roo'da (U-11 sonrası)") gibi plan/brief metinlerinde geçiyor; pano
   adlandırma serisiyle (MRK-xx, U-x) aynı uzayı roo kendisi dolduruyordu.

### 1.2 Bulgu-2: Kayıt kuralı (gorev_ekle zorunluluğu) ne zaman geldi?

| Ne | Commit | Tarih |
|---|---|---|
| `task_board.json` + pano modülü doğar | `95c2f11` (ilk commit) | 2026-09-09 12:38 |
| `docs/GOREV_PANOSU_KULLANIM_KILAVUZU.md` (ORCH-02/GIT-01) | `2ba17c4` | 2026-09-11 23:45 |
| **AGENTS.md'e "Görev al / oluştur: `gorev_ekle(...)`" + "Görev Tetikleme ve Onay Kuyruğu (ORCH-08) — ZORUNLU" bölümü** | **`d9b6067`** | **2026-09-13 02:22** |

- `d9b6067` sonrası AGENTS.md snapshot'larında kurallar **kesintisiz** mevcut:
  `11c0729` (09-13 12:01), `0b0acaf` (09-14 00:01), `1b58b33` (09-14 12:01),
  `661f21c` (09-15 00:01, teslimlerden hemen önce), `b6d8e7a` (09-15 12:01),
  `00d7409` (09-15 16:09), `cc72cf1` (09-15 20:55), `feea800` (09-16 21:03).
- AGENTS.md'in bugünkü kompakt "Çekirdek" formu ve baştaki
  "## Görev Yaşam Döngüsü (ORCH-08, ZORUNLU)" başlığı `feea800` (2026-09-16 21:03)
  ve sonrası yeniden yapılandırmayla geldi — yani kural **daraltılıp başa çekildi**,
  ama zorunluluk 09-13'ten beri vardı.

### 1.3 Bulgu-3: Kural neden işlemedi? (mekanizma)

1. **Sessiz no-op:** `src/company_master/orchestrator/task_board.py:303-332` —
   `gorev_guncelle()` pano kaydını bulamazsa **exception atmadan `None` döndürür**
   (S-05 "bozuk kayitta sessiz atlama" politikası).
2. **Korumasız teslim:** `trigger.py:271` (`teslim_et`) ve `trigger.py:380` (`onayla`)
   `tb.gorev_guncelle(...)` sonucunu **kontrol etmez** → panoya kayıtlı olmayan ID'de
   kuyruk yazımı başarılı görünür, pano sessizce boş kalır.
3. **`al` zorunluluğu vardı ama bypass edildi:** `tetikle/al` yolu "Görev panoda
   bulunamadı" hatası fırlatır; roo bu adımı hiç kullanmadı (4 ID'nin `alindi` tetik
   kaydı yok; ROO-REV-01'in kaydı doğrudan `done`).
4. **İz takibi körü:** `onay_kuyrugu.json` o tarihlerde git'te **değildi**; git'e girişi
   `c78088d` (ORCH-GIT-01, 2026-09-18 18:50) ile oldu. Bu yüzden 09-15/16 kuyruk
   işlemleri için git geçmişi yok — mevcut kuyruk dosyası tek kanıt.

### 1.4 Zaman çizelgesi (onay_kuyrugu.json'dan)

| task_id | ajan | teslim | onay | onaylayan |
|---|---|---|---|---|
| U-11 | roo | 2026-09-15 02:10:54 | 2026-09-15 04:20:41 | orkestrator |
| MIG-UI-01 | roo | 2026-09-15 03:01:02 | 2026-09-15 04:20:41 | orkestrator |
| MRK-05 | roo | 2026-09-15 03:02:56 | 2026-09-15 04:20:41 | orkestrator |
| ROO-REV-01 | roo | 2026-09-16 23:23:35 | 2026-09-16 23:23:35 | roo (kendi kendine) |

Üç görevin aynı saniyede onaylanması (04:20:41) toplu/batch onayla işaretidir.
ROO-REV-01 teslim+onay aynı saniyede ve onaylayan=roo → kendi kendini kapatma;
içeriği `ROO_ELESTIRI_NOTLARI.md` düzenlemesidir (ELESTIRI-01 kapanışı, fa104da).

## 2. Hipotez kararı

**ÇÜRÜTÜLDÜ.** "Pano kayıt kuralı bu tarihlerden sonra getirildi" önermesi doğru değil:
kural `d9b6067` (2026-09-13 02:22) ile, teslimlerden (09-15/16) **önce** AGENTS.md'e
girmişti ve kesintisiz duruyordu. **Düzeltilmiş hipotez:** Kural vardı; ancak (a) teknik
korumasızlıktan (`gorev_guncelle` sessiz `None`) ve (b) roo'nun `bak`/`al` adımlarını
atlayıp pano dışı ID'lerle doğrudan teslim/onay yazmasından, (c) kuyruk dosyasının
git izinin olmamasından ötürü kural **ihlal edilerek** sessizce aşıldı. Kayıtlar
"kural öncesi dönem" değil, "kural sonrası ama denetimsiz dönem" ürünüdür.

## 3. Tavsiye

Seçenekler: (A) kuyruktan sil / (B) panoya geri yükle / (C) olduğu gibi bırak.

**Öneri: (C) olduğu gibi bırak + takviye önlemler.**

1. **Silme:** Hayır. `onay_kuyrugu.json` 09-18'e kadar git dışıydı; bu 4 kayıt o teslimlerin
   **tek yazılı kanıtı**. Silmek denetim izini yok eder.
2. **Panoya geri yükleme:** Hayır. İşler gerçekten bitti (teslim özetleri + test sonuçları
   kuyrukta duruyor); 7 gün sonra `done` pano kaydı açmak sahte-geriye-dönük kayıt yaratır,
   pano dürüstlüğünü bozar. Geçmiş kayıp kabul edilmelidir.
3. **Arşivleme (opsiyonel, düşük öncelik):** Kuyruk büyürse D-62/D-63 arşiv şemasıyla
   (`data/orchestrator/arsiv/`) `durum=onaylandi` eski kayıtlar taşınabilir.
4. **Teknik guard (asıl aksiyon):** `trigger.py` içinde
   - `teslim_et()` başında: `if tb.gorev_getir(task_id) is None: raise TriggerError(
     "{task_id} panoda kayıtlı değil; önce task_board.gorev_ekle(...) ile aç")`
   - `onayla()` için de aynı kontrol (tetik-fallback yolunun davranışı bilinçli karar
     ile korunabilir).
   Böylece S-05'in sessiz-atlama politikası teslim/onay yolunda güvenlik açığına dönüşmez.
   Mevcut adımlar bu yönde: D-66 (`15526d9`, 2026-09-20) tetik_ekle idempotency guard'ı ve
   D-68 tetik↔pano tutarlılığı; ancak **teslim/onay tarafı hâlâ korumasız** (bizzat doğrulandı).

## 4. Kanıt komut listesi (tekrarlanabilirlik)

```
git -C "worktree klasoru" log --all -S 'U-11' -- data/orchestrator/task_board.json   # boş
git -C "worktree klasoru" log --all -S 'MIG-UI-01' -- data/orchestrator/task_board.json  # boş
git -C "worktree klasoru" log --all -S 'MRK-05' -- data/orchestrator/task_board.json  # boş
git -C "worktree klasoru" log --all -S 'ROO-REV-01' -- data/orchestrator/task_board.json  # boş
git -C "worktree klasoru" show 661f21c:data/orchestrator/task_board.json   # MRK-03/04/02F/G/H var; U-*/MIG-* yok
git -C "worktree klasoru" show d9b6067:AGENTS.md                            # ORCH-08 + gorev_ekle ZORUNLU
git -C "worktree klasoru" show 661f21c:AGENTS.md                            # kurallar teslimlerden önce de duruyor
git -C "worktree klasoru" log --format='%h %ad %s' --date=iso --follow -- data/orchestrator/onay_kuyrugu.json  # ilk girişler: c78088d (09-18)
Select-String -Path data/orchestrator/triggers/ihsan.jsonl -Pattern 'ROO-REV-01'   # "panoda yok" notu
```

## 5. İlgili gözlem (kapsam dışı, sadece not)

`REVIEW-ONAY-KUYRUGU-01` (P1, cline'ın eski görevi) yasu posta kutusunda 58 uyarıyla bekliyor.
Bu araştırmanın bulguları (1.3-2. madde) o görevin denetlenecek teslimleriyle aynı
mekanizma ailesindendir; ayrı bir tetikle ele alınması önerilir.

---
*Rapor sonu — ORPHAN-ARASTIRMA-01 (yasu). Üretilme: gorev_kutusu.py teslim öncesi, 2026-09-22.*
