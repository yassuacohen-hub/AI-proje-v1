import math


def lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(h):
    r, g, b = (lin(x) for x in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def cr(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def oklab(h):
    r, g, b = (lin(x) for x in rgb(h))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def hue(h):
    L, a, b = oklab(h)
    return math.degrees(math.atan2(b, a)) % 360, math.hypot(a, b)


def de(a, b):
    x, y = oklab(a), oklab(b)
    return 100 * math.dist(x, y)


# basit protan/deutan benzetimi (Machado 2009, siddet 1.0) - dogrusal RGB
DEUT = [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]
PROT = [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]


def sim(h, M):
    v = [lin(x) for x in rgb(h)]
    o = [max(0, min(1, sum(M[i][j] * v[j] for j in range(3)))) for i in range(3)]
    f = lambda c: round(255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055))
    return "#%02X%02X%02X" % tuple(f(c) for c in o)


BG, PAN, RAI = "#0D1B2A", "#171E26", "#202A34"
WARN = "#D6A42D"
adaylar = ["#E8743C", "#FF6A00", "#FF5A1F", "#FF5F00", "#FF4D00", "#FF6B2C", "#FF7A1A", "#FF5E3A"]
print("renk     hueOK  chroma  CR/bg  CR/pan  CR/rai  dE(warn)  dE(deut)  dE(prot)")
for c in adaylar:
    hh, ch = hue(c)
    dd = de(sim(c, DEUT), sim(WARN, DEUT))
    pp = de(sim(c, PROT), sim(WARN, PROT))
    print(f"{c} {hh:6.1f} {ch:6.3f} {cr(c,BG):6.2f} {cr(c,PAN):6.2f} {cr(c,RAI):6.2f} {de(c,WARN):8.1f} {dd:8.1f} {pp:8.1f}")
hh, ch = hue(WARN)
print(f"WARN {WARN} hueOK {hh:.1f} chroma {ch:.3f} CR/bg {cr(WARN,BG):.2f}")

# pembe aday: #EB5EAB — komsu renklerle mesafe (normal / deut / prot)
PK = "#EB5EAB"
hh, ch = hue(PK)
print(f"\nPEMBE {PK} hue {hh:.1f} chroma {ch:.3f} CR bg/pan/rai {cr(PK,BG):.2f}/{cr(PK,PAN):.2f}/{cr(PK,RAI):.2f}")
komsu = {"crit #F87171": "#F87171", "mor #A78BFA": "#A78BFA", "act #2563FF": "#2563FF",
         "info #6CB6FF": "#6CB6FF", "ok #22C55E": "#22C55E", "warn #D6A42D": WARN,
         "risk #E8743C": "#E8743C", "tur #FF5A1F": "#FF5A1F", "tur #FF4D00": "#FF4D00"}
for ad, k in komsu.items():
    hk, ck = hue(k)
    print(f"  vs {ad:14s} hue {hk:5.1f}  dE {de(PK,k):5.1f}  deut {de(sim(PK,DEUT),sim(k,DEUT)):5.1f}  prot {de(sim(PK,PROT),sim(k,PROT)):5.1f}")
