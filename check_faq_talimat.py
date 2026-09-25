import sys
sys.path.insert(0, 'src')
from company_master.orchestrator import task_board as tb

task_id = 'DOKÜMAN-KVKK-FAQ-33'
gorev = tb.gorev_getir(task_id)
print('Found:', gorev is not None)
if gorev:
    print('talimat:', gorev.get('talimat')[:80] if gorev.get('talimat') else 'None')
    print('brief:', gorev.get('brief'))