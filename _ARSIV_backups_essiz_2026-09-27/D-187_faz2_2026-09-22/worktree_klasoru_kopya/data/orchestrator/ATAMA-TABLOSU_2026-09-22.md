# Atama Tablosu — 2026-09-22 (Gece Zinciri)

Kaynak: `data/orchestrator/task_board.json` — 296 görev, **12 açık**.
Karar kaydı: **D-165**.

---

## 1. İHSAN — 5 görev (`doing`)

| # | Task ID | Ö. | Başlık | Dosya | Durum notu |
|---|---|---|---|---|---|
| 1 | `COP-26` | P1 | MÜŞTERİLER ekranı: firma listesi + filtre + bildirim bloğu | `web_dashboard/tabs/admin_musteriler.py` | Blokaj kaldırıldı (COP-25 archive) |
| 2 | `ORKESTRA-ONAY-KUYRUGU-02` | P1 | Onay kuyruğundaki 3 teslimi denetle (1s) | `data/orchestrator/REVIEW-ONAY-KUYRUGU-02_rapor_2026-09-21.md` | Temiz |
| 3 | `BRIF-03` | P1 | Copilot brifi: 03_mimari kararları → öneri/kritik/ekleme | `AI proje v1/V10/03_mimari/brifler/brif_copilot.md` | D-185 ile plan'a çekilmişti |
| 4 | `V10-BELGE-01` | P1 | 6 çürütülen iddiaya K1/K3/K4 düzeltme notu | `AI proje v1/V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md` | **D-66 ihlali geri alındı**, yeniden atandı |
| 5 | `ADLANDIRMA-GERIYE-01` | P3 | D-55 geriye dönük: 55 rapor dosyasından ajan adını kaldır | (55 rapor) | Temiz |

## 2. UTKU — 5 görev (`doing`)

| # | Task ID | Ö. | Başlık | Dosya | Durum notu |
|---|---|---|---|---|---|
| 1 | `DASH-UX-02a-SECTIONS` | P1 | admin_sistem sekmesini SECTIONS'a kaydet | `web_dashboard/tabs/__init__.py` | Blokaj: `DASH-UX-02a` (onaylandı), `ADMIN-UX-MENUTREE-01` |
| 2 | `TEST-AYARLAR-KAPSAM-01` | P2 | Kullanıcı Ayarları test iskeleti | `tests/test_admin_kullanici_ayarlari.py` | Temiz |
| 3 | `TEST-MERVE-KAPSAM-01` | P2 | Ayarlar sayfası testlerini denetle (2s) | `data/orchestrator/TEST-MERVE-KAPSAM-01_rapor_2026-09-18_denetim.md` | Temiz |
| 4 | `ORKESTRA-BASLIK-GERIYE-01` | P2 | Açık görev başlıklarını D-57 kalıbına taşı (2s) | `data/orchestrator/task_board.json` | Temiz |
| 5 | `SEC-BANDIT-01` | P2 | Bandit statik güvenlik taraması + HIGH bulgular | `scripts/sec_bandit.py`, `.bandit`, `docs/SECURITY_BANDIT.md` | ⚠️ **ÇELİŞKİ** — notunda "ERTELENDİ (D-48), bu göreve DEVAM ETME" yazıyor |

## 3. ATANMAMIŞ / BEKLEYEN — 2 görev

| Task ID | Sahip | Durum | Neden |
|---|---|---|---|
| `DASH-UX-02a` | utku | `plan` | Teslim onaylandı (9 test yeşil) ama pano `done`'a çekilmedi — D-77 tutarsızlığı |
| `DASH-UX-02b` | utku | `blocked` | `SENTEZ-01` + `DASH-UX-02a-SECTIONS` bekliyor |

---

## 4. Kime Ne Yazacaksın — hazır mesajlar

### → İhsan
```
5 görev atandı, sırayla git, her biri bitince pano durumunu güncelle + kanıt bırak (D-66):

1. COP-26   — admin_musteriler.py: firma listesi + filtre + bildirim bloğu
2. ORKESTRA-ONAY-KUYRUGU-02 — 3 teslimi denetle, raporu yaz
3. BRIF-03  — brif_copilot.md: öneri/kritik/ekleme bölümleri
4. V10-BELGE-01 — 6 çürütülen iddiaya K1/K3/K4 düzeltme notu
5. ADLANDIRMA-GERIYE-01 — 55 rapordan ajan adını kaldır, rol bazlı son eke çevir

Kural: kanıtsız "done" yasak. Test/çıktı/dosya farkı göstermeden kapatma.
```

### → Utku
```
5 görev atandı:

1. DASH-UX-02a-SECTIONS — __init__.py SECTIONS kaydı (02a onaylandı, yol açık)
2. TEST-AYARLAR-KAPSAM-01 — test_admin_kullanici_ayarlari.py iskelet
3. TEST-MERVE-KAPSAM-01 — ayarlar testleri denetim raporu
4. ORKESTRA-BASLIK-GERIYE-01 — başlıkları D-57 kalıbına taşı
5. SEC-BANDIT-01 — ÖNCE SOR: notunda "ERTELENDİ, devam etme" yazıyor. Teyit almadan başlama.

DASH-UX-02a teslimin onaylandı. 02b hâlâ blocked (SENTEZ-01 bekliyor).
```

### → Yasu / Cline (henüz atanmadı, senin onayın lazım)
```
Analiz ağırlıklı 2 iş şu an İhsan'da:
- V10-BELGE-01 (belge denetimi)
- BRIF-03 (mimari brief analizi)
Bunlar sana daha uygun. Taşınsın mı? Taşınırsa İhsan 3 göreve düşer.
```

---

## 5. Açık Riskler

1. **Backlog tükendi.** 296 görevin 284'ü kapalı. Bu zincir bitince iki ajan da boşta. Yeni parti üretilmezse sürdürülebilir zincir mümkün değil.
2. **`SEC-BANDIT-01` çelişkisi.** Not "devam etme" diyor, durum `doing`. Ya not temizlensin ya görev geri alınsın → fiilen Utku 4 göreve düşer.
3. **`DASH-UX-02a` panoda `plan`.** Onaylı teslim, durum ilerletilmemiş. D-77 pano disiplinine aykırı.
