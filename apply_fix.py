# This script applies the fix to admin_extras.py
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
        print("Old block not found in content")
        # As a fallback, we can try to split by lines and replace by line numbers
        lines = content.splitlines(keepends=True)
        # Find the line that contains "for user in bekleyen:"
        for i, line in enumerate(lines):
            if line.strip() == 'for user in bekleyen:':
                print(f"Found for loop at line {i+1}")
                # The old block from the original is 19 lines (from line 46 to 64 inclusive, 0-index 45 to 63)
                # We'll replace 19 lines starting at i
                new_block_lines = new_block.splitlines(keepends=True)
                if i + 19 <= len(lines):
                    lines[i:i+19] = new_block_lines
                    content = ''.join(lines)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print("Replacement successful using line numbers")
                else:
                    print("Not enough lines to replace")
                break

if __name__ == '__main__':
    main()
