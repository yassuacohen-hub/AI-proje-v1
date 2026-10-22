import shutil
import os
p = r"c:\Huginn Data Projesi\Huginn Data Insights\frontend"
next_dir = os.path.join(p, ".next")
if os.path.exists(next_dir):
    shutil.rmtree(next_dir)
    print("eski .next silindi")

# next-env.d.ts'i de sil (yeniden uretilir)
next_env = os.path.join(p, "next-env.d.ts")
if os.path.exists(next_env):
    os.remove(next_env)
    print("next-env.d.ts silindi")

print("Temizlik tamamlandi")