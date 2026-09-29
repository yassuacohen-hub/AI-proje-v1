# RAPOR — OSTİM Tam Tarama ve Veri Denetimi

> **Görev:** `VERI-OSTIM-TAM-TARAMA-01` · **Ajan:** yasu
> **KAHİN talebi (2026-09-29):** "eski database tekrar kirli ve hatalı
> olmasını istemiyorum, her türlü önlemi al, önce tara sonra ölçelim
> tamamını, yanlış mükerrer kayıt olmasın, şirket verileri kontrol
> ederek görevi at, raporu buna göre oluştur."
> **Kararlar:** D-290 · D-291 · D-292 · D-296 · D-297
> **Durum: ✅ TAMAMLANDI** — 3.338 kayıt tarandı

## 1. Sonuç

| Ölçüm | Değer |
|---|---|
| Taranan kayıt | **3.338** |
| Hata | **1** (404 — siteden kaldırılmış slug) |
| P-8 imza tekrarı | **0** |
| Mükerrer slug | **0** |
| K-2 kaçışı | **0** |
| Rakamlı sektör | **0** |
| Kaynak dosya bozulması | **Yok** (SHA-256 bit düzeyinde aynı) |

## 2. Önlemler (KAHİN'in asıl talebi)

| # | Önlem | Kanıt |
|---|-------|-------|
| 1 | **Çıktı izole klasörde** — `data/ostim/tamamlama_2026-09-29/` | 2 kaynak dosyanın SHA-256'sı tarama boyunca **aynı** |
| 2 | **SHA-256 koruma kilidi** | Bozma testi: dosya bozulunca tur durdu |
| 3 | **SQLite'a sıfır dokunuş** | `companies` tablosu 8.313 → **8.313** |
| 4 | **Kısmi yazım (D-291)** | Süreç öldürüldü, 3.303 kayıt **korundu**, kaldığı yerden devam etti |
| 5 | **Atomik yazım (K-3)** | `.tmp` + `replace()` |
| 6 | **Politika uygulandı** | 2,4 sn/kayıt (P-3 gerçekten çalışıyor) |

## 3. Zenginleşme

| Alan | Önce (bu kayıtlarda) | Sonra |
|---|---|---|
| Adres | %0 | **%97,2** |
| Telefon | %0 | **%91,6** |
| E-posta | %0 | **%91,4** |
| Web sitesi | %0 | %4,6 |
| Sosyal medya | %0 | %0,4 |

**Sektör %0** — sayfanın bu bloklarında sektör gerçekten yazmıyor.
Eski dosyada görünen %100 doluluk sahteydi (D-292: sıra numarası
sızıntısı).

## 4. Mükerrer kayıt denetimi

`scripts/ostim_mukerrer_denetimi.py` → `mukerrer_raporu.json`

- **Mükerrer slug: 0** — bizim hatamız değil
- **16 mükerrer unvan grubu:**
  - **9 → birleştirilebilir** (aynı unvan + aynı telefon)
  - **7 → ayrı kayıt korunacak** (ör. `ÖMER BULUT` ×2, `MURAT GÜLER`
    ×2 — adresleri farklı, sitede `-2` ekli ayrı slug)

Kaynak dosyalara **dokunulmadı**; tekillestirme kararı ayrıca verilecek.

## 5. Şirket verisi kontrolü

`company_master.db` → `companies` = **8.313** (öncesi ve sonrası aynı).
Yeni veri bu tabloya **yazılmadı**. Birleştirme/onay olmadan hiçbir
şey işlenmeyecek.

## 6. Dürüstlük notları

- Bu tarama **izin alınmadan** yapıldı. D-281 borcu (yazılı izin)
  hâlâ açık; KAHİN "izinli devam et" dediği için sürdürüldü.
- 1 kayıt 404 verdi: `objektf-proje-kopyal` — siteden kaldırılmış.
  Veri uydurulmadı, kayıt **atlandı**.
- "K-2 kaçış = 0" D-292'den önce **eksik** bir sonuçtu; sektör kolonu
  denetlenmemişti. Şimdi kapsamlı.


## 1. Kısaca

Eski veri **dokunulmadan** korundu; taramaya **tamamen izole** bir
klasörde başlandı. 1.000 kayıt tarandı: **sıfır hata, sıfır K-2 kaçışı,
sıfır mükerrer slug**.

## 2. Önlemler (KAHİN'in asıl talebi)

| # | Önlem | Kanıt |
|---|-------|-------|
| 1 | **Çıktı izole klasörde** — `data/ostim/tamamlama_2026-09-29/`. Mevcut hiçbir dosyaya dokunulmaz. | 3 kaynak dosyanın SHA-256'ı tarama boyunca **bit düzeyinde aynı** |
| 2 | **SHA-256 koruma kilidi** — kaynak dosya değişirse tur **durdurulur** | Bozma testi yapıldı: dosya bozulunca `"KAYNAK DOSYALAR DEĞİŞMİŞ…"` çıktı, geri alınınca serbest |
| 3 | **SQLite'a sıfır dokunuş** — kazıyıcı içinde `sqlite`/`INSERT` referansı **0** | `companies` tablosu 8.313 → **8.313** (ölçüldü) |
| 4 | **Kısmi yazım (D-291)** — süreç kesilirse veri kaybolmaz | Süreç çalışırken 503 → **603** satır oldu |
| 5 | **Atomik yazım (K-3)** — `.tmp` dosyası yazılır, sonra `replace()` ile değiştirilir | Yarım dosya bırakılmaz |
| 6 | **Politika gerçekten uygulanıyor** — P-3 2 sn bekleme, P-8 imza guard, P-1/P-2 robots kontrolü | 500 kayıt 1.198 sn = **2,4 sn/kayıt** (beklenen 2,0 + HTTP) |

## 3. Tarama sonucu (ilk 1.000 kayıt)

| Ölçüm | Değer |
|---|---|
| İşlenen | 1.000 (500 + 500) |
| Hata | **0** |
| P-8 imza tekrarı | **0** |
| Tekil slug | 503/503 → mükerrer **0** |
| K-2 kaçışı | **0** |
| Kalan | 2.336 |

### Doluluk (ilk 503 kayıt)

| Alan | Doluluk |
|---|---|
| E-posta | %94,6 |
| Adres | %97,6 |
| Telefon | %92,6 |
| Web sitesi | %4,6 |
| Sosyal medya | %0,8 |
| **Sektör** | **%0,0** |
| VKN | 0 (beklenen — OSTİM VKN yayımlamaz, D-282) |

**Adres/telefon/e-posta zenginleşmesi beklenen sonucu verdi.** Web
sitesi ve sosyal medya düşük çünkü bu alanlar sayfada nadiren var.
**Sektör %0 dikkat çekiyor** — mevcut 5.040 kayıtta sektör doluydu;
eksik kayıtlarda sayfa "Sektör" bloğu içermiyor olabilir. Tarama
bitince tekrar ölçülecek.

## 4. Mükerrer kayıt denetimi (KAHİN'in 2. talebi)

`scripts/ostim_mukerrer_denetimi.py` → `mukerrer_raporu.json`

- **Mükerrer slug: 0** — bizim hatamız değil
- **Mükerrer unvan: 2 grup** — incelendi ve **ayrı kayıt** olarak işaretlendi:

  | Unvan | Neden ayrı sayıldı |
  |---|---|
  | `ASAY LAZER KESİM…` (2 kayıt) | Adresler farklı: `1185. CADDE (ESKİ 17) 26` ↔ `OSTİM OSB MAH. 1185 CADDE NO:26-28` |
  | `ATASAM SAĞLIK…` (2 kayıt) | Adresler farklı: `…1151. SOKAK 1 91` ↔ `…1151. SOKAK 1 90` |

  Sitede `…-tik` ve `…-tik-2` olarak **ayrı slug'larda** listeleniyorlar.
  Telefonlar aynı, adresler farklı → **birleştirilmedi, korundu.**
  Birleştirme kararı ayrıca verilecek; araç kaynak dosyaya dokunmuyor.

## 5. Şirket verisi kontrolü (KAHİN'in 3. talebi)

`company_master.db` → `companies` tablosu: **8.313** (tarama öncesi ve
sonrası **aynı**). Yeni veri bu tabloya **yazılmadı**; tarama çıktısı
JSONL olarak izole klasörde bekliyor. Birleştirme/onay olmadan
`companies`'a **hiçbir şey işlenmeyecek**.

## 5.5 YENİ BULGU — eski verideki `sektor` kolonu **zaten sahte**

`firmalar_vkn_ekli.jsonl` (5.040 kayıt, 3 Eylül) denetlenince:

| Değer | Adet |
|---|---|
| `Otomotiv1163` | 940 |
| `Yapı ve İnşaat794` | 704 |
| `Makine ve Makine Ekipmanları757` | 574 |
| `İş Makinaları780` | 518 |
| `Metal ve Metal İşleme752` | 512 |

**Rakam içeren sektör: 5.040 / 5.040 = %100.** Sektör adının sonuna
**firma sıra numarası** yapışmış. Bu D-285'te ölçülen 10.002 kaçışın
bir parçasıydı ama o turda `sektor` kolonu denetlenmemişti —
`K-2 kaçış = 0` sonucu bu kolon için eksik kalmıştı.

Aynı dosyadaki diğer kirp de doğrulandı:
- `web_sitesi` = `https://www.ostimistihdam.com` (940 kayıt)
- `sosyal_medya` = `{"facebook": ".../OstimOSB", ...}`

**Sonuç:** Yeni parser bu alanları doğru ayıklıyor; yeni taramada
`sektor` **0/653 dolu** çünkü o bloklarda gerçekten sektör yazmıyor.
Eski dosyadaki doluluk (%100) **gerçek değil, sızıntıydı.**

**Ders:** "doluluk %100" tek başına kalite kanıtı değildir. Değerin
*içeriği* de denetlenmelidir — 5.040 kayıt boyunca aynı sayılar
eklenmiş bir kolon dolu görünür ama tek bir bilgi taşımaz.

## 6. Kalan iş

1. Kalan **2.336** kayıt taranacak (2 sn/kayıt ≈ 80 dk)
2. Tarama sonrası: `birlestirme_kalite_kontrol.py` + mükerrer denetimi
3. `sektor` %0 sorunu araştırılacak
4. **Onay olmadan** hiçbir veri `companies`'a yazılmayacak

## 7. Dürüstlük notu

- Bu rapor **ilk 1.000 kaydın** sonucudur, tamamının değil.
- 5/5 geçen pilot bile `accounts` sahtesi taşıdı; **"temiz" demek için
  satır denetimi şart.** Tam tarama sonrası aynı denetim yapılacak.
- `sektor` %0 şu an **açık bir bulgu**, çözülmedi.
