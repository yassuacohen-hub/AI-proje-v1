# -*- coding: utf-8 -*-
from pathlib import Path
p = Path("web_dashboard/tabs/__init__.py")
text = p.read_text(encoding="utf-8")
old = """        min_rol=\"admin\",
    ),
)
def varsayilan_tab()"""
new = """        min_rol=\"admin\",
    ),
    TabTanimi(
        anahtar=\"destek\",
        baslik=\"Destek\",
        ikon=\"🎫\",
        grup=GRUP_IS,
        aciklama=\"Destek merkezi ticketleri\",
        url_path=\"destek\",
        modul=\"web_dashboard.tabs.admin_destek\",
        fonksiyon=\"render_destek_tab\",
        min_rol=\"analyst\",
    ),
)
def varsayilan_tab()"""
assert old in text, "Marker not found"
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8", newline="\n")
print("Updated __init__.py")
