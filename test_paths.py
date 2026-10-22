import sys
import os

base = "c:/Huginn Data Projesi/Huginn Data Insights"
src = os.path.join(base, "src")
print("base exists:", os.path.exists(base))
print("src exists:", os.path.exists(src))
print("src contents:", os.listdir(src) if os.path.exists(src) else "N/A")
print("company_master dir:", os.path.join(src, "company_master"))
print("etl dir:", os.path.join(src, "company_master", "etl"))
etl_path = os.path.join(src, "company_master", "etl")
print("etl exists:", os.path.exists(etl_path))
if os.path.exists(etl_path):
    print("etl contents:", os.listdir(etl_path))