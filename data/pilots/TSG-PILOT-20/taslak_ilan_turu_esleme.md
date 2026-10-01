# TSG-04 taslak: `ILAN_TURU_ESLEME` sözlüğü (onay bekliyor)

**Kural (ürün sahibi, 2026-09-30):** konkordato/iflas/sermaye azaltımı → `negative`;
kuruluş/sermaye artırımı → `positive`; geri kalanı → `stable`.

**Kaynak:** `data/pilots/TSG-PILOT-20/etiket_tablosu.md` (65 ham etiket, 320 ilan).
**Kapsam:** 65/65 etiket sınıflandırıldı. `event_type` benim seçtiğim kısa koddur (serbestçe
değiştirilebilir — şemada CHECK kısıtı yok, sadece `direction` kısıtlı: 0003_intelligence.sql).

**Toplam:** positive 14 etiket / 155 ilan · negative 4 etiket / 6 ilan · stable 47 etiket / 159 ilan.

**⚠️ Belirsiz — kuralın kapsamadığı tek kalem:** `ŞUBE AÇILIŞ` (1 ilan). Kural yalnız
"kuruluş/sermaye artırımı" diyor, şube açılışı büyüme sinyali olsa da kural dışı — şimdilik
`stable` işaretledim, onayda düzeltilebilir.

| Etiket (ham, birebir) | Adet | event_type | direction |
|---|---|---|---|
| LİMİTED ŞİRKET (TADİL) | 51 | tadil | stable |
| ANONİM ŞİRKET (YÖNETİM - TEMSİL VE DİĞER) | 34 | yonetim_degisikligi | stable |
| LİMİTED ŞİRKET (YÖNETİM (MÜDÜR) - TEMSİL VE DİĞER) | 31 | yonetim_degisikligi | stable |
| LİMİTED ŞİRKET (SERMAYE ARTIRIMI) | 28 | sermaye_artirimi | positive |
| LİMİTED ŞİRKET (PAY DEVRİ) | 19 | pay_devri | stable |
| ANONİM ŞİRKET (YÖNETİM - TEMSİL VE DİĞER) TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer | 17 | yonetim_degisikligi | stable |
| LİMİTED ŞİRKET (KURULUŞ) | 13 | kurulus | positive |
| LİMİTED ŞİRKET (ADRES DEĞİŞİKLİĞİ) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Adres | 9 | adres_degisikligi | stable |
| ANONİM ŞİRKET (SERMAYE ARTIRIMI) | 8 | sermaye_artirimi | positive |
| ANONİM ŞİRKET (TADİL) | 8 | tadil | stable |
| LİMİTED ŞİRKET (SERMAYE ARTIRIMI) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Sermaye Artırımı | 7 | sermaye_artirimi | positive |
| LİMİTED ŞİRKET (YÖNETİM (MÜDÜR) - TEMSİL VE DİĞER) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer | 6 | yonetim_degisikligi | stable |
| ANONİM ŞİRKET (YÖNETİM - TEMSİL VE DİĞER) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer | 5 | yonetim_degisikligi | stable |
| DÜZELTME - BASKI KAYNAKLI | 5 | duzeltme | stable |
| ANONİM ŞİRKET (KURULUŞ) | 4 | kurulus | positive |
| ANONİM ŞİRKET (SERMAYE ARTIRIMI) TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Sermaye Artırımı | 4 | sermaye_artirimi | positive |
| DÜZELTME | 4 | duzeltme | stable |
| ALACAK ÇAĞRI (3) (S.AZALTIMI - DİĞER) | 3 | sermaye_azaltimi | **negative** |
| ANONİM ŞİRKET (YÖNETİM - TEMSİL VE DİĞER) TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer Değişiklik - Denetçi | 3 | yonetim_degisikligi | stable |
| DENETÇİ TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Denetçi | 3 | denetci_degisikligi | stable |
| LİMİTED ŞİRKET (SERMAYE ARTIRIMI) ORTAK SAYISI BİRDEN FAZLA LİMİTED ŞİRKET Değişiklik - Sermaye Artırımı | 3 | sermaye_artirimi | positive |
| LİMİTED'den ANONİM'e (TÜR DEĞİŞİKLİĞİ) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Nevi Değişikliği - Tür Değişikliği Nevi Değişikliği - Sözleşme | 3 | tur_degisikligi | stable |
| TEK ORTAKLIK BİLGİSİ PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer Değişiklik - Tek Pay Sahipliğinde Değişiklik | 3 | tek_ortaklik | stable |
| ANONİM ŞİRKET (SERMAYE ARTIRIMI) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Değişiklik - Sermaye Artırımı | 2 | sermaye_artirimi | positive |
| LİMİTED ŞİRKET (ADRES DEĞİŞİKLİĞİ) | 2 | adres_degisikligi | stable |
| LİMİTED ŞİRKET (AMAÇ VE KONU DEĞİŞİKLİĞİ) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Amaç ve Konu | 2 | amac_konu_degisikligi | stable |
| LİMİTED ŞİRKET (PAY DEVRİ) ORTAK SAYISI BİRDEN FAZLA LİMİTED ŞİRKET Değişiklik - Pay Devri | 2 | pay_devri | stable |
| LİMİTED ŞİRKET (PAY DEVRİ) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Pay Devri Değişiklik - Yönetim Kurulu / Yetkililer | 2 | pay_devri | stable |
| LİMİTED ŞİRKET (SERMAYE AZALTIMI) | 2 | sermaye_azaltimi | **negative** |
| LİMİTED ŞİRKET (YÖNETİM (MÜDÜR) - TEMSİL VE DİĞER) ORTAK SAYISI BİRDEN FAZLA LİMİTED ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer | 2 | yonetim_degisikligi | stable |
| ANONİM ŞİRKET (ADRES DEĞİŞİKLİĞİ) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Değişiklik - Adres | 1 | adres_degisikligi | stable |
| ANONİM ŞİRKET (ADRES DEĞİŞİKLİĞİ) TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Adres | 1 | adres_degisikligi | stable |
| ANONİM ŞİRKET (PAY DEVRİ) | 1 | pay_devri | stable |
| ANONİM ŞİRKET (PAY DEVRİ) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Tecil Dışı İlan (AŞ Pay Devri) - Pay Devri | 1 | pay_devri | stable |
| ANONİM ŞİRKET (PAY DEVRİ) TEK PAY SAHİPLİ ANONİM ŞİRKET Tecil Dışı İlan (AŞ Pay Devri) - Pay Devri | 1 | pay_devri | stable |
| ANONİM ŞİRKET (SERMAYE ARTIRIMI) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Değişiklik - Sermaye Artırımı Değişiklik - Genel Kurul İç Yönergesi | 1 | sermaye_artirimi | positive |
| ANONİM ŞİRKET (SERMAYE ARTIRIMI) TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Adres Değişiklik - Sermaye Artırımı | 1 | sermaye_artirimi | positive |
| ANONİM ŞİRKET (SERMAYE ARTIRIMI) TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Adres Değişiklik - Yönetim Kurulu / Yetkililer Değişiklik - Sermaye Artırımı Değişiklik - Tek Pay Sahipliğinde Değişiklik | 1 | sermaye_artirimi | positive |
| ANONİM ŞİRKET (SERMAYE ARTIRIMI) TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer Değişiklik - Sermaye Artırımı | 1 | sermaye_artirimi | positive |
| ANONİM ŞİRKET (TADİL) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Değişiklik - | 1 | tadil | stable |
| ANONİM ŞİRKET (YÖNETİM - TEMSİL VE DİĞER) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer Değişiklik - Tek Pay Sahipliğinde Değişiklik | 1 | yonetim_degisikligi | stable |
| GENEL KURUL TOPLANTIYA ÇAĞIRI | 1 | genel_kurul | stable |
| GENEL KURUL İÇ YÖNERGESİ (TTK - M.419) | 1 | genel_kurul | stable |
| KONKORDATO ALACAKLI TOP. - DURUŞMA GÜNÜ VE DİĞER | 1 | konkordato | **negative** |
| LİMİTED ŞİRKET (ADRES DEĞİŞİKLİĞİ) ORTAK SAYISI BİRDEN FAZLA LİMİTED ŞİRKET Değişiklik - Adres | 1 | adres_degisikligi | stable |
| LİMİTED ŞİRKET (ADRES DEĞİŞİKLİĞİ) ORTAK SAYISI BİRDEN FAZLA LİMİTED ŞİRKET Değişiklik - Adres Değişiklik - Pay Devri Değişiklik - Yönetim Kurulu / Yetkililer | 1 | adres_degisikligi | stable |
| LİMİTED ŞİRKET (KURULUŞ) TEK ORTAKLI LİMİTED ŞİRKET Kuruluş - | 1 | kurulus | positive |
| LİMİTED ŞİRKET (PAY DEVRİ) ORTAK SAYISI BİRDEN FAZLA LİMİTED ŞİRKET Değişiklik - Pay Devri Değişiklik - Yönetim Kurulu / Yetkililer | 1 | pay_devri | stable |
| LİMİTED ŞİRKET (PAY DEVRİ) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Pay Devri | 1 | pay_devri | stable |
| LİMİTED ŞİRKET (SERMAYE ARTIRIMI) ORTAK SAYISI BİRDEN FAZLA LİMİTED ŞİRKET Değişiklik - Pay Devri Değişiklik - Sermaye Artırımı | 1 | sermaye_artirimi | positive |
| LİMİTED ŞİRKET (UNVAN DEĞİŞİKLİĞİ) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Unvan Değişiklik - Adres Değişiklik - Amaç ve Konu Değişiklik - Pay Devri Değişiklik - Yönetim Kurulu / Yetkililer | 1 | unvan_degisikligi | stable |
| LİMİTED ŞİRKET (UNVAN DEĞİŞİKLİĞİ) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Unvan Değişiklik - Amaç ve Konu | 1 | unvan_degisikligi | stable |
| LİMİTED'den ANONİM'e (TÜR DEĞİŞİKLİĞİ) | 1 | tur_degisikligi | stable |
| LİMİTED'den ANONİM'e (TÜR DEĞİŞİKLİĞİ) TEK PAY SAHİPLİ ANONİM ŞİRKET Nevi Değişikliği - Tür Değişikliği Nevi Değişikliği - Sözleşme | 1 | tur_degisikligi | stable |
| TEK ORTAKLIK BİLGİSİ TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Tek Pay Sahipliğinde Değişiklik | 1 | tek_ortaklik | stable |
| TEK ORTAKLIK BİLGİSİ TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer Değişiklik - Tek Pay Sahipliğinde Değişiklik | 1 | tek_ortaklik | stable |
| TEK ORTAKLIK BİLGİSİ TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Yönetim Kurulu Süre ve Sayı Değişiklik - Yönetim Kurulu / Yetkililer Değişiklik - Tek Pay Sahipliğinde Değişiklik | 1 | tek_ortaklik | stable |
| TEMSİL İÇ YÖNERGESİ (TTK - M.371 - F.7) | 1 | temsil_ic_yonergesi | stable |
| TEMSİL İÇ YÖNERGESİ (TTK - M.371 - F.7) PAY SAHİBİ SAYISI BİRDEN FAZLA ANONİM ŞİRKET Değişiklik - Yönetim İç Yönergesi | 1 | temsil_ic_yonergesi | stable |
| TEMSİL İÇ YÖNERGESİ (TTK - M.371 - F.7) TEK ORTAKLI LİMİTED ŞİRKET Değişiklik - Yönetim İç Yönergesi | 1 | temsil_ic_yonergesi | stable |
| TEMSİL İÇ YÖNERGESİ (TTK - M.371 - F.7) TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer Değişiklik - Genel Kurul İç Yönergesi | 1 | temsil_ic_yonergesi | stable |
| TEMSİL İÇ YÖNERGESİ (TTK - M.371 - F.7) TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Yönetim Kurulu / Yetkililer Değişiklik - Yönetim İç Yönergesi | 1 | temsil_ic_yonergesi | stable |
| TEMSİL İÇ YÖNERGESİ (TTK - M.371 - F.7) TEK PAY SAHİPLİ ANONİM ŞİRKET Değişiklik - Yönetim İç Yönergesi | 1 | temsil_ic_yonergesi | stable |
| İFLAS AÇILIŞ TEK PAY SAHİPLİ ANONİM ŞİRKET İflas Başlatma - | 1 | iflas | **negative** |
| ŞUBE AÇILIŞ | 1 | sube_acilis | stable ⚠️ (kural dışı, aşağı bkz) |

## Onaydan sonra ne olacak

1. Bu tablo `ILAN_TURU_ESLEME` sözlüğüne birebir kopyalanır
   (`skills/services/ticaret_sicili_kanit.py:115`).
2. `tests/test_ticaret_sicili_kanit.py::test_ilan_turu_esleme_bos_ve_sessiz_dusmuyor` ve
   `tests/test_tsg_rapor.py::test_esleme_bosken_...` güncellenir (artık boş değil; mandal
   testi "sözlük dolu + her sınıflandırma iş kararına dayanıyor" şeklinde değişir).
3. TSG-04 (company_events yazıcısı) bu sözlüğü kullanarak yazmaya başlar.
