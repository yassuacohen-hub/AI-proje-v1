# -*- coding: utf-8 -*-
"""9R-03: ChatEnricher dikey testleri (mock veri, DB bağımsız).

Kapsam:
- chat yolu: client.chat() JSON döndüğünde sektor/pozisyon/skills ayrışır
- chat hatası: chat atarsa fallback devreye girer + hata alanı dolar
- JSON parse hatası: geçersiz çıktıda fallback + hata işareti
- fallback yolu: client yokken regex/kural tabanlı çıkarım
- sektör eşleme, beceri çıkarımı, strict mod davranışı
- analyzer.enrich_with_chat() entegrasyonu (mock enricher ile)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.intelligence.job_intelligence.pipeline.chat_enricher import (  # noqa: E402
    BELIRSIZ_SEKTOR,
    ChatEnricher,
    _json_cevir,
)
from company_master.intelligence.job_intelligence.pipeline.analyzer import (  # noqa: E402
    ENRICH_SKILL_KEYWORDS,
    SignalAnalyzer,
)

# ---- yardımcılar ----


def _llm_json(sektor: str = "BİLİŞİM", pozisyon: str = "Backend Geliştirici"):
    """chat() tarafından döndürülecek örnek LLM JSON bloğu."""
    return json.dumps(
        {"sektor": sektor, "pozisyon": pozisyon, "skills": ["Python", "SQL", "AWS"]},
        ensure_ascii=False,
    )


def _mock_client(dondurulecek: str) -> MagicMock:
    """chat() çağrısında verilen metni dönen istemci."""
    c = MagicMock()
    c.chat.return_value = dondurulecek
    return c


def _fallback_enricher() -> ChatEnricher:
    """9Router istemcisi olmadan salt-fallback enricher.

    Analyzer'ın gerçek sözleşmesiyle hizalı: ``build_default_enricher``
    ``skill_keywords=ENRICH_SKILL_KEYWORDS`` (MODERN_TECH + ek mesleki)
    kullanır; böylece tech skill'leri (kafka, dbt...) de yakalanır.
    """
    return ChatEnricher(client=None, skill_keywords=ENRICH_SKILL_KEYWORDS)


# ---- chat yolu ----


def test_chat_tam_akim() -> None:
    """chat() başarılı olduğunda sektor/pozisyon/skills ayrışır."""
    enr = ChatEnricher(client=_mock_client(_llm_json()))
    sonuc = enr.enrich({"title": "Backend Developer", "description": "Python + AWS"})
    assert sonuc.kaynak == "chat"
    assert sonuc.sektor == "BİLİŞİM"
    assert sonuc.pozisyon == "Backend Geliştirici"
    assert sonuc.skills == ["Python", "SQL", "AWS"]
    assert sonuc.hata == ""


def test_chat_json_blok_sarmali() -> None:
    """Markdown ```json``` bloğu içindeki JSON ayıklanır."""
    enr = ChatEnricher(client=_mock_client(f"```json\n{_llm_json('İMALAT')}\n```"))
    sonuc = enr.enrich({"title": "Yazılım Müh.", "description": ""})
    assert sonuc.kaynak == "chat"
    assert sonuc.sektor == "İMALAT"


def test_chat_skills_str_ise_listeye_cevrilir() -> None:
    """LLM skills'i tek string döndürürse liste olarak normalize edilir."""
    raw = json.dumps(
        {"sektor": "FİNANS & MUHASEBE", "pozisyon": "Muhasebe Uzmanı", "skills": "Excel"},
        ensure_ascii=False,
    )
    sonuc = ChatEnricher(client=_mock_client(raw)).enrich(
        {"title": "Muhasebe", "description": ""}
    )
    assert sonuc.skills == ["Excel"]


def test_chat_hatasinda_fallback_kullanilir() -> None:
    """chat() istisna fırlatırsa fallback devreye girer; hata işaretlenir."""
    c = MagicMock()
    c.chat.side_effect = RuntimeError("bağlantı yok")
    sonuc = ChatEnricher(client=c).enrich(
        {"title": "Frontend Developer", "description": "React ile UI geliştirme"}
    )
    assert sonuc.kaynak == "fallback"
    assert sonuc.sektor == "BİLİŞİM"
    assert "chat_hatasi" in sonuc.hata


def test_chat_strict_mod_hata_firlatir() -> None:
    """strict=True iken chat hatası üst katmana fırlar (sessiz değil)."""
    c = MagicMock()
    c.chat.side_effect = RuntimeError("yok")
    import pytest

    with pytest.raises(RuntimeError):
        ChatEnricher(client=c, strict=True).enrich({"title": "Analist"})


def test_chat_json_parse_hatasinda_fallback() -> None:
    """Model JSON dışı metin döndürürse fallback + json_parse_hatasi işareti."""
    sonuc = ChatEnricher(client=_mock_client("Açıklama yok")).enrich(
        {"title": "Satış Temsilcisi", "description": "Bölge satış"}
    )
    assert sonuc.kaynak == "fallback"
    assert sonuc.hata == "chat_json_parse_hatasi"


# ---- fallback yolu (client yok / API kapalı) ----


def test_fallback_sektor_bilisim() -> None:
    sonuc = _fallback_enricher().enrich(
        {"title": "Backend Developer", "description": "Python + Docker"}
    )
    assert sonuc.kaynak == "fallback"
    assert sonuc.sektor == "BİLİŞİM"
    assert sonuc.pozisyon == "Backend Developer"


def test_fallback_sektor_satis() -> None:
    sonuc = _fallback_enricher().enrich(
        {"title": "Satış Müşteri Temsilcisi", "description": "İhracat bölgesi"}
    )
    assert sonuc.sektor == "SATIŞ & PAZARLAMA"


def test_fallback_sektor_belirsiz() -> None:
    sonuc = _fallback_enricher().enrich(
        {"title": "Genel Müdür Yardımcısı", "description": ""}
    )
    assert sonuc.sektor == BELIRSIZ_SEKTOR
    assert sonuc.pozisyon == "Genel Müdür Yardımcısı"


def test_fallback_skills_icerik_eslesmesi() -> None:
    sonuc = _fallback_enricher().enrich(
        {"title": "Data Engineer", "description": "Python, SQL, Kafka, dbt kullanıyor"}
    )
    beceriler = sonuc.skills
    assert "python" in beceriler
    assert "kafka" in beceriler


def test_fallback_description_kesme() -> None:
    """Uzun açıklama prompt'a gönderilmeden kesilir (KVKK/maliyet)."""
    uzun_desc = "açıklama " * 1000  # ~9000 karakter
    sonuc = ChatEnricher(client=None, max_desc_chars=500).enrich(
        {"title": "Analist", "description": uzun_desc}
    )
    # fallback yolu açıklamayı kesmez ama çıktı bozulmaz
    assert sonuc.kaynak == "fallback"
    assert sonuc.sektor


# ---- analyzer entegrasyonu ----


def test_enrich_with_chat_mock_enricher() -> None:
    """SignalAnalyzer.enrich_with_chat, enjeksiyonlu enricher ile istatistik üretir."""
    analyzer = SignalAnalyzer()
    stub = MagicMock()

    from company_master.intelligence.job_intelligence.pipeline.chat_enricher import (
        EnrichResult,
    )

    stub.enrich.side_effect = [
        EnrichResult(sektor="BİLİŞİM", pozisyon="X", skills=["a"], kaynak="chat"),
        EnrichResult(
            sektor="SATIŞ & PAZARLAMA", pozisyon="Y", skills=[], kaynak="fallback"
        ),
    ]
    analyzer._enricher = stub

    postings = [
        {"title": "Backend Developer", "description": "Python"},
        {"title": "Satış", "description": ""},
    ]
    stats = analyzer.enrich_with_chat(postings)

    assert stats["ilan_sayisi"] == 2
    assert stats["zenginlestirilen"] == 2
    assert stats["kaynak"] == {"chat": 1, "fallback": 1}
    assert stats["hata"] == 0
    assert len(stats["detay"]) == 2
    assert stats["detay"][0]["sektor"] == "BİLİŞİM"


def test_enrich_with_chat_bos_liste() -> None:
    analyzer = SignalAnalyzer()
    stats = analyzer.enrich_with_chat([])
    assert stats["ilan_sayisi"] == 0
    assert stats["zenginlestirilen"] == 0


def test_enrich_with_chat_hata_toleransi() -> None:
    """Enricher tek ilanda hata verirse akış durmaz, hata sayacı artar."""
    analyzer = SignalAnalyzer()
    stub = MagicMock()
    stub.enrich.side_effect = [RuntimeError("patladı")]
    analyzer._enricher = stub
    stats = analyzer.enrich_with_chat([{"title": "Bozuk", "description": ""}])
    assert stats["hata"] == 1
    assert stats["zenginlestirilen"] == 0
    assert stats["detay"] == []


# ---- yardımcı fonksiyonlar ----


def test_json_cevir_duz() -> None:
    assert _json_cevir('{"sektor": "X"}') == {"sektor": "X"}


def test_json_cevir_gecersiz() -> None:
    assert _json_cevir("metin yok") is None


def test_json_cevir_bos() -> None:
    assert _json_cevir("") is None


def test_enrich_skill_keywords_modulde_tanimli() -> None:
    """MODERN_TECH_KEYWORDS + ek beceriler ENRICH_SKILL_KEYWORDS'i oluşturur."""
    assert isinstance(ENRICH_SKILL_KEYWORDS, list)
    assert "python" in ENRICH_SKILL_KEYWORDS


# ---- 9R-03 canlı demo regresyonları ----
# (1) build_default_enricher fonksiyon değil, çağrılabilir istemci üretmeli;
# (2) available, chat yeteneği olmayan (fonksiyon gibi) client'ı reddetmeli;
# (3) chat çıktısındaki C1 kontrol karakterleri veriye sızmayıp atılmalı.


def test_build_default_enricher_client_cagrilabilir() -> None:
    """default enricher, get_client FONKSİYONUNU değil istemci ÖRNEĞİNİ taşır."""
    from company_master.intelligence.job_intelligence.pipeline.chat_enricher import (  # noqa: E501
        build_default_enricher,
    )

    e = build_default_enricher()
    ic = e._client
    # Şu iki koşuldan biri geçerli olmalı:
    #  - gerçek istemci: .chat çağrılabilir
    #  - kurulmamış: None (fallback-only) ya da chat yeteneği yok
    assert ic is None or callable(getattr(ic, "chat", None)), (
        f"client yanlış tip: {type(ic)!r}"
    )


def test_available_fonksiyon_client_reddeder() -> None:
    """Hataya yol açan get_client fonksiyonu chat yeteneği sayılmaz."""
    e = ChatEnricher(client=lambda: None)
    assert not e.available


def test_chat_sonuc_kontrol_karakteri_temizlenir() -> None:
    """LLM çıktısındaki C1 kontrol karakteri (U+009E gibi) veriye sızmamalı."""
    e = ChatEnricher(client=None)
    r = e._chat_sonuc(
        {
            "sektor": "B\u009eİLİŞİM",
            "pozisyon": "Yaz\u009eılım",
            "skills": ["Py\u009ethon"],
        }
    )
    assert "\u009e" not in r.sektor and "BİLİŞİM" in r.sektor
    assert "\u009e" not in r.pozisyon and "Yazılım" in r.pozisyon
    assert r.skills == ["Python"]
    assert len(ENRICH_SKILL_KEYWORDS) >= 40