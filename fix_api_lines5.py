# This script replaces the api management function with the correct version using line numbers and correct indentation for except (4 spaces)
import sys

def main():
    file_path = 'web_dashboard/tabs/admin_extras.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Lines are 0-indexed
    # We want to replace lines 9 to 25 (0-index) inclusive? 
    # Line 10 (1-index) is index 9
    # Line 26 (1-index) is index 25
    # We want to replace from index 9 to index 25 inclusive.
    # So we want to replace lines[9:26] (since 26 is exclusive) -> indices 9 to 25.
    start_idx = 9  # line 10
    end_idx = 26   # line 26 (exclusive) -> we will replace up to line 25 (0-index) which is line 26 (1-index)

    correct_api_lines = [
        'def render_api_management(token: str | None = None) -> None:\n',
        '    if token is None:\n',
        '        token = st.session_state.get("admin_token")\n',
        '    st.subheader("API Yönetimi")\n',
        '    try:\n',
        '        data = get_api("/api/admin/api-usage", token=token)\n',
        '        if isinstance(data, dict):\n',
        '            items = data.get("items", [])\n',
        '            limits = data.get("rate_limits", {})\n',
        '            if items:\n',
        '                st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)\n',
        '            else:\n',
        '                st.info("API kullanım kaydı yok.")\n',
        '            if limits:\n',
        '                st.json(limits)\n',
        '        except APIError:\n',
        '            st.warning("Lütfen giriş yapın veya yetkili olla\n'
    ]

    # Replace the lines
    lines[start_idx:end_idx] = correct_api_lines

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Api management function replaced using line numbers with correct indentation for except (4 spaces)")

if __name__ == '__main__':
    main()
