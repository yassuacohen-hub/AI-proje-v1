# Sprint Planı — 2026-09-21 (Orkestratör)

## 1. Aciliyet Sıralaması (Pano Taraması)

Açık görev: **14** (3 blocked, 2 review, 9 plan). Kural: blokaj önce çöz, review kuyruğu tıkamasın, sonra P1→P2→P3.

| Sıra | Task ID | Durum | Öncelik | Sahip | Aciliyet Gerekçesi |
|---|---|---|---|---|---|
| 1 | DASH-UX-02a / DASH-UX-02a-SECTIONS | plan + blocked | P1 | utku | Aynı işin iki kaydı: biri `plan`, diğeri `blocked`. Konsolide edilmeli, tek canlı görev kalmalı. |
| 2 | DASH-UX-02b | blocked | P1 | utku | `admin_yonetim.py` blokajda; zincir `02a`'ya bağlı. |
| 3 | REVIEW-ONAY-KUYRUGU-01 | plan | P1 | yasu | 2 teslim (ADMIN-LOGIN-FIX-01, ADMIN-MODAL-S…) kuyrukta bekliyor; onay gecikirse sprint tıkanır. |
| 4 | ADMIN-UX-MENUTREE-01 | review | P1 | utku | Review'da; orkestratör onaylamalı. |
| 5 | UI-AYARLAR-SAYFA-01 | review | P1 | utku | Review'da; orkestratör onaylamalı. |
| 6 | V10-BELGE-01 | plan | P1 | ihsan | Düşük bağımlılık, hemen başlar. |
| 7 | COP-26 | plan | P1 | ihsan | MÜŞTERİLER ekranı, bağımsız iş. |
| 8 | BRIF-03 | plan | P1 | — | Sahipsiz; brif okuma işi, ihsan'a devredilebilir. |
| 9 | SEC-BANDIT-01 | blocked | P2 | utku | Güvenlik taraması; 02a/02b açılınca sıraya girer. |
| 10 | TEST-AYARLAR-KAPSAM-01 | plan | P2 | yasu | Ayarlar test iskeleti. |
| 11 | TEST-MERVE-KAPSAM-01 | plan | P2 | salih | Ayarlar test denetimi. |
| 12 | ORKESTRA-BASLIK-GERIYE-01 | plan | P2 | yasu | D-57 başlık geriye dönük düzeltme. |
| 13 | ADLANDIRMA-GERIYE-01 | plan | P3 | ihsan | D-55 55 rapor dosyası temizliği; en son. |

## 2. Kritik Tespitler (Sprint Öncesi Düzeltilecek)

1. **DASH-UX-02a çift kayıt:** `DASH-UX-02a` (`plan`) ile `DASH-UX-02a-SECTIONS` (`blocked`) aynı işin iki kaydı. D-185 split kararıyla çelişiyor. Orkestratör: `DASH-UX-02a-SECTIONS` kaydını `archive` yap, `DASH-UX-02a` tek canlı kayıt kalsın.
2. **DASH-UX-02b blokajı:** `02a` bitmeden açılmaz. Zincir sırası korunmalı: `02a` → `02b`.
3. **Review kuyruğu:** 2 utku teslimi review'da; orkestratör onaylamadan utku'ya yeni iş verme (tek görev kuralı).

## 3. Sprint Başlangıç Tablosu (D-72)

| Ajan | Yazılacak | Beklenen Sonuç |
|---|---|---|
| UTKU | `bak` | `[utku] 1 bekleyen gorev: DASH-UX-02a (P1)` |
| İHSAN | `basla` | `[ihsan] 1 bekleyen gorev: V10-BELGE-01 (P1)` |
| YASU | `başla` | `[yasu] 1 bekleyen gorev: REVIEW-ONAY-KUYRUGU-01 (P1)` |
| SALİH | `başla` | `[salih] 1 bekleyen gorev: TEST-MERVE-KAPSAM-01 (P2)` |

## 4. Sprint Sırası (Paralel Düzen)

- **Tur 1:** YASU review kuyruğunu boşalt (REVIEW-ONAY-KUYRUGU-01 + 2 utku teslimi). UTKU `02a` blokajını aç. İHSAN V10-BELGE-01'e başla.
- **Tur 2:** UTKU `02b` → `SEC-BANDIT-01`. İHSAN COP-26 → BRIF-03. YASU TEST-AYARLAR-KAPSAM-01.
- **Tur 3:** İHSAN ADLANDIRMA-GERIYE-01 (P3). YASU ORKESTRA-BASLIK-GERIYE-01.
