import sys
sys.path.insert(0, 'src')
from company_master.db.connection import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.connect() as conn:
    dist = conn.execute(text('SELECT email_validity_score as score, COUNT(*) as cnt FROM companies GROUP BY email_validity_score ORDER BY score')).mappings().all()
    print('email_validity_score distribution:')
    for d in dist:
        print('  {}: {}'.format(d['score'], d['cnt']))
    q = \"SELECT COUNT(*) FROM companies WHERE primary_email IS NOT NULL AND primary_email != ''\"
    total_email = conn.execute(text(q)).scalar()
    print()
    print('Total with primary_email: {}'.format(total_email))