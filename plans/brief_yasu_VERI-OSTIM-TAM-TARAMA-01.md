# BRİF — OSTIM Detay Taraması ve Tam Veri Denetimi

> **Görev:** `VERI-OSTIM-TAM-TARAMA-01` · **Sahip:** yasu
> **Atayan:** KAHİN (ihsan) · **Öncelik:** P1 · **Tarih:** 2026-09-29
> **Kararlar:** D-283, D-285, D-286, D-289, **D-290**

## 1. Neden bu görev

KAHİN talebi (2026-09-29):

> "eski database tekrar kirli ve hatalı olmasını istemiyorum, her türlü
> önlemi al, önce tara sonra ölçelim, tamamını, yanlış mükerrer kayıt
> olmasın, şirket verileri kontrol ederek görevi at, raporu buna göre
> oluştur."

Üç ayrı şey talep ediliyor: (a) **önlem**, (b) **önce tara**, (c) **rapor**.

## 2. Önce oku (asıl bilgi kaynağı kodu)

- `docs/BORC_DEFTERI.md` → **D-283** (politika P-1..P-10), **D-285**
  (kalite ölçümü), **D-286** (kazıyıcı düzeltmeleri), **D-290** (bu görev)
- `docs/VERI_KAYNAK_KURALLARI.md` → K-1 (sessiz tekrar yasak),
  K-2 (kolonlar karışmaz), K-3 (atomik yazım)
- `scripts/ostim_detay_tamamla.py` → docstring'deki P-1..P-10 listesi

## 3. §Tuzaklar (en pahalı bilgi)

1. **`"w"` ile yazmak yığı siler.** 3.339 kayıt `--limit 500` ile
   parçalanırsa, her parça öncekini **kaybeder**. D-289'da düzeltildi
   ama test ederken bunu bil.
2. **`time.sleep` beyaz satırdı.** Politika "2 sn" diyordu, kod
   hiç beklemiyordu. Geri **alınmadığına** emin ol.
3. **Regex doğru olsa bile sahte hesap üretir.** `/accounts/login/`
   → `{"instagram": "accounts"}`. `_gercek_hesap_mi()` var.
4. **Tahminle filtre yazma.** D-285'te telefon listesi uydurulmuştu;
   ölçüm 5 tekrar dedi ve liste **boş bırakıldı**. Ölç, sonra yaz.
5. **Güçlü konsol çıktısı UTF-8 bozuk görünür.** `├╝` gibi karakterler
   PowerShell kaynaklı; **dosyada Türkçe karakterler doğru**. Panik
   etme, `unicode_escape` ile doğrula.
6. **K-2 kaçışı "0" çıkmak kolay, "temiz" demek değil.** Satır
   denetimi gerekir: 5/5 geçen pilot bile `accounts` sahtesi taşıdı.

## 4. §Sabitler

| Sabit | Değer | Nerede |
|---|---|---|
| DIZIN | `https://ostim.org.tr` | `ostim_detay_tamamla.py` |
| GECIKME | `2.0` sn (P-3) | aynı |
| TEKIL_ESIK | `0.95` (P-6) | aynı |
| UA | gerçek Chrome UA, değiştirme (P-1) | aynı |
| KAZANIM | `data/ostim/tamamlama_2026-09-29/` | D-290 izole çıktı |
| KILIT | `data/ostim/kaynak_kilidi.json` | D-290 koruma kilidi |

## 5. Yapılacaklar

1. **Önlem (D-290 zaten kuruldu — doğrula)**
   - Çıktı izole klasörde: `data/ostim/tamamlama_2026-09-29/`
   - Kaynak dosyalar SHA-256 kilitli; değişmişse tur **durdurulur**
   - Kazıyıcı SQLite'a dokunmaz (ölçüldü: 0 referans)
   - **Doğrulama:** `python scripts/ostim_veri_koruma.py`
2. **Önce tara** — 3.339 eksik detay, 2 sn aralıkla.
   Günlük üst sınır **500 detay/gün** (dilekçe taahhüdü).
3. **Sonra ölç** — `scripts/birlestirme_kalite_kontrol.py` + mükerrer
   denetimi: aynı `slug` ve aynı normalize unvan sayısı.
4. **Şirket verisi kontrolü** — `companies` tablosu hâlâ 8.313 temiz
   kayıt. Tarama sonrası **aynı sayı** olmalı; değiştiyse raporla.
5. **Rapor yaz** — `data/ostim/tamamlama_2026-09-29/rapor.md`

## 6. §Doğrulanacak varsayım

| Varsayım | Nasıl doğrulanır |
|---|---|
| Tarama kaynak dosyalara dokunmaz | `sha256sum` öncesi/sonrası aynı |
| `companies` tablosu bozulmaz | 8.313 → 8.313 |
| Mükerrer kayıt oluşmaz | `tekil_slug == kayit` |
| Politika gerçekten uygulanıyor | 2 kayıt arası süre ≥ 2 sn |
| 3.339 eksik kayıt gerçekten eksik | liste ∩ detaylı kümesi |

## 7. Teslim

`plans/rapor_yasu_VERI-OSTIM-TAM-TARAMA-01.md` + ajan chat bildirimi.
