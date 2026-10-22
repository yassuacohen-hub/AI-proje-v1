import colorsys, sys
out = open('_tmp/renk_olc.txt', 'w', encoding='utf-8')
def p(*a): print(*a, file=out)
def lin(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def L(h):
    h = h.lstrip('#'); r, g, b = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    return 0.2126*lin(r) + 0.7152*lin(g) + 0.0722*lin(b)
def cr(a, b):
    la, lb = sorted([L(a), L(b)], reverse=True); return (la+0.05)/(lb+0.05)
def hsl(h):
    h = h.lstrip('#'); r, g, b = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    hh, l, s = colorsys.rgb_to_hls(r, g, b); return (round(hh*360), round(s*100), round(l*100))
p('YUZEY H/S/L')
for n, h in [('panel bg', '#0D1B2A'), ('panel panel', '#171E26'), ('panel raised', '#202A34'), ('panel line', '#2B3744'), ('marka dark', '#09111F'), ('marka g900', '#0F172A'), ('marka darkSec', '#131C2F'), ('marka g800', '#1E293B')]:
    p(n, h, hsl(h))
p('GRADYAN duraklari: kontrast bg #0D1B2A / panel #171E26 / gunduz #EEF2F7')
sets = {'LOGO.md prompt': ['#1FD6FF', '#2979FF', '#4F46E5', '#8B3DFF'],
        'admin MARKA_RENK': ['#22D3EE', '#3B82F6', '#4F46E5', '#8B5CF6'],
        'tokens primary/hero': ['#2563FF', '#7C3AED', '#22D3EE'],
        'ui tokens.py': ['#6366F1'],
        'wire gece act/info/mor': ['#2563FF', '#6CB6FF', '#A78BFA'],
        'wire gunduz act/info/mor': ['#1F4FD8', '#1B64AD', '#6F42C1']}
for k, v in sets.items():
    for h in v:
        p(k, h, hsl(h), 'bg %.2f panel %.2f gunduz %.2f' % (cr(h, '#0D1B2A'), cr(h, '#171E26'), cr(h, '#EEF2F7')))
p('ZEMIN-YUZEY ayrimi')
for a, b in [('#0D1B2A', '#171E26'), ('#171E26', '#202A34'), ('#09111F', '#0F172A'), ('#0F172A', '#131C2F'), ('#0D1B2A', '#09111F')]:
    p(a, b, '%.2f' % cr(a, b))
p('metin vs panel / bg')
for h in ['#E6EDF5', '#A9B6C4', '#8493A3']:
    p(h, '%.2f' % cr(h, '#171E26'), '%.2f' % cr(h, '#0D1B2A'))
out.close()
