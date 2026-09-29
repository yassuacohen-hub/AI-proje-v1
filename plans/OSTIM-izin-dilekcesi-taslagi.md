# OSTIM Organize Sanayi Bölgesi Müdürlüğü
# Ticari Veri Kullanımı İzin Talebi — TASLAK

> **DURUM: TASLAK — gönderilmemiştir.** Resmî yanıt kurumun adına
> yazılmalı; gönderimi **KAHİN** yapar (bkz. `plans/BRIEF`).
> Hazırlayan: yasu (D-283) · Tarih: 2026-09-29

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

**Talep edilmeyenler:** vergi kimlik numarası, ortak bilgisi, temsilci
kimlik bilgisi, mali/finansal tablo verisi. Bu alanlar kapsam **dışındadır**.

## 3. Kaynak ve doğruluk

| Ölçüm | Değer |
|---|---|
| Firma sayisi | 8.473 uye firmasi (sayfada yazili: 'Toplam 8473 sonuç') |
| Listeleme | 29 sayfa, 300 firma/sayfa (son sayfa 73) |
| Detay adresi | https://ostim.org.tr/firmalar/<slug> (kalici) |
| Politika | https://ostim.org.tr/kurumsal/gizlilik-politikasi |
| Mevcut kullanim kosulu | “bilgi amaçlı ve ticari olmayan kullanım için hazırlanmıştır” |

## 4. Kullanım taahhüdü

1. Veriler **yalnızca** belirtilen ticari amaçla kullanılacaktır.
2. Kaynak belirtilecektir: *“Kaynak: OSTİM OSB”*.
3. Veriler **üçüncü taraflara satılmayacak, dağıtılmayacaktır.**
4. İçe aktarım gerekirse yazılı izin ayrıca alınacaktır.
5. Maskeli veriler (KVKK gereği) **kopyalanmayacaktır.**
6. Veri seti **6 ayda bir** güncellenecektir.
7. Kurumun talebi üzerine **derhal** silinir.

## 5. Teknik taahhüt

- `robots.txt` kurallarına **uyulacaktır** (ölçüldü: yalnız
  `/admin/`, `/portal/`, `/auth/` yasak).
- İstekler arası **en az 2 saniye** beklenecektir.
- Sahte kullanıcı adı/tampon **kullanılmayacaktır**; sabit ve
  gerçek User-Agent gönderilecektir.
- Günlük istek sayısı **sınırlı** tutulacaktır (isteğe göre:
  günde 500 firma detayı).

## 6. İletişim

- **Yetkili**:
- **Telefon / E-posta**:

---

## Ek — Ölçüm dayanağı (kanıt dosyaları)

- `data/karsilastirma_raporu.json` — kolon bazlı doluluk ölçümü
- `data/ostim_kaynak_olcumu.json` — erişim + robots.txt ölçümü
- `data/ostim_gizlilik_bolumler.json` — kullanım koşulu alıntısı
- `docs/BORC_DEFTERI.md` D-281 / D-282 / D-283
