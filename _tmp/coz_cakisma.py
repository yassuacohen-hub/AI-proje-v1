import sys

p = sys.argv[1]
L = open(p, encoding="utf-8").read().split("\n")
o = []
i = 0
blk = 0
while i < len(L):
    s = L[i]
    if s.startswith("<<<<<<< "):
        blk += 1
        j = i
        while not L[j].startswith("======="):
            j += 1
        k = j
        while not L[k].startswith(">>>>>>> "):
            k += 1
        head = L[i + 1:j]
        other = L[j + 1:k]
        if blk == 1:
            cut = [n for n, x in enumerate(head) if x.startswith("**Skill atamas")]
            res = head[:cut[1]] if len(cut) > 1 else head
            # ikinci kopya skill tablosu atildi; tablo sonu bos satir kalsin
            res = list(res)
            while res and res[-1] == "":
                res.pop()
            idx = max(n for n, x in enumerate(res) if x.startswith("| bilo |"))
            res.insert(idx + 1, "| Claude | Dış ajan / veri-görselleştirme + ölçüm | Grafik paleti ölçülebilir mi? Marka kiti hangi SSOT? | **doldu (§4.8b)** |")
            o += res
        else:
            h = list(head)
            while h and h[-1] == "":
                h.pop()
            ot = [x.replace("### 4.8 Claude ajanı", "### 4.8b Claude ajanı", 1) for x in other]
            o += h + [""] + ot
        i = k + 1
        continue
    o.append(s)
    i += 1
open(p, "w", encoding="utf-8", newline="").write("\n".join(o))
print("bloklar:", blk)
