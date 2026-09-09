import re
path = r'c:\Projeler\Huginn Data Insights\web_dashboard\index.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = '''            <div class="table-wrapper">
                <div class="table-scroll">
                    <table>
                        <thead><tr><th>Firma Adı</th><th>Ticaret Adı</th><th>Web</th><th>Telefon</th><th>E-posta</th><th>VKN</th><th>NACE</th><th>Skor</th></tr></thead>
                        <tbody id="companies-tbody"><tr class="loading-row"><td colspan="8"><i class="fas fa-spinner fa-spin"></i> Yükleniyor…</td></tr></tbody>
                    </table>
                </div>
            </div>'''

new = '''            <div class="table-wrapper">
                <div id="companies-loading" class="table-loading">
                    <div class="loading-spinner">
                        <div class="spinner"></div>
                        <p>Veri yükleniyor...</p>
                    </div>
                </div>
                <div id="companies-empty" class="table-empty" style="display:none">
                    <i class="fas fa-search"></i>
                    <p>Hiç firma bulunamadı. Arama terimini değiştirin veya tüm kaynakları gösterin.</p>
                </div>
                <div class="table-scroll">
                    <table>
                        <thead><tr><th>Firma Adı</th><th>Ticaret Adı</th><th>Web</th><th>Telefon</th><th>E-posta</th><th>VKN</th><th>NACE</th><th>Skor</th></tr></thead>
                        <tbody id="companies-tbody"></tbody>
                    </table>
                </div>
            </div>'''

if old in c:
    c = c.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Table HTML updated successfully')
else:
    print('Pattern not found')
    idx = c.find('table-wrapper')
    print('Context:', repr(c[idx:idx+600]))