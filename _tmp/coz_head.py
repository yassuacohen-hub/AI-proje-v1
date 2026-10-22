import sys

p = sys.argv[1]
L = open(p, encoding="utf-8").read().split("\n")
o = []
mode = 0
n = 0
for s in L:
    if s.startswith("<<<<<<< "):
        mode = 1
        n += 1
    elif s.startswith("=======") and mode == 1:
        mode = 2
    elif s.startswith(">>>>>>> ") and mode == 2:
        mode = 0
    elif mode != 2:
        o.append(s)
open(p, "w", encoding="utf-8", newline="").write("\n".join(o))
print("bloklar:", n)
