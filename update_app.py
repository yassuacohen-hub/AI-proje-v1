import sys
path = "C:/Huginn Data Projesi/Huginn Data Insights/app.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
old = '''        TopBar(
            tanim.baslik,
            ust_etiket=f"ğŸ  Panel â€º {tanim.grup}",
        ).render()'''
new = '''        # Bu sayfada breadcrumb
        breadcrumb_path = f"🏠 {t('menu_h_ana')} > {tanim.grup} > {tanim.baslik}"
        st.caption(breadcrumb_path)
        TopBar(
            tanim.baslik,
            ust_etiket=tanim.grup,  # Fixed: was hardcoded to "İş · Yönetim"
        ).render()'''
new_content = content.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)
