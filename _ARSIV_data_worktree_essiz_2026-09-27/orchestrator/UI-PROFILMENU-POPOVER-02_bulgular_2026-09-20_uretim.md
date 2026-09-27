# Bulgu Notu: UI-PROFILMENU-POPOVER-02 — Görev Alınamadı (D-66)

**Tarih:** 2026-09-20
**Rol:** Üretim/Hacim
**Görev:** UI-PROFILMENU-POPOVER-02 (P2, zincir devamı)
**Durum:** 🔴 BLOKE — iş başlamadı

---

## Ne oldu

`python scripts/gorev_kutusu.py al --ajan utku --task-id UI-PROFILMENU-POPOVER-02` exit 1:

```
HATA: UI-PROFILMENU-POPOVER-02 icin talimat (brif) yok. Once orkestrator
`gorev_at.py at --talimat ...` veya `gorev_guncelle(talimat=...)` ile brif
yazmali; bilincli atlamak icin --zorla kullan.
```

Posta kutusunda (`bak --ajan utku`) görev **görünmüyor**. Tek bekleyen: `ALTYAPI-SQLITE-INIT` (P1) — kapsam dışı, alınmadı.

---

## Kök neden

Brif dosyası **diskte mevcut ve tam**:
`data/orchestrator/brief_UI-PROFILMENU-POPOVER-02_utku.md` (120 satır, 6 kabul kriteri + teslim listesi)

Ancak pano kaydındaki `talimat` alanı **boş**. D-66 kapısı bu yüzden tetikliyor.

Yani: brif yazılmış ama panoya bağlanmamış. Dosya adı da D-55 kalıbına uymuyor —
mevcut: `brief_UI-PROFILMENU-POPOVER-02_utku.md`
beklenen: `UI-PROFILMENU-POPOVER-02_brif_2026-09-20_uretim.md`

---

## Neden `--zorla` kullanılmadı

D-66 metni: *"Orkestratör brifsiz görev atarsa YASU/UTKU teslim ETMEYECEKTİR."*
`--zorla` bu kapıyı bilerek atlamak olur = kural ihlali. Talimat alanını yazmak
orkestratör yetkisi (D-58), üretim rolü kapsamı dışı.

---

## Bulgular

- 🔴 **Pano `talimat` alanı boş** — brif diskte var ama bağlanmamış. Zincir tetikleyicisi (`gorev_zinciri`) UI-MENUTREE-02 done olunca talimat alanını doldurmamış olabilir; zincir mekanizması kontrol edilmeli.
- 🟡 **Brif dosya adı D-55 dışı** — `brief_<TASK>_<ajanadı>.md` kalıbı hem İngilizce `brief` kullanıyor hem ajan adını dosya adına yazıyor (D-55 yasak). Rol son eki olmalı.
- 🔵 **Öneri:** `gorev_at.py at` brif path'ini doğrularken dosya adı kalıbını da denetlesin; yanlış adlandırılmış brif panoya girmesin.

---

## Eksik / erteleme

Brif içeriğinin tamamı okundu, iş yapılmaya hazır. Talimat alanı bağlanır bağlanmaz
6 kabul kriteri (st.popover migration, state mutasyonu kaldırma, form/deep-link,
emoji kaldırma, a11y, test güncellemesi) uygulanabilir. Tahmini süre değişmedi: 2s.

---

## KAHİN için elle tetikleme (D-65 bypass)

Orkestratör aşağıdakini çalıştırırsa blokaj kalkar:

```
python scripts/gorev_at.py guncelle --task-id UI-PROFILMENU-POPOVER-02 --talimat "Brif: data/orchestrator/brief_UI-PROFILMENU-POPOVER-02_utku.md"
```

Sonrasında üretim rolü şunu çalıştırır:

```
python scripts/gorev_kutusu.py al --ajan utku --task-id UI-PROFILMENU-POPOVER-02
```
