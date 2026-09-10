import re
path = "src/company_master/intelligence/job_intelligence/sources/company_career.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """            # Placeholder domainleri atla
            skip_domains = ["""
new = """            # Gecersiz domainleri atla (cift nokta, bos label, ozel karakterler)
            if not re.match(r'^(https?://)?([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\\.)+[a-zA-Z]{2,}$', website):
                logger.debug("[%s] Gecersiz domain atlandi: %s", self.source_name, website)
                continue

            # Placeholder domainleri atla
            skip_domains = ["""
assert old in content, "anchor not found"
content = content.replace(old, new, 1)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("patched")
