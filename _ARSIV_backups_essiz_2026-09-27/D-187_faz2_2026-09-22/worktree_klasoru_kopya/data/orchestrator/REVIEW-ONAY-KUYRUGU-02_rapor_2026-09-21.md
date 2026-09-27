# REVIEW-ONAY-KUYRUGU-02 — Onay Kuyruğu Denetimi

- **Görev:** `ORKESTRA-ONAY-KUYRUGU-02`
- **Tarih:** 2026-09-22
- **Kapsam:** `data/orchestrator/onay_kuyrugu.json` (1860 satır, son durum)
- **Yöntem:** Salt denetim — kod değişikliği yapılmadı. Her teslim için (1) çıktı dosyaları diskte mi, (2) özetteki iddia doğrulanabiliyor mu, (3) test kanıtı yeniden üretilebiliyor mu.

---

## 1. Kapsam düzeltmesi (önemli bulgu)

Görev başlığı "**3 teslimi denetle**" diyor. Denetim anında kuyruğun gerçek durumu farklı:

| Durum | Adet |
|---|---|
| `onaylandi` | 185 |
| `bekliyor` | **1** (`DASH-UX-02a-SECTIONS`) |

Başlıktaki "3 teslim" bir **önceki** denetime aittir: `ORKESTRA-ONAY-KUYRUK-01` (yasu, 2026-09-21T23:41) tam olarak 3 bekleyen teslim denetlemiş (`UI-AYARLAR-SAYFA-01`, `ADMIN-UX-MENUTREE-01`, `BRIK-00`). Bu görev o zincirin devamı olarak açılmış, ancak görev başlığı yazılırken sayı kopyalanmış. Aradan geçen sürede o 3 teslim kapandı (BRIK-00 red edildi, D-68 ihlali — `task_board.json:5330`).

**Karar:** Denetim, başlıktaki sabit sayıya değil, kuyruğun **gerçek** açık kalemine uygulandı + kapanmış 3 kalem geriye dönük teyit edildi.

---

## 2. Açık teslim denetimi — `DASH-UX-02a-SECTIONS`

- **Ajan:** utku
- **Teslim:** 2026-09-22T08:04:12
- **İddia:** `web_dashboard/tabs/__init__.py` içinde `admin_sistem` kaydının `fonksiyon` alanı yanlıştı (`render_sistem_tab`), gerçek ad `render_admin_sistem`. 1 satır düzeltildi.

### Doğrulama

| Kontrol | Sonuç |
|---|---|
| Çıktı dosyası diskte | ✅ `web_dashboard/tabs/__init__.py` |
| Düzeltme uygulanmış mı | ✅ `__init__.py:435` → `fonksiyon="render_admin_sistem"`. `render_sistem_tab` dizinde hiç geçmiyor (0 eşleşme) |
| Hedef fonksiyon gerçekten var mı | ✅ `web_dashboard/tabs/admin_sistem.py` mevcut |
| Test kanıtı yeniden üretildi | ✅ `pytest tests/test_dashboard_nav.py tests/test_dash_ux_tabs.py -q` → **105 passed, 1 skipped in 1.88s** |
| D-57 (ajan adı dosya adında yok) | ✅ ihlal yok |
| Kapsam disiplini (D-185 split) | ✅ tek dosya, tek satır — beyan edilen kapsamla birebir |

**Sonuç: ONAYA UYGUN.** Minimal diff, doğrulanmış kanıt, regresyon yeşil.

### Not (eleştiri)
Teslim özeti "Tam regresyon 3939 passed 22 skipped **12 failed** (hepsi onceden var, baskalari degisikliginden)" diyor. Bu 12 failed **bu teslimin sorumluluğu değil** (dar kapsamlı test seti temiz), ancak **sahipsiz bırakılmış bir borç**. Kimse sahiplenmezse sessizce kalıcılaşır → ayrı görev açılmalı (öneri: `TEST-BORC-01`).

---

## 3. Kapanmış 3 teslimin geriye dönük teyidi

| Teslim | Ajan | Durum | Teyit |
|---|---|---|---|
| `UI-AYARLAR-SAYFA-01` | utku | onaylandi (yasu) | Önceki denetimde 5/5 dosya + 173 passed doğrulanmış |
| `ADMIN-UX-MENUTREE-01` | utku | onaylandi (yasu) | `web_dashboard/tabs/__init__.py` diskte, nav testleri bugün de yeşil (105 passed) |
| `BRIK-00` | — | **RED** | Doğru karar. Pano kaydı yok + kanıt dosyası yok = D-68 ihlali. Önceki "onaylandi" kaydı geçersiz kılınmış (`task_board.json:5330`) |

`BRIK-00`'ın önce onaylanıp sonra geri alınması sistemin **çalıştığını** gösteriyor: kanıtsız onay yakalandı. Ancak asıl soru şu — o onay ilk seferde nasıl geçti? Onay adımında "pano kaydı var mı" kontrolü otomatik değil, insan/ajan dikkatine bağlı.

---

## 4. Sistemik eleştiriler

**E-1 — Görev başlıkları sayı içeriyor, sayı bayatlıyor.**
"3 teslimi denetle" başlığı yazıldığı an doğruydu, çalıştırıldığı an yanlıştı. Kuyruk canlı bir yapı; başlık statik. Öneri: başlıklar "onay kuyruğundaki **açık** teslimleri denetle" formunda yazılsın, sayı verilmesin.

**E-2 — `durum` alanı şema ile korunmuyor.**
Kuyrukta `onaylandi`, `bekliyor`, `red` değerleri serbest string. Bir yazım hatası (`beklıyor`) kalemi görünmez yapar — hiçbir filtre yakalamaz. Öneri: yazma yolunda enum doğrulaması.

**E-3 — Onay öncesi pano-kaydı kontrolü otomatik değil.**
`BRIK-00` vakası bunu kanıtladı. Onay yazarken `task_board.json`'da aynı `task_id` var mı kontrolü tek satırlık bir guard; yoksa D-68 ihlalleri tekrarlanır.

**E-4 — Kuyruk dosyası sınırsız büyüyor.**
1860 satır, 186 kayıt, hepsi tek JSON dizisi. Her okuma tüm dosyayı parse ediyor. Onaylanmış kalemler için arşiv rotasyonu (`onay_kuyrugu_arsiv_YYYY-MM.json`) gerekli.

---

## 5. Kapsam dışı bırakılanlar

- 12 failed testin kök nedeni — bu görevin kapsamı değil, ayrı görev gerektirir.
- E-2/E-3 guard'larının kodlanması — denetim görevi, kod değişikliği yapılmadı (salt denetim disiplini).
- Kuyruk arşiv rotasyonu — ayrı görev.

---

## 6. Karar

- `DASH-UX-02a-SECTIONS` → **onaya uygun** (kanıt doğrulandı, 105 passed).
- Kuyrukta başka açık kalem yok.
- Önerilen takip görevleri: `TEST-BORC-01` (12 failed), onay guard'ı (E-3), kuyruk arşivi (E-4).

**İlgili:** [[ORKESTRA-ONAY-KUYRUK-01]] · [[COP-26]]
