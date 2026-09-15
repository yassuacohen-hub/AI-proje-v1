# This script replaces the api management function with the exact correct version from the original
import sys

def main():
    file_path = 'web_dashboard/tabs/admin_extras.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Exact correct api management function from the original
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

    # Replace the api management function
    # Find the start of the api management function
    api_start = content.find('def render_api_management(token: str | None = None) -> None:')
    if api_start != -1:
        # Find the end of the api management function: look for the next function definition
        api_end = content.find('def render_user_management(token: str | None = None) -> None:', api_start)
        if api_end == -1:
            api_end = len(content)
        # Replace the segment
        content = content[:api_start] + correct_api + content[api_end:]
    else:
        print("Could not find render_api_management function")
        return

    # Write the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Api management function replaced with exact correct version")

if __name__ == '__main__':
    main()
