# This script replaces the render_user_management function with the correct version
import sys

def main():
    file_path = 'web_dashboard/tabs/admin_extras.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the line number where the render_user_management function starts
    # We know from the current file that it starts at line 29 (1-index) because we saw the PageHeader call remnants
    # But to be safe, we can search for the line that contains 'def render_user_management'
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip() == 'def render_user_management(token: str | None = None) -> None:':
            start_idx = i
            break
    if start_idx is None:
        print("Could not find the render_user_management function")
        return

    # We will replace from start_idx to the end of the file
    new_render_lines = [
        'def render_user_management(token: str | None = None) -> None:\n',
        '    if token is None:\n',
        '        token = st.session_state.get("admin_token")\n',
        '    PageHeader(\n',
        '        "Kullanıcı Yönetimi",\n',
        '        "Onay bekleyen kullanıcıları yönetin ve kredi paketi tanımlayın.",\n',
        '        ust_etiket="İş · Yönetim",\n',
        '        ikon="👥",\n',
        '    ).render()\n',
        '    if not token:\n',
        '        st.warning("Lütfen giriş yapın")\n',
        '        return\n',
        '    try:\n',
        '        pending = get_api("/api/admin/pending", token=token)\n',
        '        if isinstance(pending, dict):\n',
        '            bekleyen = pending.get("bekleyen", [])\n',
        '            if bekleyen:\n',
        '                for user in bekleyen:\n',
        '                    cols = st.columns([4, 1, 1])\n',
        '                    with cols[0]:\n',
        '                        st.write(\n',
        '                            f"**{user.get(\'email\', \'\')}** — {user.get(\'company_name\', \'\')} ({user.get(\'tier\', \'\')})"\n',
        '                        )\n',
        '                    with cols[1]:\n',
        '                        if st.button("Onayla", key=f"approve_{user.get(\'user_id\', \'\')}"):\n',
        '                            try:\n',
        '                                post_api(\n',
        '                                    "/api/admin/approve",\n',
        '                                    json={"user_id": user.get("user_id", ""), "tier": selected_tier},\n',
        '                                    token=token,\n',
        '                                )\n',
        '                                st.success(f"{user.get(\'email\', \'\')} onaylandı ({selected_tier} tier)")\n',
        '                                st.cache_data.clear()\n',
        '                                st.rerun()\n',
        '                            except APIError as e:\n',
        '                                st.error(f"Onaylama başarısız: {e}")\n',
        '            else:\n',
        '                st.info("Onay bekleyen kullanıcı yok.")\n',
        '\n',
        '            onayli_son = pending.get("onayli_son", [])\n',
        '            if onayli_son:\n',
        '                st.dataframe(pd.DataFrame(onayli_son), width="stretch", hide_index=True)\n',
        '            else:\n',
        '                st.info("Son onaylı kullanıcı yok.")\n',
        '\n',
        '        categories = get_api("/api/admin/categories", token=token)\n',
        '        if isinstance(categories, dict):\n',
        '            items = categories.get("items", [])\n',
        '            if items:\n',
        '                st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)\n',
        '            else:\n',
        '                st.info("Kategori kaydı yok.")\n',
        '\n',
        '        with st.form("kredi_formu"):\n',
        '            col1, col2 = st.columns(2)\n',
        '            with col1:\n',
        '                kredi_user_id = st.text_input("Kullanıcı ID")\n',
        '            with col2:\n',
        '                kredi_miktar = st.number_input("Kredi Miktarı", min_value=1, value=50)\n',
        '            if st.form_submit_button("Kredi Yükle") and kredi_user_id:\n',
        '                try:\n',
        '                    post_api(\n',
        '                        "/api/admin/credit",\n',
        '                        json={"user_id": kredi_user_id, "amount": kredi_miktar},\n',
        '                        token=token,\n',
        '                    )\n',
        '                    st.success(f"{kredi_miktar} kredi yüklendi.")\n',
        '                    st.cache_data.clear()\n',
        '                    st.rerun()\n',
        '                except APIError as e:\n',
        '                    st.error(f"Kredi yükleme başarısız: {e}")\n',
        '    except APIError:\n',
        '        st.warning("Lütfen giriş yapın veya yetkili olun")\n'
    ]

    # Replace the lines
    lines[start_idx:] = new_render_lines

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Render_user_management function replaced")

if __name__ == '__main__':
    main()
