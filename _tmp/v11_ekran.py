import subprocess, pathlib
src = pathlib.Path('Huginn Data Insights/docs/MUSTERI_PANEL_WIREFRAME_V11.html')
h = src.read_text(encoding='utf-8')
chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
base = pathlib.Path('_tmp').resolve()
cases = {
    'v11_ana': '',
    'v11_esles': "<script>git('esles');</script>",
    'v11_esles_sec': "<script>git('esles');document.querySelectorAll('.etk')[5].click();</script>",
}
for ad, ek in cases.items():
    p = base / f'{ad}.html'
    p.write_text(h.replace('</body>', ek + '</body>'), encoding='utf-8')
    # ponytail: kabuk .dar acik gelir; geniş menü için ayrı çekim yok
    subprocess.run([chrome, '--headless=new', '--disable-gpu', '--window-size=1440,1500',
                    '--virtual-time-budget=4000', f'--screenshot={base / (ad + ".png")}',
                    p.as_uri()], capture_output=True, timeout=90)
    print(ad, (base / (ad + '.png')).exists())
