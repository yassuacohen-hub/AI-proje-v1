# This script prints the correct_api_lines to see what they are
import sys

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

# Print each line with its index
for i, line in enumerate(correct_api_lines):
    print('{}: {}'.format(i, repr(line)))
