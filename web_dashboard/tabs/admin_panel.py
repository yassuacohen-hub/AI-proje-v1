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
            kimden = sorun.get("kimden", "orkestrator").upper()
            kime = sorun.get("ajan", "?").upper()
            with st.expander(f"**{i}. {kimden} → {kime}** — {sorun.get('task_id', '?')}"):
                st.write(f"**Sorun:** {sorun.get('sorun', '')}")
                if sorun.get("cozum"):
                    st.write(f"**İlk Çözüm Önerisi:** {sorun.get('cozum')}")
                st.caption(f"Zaman: {sorun.get('timestamp', '')}")
    
    # ---- Tüm Sorunlar (Tablo) ----
    Section("Tüm Sorunlar (Tablo Görünümü)", "Filtrelenebilir sorun listesi.", ikon="📋").render()
    
    tum_sorunlar = oku()
    if tum_sorunlar:
        rows = []
        for s in sorted(tum_sorunlar, key=lambda x: x.get("timestamp", ""), reverse=True):
            rows.append({
                "Tarih": s.get("timestamp", "")[:16],
                "Kimden": s.get("kimden", "orkestrator").upper(),
                "Kime": s.get("ajan", "").upper(),
                "Görev": s.get("task_id", ""),
                "Sorun": s.get("sorun", "")[:50],
                "Durum": s.get("durum", ""),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)
        st.caption(f"Toplam {len(tum_sorunlar)} sorun kaydedilmiş.")
    else:
        st.info("Henüz sorun kaydı yok.")
