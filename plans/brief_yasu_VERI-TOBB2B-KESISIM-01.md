# VERI-TOBB2B-KESISIM-01 — Brief (yasu)

**Başlık:** [VERI] TOBB2B tekliflerini OSB verisiyle kesistir (pilot 20 teklif)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `data/pilots/VERI-TOBB2B-KESISIM-01/teklifler.json`
**Bağımlılık:** yok
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14)

> **Tek brif kuralı (D-217):** Bir görev = bir brif.

> **Görev:** `VERI-TOBB2B-KESISIM-01` · **Sahip:** yasu
> **Atayan:** KAHİN (ihsan) · **Tarih:** 2026-09-29
> **Kararlar:** D-306 (bildirme kuralı), **D-307 (bu pilot)**

## Neden

KAHİN talebi (2026-09-29):

> "analizi biraz genişlet ve bu konuda kendine bir görev aç ve onu yapıp
> review kısmına at, daha fazla ne çıkartabilirsin tekrar bak daha iyi
> düşün"

### KESİF SONUCU (ölçüldü, varsayım yok)

**1. sanayi.org.tr → KAMUYA AÇIK VERİ YOK**
- AngularJS SPA, HTTP 200 ama 3.645 bayt **boş iskelet**
- 28 API ucu bulundu, **hepsi 401** → yetki gerekli
- Sanayi Veri Tabanı üyelere açık

**2. tobb2b.org.tr → TİCARİ İŞLEK İŞARETİ AÇIK**
- SSL sertifika geçersiz ama `http://` ile **HTTP 200** (30.509 bayt)
- `teklif_goster.php?Id=N` **açık**, ID ile erişilebilir
- Alanlar: Teklif No, tarih, **ülke**, **NACE sektör**, İngilizce açıklama
- Metinlerde *"seeking international importers/distributors"*
  → **firma satış hedefi** ifadesi

### ASIL DEĞER

Elimizdeki veri **tedarikçi** tarafı. TOBB2B teklifleri **talep eden**
taraf. İkisini eşleştirmek tek başına hiçbir kaynağın vermediği şey.

## Doğrulanacak varsayım

| Varsayım | Ölçüm | Durum |
|---|---|---|
| NACE kodu ile eşleştirme kurulabilir | 8.987 kayıtta **sadece 12'sinde** dolu (%0.1) | ❌ **KURULAMAZ** |
| Eşleştirme sektör **metni** ile kurulabilir | 29 farklı metin, 495 kayıt | ✅ |
| TOBB2B teklifleri okunabilir | 20/20 okundu | ✅ |
| 50 Id denemesinde kaçı dolu | **20/50 = %40** | ✅ |
| Ülke alanı çıkıyor | TR/NL/DE/PK/CN/BR | ✅ |
| NACE bölüm kodu doğru | 10=gıda, 13=tekstil, 24=metal | ✅ |

## Adımlar

### Faz A — Toplama (tamamlandı)
1. ✅ 20 teklif okundu (`teklif_goster.php?Id=`)
2. ✅ Alanlar ayrıştırıldı: no, tarih, ülke, NACE, açıklama
3. ✅ `ortak_arayan` işareti: *"seeking/distributors/importers"*

### Faz B — Eşleştirme (tamamlandı)
4. ✅ NACE **bölüm kodu** ile kendi sektörümüze bağlandı
5. ✅ 11/20 teklif eşleşti, **1.575 firma**

### Faz C — Rapor
6. Bulguyü raporla + review'a teslim et
7. Karar gereken noktaları ihsan'a yaz

## Kabul kriteri
- [x] 20 teklif okundu
- [x] Ülke + NACE + ortak_arayan çıkarıldı
- [x] NACE bölüm kodu ile eşleştirme yapıldı
- [x] Eşleşme sayısı ölçüldü (11/20 teklif, 1.575 firma)
- [x] Yanlış eşleşme kontrol edildi (tekstil→gıda hatası düzeltildi)
- [ ] Rapor + review teslim
- [ ] Ölçek kararı (20 teklif mi, tüm havuz mu)

## Bulgu (ölçülen)

```
20 teklif okundu (50 Id denendi, %40 dolu)
11/20 teklif kendi verimizle eşleşti
1.575 firma eşleşti
  metalurji ve makina sanayi : 7 eşleşme
  gida                       : 3
  metal ve metal işleme      : 3
  tekstil                    : 1
  mobilya                    : 1
  elektrikli cihaz sanayi    : 1

Ortak arayan teklif (niyet beyanı): 5 teklif / 7 eşleşme / 473 firma
```

**Yorum:** 20 tekliften 9'u eşleşmedi — çünkü NACE bölümü bizim
sektörlerimizle örtüşmüyor (konaklama, telekom, yazılım vb.).
Bu **kötü haber değil**: eşleşmeyen teklif bizim müşterimize
göre ilgisiz demektir.

## Kurallar (ADMIN-KİT · D-196)
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir.
- **Teslimden önce** `**Hub:**` dosyasının "Kapanan işler" bölümüne yaz (B-14).
- **D-306 bildirme kuralı:** ölçüm/bulgu/karar → chat'e.

## ⚠️ Riskler

| # | Risk | Etki | Önlem |
|---|---|---|---|
| R1 | Toplu tarama izni yok | Yasal risk | 20 teklif ile sınırlı |
| R2 | TOBB2B üye içeriği | Sözleşme riski | Ticari kullanım kararı KAHİN |
| R3 | NACE eşleştirme kaba | Yanlış eşleşme | Bölüm kodu kullanıldı, doğrulandı |
| R4 | %40 doluluk | Havuz tahmini zor | Kesin sayım yapılmadı |
| R5 | SSL geçersiz | `verify=False` gerek | Zaten http:// ile çalışıyor |

## Ajan chat zorunlu (D-210 · D-217)
```bash
python scripts/ajan_chat.py ac yasu VERI-TOBB2B-KESISIM-01 "<bulgu>" --cozum "<öneri>"
python scripts/chat_gonder.py --to ihsan --type koordinasyon --task-id VERI-TOBB2B-KESISIM-01 --mesaj "<metin>"
```

## Teslim
```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id VERI-TOBB2B-KESISIM-01 --ozet "<özet>"
```

## Önce oku
- `scripts/kaynak_kesif.py` → iki sitenin teknik keşfi
- `scripts/veri_tobb2b_kesisim.py` → pilot analizi
- `data/pilots/VERI-TOBB2B-KESISIM-01/ozet.json` → ölçüm sonucu

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
- [[plans/_brief_sablon]]
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[Huginn Data Insights/plans/brief_yasu_VERI-OSB-Tazelik-01]]
