# -*- coding: utf-8 -*-
"""Gorev aciklamalari - 10 yasindaki cocuk da okusun diye, duz Turkce yazildi.

KURAL: Her aciklamada iki sey OLMAZLI:
  1) "ne yapti"  -> ne oldu
  2) "ne etkiledi" -> bu yuzden ne degisti
En fazla 2 cumle. Cunku uzun aciklama okunmaz.
"""
from __future__ import annotations

ACIKLAMA: dict[str, dict[str, str]] = {

    # ---------- UTKU: kazima zinciri ----------
    "SCRAPE-002-LEMMLESS-ANKARA-OSB": {
        "yapti": "Ankara'daki uc sanayi sitesinin (OSTIM, Ivedik, Baskent) firma listelerini internetten topladi.",
        "etki": "Veritabanina yeni firmalar eklendi. Artik 'Ankara'da kac firma var' sorusu cevaplanabilir.",
        "bagli": "Baska hicbir goreve bagli degil. Zincirin BASI.",
        "kanit": "scripts/kazima_ostim.py",
    },
    "SCRAPE-001-DOCKER-SETUP": {
        "yapti": "Veritabani ve kazima servisini tek komutla calistiran ayarlari yazdi.",
        "etki": "Bilgisayar acilinca veritabani kendiliginden hazir. Ajanlar elle kurulum yapmiyor.",
        "bagli": "SCRAPE-002'den cikan veriyi saklamasi lazim.",
        "kanit": "docker-compose.yml",
    },
    "SCRAPE-005-KAZIMA-DOCKER-INTEGRATION": {
        "yapti": "Kazima islemini bir servis haline getirdi: kendi kendine calisir, sagligi izlenir, zamanlanabilir.",
        "etki": "Veri toplama artik 'her gun calistir' modunda. Insan baslatmak zorunda degil.",
        "bagli": "SCRAPE-001 ve SCRAPE-002 bittikten sonra.",
        "kanit": "docker-compose.yml",
    },
    "SCRAPE-003-9ROUTER-JINA-FALLBACK": {
        "yapti": "Okunamayan sayfalar icin yedek bir okuma yontemi ekledi (9Router Jina-Reader).",
        "etki": "Diger sitelerden veri alinamadigi icin kazima bos kalmiyor.",
        "bagli": "SCRAPE-002 ile toplanan sayfalari duzeltir.",
        "kanit": "scripts/kazima_jina_fallback.py",
    },
    "SCRAPE-004-QWEN-SINIFLANDIRMA": {
        "yapti": "Okunamayan verileri yapay zeka ile siniflandirdi: 'firma mi, ihale mi, ilan mi' ayirt etti.",
        "etki": "Karisik veriler kutulara ayrildi. Veri toplu degil, tek tek anlamli.",
        "bagli": "SCRAPE-003 duzeltmelerinden sonra.",
        "kanit": "scripts/kazima_qwen_classify.py",
    },
    "SCRAPE-006-QUALITY-AUDIT": {
        "yapti": "Toplanan verilerin kalitesini olctu: hangi alanlar eksik, hangisi dolu.",
        "etki": "Eksik alanlar goruldu. Bir sonraki kazimada ayni hata tekrarlanmiyor.",
        "bagli": "SCRAPE-003 ve SCRAPE-004 bitmeden yapilamaz.",
        "kanit": "scripts/_kazima_dogrula.py",
    },
    "SCRAPE-007-FINAL-REPORT": {
        "yapti": "Kazima doneminin son raporunu yazdi: ne kadar veri toplandigi, maliyetin sifir oldugu, eksikler.",
        "etki": "Isin gercekten ise yarayip yaramadigi belgelendi.",
        "bagli": "SCRAPE-006 kalite denetiminden sonra. Kazima yapilmazsa bu rapor yazilmaz.",
        "kanit": "plans/2026-10-01_kazima_verimlilik_ve_eksiklik_analizi.md",
    },
    "VERI-TENDER-KOLON-01": {
        "yapti": "Ihale kayitlarindaki eski sutun adlarini yeni sisteme gore degistirdi (D-308 uyumu).",
        "etki": "Ihale verileri dogru kutuya yaziliyor; yanlis yere dusme sorunu bitti.",
        "bagli": "Bagimsiz.",
        "kanit": "src/company_master/etl/osb_tender_monitor.py",
    },
    "VERI-RISK-MOTORU-01": {
        "yapti": "Firmalarin risk skorunu tutan sekiz olcutlu tabloyu yazdi.",
        "etki": "Hangi firmanin riskli oldugu veriden anlasiliyor; tahmin yerine olcum var.",
        "bagli": "Bagimsiz.",
        "kanit": "schema/migrations/0046_risk_skorlari.sql",
    },
    "VERI-SKOR-MOTORU-01": {
        "yapti": "Firmanin bize uygunlugunu dort baslikta puanlayan tabloyu yazdi: ihtiyac, uygunluk, zamanlama, genel.",
        "etki": "Hangi firma ilk calisilmali artik puana gore belli. Siralamak tahmine kalmadi.",
        "bagli": "F3: sirket yetenekleri ve sertifikalar verisi dolmali.",
        "kanit": "schema/migrations/0049_firsat_skorlari.sql",
    },
    "DOC-GLOBAL-INTEL-ARASTIRMA-01": {
        "yapti": "6. fazda hangi dis kaynaklardan istihbarat alinabilecegini arastirdi.",
        "etki": "Sonraki fazin kaynak listesi hazirlandi.",
        "bagli": "Bagimsiz (arastirma).",
        "kanit": "docs/FAZ6_GLOBAL_INTEL_KAPSAM.md",
    },

    # ---------- YASU ----------
    "VERI-OSB-TEMIZLIK-01": {
        "yapti": "Sanayi sitesi firma isimlerinden 'etiket' uretti. 647 kayit tarandi, 144 bozuk kayit isaretlendi. SILINEN KAYIT: 0.",
        "etki": "Ayni firma iki kez kaydedilemiyor. Arama sonuclari artik guvenilir.",
        "bagli": "Bagimsiz.",
        "kanit": "data/orchestrator/osb_temizlik_raporu_2026-10-01.md",
    },
    "ALTYAPI-RAG-EMBEDDER-01": {
        "yapti": "Sahte arama yontemini kaldirdi; yerine gercek anlam aramasi koydu (EVREN qwen3-embedding-8b, 4096 boyut).",
        "etki": "Once kelime ayni olmasa bile saglikliordu. Artik 'tasi isleyen firma' arayinca is bitmedigi anlasiliyor.",
        "bagli": "Bagimsiz.",
        "kanit": "src/company_master/vector/embedder.py",
    },
    "VERI-ENTITY-GRAPH-01": {
        "yapti": "Firma-kisi-firma arasindaki baglantilari tutan veritabani semasini yazdi (0047).",
        "etki": "Ortak sahibi olan firmalar birbirine baglaniyor; ayni grubu fark edebiliyoruz.",
        "bagli": "Faz 5 kapsam arastirmasi bitti; uygulama sira bekliyor.",
        "kanit": "schema/migrations/0047_entity_graph.sql",
    },
    "DOC-VENDOR-DD-ARASTIRMA-01": {
        "yapti": "Mal/hizmet satabilecek tedarikci firmalari arastirdi.",
        "etki": "Isbirligi yapilabilecek yeni aday havuzu olustu.",
        "bagli": "Bagimsiz (arastirma).",
        "kanit": "docs/FAZ5_VENDOR_DUE_DILIGENCE_KAPSAM.md",
    },

    # ---------- IHSAN ----------
    "ALTYAPI-ODIN-UYARLAMA-01": {
        "yapti": "Odin'in kendi islerini ve musteri sorularini ayiran guvenlik listesini hazirladi.",
        "etki": "Musteri sorusu Odin'in ic bilgilerine erisemiyor; iki taraf birbirine karismiyor.",
        "bagli": "Bagimsiz.",
        "kanit": "docs/ODIN_SECURITY_CHECKLIST.md",
    },
    "ALTYAPI-AJAN-CAKISMA-01": {
        "yapti": "Ayni dosyaya iki ajanin ayni anda yazmasini engelleyen kilit dosyasi yazdi.",
        "etki": "Ajanlar birbirinin yazdigini ezmiyor; is kaybi olmuyor.",
        "bagli": "Bagimsiz.",
        "kanit": "scripts/ajan_cakisma_kilidi.py",
    },

    # ---------- SALIH ----------
    "TEST-ODIN-PROMPT-INJECTION": {
        "yapti": "Odin'i kandirmaya calisan sorularla guvenlik testi yapiyor; sistem bilgisi siziyor mu olcuyor.",
        "etki": "Guvenlik delikleri veri kacmadan once bulunuyor.",
        "bagli": "ALTYAPI-ODIN-UYARLAMA-01 ile iliskili.",
        "kanit": "data/odin_injection_test_log.jsonl",
    },
    "ALTYAPI-MIMIR-BAGLAM-01": {
        "yapti": "Mimir servisinin baglam (context) ucunu yaziyor.",
        "etki": "Odin konusurken onceki konusmayi hatirlayabilecek.",
        "bagli": "Bagimsiz.",
        "kanit": "src/company_master/odin_ai/mimir_servis.py",
    },
}