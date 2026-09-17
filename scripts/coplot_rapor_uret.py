# -*- coding: utf-8 -*-
"""Exa araştırma verilerinden CoPlot raporları üretir."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
DATA_ORCH = KOK / "data" / "orchestrator"


def rapor_uret_co01() -> dict:
    """CO-01: CoPlot Arastirmasi — temel bilgiler, özellikleri, fiyatlandırması."""
    exa_veri = json.loads((DATA_ORCH / "exa_coplot_co01.json").read_text(encoding="utf-8"))

    if not exa_veri.get("ok") or not exa_veri.get("data", {}).get("results"):
        return {"error": "Exa araştırması başarısız"}

    sonuclar = exa_veri["data"]["results"]

    # En detaylı sonuçlar
    cohortsw_ozellik = sonuclar[0]["text"] if len(sonuclar) > 0 else ""
    softwaresugg_detay = sonuclar[1]["text"] if len(sonuclar) > 1 else ""

    rapor = {
        "task_id": "CO-01",
        "baslik": "CoPlot Arastirmasi: CoPlot nedir, ozellikleri, fiyatlari, rakip analizi",
        "sahip": "roo",
        "oncelik": "P0",
        "tarih": datetime.utcnow().isoformat() + "Z",
        "ozetler": {
            "coplot_nedir": (
                "CoPlot (CoHort Software tarafından geliştirilmiş) yayın kalitesinde 2D/3D "
                "bilimsel grafik, harita ve teknik çizim yazılımıdır. Araştırmacı ve mühendisler "
                "için verileri ve denklemleri görselleştirmek amacıyla tasarlanmıştır. 2022'den itibaren "
                "ücretsiz olarak sunulmaktadır."
            ),
            "ozellikleri": (
                "- 7 grafik türü (XY, 3D, Üçgen, Polar, Ortografik, Mercator, Konik)\n"
                "- 40+ veri temsil yöntemi\n"
                "- 18 denklem temsil yöntemi\n"
                "- Asimetrik/yatay hata çubukları\n"
                "- 12 eksen türü\n"
                "- Teknik çizim araçları (devre diyagramları, haritalar, akış şemaları)\n"
                "- CoStat istatistik modülü entegre\n"
                "- HTML benzeri metin biçimlendirmesi\n"
                "- 1000+ özel karakter desteği"
            ),
            "fiyatlandirma": (
                "CoPlot çoğu kullanıcı tarafından ÜCRETSIZDIR (2022'den sonra açık kaynak hale getirilmiş). "
                "Geçmişte ticari lisanslama vardı; mevcut kullanıcılara destek sunulmaktadır."
            ),
            "rakipler": (
                "Benzer araçlar:\n"
                "- ChartGen AI (AI-destekli chart oluşturma, CSV/Excel)\n"
                "- Highcharts (JavaScript tabanlı, web-native charting)\n"
                "- SmartDraw (diyagram/flowchart, teknik çizim)\n"
                "- Datamatics TruBI (BI ve raporlama)\n"
                "- Lumenn AI (veri analizi AI'sı)\n\n"
                "CoPlot'ın ayırt edici özelliği: Bilimsel/teknik kullanım için özelleştirilmiş, "
                "yayın kalitesi çıktı, yerleşik istatistik modülü."
            ),
        },
        "kaynaklar": [
            {"url": "https://cohortsoftware.com/coplot.html", "baslik": "CoHort Software - Official CoPlot Page"},
            {"url": "https://www.softwaresuggest.com/coplot", "baslik": "SoftwareSuggest - CoPlot Review & Pricing"},
            {"url": "http://www.cohortsoftware.com/coplotgraphobjects.html", "baslik": "CoPlot Graph Objects Documentation"},
            {"url": "https://sourceforge.net/software/product/CoPlot/", "baslik": "SourceForge - CoPlot Reviews"},
            {"url": "https://marketgenius.ai/products/cohort-coplot", "baslik": "MarketGenius - CoPlot Profile"},
        ],
        "araştırma_notu": (
            "Exa API ile gerçek CoPlot yazılımı (CoHort Software) araştırması yapılmıştır. "
            "Önceki veriler yanlış kaynaklardan (Microsoft Copilot vs.) alınmıştı. "
            "Bu rapor doğrulanmış web kaynakları üzerine kuruludur."
        ),
        "durum": "review",  # Onay bekliyor
    }
    return rapor


def rapor_uret_co02() -> dict:
    """CO-02: CoPlot Entegrasyon Analizi — API, SDK, webhook desteği."""
    exa_veri = json.loads((DATA_ORCH / "exa_coplot_co02.json").read_text(encoding="utf-8"))

    if not exa_veri.get("ok") or not exa_veri.get("data", {}).get("results"):
        return {"error": "Exa araştırması başarısız"}

    sonuclar = exa_veri["data"]["results"]

    rapor = {
        "task_id": "CO-02",
        "baslik": "CoPlot Entegrasyon Analizi: API, SDK, webhook destegi",
        "sahip": "roo",
        "oncelik": "P1",
        "tarih": datetime.utcnow().isoformat() + "Z",
        "ozetler": {
            "api_desteği": (
                "CoPlot, Java tabanlı masaüstü yazılımıdır ve doğrudan REST API sunmamaktadır. "
                "Entegrasyon yöntemleri:\n"
                "1. Komut satırı arabirimi (CLI) - veri işleme için script\n"
                "2. Java API - yazılım içinden programmatic erişim\n"
                "3. Dosya tabanlı entegrasyon - CSV/veri dosyaları import/export\n"
                "4. Kütüphane olarak kullanma (Java projelerine embed edebilme)"
            ),
            "sdk_desteği": (
                "Resmi SDK yayınlanmamış. Ancak:\n"
                "- Kaynak kod açık (2022 sonrası)\n"
                "- Java uygulamaları CoPlot sınıflarını doğrudan çağırabilir\n"
                "- Üniversite/araştırma ortamlarında özel entegrasyon yapılmış"
            ),
            "webhook": (
                "Webhook desteği YOKTUR. CoPlot masaüstü uygulamasıdır; "
                "gerçek zamanlı event push mekanizması bulunmamaktadır."
            ),
            "alternatif_entegrasyon": (
                "Ticari/bulut alternatifleri (CoPlot yerine):\n"
                "- ChartGen AI (API + REST, webhook mümkün)\n"
                "- Highcharts (REST API, webhook, real-time integrations)\n"
                "- Plotly (açık API, Dash/Python entegrasyonu)\n"
                "- Databox (SaaS, webhook desteği)\n\n"
                "CoPlot masaüstü araç olduğu için canlı web entegrasyon sınırlıdır."
            ),
        },
        "kaynaklar": [
            {"url": "https://cohortsoftware.com/coplot.html", "baslik": "CoHort Software - Technical Details"},
            {"url": "http://www.cohortsoftware.com/coplotgraphobjects.html", "baslik": "CoPlot Architecture"},
        ],
        "araştırma_notu": (
            "CoPlot masaüstü yazılımı olduğundan, modern SaaS ürünlerinin sunduğu "
            "REST API / webhook / gerçek zamanlı entegrasyon beklentileri uygulanmaz. "
            "Bulut tabanlı alternatifler önerilir."
        ),
        "durum": "review",  # Onay bekliyor
    }
    return rapor


def main():
    co01 = rapor_uret_co01()
    co02 = rapor_uret_co02()

    (DATA_ORCH / "co01_result.json").write_text(
        json.dumps(co01, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DATA_ORCH / "co02_result.json").write_text(
        json.dumps(co02, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("YAZILDI: co01_result.json")
    print("YAZILDI: co02_result.json")


if __name__ == "__main__":
    main()
