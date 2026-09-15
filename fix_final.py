# This script replaces both functions with their correct versions
import sys

def main():
    file_path = 'web_dashboard/tabs/admin_extras.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Correct api management function with proper indentation
    correct_api = '''def render_api_management(token: str | None = None) -> None:
    if token is None:
        token = st.session_state.get("admin_token")
    st.subheader("API Yönetimi")
    try:
        data = get_api("/api/admin/api-usage", token=token)
        if isinstance(data, dict):
            items = data.get("items", [])
            limits = data.get("rate_limits", {})
            if items:
                st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)
            else:
                st.info("API kullanım kaydı yok.")
            if limits:
                st.json(limits)
        except APIError:
            st.warning("Lütfen giriş yapın veya yetkili olun")
'''

    # Correct render_user_management function with the tier selector fix
    correct_render = '''def render_user_management(token: str | None = None) -> None:
    if token is None:
        token = st.session_state.get("admin_token")
    PageHeader(
        "Kullanıcı Yönetimi",
        "Onay bekleyen kullanıcıları yönetin ve kredi paketi tanımlayın.",
        ust_etiket="İş · Yönetim",
        ikon="👥",
    ).render()
    if not token:
        st.warning("Lütfen giriş yapın")
        return
    try:
        pending = get_api("/api/admin/pending", token=token)
        if isinstance(pending, dict):
            bekleyen = pending.get("bekleyen", [])
            if bekleyen:
                for user in bekleyen:
                    cols = st.columns([4, 1, 1])
                    with cols[0]:
                        st.write(
                            f"**{user.get('email', '')}** — {user.get('company_name', '')} ({user.get('tier', '')})"
                        )
                    with cols[1]:
                        # Tier selector for approval
                        tiers = ["terminal", "strategic", "enterprise"]
                        default_tier = user.get("tier", "terminal")
                        try:
                            default_index = tiers.index(default_tier)
                        except ValueError:
                            default_index = 0
                        selected_tier = st.selectbox(
                            "Tier",
                            options=tiers,
                            index=default_index,
                            key=f"tier_select_{user.get('user_id', '')}",
                            label_visibility="collapsed"
                        )
                    with cols[2]:
                        if st.button("Onayla", key=f"approve_{user.get('user_id', '')}"):
                            try:
                                post_api(
                                    "/api/admin/approve",
                                    json={"user_id": user.get("user_id", ""), "tier": selected_tier},
                                    token=token,
                                )
                                st.success(f"{user.get('email', '')} onaylandı ({selected_tier} tier)")
                                st.cache_data.clear()
                                st.rerun()
                            except APIError as e:
                                st.error(f"Onaylama başarısız: {e}")
            else:
                st.info("Onay bekleyen kullanıcı yok.")

            onayli_son = pending.get("onayli_son", [])
            if onayli_son:
                st.dataframe(pd.DataFrame(onayli_son), width="stretch", hide_index=True)
            else:
                st.info("Son onaylı kullanıcı yok.")

        categories = get_api("/api/admin/categories", token=token)
        if isinstance(categories, dict):
            items = categories.get("items", [])
            if items:
                st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)
            else:
                st.info("Kategori kaydı yok.")

        with st.form("kredi_formu"):
            col1, col2 = st.columns(2)
            with col1:
                kredi_user_id = st.text_input("Kullanıcı ID")
            with col2:
                kredi_miktar = st.number_input("Kredi Miktarı", min_value=1, value=50)
            if st.form_submit_button("Kredi Yükle") and kredi_user_id:
                try:
                    post_api(
                        "/api/admin/credit",
                        json={"user_id": kredi_user_id, "amount": kredi_miktar},
                        token=token,
                    )
                    st.success(f"{kredi_miktar} kredi yüklendi.")
                    st.cache_data.clear()
                    st.rerun()
                except APIError as e:
                    st.error(f"Kredi yükleme başarısız: {e}")
    except APIError:
        st.warning("Lütfen giriş yapın veya yetkili olun")
'''

    # Replace the functions in the content
    # We'll do a simple replacement: replace the api management function first, then the render_user_management function
    # We'll use the function definitions as markers.

    # Replace api management function
    api_start = content.find('def render_api_management(token: str | None = None) -> None:')
    if api_start != -1:
        # Find the end of the api management function: look for the next function definition or end of file
        api_end = content.find('def render_user_management(token: str | None = None) -> None:', api_start)
        if api_end == -1:
            api_end = len(content)
        # Replace the segment
        content = content[:api_start] + correct_api + content[api_end:]
    else:
        print("Could not find render_api_management function")

    # Replace render_user_management function
    render_start = content.find('def render_user_management(token: str | None = None) -> None:')
    if render_start != -1:
        # Find the end of the render_user_management function: look for the next function definition or end of file
        # Since this is the last function, we can go to the end of the file
        render_end = len(content)
        content = content[:render_start] + correct_render + content[render_end:]
    else:
        print("Could not find render_user_management function")

    # Write the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Both functions replaced with correct versions")

if __name__ == '__main__':
    main()
