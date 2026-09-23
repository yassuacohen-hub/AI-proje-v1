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


@registry.register(
    name="ninerouter_video_gen",
    description="Generate videos via 9Router /v1/videos/generations using xAI Grok Imagine (async job flow)."
)
def ninerouter_video_gen(prompt: str, model: str = "xai/grok-imagine-video", duration: int = 8,
                         aspect_ratio: str = "16:9", resolution: str = "720p",
                         ninerouter_url: str = None, ninerouter_key: str = None) -> dict:
    """Submit a video generation job to 9Router."""
    url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model, "prompt": prompt, "duration": duration, "aspect_ratio": aspect_ratio, "resolution": resolution}
    
    try:
        resp = requests.post(f"{url}/v1/videos/generations", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return {"request_id": data.get("request_id"), "status": "pending", "model": model, "prompt": prompt}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@registry.register(
    name="ninerouter_video_poll",
    description="Poll 9Router video generation job status until done or failed."
)
def ninerouter_video_poll(request_id: str, connection_id: str = None, ninerouter_url: str = None, ninerouter_key: str = None) -> dict:
    """Poll video generation job status."""
    url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}"}
    if connection_id:
        headers["x-connection-id"] = connection_id
    
    try:
        resp = requests.get(f"{url}/v1/videos/{request_id}", headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {"request_id": request_id, "status": data.get("status", "unknown"),
                "progress": data.get("progress", 0),
                "video_url": data.get("video", {}).get("url") if data.get("status") == "done" else None}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@registry.register(
    name="ninerouter_tts",
    description="Text-to-speech via 9Router /v1/audio/speech using OpenAI / ElevenLabs / Deepgram / Edge TTS / Google TTS voices."
)
def ninerouter_tts(text: str, model: str = "openai/tts-1", ninerouter_url: str = None,
                   ninerouter_key: str = None, response_format: str = "mp3") -> dict:
    """Convert text to speech via 9Router."""
    url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model, "input": text}
    
    try:
        resp = requests.post(f"{url}/v1/audio/speech", json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        if response_format == "json":
            data = resp.json()
            return {"audio": data.get("audio"), "format": data.get("format"), "status": "success"}
        return {"audio_bytes": resp.content, "content_type": resp.headers.get("Content-Type"), "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@registry.register(
    name="ninerouter_stt",
    description="Speech-to-text via 9Router /v1/audio/transcriptions using OpenAI Whisper / Groq / Gemini / Deepgram models."
)
def ninerouter_stt(audio_file_path: str, model: str = "openai/whisper-1", language: str = None,
                   ninerouter_url: str = None, ninerouter_key: str = None) -> dict:
    """Transcribe audio file via 9Router."""
    url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    try:
        with open(audio_file_path, "rb") as f:
            files = {"file": (audio_file_path, f)}
            data = {"model": model}
            if language:
                data["language"] = language
            resp = requests.post(f"{url}/v1/audio/transcriptions", files=files, data=data, headers=headers, timeout=120)
        resp.raise_for_status()
        result = resp.json()
        return {"text": result.get("text"), "model": model, "status": "success"}
    except FileNotFoundError:
        return {"error": f"Audio file not found.", "status": "failed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@registry.register(
    name="ninerouter_embeddings",
    description="Generate vector embeddings via 9Router /v1/embeddings using OpenAI / Gemini / Mistral models for RAG, semantic search."
)
def ninerouter_embeddings(text: str, model: str = "openai/text-embedding-3-small",
                          ninerouter_url: str = None, ninerouter_key: str = None) -> dict:
    """Generate vector embeddings via 9Router."""
    url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model, "input": text}
    
    try:
        resp = requests.post(f"{url}/v1/embeddings", json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        embedding = data["data"][0]["embedding"]
        return {"embedding": embedding, "model": model, "dimensions": len(embedding), "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@registry.register(
    name="ninerouter_web_search",
    description="Web and X search via 9Router /v1/search using Tavily / Exa / Brave / Serper / Perplexity."
)
def ninerouter_web_search(query: str, provider: str = "tavily", max_results: int = 5, search_type: str = "web",
                          ninerouter_url: str = None, ninerouter_key: str = None) -> dict:
    """Search the web via 9Router."""
    url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": provider, "query": query, "max_results": max_results}
    if search_type != "web":
        payload["search_type"] = search_type
    
    try:
        resp = requests.post(f"{url}/v1/search", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return {"results": data.get("results", []), "provider": provider, "query": query, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@registry.register(
    name="ninerouter_web_fetch",
    description="Fetch URL → markdown / text / HTML via 9Router /v1/web/fetch using Firecrawl / Jina Reader / Tavily Extract."
)
def ninerouter_web_fetch(url: str, format: str = "markdown", max_characters: int = None,
                        provider: str = "jina-reader", ninerouter_url: str = None,
                        ninerouter_key: str = None) -> dict:
    """Fetch a URL and extract content via 9Router."""
    base_url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": provider, "url": url, "format": format}
    if max_characters is not None:
        payload["max_characters"] = max_characters
    
    try:
        resp = requests.post(f"{base_url}/v1/web/fetch", json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content_data = data.get("content", {})
        return {"title": data.get("title"),
                "content": content_data.get("text") if isinstance(content_data, dict) else content_data,
                "provider": provider, "url": url, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@registry.register(
    name="ninerouter_discover_models",
    description="Discover all available 9Router models: chat, image, tts, embedding, web, stt, video."
)
def ninerouter_discover_models(ninerouter_url: str = None, ninerouter_key: str = None) -> dict:
    """Discover all available models across categories."""
    url = ninerouter_url or os.environ.get("NINEROUTER_URL", "http://localhost:20128")
    key = ninerouter_key or os.environ.get("NINEROUTER_KEY", "")
    headers = {"Authorization": f"Bearer {key}"}
    categories = {
        "chat": "/v1/models",
        "image": "/v1/models/image",
        "tts": "/v1/models/tts",
        "embedding": "/v1/models/embedding",
        "web": "/v1/models/web",
        "stt": "/v1/models/stt",
        "video": "/v1/models/video"
    }
    result = {}
    for category, endpoint in categories.items():
        try:
            resp = requests.get(f"{url}{endpoint}", headers=headers, timeout=10)
            if resp.status_code == 200:
                result[category] = resp.json().get("data", [])
        except Exception as e:
            result[category] = {"error": str(e)}
    return {"models": result, "status": "success"}
