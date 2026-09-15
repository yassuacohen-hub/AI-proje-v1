# -*- coding: utf-8 -*-
"""AI-CHAT-01 — MIMIR sohbet motoru testleri (Streamlit'siz)."""
from __future__ import annotations

import pytest

from company_master import ai_chat
from company_master.ai_chat import AiChatHatasi, Mesaj, Teklif
from company_master.gateway.ninerouter_client import GatewayUnavailable, NineRouterError


class SahteIstemci:
    """Model bazlı senaryo: değer str → yanıt; Exception → fırlat."""

    def __init__(self, senaryo: dict[str, object]) -> None:
        self.senaryo = senaryo
        self.cagrilar: list[str] = []

    def chat(self, prompt, model=None, system=None, temperature=None, max_tokens=1024):
        self.cagrilar.append(model)
        sonuc = self.senaryo.get(model, "")
        if isinstance(sonuc, Exception):
            raise sonuc
        return sonuc


@pytest.fixture
def sahte_baglam(monkeypatch):
    monkeypatch.setattr(ai_chat, "baglam_metni", lambda ajan="roo", limit=12: "[BAĞLAM]")


# --- Model zinciri -----------------------------------------------------------


def test_model_zinciri_varsayilan():
    assert ai_chat.model_zinciri("") == ai_chat.VARSAYILAN_MODELLER
    assert ai_chat.model_zinciri()[0] == "gpt-4o-mini"


def test_model_zinciri_env_ayristirir(monkeypatch):
    monkeypatch.delenv("ABRAKADABRA_MODELS", raising=False)
    monkeypatch.setenv("MIMIR_MODELS", " a , b ,,c ")
    assert ai_chat.model_zinciri() == ("a", "b", "c")


def test_model_zinciri_eski_env_geri_uyumlu(monkeypatch):
    monkeypatch.delenv("MIMIR_MODELS", raising=False)
    monkeypatch.setenv("ABRAKADABRA_MODELS", "x,y")
    assert ai_chat.model_zinciri() == ("x", "y")


def test_model_zinciri_yeni_env_oncelikli(monkeypatch):
    monkeypatch.setenv("MIMIR_MODELS", "yeni")
    monkeypatch.setenv("ABRAKADABRA_MODELS", "eski")
    assert ai_chat.model_zinciri() == ("yeni",)


# --- Kilit sözü (S11) --------------------------------------------------------


def test_gorunen_ad_mimir():
    assert ai_chat.GORUNEN_AD == "MIMIR"
    assert ai_chat.SISTEM_PROMPT.startswith("Sen MIMIR'sin")
    assert "Abrakadabra" not in ai_chat.SISTEM_PROMPT


def test_kilit_sozu_varsayilan_ve_env(monkeypatch):
    monkeypatch.delenv("MIMIR_KILIT_SOZU", raising=False)
    assert ai_chat.kilit_sozu() == "abrakadabra"
    monkeypatch.setenv("MIMIR_KILIT_SOZU", " Sesam ")
    assert ai_chat.kilit_sozu() == "sesam"


def test_kilit_acik_tam_sozcuk(monkeypatch):
    monkeypatch.delenv("MIMIR_KILIT_SOZU", raising=False)
    assert ai_chat.kilit_acik("onayla, ABRAKADABRA")
    assert ai_chat.kilit_acik("abrakadabra")
    assert not ai_chat.kilit_acik("abrakadabraX")
    assert not ai_chat.kilit_acik("")
    assert not ai_chat.kilit_acik(None)


def test_kilit_maskele(monkeypatch):
    monkeypatch.delenv("MIMIR_KILIT_SOZU", raising=False)
    assert ai_chat.kilit_maskele("abrakadabra T-1'i onayla") == "[KİLİT] T-1'i onayla"


def test_sohbet_kilit_sozu_modele_sizmaz(sahte_baglam, monkeypatch):
    monkeypatch.delenv("MIMIR_KILIT_SOZU", raising=False)
    istemci = SahteIstemci({"m1": "tamam"})
    gorulen: dict[str, str] = {}

    def chat(prompt, model=None, system=None, temperature=None, max_tokens=1024):
        gorulen["prompt"] = prompt
        return "tamam"

    istemci.chat = chat  # type: ignore[assignment]
    ai_chat.sohbet([Mesaj("user", "abrakadabra devam")], "tok", istemci=istemci, modeller=("m1",))
    assert "abrakadabra" not in gorulen["prompt"].lower()
    assert "[KİLİT]" in gorulen["prompt"]


def test_teklif_uygula_kilitsiz_reddedilir(monkeypatch):
    monkeypatch.delenv("MIMIR_KILIT_SOZU", raising=False)
    monkeypatch.setattr(ai_chat.tb, "gorev_guncelle", lambda *a, **k: pytest.fail("kilitsiz çağrı"))
    with pytest.raises(AiChatHatasi, match="Kilit sözü"):
        ai_chat.teklif_uygula(Teklif("gorev_guncelle", ("T-1", "aktif")))
    with pytest.raises(AiChatHatasi, match="Kilit sözü"):
        ai_chat.teklif_uygula(Teklif("gorev_guncelle", ("T-1", "aktif")), kilit="yanlış")


KILIT = "abrakadabra"


# --- Sohbet / fallback -------------------------------------------------------


def test_sohbet_admin_token_zorunlu():
    with pytest.raises(AiChatHatasi, match="Admin token"):
        ai_chat.sohbet([Mesaj("user", "selam")], admin_token="", istemci=SahteIstemci({}))


def test_sohbet_son_mesaj_user_olmali(sahte_baglam):
    with pytest.raises(AiChatHatasi, match="kullanıcıya"):
        ai_chat.sohbet([Mesaj("assistant", "x")], "tok", istemci=SahteIstemci({}))


def test_sohbet_ilk_model_basarili(sahte_baglam):
    istemci = SahteIstemci({"m1": "Merhaba!"})
    yanit, model = ai_chat.sohbet([Mesaj("user", "selam")], "tok", istemci=istemci, modeller=("m1", "m2"))
    assert (yanit, model) == ("Merhaba!", "m1")
    assert istemci.cagrilar == ["m1"]


def test_sohbet_fallback_zinciri(sahte_baglam):
    dusen: list[tuple[str, str]] = []
    istemci = SahteIstemci({
        "m1": GatewayUnavailable("gateway kapalı"),
        "m2": "",
        "m3": "Üçüncü yanıt",
    })
    yanit, model = ai_chat.sohbet(
        [Mesaj("user", "selam")], "tok", istemci=istemci, modeller=("m1", "m2", "m3"),
        hata_kaydi=lambda m, h: dusen.append((m, h)),
    )
    assert (yanit, model) == ("Üçüncü yanıt", "m3")
    assert istemci.cagrilar == ["m1", "m2", "m3"]
    assert [m for m, _ in dusen] == ["m1", "m2"]


def test_sohbet_hepsi_duserse_hata(sahte_baglam):
    istemci = SahteIstemci({"m1": NineRouterError("a"), "m2": NineRouterError("b")})
    with pytest.raises(AiChatHatasi, match="m2: b"):
        ai_chat.sohbet([Mesaj("user", "selam")], "tok", istemci=istemci, modeller=("m1", "m2"))


def test_sohbet_sistem_promptu_baglami_icerir(sahte_baglam):
    gorulen: dict[str, str] = {}

    class Kaydedici(SahteIstemci):
        def chat(self, prompt, model=None, system=None, **kw):
            gorulen["system"] = system
            gorulen["prompt"] = prompt
            return "ok"

    ai_chat.sohbet([Mesaj("user", "ilk"), Mesaj("assistant", "cevap"), Mesaj("user", "son")],
                   "tok", istemci=Kaydedici({}), modeller=("m",))
    assert "[BAĞLAM]" in gorulen["system"] and "TEKLIF" in gorulen["system"]
    assert gorulen["prompt"].endswith("Kullanıcı: son")


def test_mesaj_gecersiz_rol():
    with pytest.raises(ValueError):
        Mesaj("system", "x")


# --- TEKLİF ayıklama ---------------------------------------------------------


def test_teklif_ayikla_izinli():
    metin = ("Şunu öneririm.\n"
             "TEKLIF: gorev_guncelle T-1 blocked\n"
             "TEKLİF: tetik_ekle T-2 kilo \"lütfen bak\"\n")
    teklifler = ai_chat.teklif_ayikla(metin)
    assert teklifler == [
        Teklif("gorev_guncelle", ("T-1", "blocked")),
        Teklif("tetik_ekle", ("T-2", "kilo", "lütfen bak")),
    ]
    assert teklifler[0].metin == "gorev_guncelle T-1 blocked"


def test_teklif_ayikla_izinsiz_ve_eksik_atlanir():
    metin = ("TEKLIF: rm -rf /\n"
             "TEKLIF: gorev_guncelle T-1\n"
             "TEKLIF: \"kapanmamış\n"
             "TEKLIF: lock_birak a b\n")
    assert ai_chat.teklif_ayikla(metin) == []
    assert ai_chat.teklif_ayikla("") == []


# --- TEKLİF uygulama ---------------------------------------------------------


def test_teklif_uygula_done_reddedilir():
    with pytest.raises(AiChatHatasi, match="ORCH-08"):
        ai_chat.teklif_uygula(Teklif("gorev_guncelle", ("T-1", "done")), kilit=KILIT)


def test_teklif_uygula_izinsiz_komut():
    with pytest.raises(AiChatHatasi, match="izinsiz"):
        ai_chat.teklif_uygula(Teklif("lock_birak", ("a", "b")), kilit=KILIT)


def test_teklif_uygula_gorev_guncelle(monkeypatch):
    cagri: dict[str, object] = {}

    def sahte_guncelle(task_id, durum=None, **fields):
        cagri.update(task_id=task_id, durum=durum, **fields)
        return {"task_id": task_id}

    monkeypatch.setattr(ai_chat.tb, "gorev_guncelle", sahte_guncelle)
    sonuc = ai_chat.teklif_uygula(Teklif("gorev_guncelle", ("T-1", "blocked")), onaylayan="yasin", kilit=KILIT)
    assert sonuc == {"komut": "gorev_guncelle", "task_id": "T-1", "durum": "blocked"}
    assert cagri["durum"] == "blocked" and "yasin" in str(cagri["not"])


def test_teklif_uygula_gorev_yoksa_hata(monkeypatch):
    monkeypatch.setattr(ai_chat.tb, "gorev_guncelle", lambda *a, **k: None)
    with pytest.raises(AiChatHatasi, match="bulunamadı"):
        ai_chat.teklif_uygula(Teklif("gorev_guncelle", ("YOK", "aktif")), kilit=KILIT)


def test_teklif_uygula_tetik_ekle(monkeypatch):
    monkeypatch.setattr(ai_chat.tr, "tetik_ekle",
                        lambda task_id, ajan, talimat="": {"tarih": "2026", "talimat": talimat})
    sonuc = ai_chat.teklif_uygula(Teklif("tetik_ekle", ("T-2", "kilo", "bak", "lütfen")), kilit=KILIT)
    assert sonuc == {"komut": "tetik_ekle", "task_id": "T-2", "ajan": "kilo", "tarih": "2026"}


def test_teklif_uygula_tetik_hatasi_sarilir(monkeypatch):
    def patlat(*a, **k):
        raise ai_chat.tr.TriggerError("done göreve tetik düşmez")

    monkeypatch.setattr(ai_chat.tr, "tetik_ekle", patlat)
    with pytest.raises(AiChatHatasi, match="tetik düşmez"):
        ai_chat.teklif_uygula(Teklif("tetik_ekle", ("T-2", "kilo")), kilit=KILIT)


# --- Salt okunur bağlam ------------------------------------------------------


def test_baglam_metni_pano_ve_posta(monkeypatch):
    monkeypatch.setattr(ai_chat.tb, "gorev_listesi", lambda: [
        {"task_id": "A", "durum": "done", "sahip": "roo", "oncelik": "P1", "baslik": "bitti"},
        {"task_id": "B", "durum": "aktif", "sahip": "kilo", "oncelik": "P2", "baslik": "x" * 200},
    ])
    monkeypatch.setattr(ai_chat.tr, "bekleyen_tetikler", lambda ajan: [
        {"task_id": "B", "tarih": "t", "talimat": "yap"},
    ])
    metin = ai_chat.baglam_metni("kilo")
    assert "- A |" not in metin and "- B | aktif | kilo | P2 | " + "x" * 80 in metin
    assert "[POSTA KUTUSU: kilo]" in metin and "- B | t | yap" in metin


def test_baglam_metni_bos(monkeypatch):
    monkeypatch.setattr(ai_chat.tb, "gorev_listesi", lambda: [])
    monkeypatch.setattr(ai_chat.tr, "bekleyen_tetikler", lambda ajan: [])
    metin = ai_chat.baglam_metni()
    assert "açık görev yok" in metin and "bekleyen tetik yok" in metin
