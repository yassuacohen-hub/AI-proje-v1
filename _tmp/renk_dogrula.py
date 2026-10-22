# PO-2: nur RENK_SISTEMI §9-10 iddialarini bagimsiz yeniden olc (ihsan, D-382).
def L(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def cr(a, b):
    x, y = sorted((L(a), L(b)), reverse=True)
    return round((x + .05) / (y + .05), 2)


G = [("D6A42D", "171E26", 7.37), ("D6A42D", "202A34", 6.38), ("22C55E", "171E26", 7.37),
     ("22C55E", "202A34", 6.39), ("0CA30C", "202A34", 4.34), ("8A6500", "FFFFFF", 5.33),
     ("8A6500", "EDF1F5", 4.69), ("137A37", "FFFFFF", 5.43), ("C2410C", "FFFFFF", 5.18),
     ("6F42C1", "FFFFFF", 6.51), ("A78BFA", "171E26", 6.17), ("F87171", "171E26", 6.07),
     ("E8743C", "171E26", 5.60), ("6B7885", "FFFFFF", 4.52), ("6B7885", "EDF1F5", 3.98),
     ("1D4ED8", "FFFFFF", 6.70), ("1764C0", "FFFFFF", 5.80), ("C9281C", "FFFFFF", 5.52),
     ("4B5A67", "FFFFFF", 7.10), ("171E26", "0D1B2A", 1.04), ("202A34", "171E26", 1.15)]
bad = 0
for f, b, c in G:
    m = cr(f, b)
    ok = abs(m - c) <= 0.02
    bad += not ok
    print(f, b, "iddia", c, "olcum", m, "OK" if ok else "FARK")
print("sapma:", bad, "/", len(G))
