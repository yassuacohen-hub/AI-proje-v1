# ORKESTRA-NAMING-AUDIT-02 — Denetim Raporu

- **Tarih:** 2026-09-23
- **Sahip:** ihsan (orkestratör)
- **Brief:** `data/orchestrator/ORKESTRA-NAMING-AUDIT-02_brif_2026-09-22_orkestrator.md`
- **Durum:** teslim (review)

## 1. Brifin öncülü çürütüldü — kapsam daraltıldı

Brief "285 uygunsuz başlık → 0" istiyordu. Ölçüm başka bir tablo çıkardı:

| Metrik | Değer |
|---|---|
| Toplam görev | 376 |
| D-57 ihlali | 309 (başlangıç) |
| İhlalin durum dağılımı | 188 done · 109 archive · 3 iptal · 6 review · 2 plan · 1 aktif |
| **Kapalı kayıttaki ihlal** | **300 / 309 (%97)** |
| **Açık yüzey** | **9** |

**Karar: kapalı kayıtların (done/archive/iptal) başlığına dokunulmadı.**
Gerekçe: kapalı görev kaydı bir *denetim izidir*. Başlığı sonradan değiştirmek,
o görevin hangi adla açıldığını, hangi adla teslim edildiğini ve rapor/brief
dosya adlarıyla eşleşmesini bozar — yani geçmişi yeniden yazar. "0 ihlal"
rakamı uğruna 300 tarihsel kaydı tahrif etmek, ölçtüğü şeyden daha pahalıdır.
Kural ileriye dönük uygulanır; geçmiş kayıt dondurulur.

Brifin 4. ve 5. adımı (toplu dönüşüm scripti, 285→0) bu gerekçeyle
**uygulanmadı**. Yerine: açık yüzey onarıldı + regresyon testiyle kilitlendi.

## 2. Yapılan onarımlar (3)

| task_id | İhlal | Eylem |
|---|---|---|
| `ORKESTRA-NAMING-AUDIT-02` | kanonik FIIL yok | başlık → `... adlandırma kurallarını **denetle** → ... (2s)` |
| `ORKESTRA-DECISION-LOG-03` | kanonik FIIL yok | başlık → `Karar defterini **düzelt** → ... (2s)` |
| `ALTYAPI-KILIT-OTOMATIK-01` | sahip `roo` kanonik değil | sahip → `yasu` (teslim eden ajan) |

Sonuç: **309 → 306 ihlal; açık ihlal 9 → 6.**

## 3. Araç boşluğu kapatıldı (asıl bulgu)

Denetimin ortaya çıkardığı esas sorun ihlallerin sayısı değil, **onaracak
sanksiyonlu yol olmamasıydı**:

- `gorev_at.py guncelle` yalnız `--brief/--talimat/--oncelik/--durum` kabul ediyordu.
- Bir başlığı ya da sahibi düzeltmenin tek yolu `task_board.json`'u elle
  açmaktı → **D-77 ihlali** ve daha önce mojibake bozulma olayına yol açan yol.

Eklendi (`scripts/gorev_at.py`):

- `guncelle --baslik` / `--baslik-b64` / `--sahip`
- Yeni başlık **aynı `_d57_dogrula` kapısından** geçirilir → ihlalin yerine
  ihlal konamaz. Sahip `trigger.AJANLAR`'a karşı denetlenir (D-60).
- `--baslik-b64`: D-86 gereği `→` ve Türkçe karakter cmd.exe'de ancak base64
  ile güvenli geçiyor.

**Ayrıca bir D-86 kusuru bulundu ve düzeltildi.** cmd.exe'de
`set ORKESTRA_AJAN=roo && python ...` yazımında `&&` öncesi boşluk değere
katılıyor (`'roo '`), bu yüzden D-58 kimlik kapısı **aktif orkestratörü kendi
kimliğinden reddediyordu**:

```
HATA (D-58): ... aktif: 'roo', cagiran: 'roo '
```

`_orkestrator_kapisi` artık iki tarafı da `.strip()` ediyor. Bu sessiz bir
kilitlenme kaynağıydı; hata mesajı iki değeri aynı gösterdiği için teşhisi zor.

## 4. Onarılmayan 6 kayıt ve nedeni

Kalan altı açık ihlalin tamamının kök nedeni aynı: **`task_id` ön eki kanonik
ALAN değil.** Bunu düzeltmek başlığı değil *kimliği* değiştirir; brief dosya
adları, rapor adları, tetik kuyruğu kayıtları ve vault wikilink'leri bu id'ye
bağlıdır. Tek satırlık bir düzeltme değil, yönlendirme kaydı gerektiren bir göç.

| task_id | Durum | Sebep |
|---|---|---|
| `COP-26` | plan | eski COP serisi, ALAN ön eki yok |
| `ADMIN-UI-CACHE-OPT-01` | review | `ADMIN-` kanonik ALAN değil |
| `ADMIN-UX-SIDEBAR-TAB` | review | `ADMIN-` + ASCII `->` kullanıyor |
| `AGENTS-MERGE-UU` | review | `AGENTS-` ön ek, başlık ALAN'ı `[DOC]` |
| `VAULT-CLEANUP-BATCH` | review | `VAULT-` ön ek, başlık ALAN'ı `[ALTYAPI]` |
| `GRAPH-CANONICAL-SECER-02` | review | `GRAPH` ALAN sözlüğünde yok |

### PO/KAHİN'e iki açık soru

1. **`GRAPH` kanonik ALAN olsun mu?** Vault graph işleri süreklilik kazandı;
   `ALANLAR`'a eklenirse `GRAPH-*` serisi tek hamlede kurala girer.
2. **Kimlik göçü için kural gerekiyor mu?** Öneri: `task_id` değişmez; gerekirse
   `gorev_at yeniden-adlandir` komutu yeni id açıp eskisine `yerine: <yeni-id>`
   yönlendirme kaydı bırakır. Karar çıkmazsa bu 6 kayıt kapanana dek muaf kalır.

## 5. Test kilidi

`tests/test_naming_audit.py` — 8 test, hepsi yeşil:

- `test_acik_gorevlerde_yeni_d57_ihlali_yok` — üretim panosundaki her **açık**
  görev `_d57_dogrula`'dan geçmeli. Muafiyet listesi (yukarıdaki 6 kayıt) kodda
  açık ve gerekçeli.
- `test_muafiyet_listesi_bayatlamadi` — muaf kayıt düzelir/kapanırsa test
  kırılır; liste çöpe dönmez.
- 5 test: `guncelle --baslik` D-57 reddi, geçerli başlık yazımı, base64 Türkçe
  bütünlüğü, `--sahip` D-60 reddi, sahip düzeltme.
- 1 test: D-86 boşluk kırpma (`'ihsan '` ve `' ihsan'` kabul, `'yasu'` ret).

**Önemli not (D-TEST-HERMETIK):** `conftest.py` izolasyonu `tb.TASK_BOARD`'u
`tmp_path`'e çevirdiği için `tb.gorev_listesi()` denetimde **boş dönüyordu** —
test boş listede "geçiyor", yani *sahte yeşil* veriyordu. Denetim artık üretim
panosunu sabit yoldan **salt okunur** açıyor. Bu, hermetik izolasyonun denetim
testlerini sessizce etkisizleştirebildiğini gösteren somut bir örnek; benzer
"panoyu ölçen" testler yazılırken dikkat edilmeli.

## 6. Dosyalar

- `scripts/gorev_at.py` — `guncelle --baslik/--baslik-b64/--sahip`, D-86 strip
- `tests/test_naming_audit.py` — yeni, 8 test
- `data/orchestrator/task_board.json` — 3 kayıt onarıldı (sanksiyonlu komutla)

## İlgili Nodlar

- [[Huginn Data Insights/AGENTS]]
- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
