import re
path = "src/company_master/intelligence/job_intelligence/sources/company_career.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """        for company in self.companies_cache[:max_pages]:
            career_url = self._find_career_page(company['website_domain'])
            if not career_url:
                continue
            
            html = self._fetch(career_url)
            if not html:
                continue
            
            job = self.parse_job_detail(html, career_url)
            if job:
                # company_id'yi raw_data'ya ekle
                job.raw_data['company_id'] = company['company_id']
                job.raw_data['company_name'] = company['legal_name']
                jobs.append(job)
            
            processed += 1"""
new = """        for company in self.companies_cache[:max_pages]:
            try:
                career_url = self._find_career_page(company['website_domain'])
                if not career_url:
                    continue
                
                html = self._fetch(career_url)
                if not html:
                    continue
                
                job = self.parse_job_detail(html, career_url)
                if job:
                    job.raw_data['company_id'] = company['company_id']
                    job.raw_data['company_name'] = company['legal_name']
                    jobs.append(job)
            except Exception as e:
                logger.warning("[%s] Sirket islenirken hata: %s - %s", self.source_name, company.get('legal_name'), e)
            finally:
                processed += 1"""
assert old in content, "anchor not found"
content = content.replace(old, new, 1)
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("patched2")
