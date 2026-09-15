# This script replaces the user approval loop in admin_extras.py
import sys

def main():
    file_path = 'web_dashboard/tabs/admin_extras.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # We know the exact lines to replace (from line 46 to 64, 1-indexed)
    # Convert to 0-index: start at 45, end at 63 inclusive
    start_idx = 45
    end_idx = 63  # inclusive

    # The new block as a list of strings, using triple quotes for the f-string to avoid escaping issues
    new_block = [
        '                 for user in bekleyen:\n',
        '                     cols = st.columns([4, 1, 1])\n',
        '                     with cols[0]:\n',
        '                         st.write(\n',
        '                             f"**{user.get(\'email\', \'\')} — {user.get(\'company_name\', \'\')} ({user.get(\'tier\', \'\')})"\n',
        '                         )\n',
        '                     with cols[1]:\n',
        '                         # Tier selector for approval\n',
        '                         tiers = ["terminal", "strategic", "enterprise"]\n',
        '                         default_tier = user.get("tier", "terminal")\n',
        '                         try:\n',
        '                             default_index = tiers.index(default_tier)\n',
        '                         except ValueError:\n',
        '                             default_index = 0\n',
        '                         selected_tier = st.selectbox(\n',
        '                             "Tier",\n',
        '                             options=tiers,\n',
        '                             index=default_index,\n',
        '                             key=f"tier_select_{user.get(\'user_id\', \'\')}",\n',
        '                             label_visibility="collapsed"\n',
        '                         )\n',
        '                     with cols[2]:\n',
        '                         if st.button("Onayla", key=f"approve_{user.get(\'user_id\', \'\')}"):\n',
        '                             try:\n',
        '                                 post_api(\n',
        '                                     "/api/admin/approve",\n',
        '                                     json={"user_id": user.get("user_id", ""), "tier": selected_tier},\n',
        '                                     token=token,\n',
        '                                 )\n',
        '                                 st.success(f"{user.get(\'email\', \'\')} onaylandı ({selected_tier} tier)")\n',
        '                                 st.cache_data.clear()\n',
        '                                 st.rerun()\n',
        '                             except APIError as e:\n',
        '                                 st.error(f"Onaylama başarısız: {e}")\n'
    ]

    # Replace the lines
    new_lines = lines[:start_idx] + new_block + lines[end_idx+1:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    main()
