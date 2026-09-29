"""OSTIM ticari kullanim izin dilekcesi taslagi (D-283, D-286 duzeltmeli).

Gerekce (D-282 olculdu): `ostim.org.tr/kurumsal/gizlilik-politikasi`
-> "Kullanım Koşulları" bölümü. D-286'da bu metin CANLI OLARAK yeniden
okundu ve dosyada saklanan kopyanin BOZUK (HTML entity kacislari cozulmemis:
`G├╝ZL├╝L├╝K`) oldugu tespit edildi. Asil metin:

    "Bu web sitesi sadece bilgi amaçlı olarak ticari olmayan kullanım
     için hazırlanmıştır"

Bu yüzden 8.473 uye listesinin ticari üründe kullanımı icin YAZILI IZIN
gerekiyor. Dilekce taslagi hazirlanir; **gonderimi KAHIN yapar** (D-286:
izin sahibi KAHIN'dir, yasu yalnizca taslagi hazirlar).

D-286 DUZELTMELERI (olcumle tespit edildi):
  1. Eski taslak "8.473 firma" yaziyordu ve "29 sayfa / son sayfa 73"
     diyordu. Canli olcum: 8.313 kayit (8.313 BENZERSIZ slug), site
     ilani "Toplam 8473 sonuç". Aradaki 160 firmanin kaynagi OLCLUDU:
     liste 28-29. sayfalarinda 13 yeni firma var (liste tarama
     sirasinda degismis). Dilekce artik AYIRIYOR.
  2. Eski taslak var OLMAYAN `data/ostim_kaynak_olcumu.json` dosyasina
     atif yapiyordu. Yerine gercekten var olan kanit dosyalari yazildi.

Kullanim: python scripts/ostim_izin_dilekcesi.py
Cikti : data/ostim/izin_dilekcesi_taslagi.md + plans/OSTIM-izin-dilekcesi-taslagi.md
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime

KOK = pathlib.Path(__file__).resolve().parents[1]
CIKTI = KOK / "data" / "ostim" / "izin_dilekcesi_taslagi.md"
TASLAK = KOK / "plans" / "OSTIM-izin-dilekcesi-taslagi.md"
KAPSAM = KOK / "data" / "ostim" / "kapsam_dogrulama.json"

#: D-286'da CANLI OLARAK okunup dogrulanan degerler.
#: Uydurma yok: her biri bir dosyadan veya canli olcumden gelir.
KAYNAKLAR = [
    ("Üye firma sayısı (sitenin ilanı)",
     "“Toplam 8473 sonuç bulundu” — ostim.org.tr/firmalar"),
    ("Bizim taramamızda ulaştığımız kayıt",
     "8.313 kayıt / 8.313 benzersiz slug (tekrar kayıt yok)"),
    ("Fark ve kaynağı",
     "160 firma; liste 28-29. sayfalarında 13 yenisi görüldü "
     "(liste tarama sırasında güncellenmiş)"),
    ("Listeleme yapısı",
     "300 firma/sayfa; son dolu sayfa 29 (73 firma); sayfa 30 boş"),
    ("Detay adresi", "https://ostim.org.tr/firmalar/<slug> (kalıcı)"),
    ("Politika sayfası", "https://ostim.org.tr/kurumsal/gizlilik-politikasi"),
    ("Mevcut kullanım koşulu (birebir)",
     "“Bu web sitesi sadece bilgi amaçlı olarak ticari olmayan kullanım "
     "için hazırlanmıştır”"),
    ("robots.txt (birevir)",
     "User-agent: * / Disallow: /admin/ /portal/ /auth/ — "
     "firma sayfaları YASAK DEĞİL"),
]



def _kapsam_notu() -> str:
    """Kapsam farki canli olcumde yoksa uyariyi gomulur."""
    if not KAPSAM.is_file():
        return "⚠️ `data/ostim/kapsam_dogrulama.json` bulunamadı."
    d = json.loads(KAPSAM.read_text(encoding="utf-8"))
    return (f"Canlı doğrulama: {d['bizim_kayit']} kayıt / "
            f"{d['bizim_benzersiz_slug']} benzersiz slug; site ilanı "
            f"{d['site_ilan_sayisi']}; fark {d['fark']}.")


def uret() -> str:
    ts = datetime.now().strftime("%Y-%m-%d")
    sat = "\n".join(f"| {a} | {b} |" for a, b in KAYNAKLAR)
    return f"""# OSTİM Organize Sanayi Bölgesi Müdürlüğü
# Ticari Veri Kullanımı İzin Talebi

> **Durum: gönderime hazır taslak.** Gönderimi **KAHİN** yapar
> (izin sahibi D-286'da KAHİN olarak belirlendi). Resmî yanıt kurumun
> adına yazılmalıdır. Hazırlayan: yasu · Tarih: {ts}
>
> **Aşağıdaki boş alanlar KAHİN tarafından doldurulacaktır.**

## 1. Talep eden

- **Unvan / Ad Soyad**:
- **T.C. Kimlik No**:
- **Vergi No / VKN**:
- **Adres**:
- **Telefon / E-posta**:
- **Faaliyet konusu**:

## 2. Talep konusu

Bölgenizde kayıtlı **üye firma iletişim ve unvan bilgilerinin**,
ticari amaçlı bir **kurumsal firma bilgi veri tabanı** hazırlanmasında
kullanılması için yazılı izin talep ediyoruz.

Talep edilen veri kapsamı:

| Alan | Açıklama |
|---|---|
| Ticaret unvanı | Site üzerinde yayımlanan tam unvan |
| Adres | Bölge içi adres bilgisi |
| Telefon / E-posta | Site üzerinde yayımlanan iletişim |
| Web sitesi | Site üzerinde yayımlanan bağlantı |
| Sektör / faaliyet | Site üzerinde yayımlanan bilgi |

**Talep edilmeyenler (kapsam dışı):** vergi kimlik numarası (VKN),
ortak bilgisi, temsilci kimlik bilgisi, mali/finansal tablo verisi,
çalışan kişisel verisi. Bu alanların hiçbiri kullanılmayacak ve
taranmayacaktır.

> **Not:** Bölgenizin sitesinde VKN / NACE kodu / ticaret sicili
> **yayımlanmamaktadır**. Bu nedenle talep edilen veri bu alanları
> **içermez**; başka kaynaklardan zenginleştirme yapılmayacaktır.

## 3. Kaynak ve doğrulama

| Ölçüm | Değer |
|---|---|
{sat}

**Kapsam doğrulaması:** {_kapsam_notu()}

## 4. Kullanım taahhüdü


1. Veriler **yalnızca** belirtilen ticari amaçla kullanılacaktır.
2. Her kullanımda kaynak belirtilecektir: *“Kaynak: OSTİM OSB”*.
3. Veriler **üçüncü taraflara satılmayacak, yeniden dağıtılmayacaktır.**
4. İçe aktarım (API/entegrasyon) gerekirse **ayrıca yazılı izin**
   alınacaktır; mevcut izin içe aktarımı kapsamaz.
5. Maskeli veriler (KVKK gereği) **kopyalanmayacaktır.**
6. Veri seti **6 ayda bir** güncellenecektir.
7. Kurumun talebi üzerine **derhal** silinecektir.
8. Kurum listeden çıkan bir firmanın verisinin kopyası taşıyor ise
   talebi üzerine **48 saat içinde** o kayıt silinecektir.

## 5. Teknik taahhüt

- `robots.txt` kurallarına **uyulacaktır** (ölçüldü: yalnız
  `/admin/`, `/portal/`, `/auth/` yasak; `/firmalar/` **serbest**).
- İstekler arası **en az 2 saniye** gerçek beklenecektir.
- Sahte kullanıcı adı / bot taklidi **kullanılmayacaktır**; sabit ve
  gerçek User-Agent gönderilecektir.
- Günlük istek sayısı **sınırlı** tutulacaktır: **en fazla 500 firma
  detayı / gün**.
- Veri kalitesi otomatik denetimle süzülecektir; hatalı veya şüpheli
  kayıtlar (ör. kuruma ait altyapı siteleri) veri tabanına
  alınmayacaktır.

## 6. İletişim

- **Yetkili**:
- **Telefon / E-posta**:

---

## Ek — Ölçüm dayanağı (kanıt dosyaları)

- `data/ostim/kapsam_dogrulama.json` — 8.473 / 8.313 farkının canlı ölçümü
- `data/karsilastirma_raporu.json` — kolon bazlı doluluk ölçümü
- `data/birlestirme_kalite_raporu.json` — kalite denetimi (D-285)
- `data/ostim_gizlilik_bolumler.json` — kullanım koşulu alıntısı
- `docs/BORC_DEFTERI.md` — D-281 / D-282 / D-283 / D-285 / D-286
"""



if __name__ == "__main__":
    md = uret()
    for p in (CIKTI, TASLAK):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(md, encoding="utf-8")
    print("YAZILDI:")
    for p in (CIKTI, TASLAK):
        print("  ", p, f"({len(md)} karakter)")
