# This script replaces the user approval loop in admin_extras.py using string replacement
import sys

def main():
    file_path = 'web_dashboard/tabs/admin_extras.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    old_block = '''                 for user in bekleyen:
                     cols = st.columns([4, 1])
                     with cols[0]:
                         st.write(
                             f"**{user.get('email', '')}** — {user.get('company_name', '')} ({user.get('tier', '')})"
                         )
                     with cols[1]:
                         if st.button("Onayla", key=f"approve_{user.get('user_id', '')}"):
                             try:
                                 post_api(
                                     "/api/admin/approve",
                                     json={"user_id": user.get("user_id", ""), "tier": "terminal"},
                                     token=token,
                                 )
                                 st.success(f"{user.get('email', '')} onaylandı")
                                 st.cache_data.clear()
                                 st.rerun()
                             except APIError as e:
                                 st.error(f"Onaylama başarısız: {e}")'''

    new_block = '''                 for user in bekleyen:
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
                                 st.error(f"Onaylama başarısız: {e}")'''

    # Replace the old block with the new block
    if old_block in content:
        content = content.replace(old_block, new_block)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Replacement successful")
    else:
        print("Old block not found")
        # Try to find a similar block? Maybe the indentation is off
        # Let's try to split by lines and look for the for loop
        lines = content.splitlines(keepends=True)
        # We'll look for the line that contains "for user in bekleyen:"
        for i, line in enumerate(lines):
            if "for user in bekleyen:" in line:
                # Found the start, now we need to find the end of the block
                # We'll assume the block ends before the line that is not indented more than the for loop
                # But we know the exact lines, so we can replace from i to i+18 (19 lines) if that matches
                # Let's extract the block from i to i+18 and see if it matches the old block approximately
                pass

if __name__ == '__main__':
    main()
