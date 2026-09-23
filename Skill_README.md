# Huginn Common Skills Readme

> A standardized skill system for Huginn agents. All skills follow a unified registry pattern.

## Structure

```
skills/
├── base.py                      # SkillRegistry base class + @registry.register decorator
├── common/                      # Shared/common skills (usable by ALL agents)
│   ├── __init__.py             # Exports all common skills
│   ├── file_ops.py             # File operations (safe_file_read, safe_file_write)
│   ├── llm_helper.py           # LLM token counting & validation
│   ├── osint.py                # OSINT & risk analysis (6 skills)
│   ├── orchestrator.py         # Agent orchestration & deployment (5 skills)
│   ├── admin_panel.py          # Admin dashboard & security (6 skills)
│   └── streamlit_production.py # Streamlit production monitoring (4 skills)
├── devops/                      # DevOps & infrastructure skills
│   ├── docker.py               # Docker operations
│   ├── nginx.py                # Nginx configuration
│   └── monitor.py              # System monitoring
├── streamlit/                  # Streamlit-specific skills
│   ├── debug.py                # Streamlit debugging
│   └── ux_ui.py                # Streamlit UX/UI (registry pattern)
└── Skill_README.md              # This documentation
```
## What is a Skill?

A skill is a modular, reusable capability that agents can use. Each skill:

- Has a **single responsibility**
- Is **reusable** across agents
- Has **clear inputs/outputs** (typed parameters, dict return)
- Is **registered** via `@registry.register` decorator
- Is **testable** independently

## Quick Start

### Creating a New Skill

```python
from skills.base import registry

@registry.register(
    name="my_skill_name",           # snake_case, unique
    description="Clear description of what this skill does"
)
def my_skill_name(param1: str, param2: int = 0) -> dict:
    """Detailed docstring with parameters and return value."""
    # Implementation
    return {"result": "value", "status": "success"}
```
## Skill Categories

### 1. Common Skills (`skills/common/`) — Available to ALL Agents

| Module | Skills | Purpose |
|--------|--------|---------|
| `file_ops.py` | `safe_file_read`, `safe_file_write` | Safe file I/O |
| `llm_helper.py` | `count_tokens`, `validate_llm_response` | LLM utilities |
| `osint.py` | `extract_company_identity`, `analyze_reputation`, `assess_security_posture`, `detect_fraud_risk`, `map_financial_signals`, `enrich_vendor_data` | OSINT & risk |
| `orchestrator.py` | `analyze_bottlenecks`, `optimize_plan`, `deploy_agent_groups`, `trigger_deployment`, `generate_operator_briefing` | Agent orchestration |
| `admin_panel.py` | `generate_admin_dashboard_kpis`, `analyze_tenant_health`, `analyze_churn_risk`, `track_ai_costs`, `analyze_data_quality`, `generate_security_alerts` | Admin & security |
| `streamlit_production.py` | `analyze_streamlit_lifecycle`, `fix_streamlit_websocket`, `generate_streamlit_config`, `analyze_performance_metrics` | Streamlit production |

### 2. DevOps Skills (`skills/devops/`)

| Module | Skills | Purpose |
|--------|--------|---------|
| `docker.py` | Docker operations | Container management |
| `nginx.py` | Nginx configuration | Web server config |
| `monitor.py` | System monitoring | Health checks |

### 3. Streamlit Skills (`skills/streamlit/`)

| Module | Skills | Purpose |
|--------|--------|---------|
| `debug.py` | Streamlit debugging | Troubleshooting |
| `ux_ui.py` | Streamlit UX/UI | UI improvements |

## 9Router Skill Integration

The following external skills from [decolua/9router](https://github.com/decolua/9router) are integrated as common skills:

| 9Router Skill | Huginn Skill Name | Description |
|---------------|-------------------|-------------|
| 9router | `ninerouter_setup` | Entry point, setup & health check |
| 9router-chat | `ninerouter_chat` | Chat/code generation via OpenAI-compatible API |
| 9router-image | `ninerouter_image_gen` | Image generation via multiple providers |
| 9router-video | `ninerouter_video_gen` | Video generation (xAI Grok Imagine, async) |
| 9router-tts | `ninerouter_tts` | Text-to-speech via multiple providers |
| 9router-stt | `ninerouter_stt` | Speech-to-text (Whisper, Deepgram, etc.) |
| 9router-embeddings | `ninerouter_embeddings` | Vector embeddings for RAG & similarity |
| 9router-web-search | `ninerouter_web_search` | Web/X search (Tavily, Exa, etc.) |
| 9router-web-fetch | `ninerouter_web_fetch` | URL → markdown extraction |

These skills are created in `skills/common/ninerouter.py` and follow the same `@registry.register` pattern.
### Executing a Skill
## How to Add a New Skill

1. **Create** a new `.py` file in the appropriate directory
2. **Import** the registry: `from skills.base import registry`
3. **Decorate** your function with `@registry.register(name=..., description=...)`
4. **Define** typed parameters and return type `-> dict`
5. **Add** to `__init__.py` exports
6. **Test** with unit tests
7. **Update** this README if adding a new category

## Naming Conventions

- **snake_case** for all function and skill names
- **descriptive** names that indicate purpose
- **prefixes** for external integrations: `ninerouter_`, `devops_`, `streamlit_`
- **No prefixes** for internal/common skills

## Best Practices

1. **Single Responsibility**: Each skill does one thing well
## Migration from 9Router Skills

To integrate 9Router skills into the Huginn system:

1. **Extract** the core functionality from each 9Router SKILL.md
2. **Define** Python function parameters matching the API inputs
3. **Implement** the logic using `requests` to 9Router endpoints
4. **Register** with `@registry.register` decorator
5. **Place** in `skills/common/ninerouter.py`
6. **Add** to `skills/common/__init__.py`

### Example Migration Template

```python
from skills.base import registry
import requests, os

@registry.register(
    name="ninerouter_chat",
    description="Chat / code generation via 9Router using OpenAI /v1/chat/completions format."
)
def ninerouter_chat(prompt: str, model: str = "openai/gpt-5", stream: bool = False) -> dict:
    """Send a prompt to 9Router and get a chat completion.
    
    Args:
        prompt: The user message
        model: Model ID from /v1/models
        stream: Whether to stream the response
        
    Returns:
        dict: Response with 'content', 'model', 'tokens_used'
    """
    url = f"{os.environ.get('NINEROUTER_URL', 'http://localhost:20128')}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.environ.get('NINEROUTER_KEY', '')}"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return {
            "content": data["choices"][0]["message"]["content"],
            "model": model,
            "tokens_used": data.get("usage", {}).get("total_tokens", 0)
        }
    except Exception as e:
## Agent Skill Access Pattern

Agents can access skills in two ways:

1. **Direct Import**: `from skills.common.orchestrator import analyze_bottlenecks`
2. **Registry Execution**: `registry.execute_skill("analyze_bottlenecks", **params)`

All agents should be able to:
- **Create** new skills in the appropriate category
- **Upload** skills to the common skills directory
- **Share** skills across agents via the registry
- **Discover** available skills via `registry.get_all_schemas()`

## Troubleshooting

- **Skill not found**: Ensure it's in `__init__.py` and the file imports correctly
- **Registry error**: Check that `@registry.register` decorator is used correctly
- **Import error**: Verify the file path and module name match

---

> **Note**: This README is maintained as part of the skill system. Update it when adding new categories or major changes.
        return {"error": str(e), "status": "failed"}
```
2. **Type Annotations**: Always use `-> dict` return type
3. **Docstrings**: Include parameter descriptions and return value
4. **Error Handling**: Return meaningful error dicts, don't raise bare exceptions
5. **Graceful Degradation**: Return `{"error": "..."}` when data is missing
5. **Testable**: Write unit tests for each new skill
6. **Documented**: Update this README for new categories or major changes

```python
from skills.base import registry

# Execute by name
result = registry.execute_skill("my_skill_name", param1="hello", param2=42)

# Get all skill schemas (for LLM tool descriptions)
schemas = registry.get_all_schemas()
```

### Importing Skills

```python
from skills.common.orchestrator import analyze_bottlenecks, optimize_plan
from skills.common.admin_panel import generate_admin_dashboard_kpis
from skills.common.osint import extract_company_identity, analyze_reputation
```