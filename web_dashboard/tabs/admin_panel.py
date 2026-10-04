"""Admin Panel - Karar Defteri ve Kullanici Ayarlari sekmeleri.

- `render_decision_tab`: Decision Log kayitlarini Streamlit dataframe olarak gosterir.
- `render_ayarlar_tab` (P7-46): Kullanici ayarlar paneli; sema odakli form uretimi,
  dogrulama ve kalici kayit `company_master.settings` uzerinden yapilir.

ADMIN-UI-10:
  Sayfa iskeleti Playground dokumantasyon mantigina tasindi:
  ``PageHeader`` -> ``SectionNav`` -> ``Section``. Renk, ikon ve tipografi
  secimleri **degismedi**; yalnizca hiyerarsi disipline edildi. Bu ekranin tek
  birincil butonu form icindeki "Kaydet" dugmesidir; bu yuzden baslik seridinde
  ikinci bir birincil buton yoktur.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from scripts.decision_log import read_decisions, log_decision

_KOK = Path(__file__).resolve().parents[2]
if str(_KOK / "src") not in sys.path:
    sys.path.insert(0, str(_KOK / "src"))
if str(_KOK / "scripts") not in sys.path:
    sys.path.insert(0, str(_KOK / "scripts"))  # liderlik_verisi (ajan_chat.py) icin

from company_master.settings import (  # noqa: E402
    AyarHatasi,
    AyarTanimi,
    ayarlari_getir,
    ayarlari_sifirla,
    ayarlari_yaz,
    gruplar,
    varsayilanlar,
)
from company_master.ui import PageHeader, Section, SectionNav  # noqa: E402
from company_master.chat import ac, oku, ozet, kahin_gonder, guncelle  # noqa: E402
from web_dashboard.tabs.admin_mfa import render_mfa_tab  # noqa: E402 (UI-ADMIN-MFA-26 B-05)
import requests  # noqa: E402 (UI-ADMIN-KVKK-MODU-26: KVKK mode API çağrısı, UI-ADMIN-MFA-26: MFA API çağrısı)

#: D-192 Faz 2 — ajan başına sabit renk (tema uyumlu: gece/gündüz)
_AJAN_RENKLERI: dict[str, str] = {
    "ihsan": "#FFD4D9",
    "utku": "#D4E8FF",
    "salih": "#D4FFD4",
    "yasu": "#FFF5CC",
    "orkestrator": "#E8D4FF",
    "mimir": "#D4FFFF",
}
#: Önem derecesi (4 tip) → renk + etiket (tema uyumlu kontrastlı)
_ONEM_ETIKET: dict[str, str] = {
    "kritik": "🔴 Kritik",
    "yuksek": "🟠 Yüksek",
    "orta": "🟡 Orta",
    "dusuk": "🟢 Düşük",
}
_ONEM_RENKLERI: dict[str, str] = {
    "kritik": "#E8564D",
    "yuksek": "#F0A540",
    "orta": "#F5D13D",
    "dusuk": "#5FB375",
}


def _sohbet_tablo_stil(row: "pd.Series") -> list[str]:
     """Gönderen ve Alıcı hücrelerini ajan renklerine göre, Önem Derecesi'ni önem rengine göre renklendirir (D-192 Faz 2).
     Yazı rengi tema-uyumlu: gece modda açık, gündüz modda koyu."""
     stiller = [""] * len(row)
     # Gönderen renklendir
     if "Gönderen" in row.index:
         renk = _AJAN_RENKLERI.get(str(row["_ajan_gonderici"]).lower(), "#EEEEEE")
         stiller[row.index.get_loc("Gönderen")] = f"background-color: {renk}; color: #0a0a0a; font-weight: 900; text-shadow: 0 0 3px rgba(255,255,255,0.5)"
     # Alıcı renklendir
     if "Alıcı" in row.index:
         renk = _AJAN_RENKLERI.get(str(row["_ajan_alici"]).lower(), "#EEEEEE")
         stiller[row.index.get_loc("Alıcı")] = f"background-color: {renk}; color: #0a0a0a; font-weight: 900; text-shadow: 0 0 3px rgba(255,255,255,0.5)"
     # Önem Derecesi renklendir
     if "Önem Derecesi" in row.index:
         renk = _ONEM_RENKLERI.get(str(row["_onem_ham"]).lower(), "#EEEEEE")
         stiller[row.index.get_loc("Önem Derecesi")] = f"background-color: {renk}; color: #ffffff; font-weight: bold; text-shadow: 0 1px 3px rgba(0,0,0,0.5)"
     return stiller

_log = logging.getLogger(__name__)

#: ADMIN-UI-10 — Bolumler tek yerde tanimlanir (anchor tutarliligi).
BOLUMLER: tuple[Section, ...] = (
    Section("Ayar Grupları", "Gruplara ayrılmış tercihler; kaydetme tek işlemde doğrulanır.",
            ikon="🎛️", kimlik="ayar-gruplari"),
    Section("Sıfırlama", "Tüm tercihleri şema varsayılanlarına döndürür.",
            ikon="↩️", kimlik="ayar-sifirlama"),
    Section("MFA Yönetimi", "Çok faktörlü kimlik doğrulama (TOTP) ayarları.",
            ikon="🔐", kimlik="mfa-yonetimi"),
)

GIRIS_METNI = (
    "Panel davranışını kendi kullanıcı kimliğinize göre ayarlayın. Değişiklikler "
    "sunucuda saklanır; tarayıcı değiştirseniz de korunur. Kaydetme hepsi-ya-hiç "
    "çalışır: bir alan geçersizse hiçbiri yazılmaz."
)


def _bolum(kimlik: str) -> Section:
    """Kimlige gore bolum tanimini getirir (anchor tutarliligi icin)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


def render_decision_tab(decisions: list[dict[str, Any]] | None = None) -> None:
    """Admin panelinde karar defteri kayitlarini gosterir.

    Args:
        decisions: Karar listesi. None ise decision_log.jsonl dosyasindan okur.
    """
    if decisions is None:
        decisions = read_decisions()

    PageHeader(
        "Karar Defteri", ust_etiket="İş · Yönetim", ikon="📒",
        giris="Karar kayıtlarını görüntüleyin, filtreleyin ve yeni kararlar ekleyin.",
    ).render()

    # ---- Filtreler ----
    Section(
        "Filtreler", "Karar listesini karar veren, etiket veya metin ile filtreleyin.", ikon="🔍",
    ).render()

    tum_etiketler = sorted(
        {
            t
            for d in decisions
            for t in (d.get("tags", []) if isinstance(d.get("tags", []), list) else [])
        }
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        secilen_karar_veren = st.selectbox(
            "Karar Veren",
            ["Hepsi"] + sorted({d.get("decider", "") for d in decisions if d.get("decider")}),
            key="kd_karar_veren",
        )
    with col2:
        secilen_etiketler = st.multiselect("Etiket", tum_etiketler, key="kd_etiketler")
    with col3:
        arama = st.text_input("Ara", key="kd_ara", placeholder="Başlık, karar veya gerekçe...")

    filtrelenmis = decisions
    if secilen_karar_veren != "Hepsi":
        filtrelenmis = [d for d in filtrelenmis if d.get("decider") == secilen_karar_veren]
    if secilen_etiketler:
        filtrelenmis = [
            d
            for d in filtrelenmis
            if any(t in (d.get("tags", []) if isinstance(d.get("tags", []), list) else []) for t in secilen_etiketler)
        ]
    if arama:
        q = arama.lower()
        filtrelenmis = [
            d
            for d in filtrelenmis
            if q in str(d.get("title", "")).lower()
            or q in str(d.get("decision", "")).lower()
            or q in str(d.get("reason", "")).lower()
        ]

    # ---- Karar Listesi ----
    Section(
        "Karar Listesi", "Son karar kayıtları, en yeni üstte (son 50).", ikon="📋",
    ).render()

    if not filtrelenmis:
        st.info("Henüz karar kaydı yok — ilk kararı aşağıdaki formdan ekleyin.")


    filtrelenmis_sorted = sorted(filtrelenmis, key=lambda d: d.get("ts", ""), reverse=True)
    recent = filtrelenmis_sorted[:50]

    rows = []
    for d in recent:
        tags = d.get("tags", [])
        if not isinstance(tags, list):
            tags = [str(t) for t in tags]
        rows.append({
            "Tarih": d.get("ts", ""),
            "Baslik": d.get("title", ""),
            "Karar": d.get("decision", ""),
            "Karar Veren": d.get("decider", ""),
            "Aciklama": d.get("reason", ""),
            "Etiketler": ", ".join(str(t) for t in tags),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption("Toplam " + str(len(filtrelenmis)) + " karar kaydi gosterniliyor (son 50).")

    # ---- Yeni Karar ----
    Section("Yeni Karar", "Yeni bir karar kaydı ekleyin.", ikon="➕").render()

    with st.form("yeni_karar"):
        baslik = st.text_input("Başlık")
        karar = st.text_input("Karar")
        gerekce = st.text_input("Gerekçe")
        etiketler_str = st.text_input("Etiketler (virgülle ayrılmış)")
        kaydet = st.form_submit_button("Kaydet", type="primary")

    if kaydet:
        if not baslik.strip() or not karar.strip():
            st.error("Başlık ve Karar alanları zorunludur.")
        else:
            tags = [t.strip() for t in etiketler_str.split(",") if t.strip()]
            decider = aktif_kullanici()
            log_decision(baslik.strip(), karar.strip(), decider, gerekce.strip(), tags)
            st.success("Karar kaydedildi.")
            st.rerun()


# ---------------------------------------------------------------------------
# P7-46: Kullanici Ayarlar Paneli
# ---------------------------------------------------------------------------

#: Oturum acmamis kullanicilar icin ayarlarin yazildigi kimlik.
MISAFIR_KIMLIK = "misafir"


def aktif_kullanici(oturum: dict[str, Any] | None = None) -> str:
    """Oturumdan kullanici kimligini cozer; yoksa misafir kimligi doner.

    Streamlit `session_state` disinda da calisabilmesi icin sozluk alir
    (test edilebilirlik).
    """
    if oturum is None:
        try:
            oturum = dict(st.session_state)
        except Exception as exc:  # noqa: BLE001 — Streamlit bağlamı dışında (test/CLI)
            _log.debug("session_state okunamadı, misafir sayılıyor: %s", exc)
            oturum = {}
    for anahtar in ("admin_email", "user_email", "kullanici_id"):
        deger = oturum.get(anahtar)
        if isinstance(deger, str) and deger.strip():
            return deger.strip()
    return MISAFIR_KIMLIK


def render_rapor_listesi_tab() -> None:
    """D-190: Admin panelde MIMIR raporlarını göster ve indir.

    - Rapor dizinini tara: *_rapor_*_mimir.md
    - Filtrele: rapor türü, tarih
    - Sırala: en yeni ilk
    - İndir: Markdown dosyası download

    Erişim: rol kontrolü (future: granüler)
    """
    # Erişim kontrolü (şu an tüm roller)
    if not rapor_erisisim_denetimi():
        st.error("Bu rapora erişim izniniz yok.")
        return

    PageHeader(
        "MIMIR Architect Raporları", ust_etiket="Yönetim", ikon="📋",
        giris="MIMIR tarafından otomatik oluşturulan architect raporlarını görüntüleyin.",
    ).render()

    # Rapor dizinini bul
    rapor_dir = Path(_KOK) / "data" / "orchestrator" / "raporlar"

    if not rapor_dir.exists():
        st.info("Henüz rapor oluşturulmamış.")
        return

    # Raporları topla: *_rapor_*_mimir.md
    raporlar = sorted(
        rapor_dir.glob("*_rapor_*_mimir.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if not raporlar:
        st.info("Henüz rapor oluşturulmamış.")
        return

    # Rapor listesi
    col1, col2 = st.columns([3, 1])
    with col1:
        Section(f"Raporlar ({len(raporlar)})", "Rapor listesi görüntüleme").render()

    # Tablo: task_id | tarih | dosya | indir
    table_data = []
    for rapor_dosya in raporlar:
        # Dosya adından task_id çıkar: {TASK_ID}_rapor_{TARIH}_mimir.md
        parts = rapor_dosya.stem.rsplit("_rapor_", 1)
        task_id = parts[0] if parts else "?"
        tarih_str = parts[1].rsplit("_mimir", 1)[0] if len(parts) > 1 else "?"

        # Dosya boyutu
        boyut = rapor_dosya.stat().st_size
        boyut_kb = f"{boyut / 1024:.1f} KB" if boyut > 0 else "0 B"

        # İçerik oku (preview için ilk 100 karakter)
        try:
            icerik = rapor_dosya.read_text(encoding="utf-8")
            ilk_100 = icerik[:100].replace("\n", " ")
        except Exception:
            ilk_100 = "(Okunulamadı)"

        table_data.append({
            "Task ID": task_id,
            "Tarih": tarih_str,
            "Boyut": boyut_kb,
            "Dosya": rapor_dosya.name,
        })

    # DataFrame olarak göster
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)

    # İndir seçeneği
    Section("İndir", "Rapor indirme seçeneği").render()
    selected_rapor = st.selectbox(
        "Rapor seçin",
        [r.name for r in raporlar],
        key="rapor_indir_select"
    )

    if selected_rapor:
        rapor_yolu = rapor_dir / selected_rapor
        rapor_icerik = rapor_yolu.read_text(encoding="utf-8")

        st.download_button(
            label=f"📥 {selected_rapor} indir",
            data=rapor_icerik,
            file_name=selected_rapor,
            mime="text/markdown",
            key="rapor_download"
        )


# ---------------------------------------------------------------------------
# D-192: Ajan Chat Sistemi — Dashboard Widget
# ---------------------------------------------------------------------------


def _form_degeri(tanim: AyarTanimi, mevcut: Any) -> Any:
    """Tek bir ayar icin uygun Streamlit girdisini cizer ve degerini doner."""
    anahtar = f"ayar_{tanim.anahtar}"

    if tanim.tip == "bool":
        return st.checkbox(
            tanim.etiket,
            value=bool(mevcut),
            key=anahtar,
            help=tanim.aciklama or None,
        )

    if tanim.tip == "sayi":
        return int(
            st.number_input(
                tanim.etiket,
                min_value=tanim.alt_sinir,
                max_value=tanim.ust_sinir,
                value=int(mevcut),
                step=10,
                key=anahtar,
                help=tanim.aciklama or None,
            )
        )

    if tanim.tip == "secim":
        secenekler = list(tanim.secenekler)
        indeks = secenekler.index(mevcut) if mevcut in secenekler else 0
        return st.selectbox(
            tanim.etiket,
            secenekler,
            index=indeks,
            key=anahtar,
            help=tanim.aciklama or None,
        )

    return st.text_input(
        tanim.etiket,
        value=str(mevcut),
        key=anahtar,
        help=tanim.aciklama or None,
    )


def render_ayarlar_tab(kullanici_id: str | None = None) -> None:
    """Kullanici ayarlar panelini cizer (P7-46).

    Ayarlar `company_master.settings` semasindan uretilir; grup basina bir
    sekme acilir. Kaydet tek islemde dogrular (hepsi-ya-hic).
    """
    if kullanici_id is None:
        kullanici_id = aktif_kullanici()

    PageHeader("Kullanıcı Ayarları", giris=GIRIS_METNI,
               ust_etiket="Sistem · Ayarlar", ikon="⚙️").render()

    # K3-10g: rehber anahtarı sayfa altında (`app.REHBER_KEY`); modül yalnız okur.
    st.caption(
        f"Ayarlar bu kullanıcıya özeldir (`{kullanici_id}`) ve tarayıcıdan bağımsız "
        "olarak sunucuda saklanır."
    )


    SectionNav(BOLUMLER, yatay=True).render()

    _misafir = kullanici_id == MISAFIR_KIMLIK

    if _misafir:
        st.info("Ayarları kaydetmek için giriş yapın")
        mevcut = varsayilanlar()
        grup_haritasi = gruplar()
        grup_adlari = list(grup_haritasi)
        _bolum("ayar-gruplari").render()
        for grup_adi in grup_adlari:
            with st.tabs([grup_adi])[0]:
                for tanim in grup_haritasi[grup_adi]:
                    deger = mevcut.get(tanim.anahtar, tanim.varsayilan)
                    st.caption(f"{tanim.etiket}: {deger}")
        _bolum("ayar-sifirlama").render()
        st.caption("Misafir modunda ayarlar yazılamaz; yalnızca mevcut değerler gösterilir.")
        return

    mevcut = ayarlari_getir(kullanici_id)
    grup_haritasi = gruplar()
    grup_adlari = list(grup_haritasi)

    _bolum("ayar-gruplari").render()
    yeni_degerler: dict[str, Any] = {}
    with st.form("kullanici_ayarlari_form"):
        sekmeler = st.tabs(grup_adlari)
        for sekme, grup_adi in zip(sekmeler, grup_adlari):
            with sekme:
                for tanim in grup_haritasi[grup_adi]:
                    yeni_degerler[tanim.anahtar] = _form_degeri(
                        tanim, mevcut.get(tanim.anahtar, tanim.varsayilan)
                    )

        kaydet = st.form_submit_button("💾 Kaydet", type="primary")

    if kaydet:
        try:
            ayarlari_yaz(kullanici_id, yeni_degerler)
        except AyarHatasi as hata:
            st.error(f"Ayar kaydedilemedi: {hata}")
        else:
            st.success("Ayarlar kaydedildi.")

    _bolum("ayar-sifirlama").render()
    if st.button("↩️ Varsayılanlara dön", key="ayar_sifirla"):
        ayarlari_sifirla(kullanici_id)
        st.success("Ayarlar varsayılanlara döndürüldü.")
    st.caption(
        "Not: Tema ayarı 'sistem' seçiliyken panel, işletim sistemi renk tercihini izler."
    )


def rapor_erisisim_denetimi(rol: str | None = None) -> bool:
    """D-190: MIMIR architect raporlarına erişim kontrolü.

    Tüm agentle açık: orkestrator + kahin + diğerleri.
    Future: granüler kontrol (başka rollerin kendi raporları).

    Args:
        rol: Kullanıcı rolü

    Returns:
        True = rapor erişim izni var
    """
    # Şu an: tüm roller erişebilir (ürün sahibi isteği)
    return True



def render_chat_summary() -> None:
    """Ajan Chat özeti: açık sorunlar, çözüm bekleniyor, çözüldü metrikler + son 3 sorun.

    Admin panelinde KAHİN ve orkestratör sorunları takip edebilir.
    """
    PageHeader(
        "Ajan Chat Sistemi", ust_etiket="İş · Takip", ikon="💬",
        giris="Ajanlar arasında bildirilen sorunlar ve çözüm önerileri.",
    ).render()

    # ---- Liderlik tablosu (Mesaj 6 · Yol A) — en üstte, tablo + grafik yan yana ----
    Section("🏆 Liderlik Tablosu", "Gorev(done) + bulgu + mesaj sayisi, azalan siralama.", ikon="🏆").render()
    try:
        from ajan_chat import liderlik_verisi  # noqa: E402 (scripts/ — lazy import, CLI ile ayni hesap)
        liderlik_df = pd.DataFrame(liderlik_verisi())
        col_lb_tablo, col_lb_grafik = st.columns([1, 1])
        with col_lb_tablo:
            st.dataframe(liderlik_df, use_container_width=True, hide_index=True)
        with col_lb_grafik:
            if not liderlik_df.empty:
                st.bar_chart(liderlik_df.set_index("ajan")[["gorev", "bulgu", "mesaj"]])
    except Exception as e:  # pragma: no cover - UI hata gostergesi
        st.warning(f"Liderlik tablosu yuklenemedi: {e}")

    # ---- Metrikler ----
    Section("Sorun Durumu Özeti", "Açık, çözüm bekleniyor ve çözüldü sayıları.", ikon="📊").render()

    # K3-10h madde 6: tek dosya okuma, 4 ayrı oku()/ozet() I/O yerine bellekte filtrele
    tum_sorunlar = oku()
    acik = [s for s in tum_sorunlar if s.get("durum") == "acik"]
    cokundurmus = [s for s in tum_sorunlar if s.get("durum") == "cokundurmus"]
    cozuldu = [s for s in tum_sorunlar if s.get("durum") == "cozuldu"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 Açık Sorunlar", len(acik))
    with col2:
        st.metric("🟡 Çözüm Bekleniyor", len(cokundurmus))
    with col3:
        st.metric("🟢 Çözüldü", len(cozuldu))

    # ---- Son Açık Sorunlar ----
    Section("Son 3 Açık Sorun", "Ajanlar tarafından en son bildirilen açık sorunlar.", ikon="🔴").render()

    if not acik:
        st.info("Henüz açık sorun yok.")
    else:
        son_acik = sorted(acik, key=lambda x: x.get("timestamp", ""), reverse=True)[:3]
        for i, sorun in enumerate(son_acik, 1):
            ajan_gonderici = sorun.get("kimden", "orkestrator").lower()
            ajan_alici = sorun.get("ajan", "?").lower()
            ajan_gonderici_display = ajan_gonderici.upper()
            ajan_alici_display = "📢 BROADCAST" if ajan_alici == "*" else ajan_alici.upper()
            onem_ham = sorun.get("onem", "orta")
            onem_etiket = _ONEM_ETIKET.get(onem_ham, onem_ham)

            # Ajan renklerini al
            renk_gonderici = _AJAN_RENKLERI.get(ajan_gonderici, "#EEEEEE")
            renk_alici = _AJAN_RENKLERI.get(ajan_alici, "#EEEEEE")

            baslik = f"**{i}. "
            baslik += f":{ajan_gonderici}:** {ajan_gonderici_display} → "
            baslik += f":{ajan_alici}:** {ajan_alici_display} · {sorun.get('task_id', '?')}"

            with st.expander(baslik):
                st.write(f"**Sorun:** {sorun.get('sorun', '')}")
                if sorun.get("cozum"):
                    st.write(f"**İlk Çözüm Önerisi:** {sorun.get('cozum')}")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Durum:** {sorun.get('durum', '—')}")
                with col2:
                    st.write(f"**{onem_etiket}**")
                st.caption(f"📅 {sorun.get('timestamp', '')}")

    # ---- Tüm Sorunlar (Tablo) ----
    Section("Tüm Sorunlar (Tablo Görünümü)", "Filtrelenebilir sorun listesi.", ikon="📋").render()

    if tum_sorunlar:
        rows = []
        for s in sorted(tum_sorunlar, key=lambda x: x.get("timestamp", ""), reverse=True):
            # Eski kayıtlarda kimden yoksa orkestrator kabul et
            ajan_gonderici = s.get("kimden") or "orkestrator"
            ajan_alici = s.get("ajan", "?")
            ajan_alici_display = "📢 BROADCAST" if ajan_alici == "*" else ajan_alici.upper()
            onem_ham = s.get("onem", "orta")
            rows.append({
                "Gönderen": ajan_gonderici.upper(),
                "Alıcı": ajan_alici_display,
                "Görev": s.get("task_id", ""),
                "Sorun": s.get("sorun", "")[:50],
                "Çözüm": s.get("cozum", "")[:50] or "—",
                "Durum": s.get("durum", ""),
                "Önem Derecesi": _ONEM_ETIKET.get(onem_ham, onem_ham),
                "Tarih": s.get("timestamp", "")[:16],
                "_ajan_gonderici": ajan_gonderici,
                "_ajan_alici": ajan_alici,
                "_onem_ham": onem_ham,
            })
        df = pd.DataFrame(rows)
        # Sütun sırası: Gönderen-Alıcı-Önem-Görev-Sorun-Çözüm-Durum-Tarih
        gorunen_kolonlar = ["Gönderen", "Alıcı", "Önem Derecesi", "Görev", "Sorun", "Çözüm", "Durum", "Tarih"]

        # Sütun konfigürasyonu — Gönderen/Alıcı/Önem dar, Sorun/Çözüm geniş
        col_config = {
            "Gönderen": st.column_config.Column(width="small"),
            "Alıcı": st.column_config.Column(width="small"),
            "Önem Derecesi": st.column_config.Column(width="small"),
            "Görev": st.column_config.Column(width="small"),
            "Sorun": st.column_config.Column(width="medium"),
            "Çözüm": st.column_config.Column(width="medium"),
            "Durum": st.column_config.Column(width="small"),
            "Tarih": st.column_config.Column(width="small"),
        }

        st.dataframe(
            df.style.apply(_sohbet_tablo_stil, axis=1),
            width="stretch", hide_index=True, column_order=gorunen_kolonlar, column_config=col_config,
        )
        st.caption(f"Toplam {len(tum_sorunlar)} sorun kaydedilmiş.")

    # ---- Mesaj Gönder + Çözüme Bağla — aynı blokta yan yana (D-213/D-217, kullanıcı isteği) ----
    Section(
        "Mesaj Gönder & Çözüme Bağla",
        "Solda yeni mesaj yaz, sağda açık soruna çözüm iliştir — ikisi aynı blokta.",
        ikon="📤",
    ).render()

    col_mesaj, col_cozum = st.columns([1, 1])

    _GONDEREN_SECENEKLERI = ["kahin", "ihsan", "utku", "salih", "yasu", "mimir", "orkestrator"]
    _ALICI_SECENEKLERI = ["herkes", "ihsan", "utku", "salih", "yasu", "mimir", "orkestrator", "kahin"]

    with col_mesaj:
        st.markdown("**📨 Mesaj Gönder**")
        with st.form("kahin_mesaj_formu", clear_on_submit=True):
            col_gonderen, col_alici, col_onem = st.columns([1, 1, 1])
            with col_gonderen:
                gonderen = st.selectbox(
                    "Gönderen",
                    options=_GONDEREN_SECENEKLERI,
                    format_func=lambda x: x.upper(),
                    index=0,
                )
            with col_alici:
                alici = st.selectbox(
                    "Alıcı",
                    options=_ALICI_SECENEKLERI,
                    format_func=lambda x: "📢 HERKES" if x == "herkes" else x.upper(),
                    index=0,
                )
            with col_onem:
                onem = st.selectbox(
                    "Önem Derecesi",
                    options=["orta", "yuksek", "kritik", "dusuk"],
                    index=0,
                )

            mesaj = st.text_area(
                "Mesaj",
                placeholder="Örn: Acil update: API v2 maintenance yarın saat 14:00-15:00 arasında.",
                max_chars=500,
                height=100,
            )

            task_id = st.text_input(
                "Görev ID (isteğe bağlı)",
                placeholder="Örn: API-12, P7-50, vb. — boşsa 'genel' kaydedilir.",
                max_chars=50,
            )

            submitted = st.form_submit_button("📨 Mesaj Gönder", type="primary", use_container_width=True)

        if submitted:
            if not mesaj.strip():
                st.error("Mesaj boş olamaz.")
            else:
                try:
                    hedef_ajan = "*" if alici == "herkes" else alici
                    if gonderen == "kahin":
                        # kahin_gonder Telegram bildirimini de tetikler (D-212)
                        sonuc = kahin_gonder(
                            mesaj=mesaj.strip(),
                            task_id=task_id.strip() if task_id else "",
                            onem=onem,
                            ajan=hedef_ajan,
                        )
                    else:
                        # Diğer ajanlar: ac() ile doğru "kimden" attribution + Telegram bildirimi (D-217)
                        sonuc = ac(
                            ajan=hedef_ajan,
                            task_id=task_id.strip() if task_id else "genel",
                            sorun=mesaj.strip(),
                            kimden=gonderen,
                            onem=onem,
                        )
                        try:
                            from company_master.chat import _gonder_telegram_kahin
                            _gonder_telegram_kahin(mesaj.strip(), sonuc.get("task_id", ""), onem, gonderen)
                        except Exception:
                            pass  # Telegram hatası web kaydını etkilemesin
                    alici_gosterim = "herkes" if alici == "herkes" else alici.upper()
                    st.success(
                        f"✅ Mesaj gönderildi! ({gonderen.upper()} → {alici_gosterim}, task_id: {sonuc.get('task_id', '—')})"
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Hata: {e}")

    with col_cozum:
        st.markdown("**✅ Çözüme Bağla**")
        acik_sorunlar_liste = ozet("acik")
        if not acik_sorunlar_liste:
            st.caption("Şu an açık sorun yok.")
        else:
            _secim_etiketleri = [
                f"[{s.get('task_id', '?')}] {s.get('kimden', '?').upper()}: {s.get('sorun', '')[:40]}"
                for s in acik_sorunlar_liste
            ]
            with st.form("cozum_formu", clear_on_submit=True):
                secilen_idx = st.selectbox(
                    "Hangi soruna çözüm yazılacak?",
                    options=list(range(len(acik_sorunlar_liste))),
                    format_func=lambda i: _secim_etiketleri[i],
                )
                cozum_metni = st.text_area(
                    "Çözüm",
                    placeholder="Örn: Migration script'i review edildi, sorun giderildi.",
                    max_chars=300,
                    height=80,
                )
                durum_secim = st.selectbox(
                    "Durum",
                    options=["cozuldu", "cokundurmus"],
                    format_func=lambda x: "🟢 Çözüldü" if x == "cozuldu" else "🟡 Çözüm Bekleniyor",
                    index=0,
                )
                cozum_submit = st.form_submit_button("✅ Çözümü Kaydet", type="primary", use_container_width=True)

            if cozum_submit:
                if not cozum_metni.strip():
                    st.error("Çözüm metni boş olamaz.")
                else:
                    secilen_sorun = acik_sorunlar_liste[secilen_idx]
                    hedef_task_id = secilen_sorun.get("task_id", "")
                    try:
                        sorun_index = 0
                        for i, s in enumerate(oku(task_id=hedef_task_id)):
                            if s is secilen_sorun or (
                                s.get("timestamp") == secilen_sorun.get("timestamp")
                                and s.get("sorun") == secilen_sorun.get("sorun")
                            ):
                                sorun_index = i
                                break
                        sonuc = guncelle(
                            task_id=hedef_task_id,
                            sorun_index=sorun_index,
                            cozum_guncel=cozum_metni.strip(),
                            durum=durum_secim,
                        )
                        if sonuc:
                            st.success("✅ Çözüm kaydedildi.")
                            st.rerun()
                        else:
                            st.error("Sorun bulunamadı — tekrar deneyin.")
                    except Exception as e:
                        st.error(f"❌ Hata: {e}")

# ---------------------------------------------------------------------------
# ALTYAPI-ADMIN-PANO-01: Task Board Gerçek Zamanlı Görünümü
# ---------------------------------------------------------------------------

# Bölüm renkleri (D-77 pano durum eşlemeleri)
_PANO_BOLUM_RENKLERI: dict[str, str] = {
    "tamamlandi": "#6BCB77",   # yeşil
    "beklemede": "#FFD93D",    # sarı
    "yedek": "#B0B0B0",        # gri
    "degerlendirme": "#FF4D4D", # kırmızı
}

_PANO_DURUM_BOLUM: dict[str, str] = {
    "done": "tamamlandi",
    "aktif": "beklemede",
    "review": "beklemede",
    "bekliyor": "beklemede",
    "plan": "yedek",
    "blocked": "degerlendirme",
    "reddet": "degerlendirme",
    "iptal": "degerlendirme",
    "archive": "tamamlandi",
    "yedek": "yedek",
}


@st.cache_data(ttl=30)
def _gorev_panou_yukle() -> list[dict]:
    """Görev panosunu data/orchestrator/task_board.json'dan yükler."""
    panoyol = _KOK / "data" / "orchestrator" / "task_board.json"
    if panoyol.exists():
        import json
        return json.loads(panoyol.read_text(encoding="utf-8-sig"))
    return []


def _gorev_bolum_getir(durum: str) -> str:
    """Görev durumundan bölüm adını belirler."""
    return _PANO_DURUM_BOLUM.get(durum, "yedek")


def render_task_board_tab() -> None:
    """Admin panelinde görev panosunu 4 bölüm halinde gösterir (ALTYAPI-ADMIN-PANO-01).

    Bölümler:
    1. Tamamlandı — done durumu görevler
    2. Beklemede — aktif, review, bekliyor durumu görevler
    3. Yedek — plan durumu görevler
    4. Değerlendirme — blocked, reddet, iptal durumu görevler (kritik + not)

    Filtreleme: ajan / aciliyet / tarih aralığı
    Renk kodlaması: bölüme göre
    """
    PageHeader(
        "Görev Panosu", ust_etiket="İş · Takip", ikon="📋",
        giris="Merkezi görev panosu — 4 bölüm: Tamamlandı / Beklemede / Yedek / Değerlendirme",
    ).render()

    # Panoyu yükle
    tum_gorevler = _gorev_panou_yukle()
    if not tum_gorevler:
        st.info("Görev panosu boş.")
        return

    # ---- Filtreler ----
    Section("Filtreler", "Görev listesini ajan, aciliyet ve tarih ile filtreleyin.", ikon="🔍").render()

    ajanlar = sorted({g.get("sahip", "") for g in tum_gorevler if g.get("sahip")})
    aciliyetler = ["P0", "P1", "P2", "P3"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        secilen_ajan = st.selectbox("Ajan", ["Hepsi"] + ajanlar, key="pano_ajan")
    with col2:
        secilen_aciliyet = st.selectbox("Aciliyet", ["Hepsi"] + aciliyetler, key="pano_aciliyet")
    with col3:
        baslangic_tarihi = st.date_input("Başlangıç", value=None, key="pano_baslangic")
    with col4:
        bitis_tarihi = st.date_input("Bitiş", value=None, key="pano_bitis")

    # Filtreleme uygula
    filtrelenmis = tum_gorevler
    if secilen_ajan != "Hepsi":
        filtrelenmis = [g for g in filtrelenmis if g.get("sahip") == secilen_ajan]
    if secilen_aciliyet != "Hepsi":
        filtrelenmis = [g for g in filtrelenmis if g.get("oncelik") == secilen_aciliyet]
    if baslangic_tarihi:
        filtrelenmis = [g for g in filtrelenmis
                       if g.get("baslangic") and g["baslangic"][:10] >= str(baslangic_tarihi)]
    if bitis_tarihi:
        filtrelenmis = [g for g in filtrelenmis
                       if g.get("bitis") and g["bitis"][:10] <= str(bitis_tarihi)]

    # Bölümlere ayır
    bolumler: dict[str, list[dict]] = {
        "tamamlandi": [],
        "beklemede": [],
        "yedek": [],
        "degerlendirme": [],
    }
    for g in filtrelenmis:
        bolum = _gorev_bolum_getir(g.get("durum", ""))
        bolumler[bolum].append(g)

    # ---- 4 Bölümü Göster ----
    bolum_bilgileri = [
        ("tamamlandi", "✅ Tamamlandı", "done durumu görevler"),
        ("beklemede", "⏳ Beklemede", "aktif + review + bekliyor durumu görevler"),
        ("yedek", "📋 Yedek", "plan durumu görevler"),
        ("degerlendirme", "🔴 Değerlendirme", "blocked + reddet + iptal durumu görevler"),
    ]

    for bolum_key, bolum_baslik, bolum_aciklama in bolum_bilgileri:
        gorevler = bolumler[bolum_key]
        renk = _PANO_BOLUM_RENKLERI[bolum_key]

        Section(
            f"{bolum_baslik} ({len(gorevler)})",
            bolum_aciklama,
            ikon="",
        ).render()

        if not gorevler:
            st.caption("Görev yok")
            continue

        # Tablo verisi hazırla
        rows = []
        for g in gorevler:
            dosyalar = g.get("dosyalar", [])
            dosya_str = ", ".join(dosyalar[:3]) if dosyalar else "-"
            if len(dosyalar) > 3:
                dosya_str += f" +{len(dosyalar)-3} daha"

            rows.append({
                "Görev ID": g.get("task_id", "-"),
                "Ajan": g.get("sahip", "-"),
                "Başlık": g.get("baslik", "-")[:60],
                "Aciliyet": g.get("oncelik", "-"),
                "Durum": g.get("durum", "-"),
                "Başlangıç": g.get("baslangic", "-")[:10] if g.get("baslangic") else "-",
                "Bitiş": g.get("bitis", "-")[:10] if g.get("bitis") else "-",
                "Dosyalar": dosya_str,
                "Not": (g.get("not", "")[:50] + "...") if g.get("not") and len(g.get("not", "")) > 50 else g.get("not", "-"),
            })

        df = pd.DataFrame(rows)

        # Stil fonksiyonu: satır rengini bölüme göre ayarla
        def _bolum_stil(row: pd.Series) -> list[str]:
            return [f"background-color: {renk}22"] * len(row)

        st.dataframe(
            df.style.apply(_bolum_stil, axis=1),
            width="stretch", hide_index=True,
        )

    # Özet metrikler
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Tamamlandı", len(bolumler["tamamlandi"]))
    with col2:
        st.metric("⏳ Beklemede", len(bolumler["beklemede"]))
    with col3:
        st.metric("📋 Yedek", len(bolumler["yedek"]))
    with col4:
        st.metric("🔴 Değerlendirme", len(bolumler["degerlendirme"]))

    st.caption(f"Toplam {len(filtrelenmis)} görev gösteriliyor (filtreli). Kaynak: data/orchestrator/task_board.json")


# ---------------------------------------------------------------------------
# UI-ADMIN-KVKK-MODU-26: KVKK Mode Kontrol Sekmesi
# ---------------------------------------------------------------------------

def _kvkk_api_token() -> str | None:
    """Oturumdan admin token al."""
    try:
        oturum = dict(st.session_state)
        return oturum.get("admin_token") or oturum.get("user_token")
    except Exception:
        return None


def _kvkk_mode_getir() -> dict | None:
    """Mevcut KVKK modunu API'den getir."""
    token = _kvkk_api_token()
    if not token:
        return None
    try:
        resp = requests.get(
            "/api/admin/kvkk-mode",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return None


def render_kvkk_mode_tab() -> None:
    """UI-ADMIN-KVKK-MODU-26: KVKK Mode Kontrol Sekmesi.

    Admin panel'de strict/lenient toggle ekler. Kullanıcı mod seçer,
    reason yazar, `/api/admin/kvkk-mode` POST çağırır.
    """
    PageHeader(
        "KVKK Mode Kontrolü", ust_etiket="İş · Yönetim", ikon="🔒",
        giris="KVKK maskeleme modunu değiştirin: Strict (varsayılan) / Lenient (admin onayıyla).",
    ).render()

    # Mevcut mod bilgisi
    mevcut = _kvkk_mode_getir()
    col1, col2 = st.columns(2)
    with col1:
        if mevcut:
            st.metric("Mevcut Mode", mevcut.get("mode", "?").capitalize())
        else:
            st.metric("Mevcut Mode", "—")
    with col2:
        if mevcut:
            st.metric("Son Değişim", str(mevcut.get("changed_at", "—"))[:16])
        else:
            st.metric("Son Değişim", "—")

    st.divider()

    # Toggle form
    with st.form("kvkk_mode_form"):
        mode = st.radio("Mode Seç", ["strict", "lenient"], horizontal=True)
        reason = st.text_area("Sebep (min 3 karakter)", placeholder="Neden değiştiriyorsunuz?")
        submit = st.form_submit_button("Mode Değiştir", type="primary")

        if submit:
            if len(reason) < 3:
                st.error("Sebep en az 3 karakter olmalı")
            else:
                token = _kvkk_api_token()
                if not token:
                    st.error("Oturum token bulunamadı. Yeniden giriş yapın.")
                else:
                    try:
                        resp = requests.post(
                            "/api/admin/kvkk-mode",
                            json={"mode": mode, "reason": reason},
                            headers={"Authorization": f"Bearer {token}"},
                            timeout=10,
                        )
                        if resp.ok:
                            st.success(f"Mode '{mode}' olarak değiştirildi")
                            st.rerun()
                        else:
                            st.error(f"Hata: {resp.json().get('detail', resp.text)}")
                    except Exception as exc:
                        st.error(f"İstek hatası: {exc}")

    # D-214: KVKK Rapor (gecmis/trend) bu sayfaya gomuldu (UI-ADMIN-KVKK-RAPOR-28).
    render_kvkk_rapor_tab()


# ---------------------------------------------------------------------------
# UI-ADMIN-KVKK-RAPOR-28: KVKK Maskeleme Raporu (D-214: kvkk_mode sayfasina gomulu)
# ---------------------------------------------------------------------------

def _kvkk_rapor_getir(limit: int = 30) -> list[dict]:
    """KVKK mode geçmişini getir."""
    token = _kvkk_api_token()
    if not token:
        return []
    try:
        resp = requests.get(
            f"/api/admin/kvkk-mode/history?limit={limit}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return []


def render_kvkk_rapor_tab() -> None:
    """UI-ADMIN-KVKK-RAPOR-28: KVKK Maskeleme Raporu.

    admin_kvkk_mode geçmişi + KPI + trend grafik. D-214: artik ayri sekme
    degil, `render_kvkk_mode_tab` sonunda cagrilan yardimci bolum.
    """
    st.divider()
    Section(
        "KVKK Maskeleme Raporu",
        "Mode geçiş geçmişi, istatistikler ve trend analizi",
        ikon="📊",
    ).render()

    # KPI'lar
    gecmis = _kvkk_rapor_getir(limit=100)
    strict_say = sum(1 for r in gecmis if r.get("mode") == "strict")
    lenient_say = sum(1 for r in gecmis if r.get("mode") == "lenient")
    en_sik_sebep = "Audit" if gecmis else "—"
    son_degisim = gecmis[0].get("changed_at", "—")[:16] if gecmis else "—"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Strict Mode", strict_say)
    with col2:
        st.metric("Lenient Mode", lenient_say)
    with col3:
        st.metric("En Sık Sebep", en_sik_sebep)
    with col4:
        st.metric("Son Değişim", son_degisim)

    st.divider()

    # Geçmiş tablo
    Section("Mode Geçişleri (son 30 gün)", "admin_kvkk_mode tablosundan", ikon="📋").render()

    if not gecmis:
        st.info("Henüz mode geçişi kaydı yok.")
    else:
        rows = []
        for r in gecmis[:30]:
            rows.append({
                "Admin": r.get("admin_id", "—"),
                "Mode": r.get("mode", "—").capitalize(),
                "Zaman": str(r.get("changed_at", "—"))[:19],
                "Sebep": r.get("reason", "—"),
                "Geçerli": str(r.get("effective_to", "—"))[:19] if r.get("effective_to") else "Süresiz",
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)

    # Trend grafik (son 7 gün)
    Section("Trend (son 7 gün)", "Günlük mode geçiş sayısı", ikon="📈").render()

    if gecmis:
        from datetime import datetime, timedelta
        bugun = datetime.now().date()
        gunluk: dict[str, dict[str, int]] = {}
        for i in range(7):
            gun = (bugun - timedelta(days=i)).isoformat()
            gunluk[gun] = {"strict": 0, "lenient": 0}

        for r in gecmis:
            zaman_str = r.get("changed_at", "")
            if zaman_str:
                try:
                    gun = zaman_str[:10]
                    if gun in gunluk:
                        gunluk[gun][r.get("mode", "strict")] += 1
                except Exception:
                    pass

        chart_data = pd.DataFrame([
            {"Tarih": gun, "Strict": v["strict"], "Lenient": v["lenient"]}
            for gun, v in sorted(gunluk.items())
        ])
        st.line_chart(chart_data.set_index("Tarih"))
    else:
        st.info("Trend için veri yok.")


# ---------------------------------------------------------------------------
# UI-KONTROL-PANOSU-32: Admin Kontrol Panosu
# ---------------------------------------------------------------------------

def _kontrol_panosu_getir() -> dict:
    """Kontrol panosu verilerini topla."""
    token = _kvkk_api_token()
    if not token:
        return {"maskeli": 0, "acik": 0, "tier_dagilimi": {}, "trend": []}

    sonuc = {"maskeli": 0, "acik": 0, "tier_dagilimi": {}, "trend": []}

    try:
        # admin_kvkk_mode istatistikleri
        resp = requests.get(
            "/api/admin/kvkk-mode/stats",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.ok:
            data = resp.json()
            sonuc["maskeli"] = data.get("masked_fields_strict", 0)
            sonuc["acik"] = data.get("visible_fields_lenient", 0)
    except Exception:
        pass

    try:
        # Tier dağılımı
        resp = requests.get(
            "/api/admin/tier-distribution",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.ok:
            sonuc["tier_dagilimi"] = resp.json()
    except Exception:
        pass

    return sonuc


def render_kontrol_panosu_tab() -> None:
    """UI-KONTROL-PANOSU-32: Admin Kontrol Panosu.

    Metrikler: maskeli alanlar (strict), açık alanlar (lenient), tier dağılımı, günlük trend.
    """
    PageHeader(
        "Kontrol Panosu", ust_etiket="İş · Yönetim", ikon="📈",
        giris="KVKK maskeleme durumu, tier dağılımı ve günlük trendler.",
    ).render()

    veri = _kontrol_panosu_getir()

    # KPI Row 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Maskeli Alan (Strict)", veri.get("maskeli", 0))
    with col2:
        st.metric("Açık Alan (Lenient)", veri.get("acik", 0))
    with col3:
        st.metric("Terminal User", "—")
    with col4:
        st.metric("Enterprise User", "—")

    # Tier Dağılımı (bar chart)
    Section("User Dağılımı (Tier)", "Paket bazlı kullanıcı sayıları", ikon="📊").render()

    tier_data = veri.get("tier_dagilimi", {})
    if tier_data:
        st.bar_chart(pd.DataFrame(list(tier_data.items()), columns=["Tier", "Sayı"]).set_index("Tier"))
    else:
        st.info("Tier dağılımı verisi yok.")

    # Günlük Trend (7 gün, line chart)
    Section("Trend (son 7 gün)", "Günlük maskeli/açık alan trendi", ikon="📈").render()

    trend = veri.get("trend", [])
    if trend:
        st.line_chart(pd.DataFrame(trend).set_index("date"))
    else:
        st.info("Trend verisi yok.")

    # Mode Geçişleri (mini tablo)
    Section("Son Mode Geçişleri", "admin_kvkk_mode (son 10)", ikon="🔒").render()

    gecmis = _kvkk_rapor_getir(limit=10)
    if gecmis:
        rows = []
        for r in gecmis:
            rows.append({
                "Admin": r.get("admin_id", "—"),
                "Mode": r.get("mode", "—").capitalize(),
                "Zaman": str(r.get("changed_at", "—"))[:19],
                "Sebep": r.get("reason", "—")[:30],
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("Mode geçişi yok.")


# ---------------------------------------------------------------------------
# UI-ADMIN-FEATURE-FLAG-25: Feature Flag Yönetim Sekmesi
# ---------------------------------------------------------------------------

def _get_feature_flags() -> dict[str, bool]:
    """Feature flag'leri session state'ten oku."""
    return dict(st.session_state.get("_feature_flags", {}))


def _save_feature_flags(flags: dict[str, bool]) -> None:
    """Feature flag'leri session state'e yaz."""
    st.session_state["_feature_flags"] = dict(flags)


def _feature_flag_audit_getir(limit: int = 20) -> list[dict]:
    """Feature flag audit log'larını getir."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT admin_id, action, target as flag_name, old_value, new_value, changed_at
                    FROM admin_audit_log
                    WHERE action = 'feature_flag_toggle'
                    ORDER BY changed_at DESC
                    LIMIT :lim
                """),
                {"lim": limit}
            ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


def render_feature_flags_tab() -> None:
    """UI-ADMIN-FEATURE-FLAG-25: Feature Flag Yönetim Sekmesi.

    - Flag listesi (aktif/pasif + açıklama)
    - Toggle UI (switch componentli)
    - Geçmiş kayıtları (kim, ne zaman, eski→yeni)
    - Sadece admin rolü
    """
    PageHeader(
        "Feature Flags", ust_etiket="İş · Yönetim", ikon="🚩",
        giris="Sistem feature flag'lerini yönetin. Sadece admin rolü erişebilir.",
    ).render()

    # Admin rol kontrolü
    try:
        session = dict(st.session_state)
        user_email = session.get("admin_email") or session.get("user_email")
        user_role = session.get("user_role", "anon")
    except Exception:
        user_email = None
        user_role = "anon"

    if user_role != "admin":
        st.error("Bu sekmeye sadece admin rolü erişebilir.")
        return

    # Default feature flags
    DEFAULT_FLAGS = {
        "new_dashboard": {"desc": "Yeni dashboard tasarımı", "default": False},
        "advanced_analytics": {"desc": "Gelişmiş analitik modülü", "default": False},
        "beta_api": {"desc": "Beta API erişimi", "default": False},
        "maintenance_mode": {"desc": "Bakım modu (tüm istekleri reddet)", "default": False},
    }

    flags = _get_feature_flags()
    # Default değerleri merge et
    for fname, fdef in DEFAULT_FLAGS.items():
        if fname not in flags:
            flags[fname] = fdef["default"]
    _save_feature_flags(flags)

    # Flag listesi + toggle
    Section("Feature Flag Listesi", "Aktif/pasif toggle + açıklama", ikon="🚩").render()

    for fname, fdef in DEFAULT_FLAGS.items():
        current = flags.get(fname, fdef["default"])
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            st.write(f"**{fname}**")
        with col2:
            new_val = st.checkbox(
                "Aktif",
                value=current,
                key=f"ff_toggle_{fname}",
                label_visibility="collapsed",
            )
            if new_val != current:
                # API çağrısı
                import requests
                try:
                    resp = requests.post(
                        "/api/admin/feature-flags",
                        json={"flag_name": fname, "new_value": new_val},
                        headers={"Authorization": f"Bearer {st.session_state.get('admin_token', '')}"},
                        timeout=5,
                    )
                    if resp.ok:
                        st.success(f"{fname} → {'Aktif' if new_val else 'Pasif'}")
                        st.rerun()
                    else:
                        st.error(f"Hata: {resp.json().get('detail', 'Bilinmeyen hata')}")
                except Exception as e:
                    st.error(f"İstek hatası: {e}")
        with col3:
            st.caption(fdef["desc"])

    st.divider()

    # Audit trail
    Section("Değişiklik Geçmişi (Audit Trail)", "Son 20 değişiklik", ikon="📋").render()

    audit = _feature_flag_audit_getir(limit=20)
    if audit:
        rows = []
        for r in audit:
            rows.append({
                "Admin": r.get("admin_id", "—"),
                "Flag": r.get("flag_name", "—"),
                "Eski": "Aktif" if r.get("old_value") == "true" else "Pasif",
                "Yeni": "Aktif" if r.get("new_value") == "true" else "Pasif",
                "Zaman": str(r.get("changed_at", "—"))[:19],
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("Henüz feature flag değişikliği yok.")



# ---------------------------------------------------------------------------
# UI-ADMIN-LTV-CAC-27: LTV/CAC Analiz Sekmesi
# ---------------------------------------------------------------------------

def _ltv_cac_api_token() -> str | None:
    """Oturumdan admin token al."""
    try:
        oturum = dict(st.session_state)
        return oturum.get("admin_token") or oturum.get("user_token")
    except Exception:
        return None


def _ltv_cac_verileri_getir(days: int = 30) -> dict | None:
    """LTV/CAC verilerini API'den getir."""
    import requests
    token = _ltv_cac_api_token()
    if not token:
        return None
    try:
        resp = requests.get(
            f"/api/admin/ltv-cac?days={days}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return None


def render_ltv_cac_tab() -> None:
    """UI-ADMIN-LTV-CAC-27: LTV/CAC Analiz Sekmesi.

    KPI kartları: LTV, CAC, Ratio
    3 tab: 30 gün | 90 gün | 180 gün
    Line chart: LTV vs CAC trend
    Stacked bar chart: Tier breakdown
    """
    from datetime import datetime, timedelta

    PageHeader(
        "LTV/CAC Analiz", ust_etiket="İş · Analitik", ikon="💰",
        giris="Müşteri yaşam boyu değeri (LTV) ve kazanım maliyeti (CAC) analizi. Ratio ≥3 sağlıklı.",
    ).render()

    # Period seçici
    days_options = {"30 gün": 30, "90 gün": 90, "180 gün": 180}
    secilen_label = st.selectbox("Periyot", list(days_options.keys()), index=0, key="ltv_cac_periyot")
    days = days_options[secilen_label]

    # Veri getir
    veri = _ltv_cac_verileri_getir(days)

    if not veri:
        st.warning("⚠️ Veri kaynağı yok — API endpoint çalışmıyor veya token bulunamadı.")
        return

    # KPI kartları
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("LTV (Ortalama)", f"{veri.get('ltv', 0):,.0f} TRY")
    with col2:
        st.metric("CAC (Kazanım Maliyeti)", f"{veri.get('cac', 0):,.0f} TRY")
    with col3:
        ratio = veri.get('ratio', 0)
        st.metric("LTV/CAC Ratio", f"{ratio:.1f}x")
    with col4:
        st.metric("Periyot", f"{days} gün")

    # Ratio durumu
    ratio = veri.get('ratio', 0)
    if ratio >= 3:
        st.success(f"✅ Sağlıklı: LTV/CAC = {ratio:.1f}x (≥3 hedef)")
    elif ratio >= 1:
        st.warning(f"⚠️ Dikkat: LTV/CAC = {ratio:.1f}x (1-3 arası)")
    else:
        st.error(f"🔴 Zarar: LTV/CAC = {ratio:.1f}x (<1)")

    st.divider()

    # 3 Tab: 30/90/180 gün trend
    tab30, tab90, tab180 = st.tabs(["📅 30 Gün", "📅 90 Gün", "📅 180 Gün"])

    trend_verisi = veri.get("trend", [])

    for tab_label, tab_days, tab_obj in [
        ("30 gün", 30, tab30),
        ("90 gün", 90, tab90),
        ("180 gün", 180, tab180),
    ]:
        with tab_obj:
            filtered_trend = [
                t for t in trend_verisi
                if (datetime.strptime(t["date"], "%Y-%m-%d").date() >= datetime.now().date() - timedelta(days=tab_days))
            ]

            if filtered_trend:
                df_trend = pd.DataFrame(filtered_trend)
                df_trend["date"] = pd.to_datetime(df_trend["date"])
                df_trend = df_trend.set_index("date")

                col1, col2 = st.columns(2)
                with col1:
                    st.line_chart(df_trend[["ltv", "cac"]])
                with col2:
                    st.line_chart(df_trend[["ratio"]])
            else:
                st.info(f"{tab_label} için trend verisi yok.")

    st.divider()

    # Tier breakdown (stacked bar chart)
    Section("Tier Bazlı LTV/CAC", "Paket bazlı LTV, CAC ve Ratio dağılımı", ikon="📊").render()

    by_tier = veri.get("by_tier", {})
    if by_tier:
        tier_df = pd.DataFrame(by_tier).T
        tier_df = tier_df.reset_index().rename(columns={"index": "Tier"})

        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(tier_df.set_index("Tier")[["ltv", "cac"]])
        with col2:
            st.bar_chart(tier_df.set_index("Tier")[["ratio"]])

        # Detay tablo
        st.dataframe(
            tier_df.rename(columns={
                "ltv": "LTV (TRY)",
                "cac": "CAC (TRY)",
                "ratio": "Ratio"
            }),
            width="stretch", hide_index=True
        )
    else:
        st.info("Tier breakdown verisi yok.")

    st.caption("Not: Ratio ≥3 sağlıklı, 1-3 arası dikkat, <1 zarar. CAC: marketing_spend / yeni_müşteri. LTV: revenue / aktif_müşteri.")

