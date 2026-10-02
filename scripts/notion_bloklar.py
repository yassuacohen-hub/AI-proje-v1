# -*- coding: utf-8 -*-
"""Pano sayfasina eklenecek ACIKLAMA BLOKLARI.

Kural: Her metin 10 yasindaki cocuk tarafindan anlasilacak sekilde yazilir.
- Kisa cumle, gunluk dil, kisaltma yok.
- Her bolum "ne ise yarar" sorusunu cevaplar.
"""
from __future__ import annotations

BLOKLAR: list[tuple[str, str, list[tuple[str, str]]]] = [
    ("h2", "Bu pano ne ise yarar?", []),
    ("p", "Burada 4 ajanin yaptigi isleri gorursun. Hangi is kimde, ne kadar onemli, "
          "ne zaman bitecek ve neyi degistirecek. Sadece bakmak icindir; burada yazan "
          "bilgiler bilgisayardaki asil dosyadan gelir.", []),

    ("h2", "Burada neye bakmalisin?", []),
    ("p", "Uc tablo var. Hangisine bakacagin ona gore sec:", []),
    ("bulleted_list_item", "", [
        ("KRITIK - Simdi Buraya Bak", "Sadece en onemli (kirmizi) isler. "
         "Bunlara bakarsan sistem ilerler."),
        ("Tum Gorevler", "Acik olan butun isler. Kim yapiyor, ne bekliyor."),
        ("Ilerleme Matrisi", "Projenin nereye kadar geldigi."),
        ("Ajan Ilerlemesi", "Kim ne kadar is tasidi."),
    ]),
    ("h2", "Once bu uc yeri bil", []),
    ("callout", "\u26a0\ufe0f Tek kural: Gercek kaynak hep bilgisayardaki dosyadadir. "
               "Bu pano sadece bir ayna. Iki ayri yere yazilirsa karisirlik olur.", []),

    ("h3", "1) Kim yapiyor?", []),
    ("p", "Dort ajan var. Her biri farkli is yapar:", []),
    ("bulleted_list_item", "", [
        ("yasu", "Kod inceler ve guvenligi kontrol eder. Isler dogru mu diye bakar."),
        ("utku", "Veri toplar, test yazar. Hata varsa duzeltmeden teslim etmez."),
        ("ihsan", "Sistemi kurar ve ajanlarin birbirine karismasini engeller."),
        ("salih", "Guvenlik testi yapar ve Mimir baglamini yazar."),
    ]),

    ("h3", "2) Renkler ne anlama geliyor?", []),
    ("bulleted_list_item", "", [
        ("Kirmizi - en onemli", "Once bunlar. Sirayla bunlara bak."),
        ("Turuncu - onemli", "Kirmizidan sonra gelir."),
        ("Sari - orta", "Zaman varsa yapilir."),
        ("Gri - sonra", "En sona birakilir."),
    ]),

    ("h3", "3) Durumlar ne anlama geliyor?", []),
    ("bulleted_list_item", "", [
        ("YAPILACAK", "Henuz baslanmadi."),
        ("SU ANDA YAPILIYOR", "Su anda calisiyor."),
        ("ONAY BEKLIYOR", "Bitti, ama birinin bakip onaylamasi gerekiyor."),
        ("BITTI", "Tamamlandi."),
    ]),

    ("h2", "Hangi is hangisini acar?", []),
    ("p", "Bazi isler tek basina yapilamaz. Onlardan once baska bir is bitmeli. "
          "Asagidaki sira Kazima isleri icin:", []),
    ("numbered", "", []),
    ("quote", "1) Ankara'dan sirket topla  ->  2) Veritabanini kur ve kazimayi "
              "servise cevir  ->  3) Okunamayan sayfalari duzelt ve siniflandir  ->  "
              "4) Verinin kalitesini olc  ->  5) Son raporu yaz", []),
    ("p", "5. adim hicbiri bitmeden yazilmaz. Cunku rapor, toplanan veriye bakar.", []),

    ("h2", "Her sey nerede duruyor?", []),
    ("p", "Isler farkli klasorlerde duruyor. Her birinin ne ise yaradigi:", []),
    ("bulleted_list_item", "", [
        ("AGENTS.md", "Kurallar ve kararlar. Yeni karar buraya yazilir."),
        ("data/orchestrator/", "Gorev panosu, sohbetler, bulgu defteri."),
        ("hubs/", "Konu klasorleri. Konuya gore bakmak icin."),
        ("src/company_master/", "Asil kod. Veritabani, arama, zeka modulleri."),
        ("plans/", "Is basinda yapilan planlar."),
        ("docs/", "Bitmis islerin raporlari."),
        ("tests/", "Testler. Kodun dogru calistigini kanitlar."),
        ("scripts/", "Kucuk yardimci programlar."),
    ]),

    ("h2", "Isler ne kadar ilerledi?", []),
    ("p", "Sistemin buyuklugu ve nerede durdugu:", []),
    ("bulleted_list_item", "", [
        ("Karar sayisi", "103 karar kaydi var. Her biri bir kural."),
        ("Ajan", "4 ajan calisiyor."),
        ("Ajan hafizasi", "Her ajanin kendi not dosyasi var."),
        ("Markdown dosya", "3075 dosya."),
        ("Bilgi baglantisi", "482 dosya birbirine bagli."),
        ("Git gecmisi", "485 kayit. Kim ne yapti gorulebilir."),
        ("Bu panodaki is", "19 is."),
    ]),

    ("h2", "Tek otorite kurali (D-223)", []),
    ("p", "Once iki klasor vardi ve hangisine yazilacagi belirsizdi. Artik tek kural var: "
          "Huginn Data Insights/ klasoru hem yazma yeridir hem de bilgi baglarinin merkezi. "
          "Eski kural (worktree klasoru) iptal edildi.", []),

    ("divider", "", []),
    ("p", "Son guncelleme: pano her kuruldugunda yeniden yazilir. Kaynak dosya: "
          "data/orchestrator/task_board.json", []),
]