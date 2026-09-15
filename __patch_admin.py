import io

path = r"C:\Huginn Data Projesi\Huginn Data Insights\tabs\admin_auto_refresh.py"
with io.open(path, "r", encoding="utf-8") as f:
    content = f.read()

marker = "    st.caption(\"Not: Streamlit auto_refresh, sayfa elemanlarini otomatik olarak gunceller. Cache'ler otomatik temizlenir.\")"
idx = content.rfind(marker)
if idx == -1:
    print("MARKER NOT FOUND")
else:
    new_block = (
        "    # --- Tazelik Etiketi + Yenile Butonu ---\n"
        "    st.divider()\n"
        '    st.subheader("\U0001f4fc Veri Tazelik")\n'
        "    from company_master.tazelik import tazelik_etiketi as _tazelik_etiketi\n"
        "    _guncelleme_zamani = datetime.now()\n"
        "    tazelik = _tazelik_etiketi(_guncelleme_zamani, datetime.now())\n"
        '    etiket = tazelik.get("etiketi", "bilinmiyor")\n'
        '    renk = tazelik.get("renk", "gray")\n'
        '    renk_map = {"green": "\U0001f7e2", "yellow": "\U0001f7e1", "red": "\U0001f534", "gray": "\u26aa"}\n'
        '    icon = renk_map.get(renk, "\u26aa")\n'
        '    st.markdown(f"**Son guncelleme:** {etiket} {icon}")\n'
        '    if st.button("\U0001f504 Yenile", key="tazelik-yenile"):\n'
        '        st.session_state["tazelik_yenildi"] = True\n'
        "        st.rerun()\n"
        "\n"
        "    st.caption(\"Not: Streamlit auto_refresh, sayfa elemanlarini otomatik olarak gunceller. Cache'ler otomatik temizlenir.\")"
    )
    content = content[:idx] + new_block
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("UPDATED")
