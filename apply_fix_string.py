# This script applies the fix using string replacement on the restored original
import sys

def main():
    file_path = 'web_dashboard/tabs/admin_extras.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    old_block = '''                for user in bekleyen:
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

    new_block = '''                for user in bekleyen:
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
        # Print the first 200 characters of content to see what we have
        print("First 200 chars of content:")
        print(repr(content[:200]))
        # Also print the old_block we are looking for
        print("Old block we are looking for:")
        print(repr(old_block))

if __name__ == '__main__':
    main()
