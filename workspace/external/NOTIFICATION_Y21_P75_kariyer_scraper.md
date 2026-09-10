# Y21 Sonuçları + P7-5 Revizyonu — Bildirim (sahip: kariyer_scraper)

> Tarih: 2026-09-10
> Y21 araştırması tamamlandı. P7-5 İŞKUR Scraper revize edildi.

---

## Özet

Y21 araştırması sonucunda İŞKUR e-sub'da **açık API YOK** ve özel sektör işyeri adları **public erişimde GİZLİ** bulundu.

- **Açık API:** Yok. Tamamen HTML/ASP.NET WebForms.
- **Firma adı:** Özel sektör ilanlarında `"İşyeri adını görmek için Sisteme Üye Girişi yapmanız gerekmektedir."` Kamu ilanlarında görünür.
- **Public veri:** ilan no, başlık, şehir/ilçe, tarih, pozisyon sayısı, çalışma tipi — firma adı, VKN, vergi no GİZLİ.
- **KVKK/ToS riski:** Üye girişi olmadan firma adı elde etmek ToS ihlali; ticari yeniden dağıtım için lisans gerekli.

## P7-5 Durumu

`aktif` → `plan` olarak revize edildi.

- **Eski yaklaşım:** Firma adı ile kurumsal eşleştirme
- **Yeni yaklaşım:** İlan metadata + aggregation intelligence odaklı çalışma
- **Neden:** Firma adı public erişimde yok; ISKUR'dan firma-level matching yapılamaz

## Gelecek için Not

**İşveren Kayıt Sorgulama** (`esube.iskur.gov.tr/Ortak/KullaniciIslemleri/IsverenSorgulama.aspx`) SGK/VKN ile firma adı üretebilir. Resmi üye girişli/authenticated erişim kurulursa P7-5 **firma-level matching** için tekrar revize edilecek.

## Referans

- Detaylı araştırma: `data/orchestrator/y21_result.json`
- Task board: `data/orchestrator/task_board.json` (Y21 `done`, P7-5 `plan`)
- Görev panosu: `data/orchestrator/gorev_panosu.md`

---

**Bu değişiklikler P7-6 (Kariyer.net Scraper) ve diğer Job Intelligence kaynaklarını doğrudan etkilemez.** Kariyer.net scraper çalışmaya devam edebilir.
