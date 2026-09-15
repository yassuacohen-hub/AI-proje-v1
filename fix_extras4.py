# This script replaces the user approval loop in admin_extras.py with correct encoding
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
                                 st.success(f"{user.get('email', '')} onayland\u0131 ({selected_tier} tier)")
                                 st.cache_data.clear()
                                 st.rerun()
                             except APIError as e:
                                 st.error(f"Onaylama ba\u015far\u0131s\u0131z: {e}")'''

    # Replace the old block with the new block
    if old_block in content:
        content = content.replace(old_block, new_block)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Replacement successful")
    else:
        print("Old block not found in content")
        # Try to find the block with some flexibility
        # We'll split the content into lines and look for the for loop
        lines = content.splitlines(keepends=True)
        # We know the for loop starts at line 46 (0-index 45) from earlier examination
        # But let's search for the line
        for i, line in enumerate(lines):
            if line.strip() == 'for user in bekleyen:':
                print(f"Found for loop at line {i+1}")
                # We'll replace from this line to the line before the next dedented line
                # But we know the exact length of the old block in lines: 19 lines (from line 46 to 64 inclusive)
                # Let's check if the next 19 lines match the old block approximately
                # We'll just replace the next 19 lines with the new block lines
                new_block_lines = new_block.splitlines(keepends=True)
                # Ensure we have the same number of lines? We'll just replace 19 lines
                if i + 19 <= len(lines):
                    # Replace lines[i:i+19] with new_block_lines
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
