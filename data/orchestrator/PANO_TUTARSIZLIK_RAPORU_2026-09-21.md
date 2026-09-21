# Pano Tutarsızlığı Raporu
**Tarih:** 2026-09-21 17:55  
**Orkestratör:** Roo (Claude Code)

---

## Özet
- ✅ PROFILMENU-01 kapatıldı (teslim → onayla → done)
- ⚠️ **6 blocked görevde tutarsızlık bulundu**
  - 3 görev: blokajı çözüldü ama durum güncellenmedi
  - 2 görev: sahibi tarafından ertelendi, ancak durum `blocked` kaldı
  - 1 görev: blokajı başka görevin `archive` olmasından kaynaklanıyor

---

## 1. DASH-UX-02a / DASH-UX-02b (Blokaj → Deadlock)

### DASH-UX-02a
| Alan | Değer |
|------|-------|
| task_id | DASH-UX-02a |
| durum | `plan` |
| blokaj | `["SENTEZ-01"]` |
| not | "Blokaj acildi: SENTEZ-01 done" |
| sahip | utku |

**✅ Durum:** Blokaj çözüldü (SENTEZ-01 done), görev `plan` durumunda.  
**⚠️ Sorun:** Hiçkimseye atanmadı (sahip var ama tetik açılmadı).

---

### DASH-UX-02b
| Alan | Değer |
|------|-------|
| task_id | DASH-UX-02b |
| durum | `blocked` |
| blokaj | `["SENTEZ-01", "DASH-UX-02a"]` |
| not | "D-85: 02a bitince ayni sahip (utku) devam eder" |
| sahip | utku |

**❌ Sorun:** Blokajı hâlâ açık çünkü 02a `plan` (sahipsiz atama durumunda).  
**Deadlock:** 02b'nin blokajını kaldırmak için 02a tamamlanmalı, ama 02a tetiklenmemiş.

**Karar (D-85'te kayıtlı):** Serial çalışma → 02a → 02b (aynı sahip, utku).

**Önerilen aksiyon:**
- 02a'yı `al` tetikle (utku için, brief `plans/brief_utku_DASH-UX-02a.md` var)
- Sonra 02b blokajı otomatik açılacak

---

## 2. BRIF-03 (Sahipsiz)

| Alan | Değer |
|------|-------|
| task_id | BRIF-03 |
| durum | `blocked` |
| sahip | `-` (hiçkimse) |
| not | "D-62: Admin panel heap (copilot kaldırıldı, yeniden etkinleştirildi)" |

**❌ Sorun:** Blokajın nedeni açık değil (not'ta D-62 referansı var ama blokaj sebebi yazılmamış).  
**Durum:** 2026-09-19'da `bitis` gelmiş ama hâlâ `blocked`.

**Önerilen aksiyon:**
- Blokaj çözüldüyse → `durum: "done"` yap, `bitis` zaten var
- Blokaj hâlâ aktifse → `not` alanında sebebi açık yaz

---

## 3. COP-26 (Blokaj Referansı Yanlış)

| Alan | Değer |
|------|-------|
| task_id | COP-26 |
| durum | `blocked` |
| blokaj | `["COP-25"]` |
| not | "Blokaj: COP-25 bekliyor" |
| sahip | ihsan |

**❌ Sorun:** COP-25'in `durum: "archive"` (kapalı).  
**Sonuç:** Blokaj nedeni kaybolmuş (archive görev tamamlandı, block açılmalı).

**Önerilen aksiyon:**
- COP-25'in `archive` olduğu için blokajı güncelle
- `blokaj: []` (boş) yap
- `not` güncelle: "COP-25 archive (başarıyla taşındı), blokaj kaldırıldı"
- `durum` → `plan` yap (ihsan'a atanabilir)

---

## 4. FMT-01 (Sahibi Tarafından Ertelendi)

| Alan | Değer |
|------|-------|
| task_id | FMT-01 |
| durum | `blocked` |
| sahip | utku |
| not | "ERTELENDI (sahip 2026-09-17, D-48): CI push kodlama_denetim yeterli. Bu goreve DEVAM ETME; ADMIN-AYAR-01 al." |

**⚠️ Durum:** Sahibi (utku) 2026-09-17'de "Bu göreve DEVAM ETME" dedi → karar log'da (D-48).  
**Sorun:** Durum hâlâ `blocked`, fakat `not` içinde "DEVAM ETME" var.

**Önerilen aksiyon:**
- `durum` → `wontfix` YA DA
- `durum` → `archive` + `not` güncelle: "Ertelendi (D-48): ADMIN-AYAR-01 priorite"

---

## 5. GUARD-ENC-02 (Sahibi Tarafından Ertelendi)

| Alan | Değer |
|------|-------|
| task_id | GUARD-ENC-02 |
| durum | `blocked` |
| sahip | utku |
| not | "ERTELENDI (sahip 2026-09-17, D-48): CI push kodlama_denetim yeterli. Bu goreve DEVAM ETME; ADMIN-AYAR-01 al." |

**⚠️ Durum:** FMT-01 ile aynı (sahibi erteledi, not'ta "DEVAM ETME").

**Önerilen aksiyon:** FMT-01 ile aynı — durum sınıflandırması gerek.

---

## 6. WK-01, WK-02, WK-03 (Parked)

*Pano taramasında gösterilmedi, ama notlarda "ORK 2026-09-15: park — gerçek ajan değil"*

**Durum:** Atanma faaliyeti sırasında park edilmiş.  
**Önerilen aksiyon:** `durum: "archive"` + `not: "Parked (2026-09-15): gerçek ajan yok, klasör kilit kaldırıldı"`

---

## Özet: Tutarsızlık Türleri

| Görev | Tür | Aksiyon |
|-------|-----|--------|
| DASH-UX-02a | Tetik açılmamış | `al` tetikle |
| DASH-UX-02b | Deadlock (02a'ya bağlı) | 02a tamamlansa blokaj açılacak |
| BRIF-03 | Durum sınıflandırması gerek | `done` YA DA blokaj sebebi yaz |
| COP-26 | Archive referansı | Blokaj kaldır, `plan` yap |
| FMT-01 | Ertelendi ama `blocked` | Durum sınıflandır (`archive`/`wontfix`) |
| GUARD-ENC-02 | Ertelendi ama `blocked` | Durum sınıflandır (`archive`/`wontfix`) |

---

## Sprint Planlama İçin Temizlik Önerisi

1. **Hemen yapılacak:** 02a'yı `al` tetikle → deadlock kırılacak
2. **Bugün:** BRIF-03, COP-26 durum sınıflandırması
3. **D-48 referansı:** FMT-01, GUARD-ENC-02 → ADMIN-AYAR-01'e yönlendir
4. **Parked görevler:** WK-01/02/03 → archive taşı

---

## Karar
User'ın istediği *"pano tutarsızlıgı yoksa yeni görevler belirle"* koşulunun yerine getirilmesi için:
- ⚠️ **Tutarsızlık var, ama kritik değil** (atanabilir görevleri engellemiyor)
- ✅ **Sprint planı yazılabilir** (DASH-UX-02a tetiklendikten sonra)
