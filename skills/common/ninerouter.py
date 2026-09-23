# 9Router AI Gateway Skills
# Source: https://github.com/decolua/9router/tree/master/skills
# All skills follow the @registry.register pattern for Huginn agent integration

import os
import requests
from skills.base import registry

@registry.register(
    name="ninerouter_setup",
    description="Entry point for 9Router — setup, health check, model discovery. Use when the user mentions NINEROUTER_URL or wants to verify 9Router connectivity."
)
def ninerouter_setup(ninerouter_url: str = "http://localhost:20128", ninerouter_key: str = None) -> dict:
    """Verify 9Router connectivity and discover available models."""
    headers = {"Authorization": f"Bearer {ninerouter_key}"} if ninerouter_key else {}
    result = {"url": ninerouter_url, "connected": False}
    
    try:
        resp = requests.get(f"{ninerouter_url}/api/health", headers=headers, timeout=5)
        if resp.status_code == 200:
            result["connected"] = True
            result["health"] = resp.json()
            models_resp = requests.get(f"{ninerouter_url}/v1/models", headers=headers, timeout=10)
            if models_resp.status_code == 200:
                data = models_resp.json()
                result["models"] = data.get("data", [])
                result["model_count"] = len(result["models"])
            return result
        result["error"] = f"Health check returned {resp.status_code}"
        return result
    except requests.ConnectionError:
        result["error"] = "Cannot connect to 9Router. Check NINEROUTER_URL."
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


@registry.register(
    name="ninerouter_chat",
    description="Chat / code generation via 9Router using OpenAI /v1/chat/completions or Anthropic /v1/messages format with streaming + auto-fallback combos."
)
def ninerouter_chat(prompt: str, model: str = "openai/gpt-5", stream: bool = False,
                    ninerouter_url: str = None, ninerouter_key: str = None) -> dict:
    """Send a prompt to 9Router and get a chat completion."""
    url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": stream}
    
    try:
        resp = requests.post(f"{url}/v1/chat/completions", json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return {
            "content": data["choices"][0]["message"]["content"],
            "model": model,
            "tokens_used": data.get("usage", {}).get("total_tokens", 0),
            "status": "success"
        }
    except requests.HTTPError as e:
        if resp.status_code == 401:
            return {"error": "Invalid NINEROUTER_KEY. Set from Dashboard → Keys.", "status": "auth_error"}
        return {"error": f"HTTP {resp.status_code}: {resp.text}", "status": "failed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@registry.register(
    name="ninerouter_chat_anthropic",
    description="Chat via 9Router using Anthropic /v1/messages format."
)
def ninerouter_chat_anthropic(prompt: str, model: str = "cc/claude-opus-4-7", max_tokens: int = 1024,
                               ninerouter_url: str = None, ninerouter_key: str = None) -> dict:
    """Send a prompt to 9Router using Anthropic format."""
    url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}", "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
    payload = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
    
    try:
        resp = requests.post(f"{url}/v1/messages", json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        content = "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")
        return {"content": content, "model": model, "tokens_used": data.get("usage", {}).get("output_tokens", 0), "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@registry.register(
    name="ninerouter_image_gen",
    description="Generate images via 9Router /v1/images/generations using OpenAI / Gemini Imagen / DALL-E / FLUX / MiniMax / SDWebUI / ComfyUI models."
)
def ninerouter_image_gen(prompt: str, model: str = "gemini/gemini-3-pro-image-preview", size: str = "1024x1024",
                         ninerouter_url: str = None, ninerouter_key: str = None, response_format: str = "url",
                         quality: str = None) -> dict:
    """Generate an image via 9Router."""
    url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model, "prompt": prompt, "size": size, "response_format": response_format}
    if quality:
        payload["quality"] = quality
    
    try:
        resp = requests.post(f"{url}/v1/images/generations", json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return {"images": data.get("data", []), "model": model, "prompt": prompt, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}