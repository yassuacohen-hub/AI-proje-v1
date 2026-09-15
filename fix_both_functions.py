# This script replaces both the api management and render_user_management functions with their correct versions
import sys

def main():
    file_path = 'web_dashboard/tabs/admin_extras.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Correct api management function
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

    # Correct render_user_management function
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

    # Replace the api management function
    # We'll find the start and end of the api management function by looking for the function definition and the next function definition
    # We know the api management function starts with "def render_api_management"
    # and ends before the render_user_management function
    # We'll do a simple replacement: replace the entire content between the two function definitions
    # But we can also do two separate replacements.

    # First, replace the api management function
    # We'll use a marker: the string "def render_api_management" and replace until we see "def render_user_management"
    # We'll split the content by lines and rebuild.

    lines = content.splitlines(keepends=True)
    new_lines = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == 'def render_api_management(token: str | None = None) -> None:':
            # We found the start of the api management function
            # We will skip the old api management function and insert the correct one
            new_lines.extend(correct_api.splitlines(keepends=True))
            # Now we need to skip the old api management function lines until we reach the render_user_management function
            # We'll advance i until we find the line that starts with "def render_user_management"
            while i < len(lines) and not lines[i].strip().startswith('def render_user_management'):
                i += 1
            # Now i is at the line of the render_user_management function, we will not add the old lines, and we will continue the loop to add the correct render function later
            continue
        elif lines[i].strip() == 'def render_user_management(token: str | None = None) -> None:':
            # We found the start of the render_user_management function
            # We will skip the old render_user_management function and insert the correct one
            new_lines.extend(correct_render.splitlines(keepends=True))
            # Skip the old render_user_management function lines until the end of the file
            while i < len(lines) and not (i+1 < len(lines) and lines[i+1].strip() == '' and lines[i+2].strip().startswith('def ')):
                # We'll skip until we see a blank line followed by a function definition, or just skip to the end
                # For simplicity, we'll skip until the end of the file
                i += 1
            # We will break out of the loop after adding the correct render function, but we need to add the remaining lines if any
            # We'll break and then add the remaining lines after the function
            break
        else:
            new_lines.append(lines[i])
            i += 1

    # If we broke out of the loop, we need to add the remaining lines
    if i < len(lines):
        # We have already added the correct render function, so we need to add the lines after the old render function
        # We have skipped the old render function lines, so we need to add the lines from i onwards
        new_lines.extend(lines[i:])

    # Join the lines back into a string
    new_content = ''.join(new_lines)

    # Write the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Both functions replaced")

if __name__ == '__main__':
    main()
