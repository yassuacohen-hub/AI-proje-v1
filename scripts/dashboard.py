#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Huginn Data Insights - Dashboard (search, real-time, agent panel)"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd
import streamlit as st
from sqlalchemy import text

from company_master.db.connection import get_engine
from company_master.orchestrator import task_board as tb

st.set_page_config(page_title="Huginn Data Insights", layout="wide", initial_sidebar_state="expanded")
engine = get_engine()
PROJECT_ROOT = Path(__file__).resolve().parents[1]

st.sidebar.title("Navigasyon")
nav = st.sidebar.radio(
    "Sayfa",
    ["Genel Bakış", "Firma Ara", "Ajan Durumu", "Proje Yönetimi", "Web Kazıma Raporu"],
    index=0,
    key="nav",
)
st.sidebar.markdown("---")
st.sidebar.subheader("Filtreler")
ankara = st.sidebar.checkbox("Ankara", value=True)
osb = st.sidebar.checkbox("OSB", value=False)
if st.sidebar.button("Yenile", width="stretch"):
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.caption("Huginn Data Insights v1.0")

where = []
if ankara:
    where.append("is_ankara = TRUE")
if osb:
    where.append("is_osb_member = TRUE")
where_sql = "WHERE " + " AND ".join(where) if where else ""

if nav == "Genel Bakış":
    st.title("🏢 Firma Ana Veri Paneli")
    st.caption(time.strftime("%Y-%m-%d %H:%M:%S"))
    with engine.connect() as conn:
        kpi = conn.execute(text(f"""
            SELECT COUNT(*) AS total,
                   AVG(data_quality_score) AS avg_score,
                   COUNT(*) FILTER (WHERE data_quality_score >= 70) AS high,
                   COUNT(*) FILTER (WHERE data_quality_score < 30) AS low,
                   COUNT(*) FILTER (WHERE website_domain IS NOT NULL AND website_domain <> '') AS web,
                   COUNT(*) FILTER (WHERE primary_phone IS NOT NULL AND primary_phone <> '') AS tel,
                   COUNT(*) FILTER (WHERE primary_email IS NOT NULL AND primary_email <> '') AS email,
                   COUNT(*) FILTER (WHERE COALESCE(tax_number::text, vergi_no::text) IS NOT NULL) AS vkn,
                   COUNT(*) FILTER (WHERE nace_code IS NOT NULL AND nace_code <> '') AS nace
            FROM companies {where_sql}
        """)).fetchone()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Toplam", f"{kpi[0]:,}")
    c2.metric("Ortalama Skor", f"{float(kpi[1] or 0):.1f}/100")
    c3.metric("Yüksek (≥70)", f"{kpi[2]:,}")
    c4.metric("Düşük (<30)", f"{kpi[3]:,}")
    st.markdown("---")
    st.subheader("Doluluk Oranları")
    cols = st.columns(5)
    for col, label, val in zip(cols, ["Web", "Telefon", "Email", "VKN", "NACE"], kpi[4:9]):
        pct = round(float(val) / max(kpi[0], 1) * 100, 1)
        col.metric(label, f"{val:,}", delta=f"{pct}%")

    st.markdown("---")
    st.subheader("📊 Kalite Skoru Dağılımı")
    try:
        with engine.connect() as conn:
            buckets = conn.execute(text(f"""
                SELECT width_bucket(COALESCE(data_quality_score, 0), 0, 100, 10) AS b,
                       COUNT(*) AS adet
                FROM companies {where_sql}
                GROUP BY b ORDER BY b
            """)).fetchall()
        if buckets:
            hist = pd.DataFrame(
                [{"Skor Aralığı": f"{int(b) * 10 - 10}-{int(b) * 10}", "Firma": int(n)} for b, n in buckets]
            )
            st.bar_chart(hist.set_index("Skor Aralığı"))
        else:
            st.info("Veri yok")
    except Exception as exc:
        st.error(f"Grafik hatası: {exc}")

    st.markdown("---")
    st.subheader("🏭 Sektör Dağılımı (İlk 10 NACE)")
    try:
        with engine.connect() as conn:
            nace_rows = conn.execute(text(f"""
                SELECT COALESCE(NULLIF(nace_code, ''), 'Bilinmiyor') AS nace,
                       COUNT(*) AS adet
                FROM companies {where_sql}
                GROUP BY 1 ORDER BY adet DESC LIMIT 10
            """)).fetchall()
        if nace_rows:
            nace_df = pd.DataFrame(nace_rows, columns=["NACE Kodu", "Firma Sayısı"])
            st.bar_chart(nace_df.set_index("NACE Kodu"))
            st.dataframe(nace_df, width="stretch", hide_index=True)
        else:
            st.info("NACE verisi yok")
    except Exception as exc:
        st.error(f"Grafik hatası: {exc}")

elif nav == "Firma Ara":
    st.title("Firma Arama")
    search = st.text_input("Arama", placeholder="Ad, VKN, Tel, Email")
    if search:
        term = f"%{search}%"
        search_cond = (
            "(legal_name ILIKE :term "
            "OR primary_phone::text ILIKE :term "
            "OR primary_email ILIKE :term "
            "OR COALESCE(tax_number::text, vergi_no::text, '') ILIKE :term)"
        )
        full_where = (where_sql + " AND " + search_cond) if where_sql else ("WHERE " + search_cond)
        try:
            with engine.connect() as conn:
                rows = conn.execute(text(f"""
                    SELECT legal_name, primary_phone, primary_email,
                           COALESCE(tax_number::text, vergi_no::text) AS vkn,
                           data_quality_score, website_domain
                    FROM companies
                    {full_where}
                    ORDER BY data_quality_score DESC
                    LIMIT 50
                """), {"term": term}).fetchall()
        except Exception as exc:
            st.error(f"Sorgu hatası: {exc}")
            rows = []
        if rows:
            df = pd.DataFrame(rows, columns=["Firma", "Telefon", "Email", "VKN", "Skor", "Web"])
            st.dataframe(df, width="stretch", hide_index=True)
            st.caption(f"{len(rows)} sonuç")
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇️ Sonuçları CSV olarak indir",
                csv,
                file_name="firma_arama_sonuclari.csv",
                mime="text/csv",
                width="stretch",
            )
        else:
            st.info("Sonuç bulunamadı")
    else:
        st.info("Aramak için bir terim girin")

elif nav == "Ajan Durumu":
    st.title("🤖 Ajan Durumu & Görev Paneli")
    st.caption("Görev panosu, dosya kilitleri ve orkestratör durumu — gerçek zamanlı")
    otomatik = st.toggle("⏱️ Otomatik yenileme (30 saniyede bir)", value=False)

    tasks = tb.gorev_listesi()
    active_tasks = [t for t in tasks if t.get("durum") == "aktif"]
    plan_tasks = [t for t in tasks if t.get("durum") == "plan"]
    review_tasks = [t for t in tasks if t.get("durum") == "review"]
    blocked_tasks = [t for t in tasks if t.get("durum") == "blocked"]
    done_tasks = [t for t in tasks if t.get("durum") == "done"]

    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    col_a.metric("🔴 Aktif", len(active_tasks))
    col_b.metric("🟡 Plan", len(plan_tasks))
    col_c.metric("🔵 Review", len(review_tasks))
    col_d.metric("⚫ Bloklu", len(blocked_tasks))
    col_e.metric("🟢 Bitti", len(done_tasks))

    st.markdown("---")

    PRIO_ICON = {"P0": "🔴", "P1": "🟠", "P2": "🟡"}

    def _task_card(t: dict, show_end: bool = False) -> None:
        p = t.get("oncelik", "?")
        icon = PRIO_ICON.get(p, "⚪")
        st.markdown(f"**{icon} {t.get('task_id', '?')} — {t.get('baslik', '??')}**")
        bits = [f"Sahip: `{t.get('sahip', '?')}`", f"Öncelik: `{p}`"]
        if t.get("baslangic"):
            bits.append(f"Başlangıç: {str(t['baslangic'])[:16]}")
        if show_end and t.get("bitis"):
            bits.append(f"Bitiş: {str(t['bitis'])[:16]}")
        st.caption(" | ".join(bits))
        files = t.get("dosyalar") or []
        if files:
            st.caption("📎 " + ", ".join(files[:3]) + (" …" if len(files) > 3 else ""))
        note = (t.get("not") or "").strip()
        if note:
            st.caption(f"📝 {note}")
        st.markdown("")

    if active_tasks:
        with st.expander(f"📋 Aktif Görevler ({len(active_tasks)})", expanded=True):
            for t in active_tasks:
                _task_card(t)
    else:
        st.info("Aktif görev yok")

    if plan_tasks:
        with st.expander(f"📌 Planlanan Görevler ({len(plan_tasks)})"):
            for t in plan_tasks:
                _task_card(t)

    if review_tasks:
        with st.expander(f"🔍 İncelemede ({len(review_tasks)})"):
            for t in review_tasks:
                _task_card(t)

    if blocked_tasks:
        with st.expander(f"🚫 Bloklanmış ({len(blocked_tasks)})"):
            for t in blocked_tasks:
                _task_card(t)

    if done_tasks:
        with st.expander(f"✅ Tamamlanan ({len(done_tasks)})"):
            for t in done_tasks:
                _task_card(t, show_end=True)

    st.markdown("---")
    st.subheader("🔒 Dosya Kilitleri")
    try:
        locks = tb.locklar() or {}
    except Exception:
        locks = {}
    if locks:
        lock_rows = [
            {"Dosya": k, "Sahip": v.get("sahip", "?"), "Görev": v.get("task_id", "?"),
             "Kilitlenme": str(v.get("litkilendi") or v.get("kilitlendi") or "?")[:16]}
            for k, v in locks.items()
        ]
        st.dataframe(pd.DataFrame(lock_rows), width="stretch", hide_index=True)
    else:
        st.info("Açık dosya kilidi yok")

    st.markdown("---")
    st.subheader("⚙️ Orkestrator Durumu")
    state_file = PROJECT_ROOT / "data" / "orchestrator" / "state.json"
    if state_file.exists():
        try:
            state_data = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            state_data = {}
        if state_data:
            c1, c2 = st.columns(2)
            c1.metric("Durum", state_data.get("status", "?"))
            c2.metric("Son Güncelleme", str(state_data.get("last_updated", "?"))[:16])
            with st.expander("📄 state.json detayı"):
                st.json(state_data)
        else:
            st.info("state.json boş — orkestrator henüz durum yazmamış")

    try:
        handoffs = tb.handoff_tum() or {}
    except Exception:
        handoffs = {}
    if handoffs:
        with st.expander(f"🤝 Handoff Kayıtları ({len(handoffs)})"):
            st.json(handoffs)

    st.markdown("---")
    st.subheader("🌐 Harici Ajan Görevleri")
    ext_file = PROJECT_ROOT / "data" / "orchestrator" / "harici_ajan_gorevleri.json"
    if ext_file.exists():
        try:
            ext_tasks = json.loads(ext_file.read_text(encoding="utf-8"))
        except Exception:
            ext_tasks = []
        for et in ext_tasks:
            with st.expander(f"🛰️ {et.get('gorev_id', '?')} — {et.get('baslik', '??')} ({et.get('ajan', '?')})"):
                st.markdown(f"**Ajan:** `{et.get('ajan', '?')}` | **Öncelik:** `{et.get('oncelik', '?')}`")
                st.write(et.get("aciklama", ""))
                if et.get("dosyalar"):
                    st.caption("📎 " + ", ".join(et["dosyalar"]))
                if et.get("beklenen_cikti"):
                    st.caption(f"🎯 Beklenen çıktı: `{et['beklenen_cikti']}`")
    else:
        st.info("Harici ajan görev dosyası yok")

    if otomatik:
        time.sleep(30)
        st.rerun()

elif nav == "Proje Yönetimi":
    st.title("📋 Proje Yönetimi & Durum")
    st.caption("Huginn Data Insights — V1.0 proje durumu, kilometre taşları ve kararlar")

    state_md = PROJECT_ROOT / "AI proje v1" / "V10" / "project_state.md"
    roadmap_md = PROJECT_ROOT / "PROJECT_ROADMAP.md"
    kpi_md = PROJECT_ROOT / "data" / "kpi_raporu.md"

    st.subheader("📈 Veri Kalitesi KPI Özeti")
    if kpi_md.exists():
        kpi_text = kpi_md.read_text(encoding="utf-8")
        lines = kpi_text.splitlines()
        for line in lines:
            l = line.replace("#", "").strip()
            if any(x in l for x in ["Toplam Firma", "Ortalama Kalite", "Hedef", "VERİ KALİTESİ"]):
                st.write(f"**{l}**")
        st.markdown("**Alan Doluluk Oranları:**")
        rows = []
        for line in lines:
            if "|" in line and "%" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and parts[0] not in ("Alan", "------"):
                    rows.append(parts)
        if rows:
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            st.markdown("**İlerleme Görselleştirme:**")
            for row in rows[:7]:
                if len(row) >= 2:
                    try:
                        val_str = row[1]
                        if "(" in val_str and "%" in val_str:
                            pct = float(val_str.split("(")[1].split("%")[0])
                            st.progress(pct / 100, text=f"{row[0]}: {pct}%")
                    except Exception:
                        pass
    else:
        st.info("KPI raporu bulunamadı")

    st.markdown("---")
    st.subheader("📄 Proje Durumu (project_state.md)")
    if state_md.exists():
        st.caption("`AI proje v1/V10/project_state.md`")
        with st.expander("Tam dosyayı görüntüle"):
            st.markdown(state_md.read_text(encoding="utf-8"))
        st.markdown("**Kararlar & Riskler:**")
        content = state_md.read_text(encoding="utf-8")
        for section in ["Aktif Kararlar", "Bilinen Riskler", "Açık Sorunlar", "Çözülen Kararlar"]:
            if f"## {section}" in content:
                st.markdown(f"**{section}:**")
                sec = content.split(f"## {section}")[1].split("##")[0]
                st.markdown(sec[:1500])
    else:
        st.warning("project_state.md bulunamadı")

    st.markdown("---")
    st.subheader("🗺️ Proje Yol Haritası")
    if roadmap_md.exists():
        with st.expander("PROJECT_ROADMAP.md"):
            st.markdown(roadmap_md.read_text(encoding="utf-8"))
    else:
        st.info("Roadmap dosyası bulunamadı")

elif nav == "Web Kazıma Raporu":
    st.title("🕷️ Web Kazıma Raporları")
    st.caption("OSINT Scraper motoru verileri — kaynak bazlı scrape durumu ve kalite")

    data_dir = PROJECT_ROOT / "data"
    ostim_dir = data_dir / "ostim"
    scrape_state_file = ostim_dir / ".scrape_state.json"
    kalite_file = ostim_dir / "kalite_raporu.md"
    detay_rapor = PROJECT_ROOT / "logs" / "ostim_detay_raporu.md"

    st.subheader("📊 Kazıma Özeti")
    total_records = 0
    completed_sectors = 0
    if scrape_state_file.exists():
        try:
            state = json.loads(scrape_state_file.read_text(encoding="utf-8"))
            total_records = state.get("total_records", 0)
            completed_sectors = len(state.get("completed_sectors", {}))
        except Exception:
            pass
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Kayıt", f"{total_records:,}")
    col2.metric("Tamamlanan Sektör", f"{completed_sectors}/17")
    col3.metric("Ortalama Kalite", "69.7/100" if kalite_file.exists() else "-")
    col4.metric("Aktif Kaynak", "OSTİM")

    st.markdown("---")
    st.subheader("🎯 Sektör Bazlı İlerleme")
    if scrape_state_file.exists():
        try:
            state = json.loads(scrape_state_file.read_text(encoding="utf-8"))
            sectors = state.get("completed_sectors", {})
            if sectors:
                df = pd.DataFrame(
                    [{"Sektör": k, "Tamamlanan": v} for k, v in sectors.items()]
                ).sort_values("Tamamlanan", ascending=False)
                st.dataframe(df, width="stretch", hide_index=True)
                st.bar_chart(df.set_index("Sektör"))
            else:
                st.info("Sektör verisi yok")
        except Exception as exc:
            st.error(f"state okunamadı: {exc}")

    st.markdown("---")
    st.subheader("📈 OSTİM Veri Kalite Raporu")
    if kalite_file.exists():
        with st.expander("📄 kalite_raporu.md — Detaylı rapor"):
            st.markdown(kalite_file.read_text(encoding="utf-8"))
    else:
        st.info("Kalite raporu yok")

    st.subheader("🔍 Detay Scrape Raporu")
    if detay_rapor.exists():
        with st.expander("📄 ostim_detay_raporu.md"):
            st.markdown(detay_rapor.read_text(encoding="utf-8"))
    else:
        st.info("Detay raporu henüz yok")

    st.markdown("---")
    st.subheader("⚙️ OSINT Scraper Motoru")
    docs_file = PROJECT_ROOT / "docs" / "OSINT_SCRAPER_MOTORU.md"
    if docs_file.exists():
        with st.expander("📚 OSINT Scraper Dokümantasyonu"):
            st.markdown(docs_file.read_text(encoding="utf-8"))

    st.subheader("📂 Ham Veri Önizleme")
    raw_files = []
    for sub in ["ostim", "aso"]:
        d = data_dir / sub
        if d.exists():
            raw_files.extend(sorted(d.glob("*.jsonl")))
            raw_files.extend(sorted(d.glob("*.json")))
    if raw_files:
        chosen = st.selectbox("Dosya seç", [f.name for f in raw_files])
        sel = next((f for f in raw_files if f.name == chosen), None)
        if sel is not None:
            try:
                head = sel.read_text(encoding="utf-8", errors="ignore").splitlines()[:20]
                st.caption(f"`{sel}` — ilk {len(head)} satır")
                st.code("\n".join(head), language="json")
            except Exception as exc:
                st.error(f"Okunamadı: {exc}")
    else:
        st.info("Ham veri dosyası bulunamadı")
