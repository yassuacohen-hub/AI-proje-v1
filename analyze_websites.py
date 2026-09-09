from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    total_web = conn.execute(text("""
        SELECT COUNT(*) FROM companies 
        WHERE website_domain IS NOT NULL AND website_domain != ''
    """)).scalar()
    print(f"Companies with website_domain: {total_web}")

    samples = conn.execute(text("""
        SELECT company_id, legal_name, website_domain
        FROM companies 
        WHERE website_domain IS NOT NULL AND website_domain != ''
        LIMIT 20
    """)).mappings().all()
    print("\nSample websites:")
    for s in samples:
        print(f"  {s['company_id']}: {s['legal_name'][:50]} -> {s['website_domain']}")

    career_patterns = [
        '/career', '/careers', '/is-ilanlari', '/kariera',
        '/join-us', '/jobs', '/calisma-hayati', '/insan-kaynaklari',
        '/kariyer', '/is-basvuru', '/basvuru'
    ]
    print("\nCareer page path patterns to check:")
    for p in career_patterns:
        print(f"  {p}")
