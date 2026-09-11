{
  "agent_id": "cursor_grok",
  "task_id": "RO-01",
  "task_type": "research",
  "title": "RO (Readme Orchestrator) - Orchestrator yapısı ve README oluşturma",
  "brief_path": "workspace/external/cursor_grok/brief_RO-01.md",
  "context_files": ["src/company_master/orchestrator/README.md"],
  "constraints": {
    "no_db_schema_access": true,
    "no_env_access": true
  },
  "success_criteria": [
    "Brief JSON formatında olmalı",
    "README.md referansları içermeli"
  ],
  "deadline": null,
  "source": "harici"
}