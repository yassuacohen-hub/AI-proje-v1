# VERI-LONCA-FIRMA-01 — Brief (yasu)

**Başlık:** [VERI] lonca firma bilgi ucunu tarama ile ölç → firma kaydı raporu (5g)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `data/pilots/VERI-LONCA-FIRMA-01/olcum.json`
**Bağımlılık:** `VERI-TOBB2B-KESISIM-01` (lonca keşfi)
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14)

> **Görev:** `VERI-LONCA-FIRMA-01` · **Sahip:** yasu
> **Atayan:** KAHİN (ihsan) · **Tarih:** 2026-09-30
> **Kararlar:** D-306 (bildirme kuralı), D-307 (bu pilot)

## Neden

KAHİN ekran görüntüsü gönderdi ve **benim önceki tespitimi düzeltti**:

> *"ayrı görev aç ve son kontrolü ve kararı ihsan review yaparken versin tekrar
> emin ol ve iyice bak görmediğin şeyler varmı bakmadığın durumlar oluşmuşmu
> örnek şirket taramamda mail ve telefon buldum"*

**Haklı.** Önceki turda "GET ile arama sonucu gelmiyor, tarama yapılamaz"
dedim ve görevi kapattım. Oysa `/FirmaBilgisi?Id=` ucu **GET ile açılıyor**
ve ekranda görüldüğü gibi **adres, telefon, faks, e-posta, web** ve
**firma ürün grupları** içeriyor.

Ben o ucu **hiç denemedim**. Ana sayfadaki link taraması yetmedi çünkü
detay sayfaları arama sonucundan geliyor.

## Doğrulanacak varsayım

| Varsayım | Şu anki durum | Nasıl ölçülecek |
|---|---|---|
| `/FirmaBilgisi?Id=` GET ile veri verir | **TARAYICIDA DOĞRU** (KAHİN ekranı) | 1 Id ile tekrar ölç |
| Sayfada e-posta var | **DOGRULANDI** (ekranda `info@akarna.com.tr`) | Id ile çek |
| Sayfada telefon var | **DOGRULANDI** (`0 (312) 840-1595`) | Id ile çek |
| Sayfada web var | **DOGRULANDI** (`www.akarna.com.tr`) | Id ile çek |
| Sayfada adres var | **DOGRULANDI** (Açıcı, Ankara) | Id ile çek |
| Firma ürün grupları var | **DOGRULANDI** (ürün listesi ekranda) | Id ile çek |
| POST hâlâ WAF reddi | VAR (3/3) | Değişti mi, ölç |
| **Id nereden geliyor?** | **BİLİNMİYOR** | Arama akışını çöz |

> **Eksik ölçüm kuralı (D-217):** Ölçülmeyen kalem "bilinmiyor" yazılır,
> tahminle doldurulmaz.

## Bilinen engel (DURMAK ZORUNDA)

**Geçerli `Id` değeri yok.** KAHİN'in ekran görüntüsündeki URL
`...Id=GılaıBıA%2BpzS%2FLpqr6uYKmeSq...` şeklinde **kırpılmış**.
Bu Id ile yapılan 2 deneme de (tek istek + tarayıcı benzeri akış)
**boş şablon** döndü: HTTP 200, 82.176 bayt, ancak firma alanları yok.

> Boş dönen sayfada `10.11`, `10.12`, `13.92` … **sektör kodları** var —
> yani geçersiz Id'de sistem o firmayı değil **sektör listesini** basıyor.

**Bu görev `Id` üretmeden ilerlemez.** İki yol:
1. KAHİN'den **bir tam `Id`** istenmesi (en hızlı, 1 dakika)
2. `/Ara` POST'unun WAF'a takılmadan çalıştırılması → sonuç listesi → Id'ler

## Adımlar

1. **Geçerli `Id` edin** (yol 1 veya 2). Edilemezse **dur ve ihsan'a sor**.
2. 1 Id ile `/FirmaBilgisi` aç, **7 alanı** çıkar (unvan, adres, telefon,
   faks, e-posta, web, ürün grupları).
3. **POST'u yeniden dene** — WAF durumu değişmiş mi, ölç (n/3).
4. `/Sektor?sektorKodu=` sayfasında `FirmaBilgisi` Id'si var mı, ölç.
5. Id toplama yolu bulunursa: **5 Id** ile tekrar ölç (fazla yük yok).
6. Rapor + Hub + `teslim`.

> **Ölçek kuralı:** 5 Id fazlası değil. WAF reddi sürüyorsa ** DUR **,
> raporla, ihsan'a bildir. KAHİN'den izin alınmadan toplu tarama yapılmaz.

## Kurallar (D-196 · D-306)
- Kanıtsız "yapıldı" satırı yasak.
- **Ölçüm/bulgu/karar → ajan chat + ihsan'a.**
- **Supabase'e yazma yok.**
- WAF reddi bir **ölçüm sonucudur**; bypass denenmez.

## Kabul kriteri
- [ ] Geçerli Id ile 7 alan çıkarıldı (veya "ölçülemedi" + sebep)
- [ ] POST WAF durumu yeniden ölçüldü (n/n)
- [ ] Id üretim yolu belirlendi ya da **yokluğu kanıtlandı**
- [ ] 5 Id ölçümü yapıldı (WAF izin verdiyse)
- [ ] Rapor yazıldı, Hub güncellendi

## Ajan chat zorunlu (D-210 · D-217)

Sessiz çalışma yasak. Ölçüm görevi: **ölçüm tutmazsusam susmak, ölçümü
uydurmakla aynı şeydir.**

```bash
python scripts/ajan_chat.py ac yasu VERI-LONCA-FIRMA-01 "<bulgu>" --cozum "<öneri>"
python scripts/ajan_chat.py oku --task_id VERI-LONCA-FIRMA-01
python scripts/chat_gonder.py --to ihsan --type bilgi --task-id VERI-LONCA-FIRMA-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id VERI-LONCA-FIRMA-01 \
  --ozet "<sayı içeren özet>" --cikti plans/rapor_yasu_VERI-LONCA-FIRMA-01.md
```

Özet **sayı** içerecek. "İnceledim, veri var" reddedilir.

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[plans/brief_yasu_VERI-TOBB2B-KESISIM-01]]
- [[plans/_brief_sablon]]
- [[hubs/OSINT_VERI_TOPLAMA_HUB]]