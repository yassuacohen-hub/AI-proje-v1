lines = open("web_dashboard/tabs/admin_extras.py", "r").readlines()
lines[25] = "    except APIError:\n"
lines[26] = "            st.warning(\"L?tfen giri? yap?n veya yetkili olun\")\n"
open("web_dashboard/tabs/admin_extras.py", "w").write("".join(lines))
