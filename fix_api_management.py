# This script fixes the api management function by replacing it with the correct version
import sys

def main():
    file_path = 'web_dashboard/tabs/admin_extras.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the line numbers for the api management function
    # We know from the restored file that the api management function starts at line 10 (1-index)
    # and ends before the render_user_management function at line 29 (1-index)
    # So we replace lines 9 to 27 (0-index) inclusive? Actually, we want to replace from line 10 to line 28 (1-index) because line 29 is the next function.
    # In 0-index: start_index = 9 (line 10), end_index = 27 (line 28) -> we want to replace up to but not including index 28? 
    # Let's think: we want to replace lines 10 through 28 (1-index) -> indices 9 through 27 (0-index) inclusive.
    # So we want to replace lines[9:28] (since 28 is exclusive) -> indices 9 to 27.
    start_idx = 9  # line 10
    end_idx = 28   # line 28 (exclusive) -> we will replace up to line 27 (0-index) which is line 28 (1-index)

    new_api_lines = [
        'def render_api_management(token: str | None = None) -> None:\n',
        '    if token is None:\n',
        '        token = st.session_state.get("admin_token")\n',
        '    st.subheader("API Yönetimi")\n',
        '    try:\n',
        '        data = get_api("/api/admin/api-usage", token=token)\n',
        '        if isinstance(data, dict):\n',
        '            items = data.get("items", [])',
        '            limits = data.get("rate_limits", {})',
        '            if items:\n',
        '                st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)\n',
        '            else:\n',
        '                st.info("API kullanım kaydı yok.")\n',
        '            if limits:\n',
        '                st.json(limits)\n',
        '        except APIError:\n',
        '            st.warning("Lütfen giriş yapın veya yetkili olun")\n'
    ]

    # Replace the lines
    lines[start_idx:end_idx] = new_api_lines

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Api management function replaced")

if __name__ == '__main__':
    main()
