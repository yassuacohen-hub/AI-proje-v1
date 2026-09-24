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
from company_master.chat import oku, ozet  # noqa: E402

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

    col_rehber, col_kimlik = st.columns([1, 3], vertical_alignment="center")
    with col_rehber:
        rehber = st.toggle("ℹ️ Sekme rehberi", key="ayarlar_rehber",
                           help="Bu ekranın amacını, veri kaynağını ve kısıtlarını gösterir.")
    with col_kimlik:
        st.caption(
            f"Ayarlar bu kullanıcıya özeldir (`{kullanici_id}`) ve tarayıcıdan bağımsız "
            "olarak sunucuda saklanır."
        )

    if rehber:
        st.info(
            "**Bu ekran ne işe yarar?** Panel tercihlerinizi (tema, tablo satır sayısı, "
            "bildirimler vb.) kullanıcı bazında kalıcı olarak saklar. Bir kez kaydettiğinizde "
            "farklı tarayıcı veya cihazdan girseniz bile aynı ayarlar geçerli olur.\n\n"
            "**Nasıl kullanılır?** Her sekme bir ayar grubudur. İstediğiniz alanları değiştirip "
            "en alttaki **Kaydet** düğmesine basın. **Varsayılana dön** ile tüm ayarları "
            "başlangıç değerlerine sıfırlayabilirsiniz.\n\n"
            "**Veriler nereden gelir?** Ayar tanımları `company_master.settings` şemasından "
            "otomatik üretilir; yeni bir ayar eklendiğinde bu ekranda kendiliğinden görünür.\n\n"
            "**Dikkat:** Kaydetme işlemi hepsi-ya-hiç çalışır. Bir alan geçersizse "
            "hata gösterilir ve hiçbir değer kaydedilmez; düzeltip yeniden kaydedin."
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

    # ---- Metrikler ----
    Section("Sorun Durumu Özeti", "Açık, çözüm bekleniyor ve çözüldü sayıları.", ikon="📊").render()

    acik = ozet("acik")
    cokundurmus = ozet("cokundurmus")
    cozuldu = ozet("cozuldu")

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
            ajan_alici_display = ajan_alici.upper()
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

    tum_sorunlar = oku()
    if tum_sorunlar:
        rows = []
        for s in sorted(tum_sorunlar, key=lambda x: x.get("timestamp", ""), reverse=True):
            # Eski kayıtlarda kimden yoksa orkestrator kabul et
            ajan_gonderici = s.get("kimden") or "orkestrator"
            ajan_alici = s.get("ajan", "?")
            onem_ham = s.get("onem", "orta")
            rows.append({
                "Gönderen": ajan_gonderici.upper(),
                "Alıcı": ajan_alici.upper(),
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
