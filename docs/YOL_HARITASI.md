# Yol Haritası — Huginn Data Insights

> Bu dosya **özet ve işaretçidir**, kopya değildir. Ayrıntı: [`docs/BORC_DEFTERI.md`](BORC_DEFTERI.md),
> kural ve karar kaydı: [`AGENTS.md`](../AGENTS.md), kapsam: [`docs/HEDEF_VERI_KAPSAMI.md`](HEDEF_VERI_KAPSAMI.md).
> Her satır bir borç kimliğine veya D numarasına bağlıdır. **Ölçülmemiş sayı yazılmaz** — "ölçülmedi" yazılır.
> Son güncelleme: D-299 turu (2026-09-29).

---

## 1. Bugünkü gerçek

Süsleme yok. D-295'in ölçüm hükmü ve bu turda ölçülenler:

| Ölçüm | Değer | Kaynak |
|---|---|---|
| Firma (canlı Postgres `companies`) | 9.412 (OSB üyesi 9.409) | D-295 |
| Ortalama kimlik tamlığı | **3,72 / 10** | D-295 |
| 8+ bandındaki firma | **0** | D-295 |
| Vaat karşılanma | **%14** | D-295 |
| Adreste "ankara" geçmeyen | %82,7 | D-295 |
| Posta kodu dolu | 0 | D-295 |

Panel doluluk oranları — **D-299 şablon kesimi sonrası** (canlı ölçüm, 9.409 OSB kaydı):

| Alan | Dolu | Oran | Not |
|---|---|---|---|
| NACE | 8.289 | %88,1 | puanlanmıyor → §5 |
| Telefon | 8.251 | %87,7 | — |
| Adres | 5.711 | %60,7 | kesim öncesi %61,6 |
| E-posta | 4.021 | %42,7 | kesim öncesi %42,9 |
| Web Sitesi | 2.781 | **%29,6** | **kesim öncesi %57,9** |
| VKN | 5 | %0,1 | — |
| OSB Parsel | 19 | %0,2 | — |

**Ürün bu haliyle satılabilir değil.** Tek satır özet: iki alan (telefon, NACE) taşıyor,
kimlik alanları (VKN, parsel, posta kodu) fiilen yok.

---

## 2. Darboğaz

Tek cümle: **kapalı kaynaklar**. Aşağıdaki iki kapı açılmadan kimlik alanları dolmaz.

| Kapı | Bugün | Açılırsa | Süre |
|---|---|---|---|
| MERSIS (`mersis_number`) | **%0** — kolon tamamen boş (D-299 ölçümü) | ölçülmedi — A/B seçimi yapılmadan tahmin edilemez | ölçülmedi |
| OSTİM (yazılı izin, `BORC-D-281`) | izinsiz tarama yapıldı, veri izole klasörde bekliyor | adres **+1.427**, e-posta **+982**, telefon **+0** (bu tur ölçüldü) | yazma işi ölçülmedi |

OSTİM satırı ölçülmüş, MERSIS satırı **ölçülmedi** — karar gelmeden ölçülemez de.

---

## 3. Karar bekleyenler (PO)

Hiçbiri ajan tarafından kesilemez (D-8, D-226).

| Konu | Ölçülmüş bedel / fayda | İşaretçi |
|---|---|---|
| **OSTİM verisinin `companies`e yazılması** | 3.338 kayıt hazır. Eşleşen 1.577; **adres kazancı 1.427**, **e-posta 982**, **telefon 0**. Canlıda hiç olmayan 1.742 kayıt. Yazma **yapılmadı** | `BORC-D-281`, bu tur ölçümü |
| **OSTİM yazılı izni** | Tarama izinsiz yapıldı (yasu kendi beyan etti). Hukuki risk ölçülmedi | `BORC-D-281` |
| **MERSIS A/B** | ölçülmedi | D-295 |
| **KVKK-TCKN-02** | ölçülmedi | `BORC-KVKK-TCKN-02` |
| **KAPSAM-HEDEF-01** | ölçülmedi | `BORC-KAPSAM-HEDEF-01` |
| **VERI-02** | ölçülmedi | `BORC-VERI-02` |
| **Üst depo özel repo** | ölçülmedi | D-295 devir |
| **Yazma kapısı birleştirme** | ölçülmedi | D-295 devir |
| **Şablon verinin silinmesi** | ~2.769 kayıt (bkz. §5). D-299'da **silinmedi**, yalnız sayılmadı. Silme kararı PO'da | D-299 |
| **Mükerrer tekilleştirme** | yasu ölçtü: 16 unvan grubu → 9 birleştirilebilir, 7 ayrı kalmalı. Uygulanmadı | yasu, bu tur |

---

## 4. Kaynak bekleyenler

Dış veri gelmeden kod yazmak boşa iş.

| Borç | Durum |
|---|---|
| `BORC-VERI-CALISAN-01` | `employee_count*` üç kolon da **%100 boş** (D-299 ölçümü) |
| `BORC-VERI-ILAN-01` | `job_postings` 8 kayıt — istatistik üretemez |
| `mersis_number`, `tax_office`, `establishment_date`, `company_type` | dört kolon da **%100 boş** (D-299 ölçümü) |

---

## 5. Şimdi kesilebilir olanlar

Dış kaynağa bağlı **değil**. Etki sırasına göre:

| # | İş | Durum | İşaretçi |
|---|---|---|---|
| 1 | Şablon değer yalanı — `isim.org.tr` ×2142, `ostimistihdam.com` ×474, `ostimonline` ×49, `Adres bilgisi girilmemiştir.` ×87, `bilinmeyen@bilinmeyen.com` ×17 | **KESİLDİ** — Web Sitesi %57,9→%29,6 | D-299 |
| 2 | `admin_executive._firma_kayitlari()` canlıda patlıyordu (kolon adı + naive/aware datetime + Decimal/float) | **KESİLDİ**, kırarak doğrulandı | `BORC-PANEL-SAHTE-TEST-01` |
| 3 | `admin_quality` / `admin_kpi` "hepsi %0 eksik" yalanı + transaction abort | **KESİLDİ** | D-249 |
| 4 | NACE etiketi export çıkış kapısına bağlandı + `nace_metni` NaN sızıntısı | **KESİLDİ** | D-287 |
| 5 | `load_risky_companies` hatayı yutuyor → kullanıcı "riskli firma yok" sanıyor | **AÇIK** | D-249 ihlali |
| 6 | `tests/test_admin_kpi.py` **hiç yok** — panel testsiz | **AÇIK** | yeni borç |
| 7 | NACE %88,1 dolu ama puanlanmıyor; "tahmin" etiketiyle gösterim | **AÇIK** — D-287 puan vermemekte haklı, gösterim ayrı | D-287 |

---

## 6. Dondurulmuş / kapalı

| Konu | Neden |
|---|---|
| 76 index hayaleti | PO kararı — dondurulmuş | D-281 (AGENTS.md) |
| **9 boş kolon / 31 boş tablo** | Ölü mü bekleyen mi ayrılamadı; veri kaybı riski var → D-266 gereği **düşürülmedi**. Devir notu "28 kolon / 8 tablo" diyordu, **gerçek 9 ve 31** | D-266, D-299 |
| Otomasyon durdurma | PO kararı | D-295 devir |
| Git temizliği | PO kararı | D-295 devir |
| **D-281 numara çatışması** | `AGENTS.md` D-281 = index hayaleti, `BORC_DEFTERI.md` D-281 = OSTİM kaynak araştırması. **İki farklı karar, aynı numara.** Yasu'nun satırı → D-226 gereği dokunulmadı | `karar_no.py --al` çıktısı |

---

## Ölçülmedi diye yazılanlar

Bu haritada **13 satır "ölçülmedi"** taşıyor. Sayı uydurmak yerine boşluk bırakıldı (D-260: beyan kanıt değildir).
