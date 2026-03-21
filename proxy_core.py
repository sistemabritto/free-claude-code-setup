#!/usr/bin/env python3
"""
Proxy Core - Servidor Proxy para APIs AI
Traduz requisições Anthropic para OpenAI e vice-versa
Com suporte a Hot Reload e Painel Admin melhorado

Repositório: sistemabritto/free-claude-code-setup
Versão: 2.1.0
"""

import os
import sys
import json
import time
import logging
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List, Generator
from dataclasses import dataclass, field
from functools import wraps

from flask import Flask, request, jsonify, Response, render_template_string, redirect, url_for, make_response
import requests
from dotenv import load_dotenv

# Importar configuração de modelos
try:
    from models_config import PROVIDERS, PROVIDER_HEADERS, get_model_info, get_free_models, RECOMMENDATIONS
    USE_MODELS_CONFIG = True
except ImportError:
    USE_MODELS_CONFIG = False

# =============================================================================
# CONFIGURAÇÃO DE LOGGING
# =============================================================================

def setup_logging():
    """Configura logging para arquivo e stdout"""
    log_dir = Path(os.path.expanduser('~/.claude-free/logs'))
    log_dir.mkdir(parents=True, exist_ok=True)
    
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(
        log_dir / 'proxy.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)
    
    return logging.getLogger('proxy')

logger = setup_logging()


# =============================================================================
# PROVEDORES - Usando models_config.py ou fallback
# =============================================================================

if USE_MODELS_CONFIG:
    # Converter PROVIDERS para formato do proxy
    PROVIDER_CONFIG = {}
    for prov_id, prov_data in PROVIDERS.items():
        PROVIDER_CONFIG[prov_id] = {
            "name": prov_data["name"],
            "base_url": prov_data["base_url"],
            "models": list(prov_data["models"].keys()),
            "env_key": f"{prov_id.upper()}_API_KEY",
            "description": prov_data.get("description", ""),
            "headers": PROVIDER_HEADERS.get(prov_id, lambda k: {
                "Authorization": f"Bearer {k}",
                "Content-Type": "application/json"
            }),
            "test_endpoint": "/models"
        }
else:
    # Fallback se models_config não disponível
    PROVIDER_CONFIG = {
        "groq": {
            "name": "Groq",
            "base_url": "https://api.groq.com/openai/v1",
            "models": ["llama-4-scout-17b-16e", "llama-3.3-70b-versatile"],
            "env_key": "GROQ_API_KEY",
            "description": "Inferência ultra-rápida",
            "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
            "test_endpoint": "/models"
        },
        "nvidia": {
            "name": "NVIDIA NIM",
            "base_url": "https://integrate.api.nvidia.com/v1",
            "models": ["moonshotai/kimi-k2-instruct"],
            "env_key": "NVIDIA_API_KEY",
            "description": "API gratuita NVIDIA",
            "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
            "test_endpoint": "/models"
        },
        "openrouter": {
            "name": "OpenRouter",
            "base_url": "https://openrouter.ai/api/v1",
            "models": ["qwen/qwen3-coder:free", "deepseek/deepseek-chat-v3-0324:free"],
            "env_key": "OPENROUTER_API_KEY",
            "description": "Gateway múltiplos modelos",
            "headers": lambda k: {
                "Authorization": f"Bearer {k}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://claude-free.local",
                "X-Title": "Claude Free Proxy"
            },
            "test_endpoint": "/models"
        },
        "zai": {
            "name": "Z.AI",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "models": ["glm-4.5-air"],
            "env_key": "ZAI_API_KEY",
            "description": "GLM models",
            "headers": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
            "test_endpoint": "/models"
        }
    }


# =============================================================================
# CONFIG MANAGER COM HOT RELOAD
# =============================================================================

@dataclass
class ProxyConfig:
    """Configuração do proxy com hot reload automático"""
    active_provider: str = "groq"
    active_model: str = "llama-4-scout-17b-16e"
    proxy_port: int = 8323
    master_key: str = ""
    config_reload_interval: int = 10
    log_level: str = "INFO"
    
    groq_api_key: str = ""
    nvidia_api_key: str = ""
    openrouter_api_key: str = ""
    zai_api_key: str = ""
    
    _last_modified: float = 0.0
    _last_reload: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    
    @property
    def env_file(self) -> Path:
        return Path(os.path.expanduser("~/.claude-free/config/.env"))
    
    def reload_if_changed(self) -> bool:
        with self._lock:
            try:
                if not self.env_file.exists():
                    return False
                
                current_mtime = self.env_file.stat().st_mtime
                current_time = time.time()
                
                if current_time - self._last_reload < 1:
                    return False
                
                if current_mtime > self._last_modified:
                    logger.info("Detectada mudança no arquivo .env, recarregando...")
                    self._last_modified = current_mtime
                    self._last_reload = current_time
                    self.load_from_env()
                    logger.info(f"Configuração recarregada: {self.active_provider} - {self.active_model}")
                    return True
                
                self._last_reload = current_time
                return False
                
            except Exception as e:
                logger.error(f"Erro ao verificar mudanças no .env: {e}")
                return False
    
    def load_from_env(self) -> None:
        try:
            if self.env_file.exists():
                load_dotenv(self.env_file, override=True)
            
            self.active_provider = os.getenv("ACTIVE_PROVIDER", self.active_provider)
            self.active_model = os.getenv("ACTIVE_MODEL", self.active_model)
            
            try:
                self.proxy_port = int(os.getenv("PROXY_PORT", str(self.proxy_port)))
            except ValueError:
                pass
            
            self.master_key = os.getenv("MASTER_KEY", "")
            
            try:
                self.config_reload_interval = int(os.getenv("CONFIG_RELOAD_INTERVAL", str(self.config_reload_interval)))
            except ValueError:
                pass
            
            self.log_level = os.getenv("LOG_LEVEL", "INFO")
            
            self.groq_api_key = os.getenv("GROQ_API_KEY", "")
            self.nvidia_api_key = os.getenv("NVIDIA_API_KEY", "")
            self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
            self.zai_api_key = os.getenv("ZAI_API_KEY", "")
            
            if self.active_provider not in PROVIDER_CONFIG:
                logger.warning(f"Provedor inválido '{self.active_provider}', usando 'groq'")
                self.active_provider = "groq"
                self.active_model = PROVIDER_CONFIG["groq"]["models"][0]
            
            logger.debug("Configuração carregada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar .env: {e}")
    
    def save_to_env(self) -> None:
        with self._lock:
            try:
                env_content = f"""# Configuração do Setup Claude Free
# Atualizado em: {datetime.now().isoformat()}

ACTIVE_PROVIDER={self.active_provider}
ACTIVE_MODEL={self.active_model}

GROQ_API_KEY={self.groq_api_key}
NVIDIA_API_KEY={self.nvidia_api_key}
OPENROUTER_API_KEY={self.openrouter_api_key}
ZAI_API_KEY={self.zai_api_key}

PROXY_PORT={self.proxy_port}
MASTER_KEY={self.master_key}
CONFIG_RELOAD_INTERVAL={self.config_reload_interval}
LOG_LEVEL={self.log_level}
"""
                self.env_file.parent.mkdir(parents=True, exist_ok=True)
                
                temp_file = self.env_file.with_suffix('.tmp')
                temp_file.write_text(env_content)
                temp_file.replace(self.env_file)
                
                self._last_modified = self.env_file.stat().st_mtime
                logger.info("Configuração salva no arquivo .env")
                
            except Exception as e:
                logger.error(f"Erro ao salvar .env: {e}")
    
    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        provider = provider or self.active_provider
        key_mapping = {
            "groq": self.groq_api_key,
            "nvidia": self.nvidia_api_key,
            "openrouter": self.openrouter_api_key,
            "zai": self.zai_api_key
        }
        return key_mapping.get(provider, "")
    
    def get_provider_config(self, provider: Optional[str] = None) -> Optional[Dict]:
        provider = provider or self.active_provider
        return PROVIDER_CONFIG.get(provider)
    
    def get_available_providers(self) -> List[str]:
        available = []
        if self.groq_api_key:
            available.append("groq")
        if self.nvidia_api_key:
            available.append("nvidia")
        if self.openrouter_api_key:
            available.append("openrouter")
        if self.zai_api_key:
            available.append("zai")
        return available
    
    def is_provider_available(self, provider: str) -> bool:
        return bool(self.get_api_key(provider))
    
    def set_active_provider(self, provider: str, model: Optional[str] = None) -> bool:
        if provider not in PROVIDER_CONFIG:
            logger.error(f"Provedor inválido: {provider}")
            return False
        
        if not self.get_api_key(provider):
            logger.error(f"API Key não configurada para: {provider}")
            return False
        
        self.active_provider = provider
        
        if model:
            self.active_model = model
        else:
            self.active_model = PROVIDER_CONFIG[provider]["models"][0]
        
        self.save_to_env()
        return True


config = ProxyConfig()


# =============================================================================
# THREAD DE HOT RELOAD
# =============================================================================

class HotReloadWorker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name="HotReloadWorker")
        self._running = True
    
    def run(self) -> None:
        logger.info("Thread de Hot Reload iniciada")
        while self._running:
            try:
                config.reload_if_changed()
            except Exception as e:
                logger.error(f"Erro no hot reload: {e}")
            time.sleep(1)
    
    def stop(self) -> None:
        self._running = False


# =============================================================================
# TRADUÇÃO DE FORMATOS
# =============================================================================

# Limite máximo de tokens por modelo (evita erro 400)
MAX_OUTPUT_TOKENS = {
    "meta-llama/llama-4-scout-17b-16e-instruct": 8192,
    "meta-llama/llama-4-scout-17b-16e": 8192,
    "llama-4-scout-17b-16e": 8192,
    "openai/gpt-oss-120b": 32768,
    "openai/gpt-oss-20b": 32768,
    "moonshotai/kimi-k2-instruct": 16384,
    "qwen/qwen3-32b": 32768,
    "llama-3.3-70b-versatile": 32768,
    "deepseek-r1-distill-llama-70b": 16384,
    # OpenRouter — sem limitação problemática
    "qwen/qwen3-coder:free": 32768,
    "nvidia/nemotron-3-super-120b-a12b:free": 32768,
    "deepseek/deepseek-r1:free": 32768,
    "deepseek/deepseek-chat-v3-0324:free": 32768,
    "google/gemini-2.0-flash-exp:free": 32768,
    "openrouter/free": 32768,
}

def translate_anthropic_to_openai(anthropic_request: Dict) -> Dict:
    model_max = MAX_OUTPUT_TOKENS.get(config.active_model, 32768)
    requested_tokens = anthropic_request.get("max_tokens", 4096)
    safe_tokens = min(requested_tokens, model_max)
    
    openai_request = {
        "model": config.active_model,
        "messages": [],
        "temperature": anthropic_request.get("temperature", 1.0),
        "max_tokens": safe_tokens,
        "stream": anthropic_request.get("stream", False),
        "top_p": anthropic_request.get("top_p"),
        "top_k": anthropic_request.get("top_k"),
    }
    
    openai_request = {k: v for k, v in openai_request.items() if v is not None}
    
    system_content = anthropic_request.get("system", "")
    messages = anthropic_request.get("messages", [])
    
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if isinstance(content, list):
            openai_content = []
            for item in content:
                if item.get("type") == "text":
                    openai_content.append({"type": "text", "text": item.get("text", "")})
                elif item.get("type") == "image":
                    source = item.get("source", {})
                    if source.get("type") == "base64":
                        openai_content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:{source.get('media_type', 'image/png')};base64,{source.get('data', '')}"}
                        })
            
            if openai_content:
                openai_request["messages"].append({"role": role, "content": openai_content})
        else:
            openai_request["messages"].append({"role": role, "content": str(content)})
    
    if system_content:
        openai_request["messages"].insert(0, {"role": "system", "content": system_content})
    
    for param in ["stop", "presence_penalty", "frequency_penalty", "user"]:
        if param in anthropic_request:
            openai_request[param] = anthropic_request[param]
    
    return openai_request


def translate_openai_to_anthropic(openai_response: Dict, input_tokens: int = 0) -> Dict:
    choices = openai_response.get("choices", [{}])
    first_choice = choices[0] if choices else {}
    message = first_choice.get("message", {})
    content = message.get("content", "")
    
    finish_reason_map = {
        "stop": "end_turn",
        "length": "max_tokens",
        "content_filter": "stop_sequence",
        "tool_calls": "tool_use"
    }
    
    return {
        "id": openai_response.get("id", f"msg_{hashlib.md5(str(time.time()).encode()).hexdigest()[:24]}"),
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": content}],
        "model": openai_response.get("model", config.active_model),
        "stop_reason": finish_reason_map.get(first_choice.get("finish_reason", "stop"), "end_turn"),
        "stop_sequence": None,
        "usage": {
            "input_tokens": openai_response.get("usage", {}).get("prompt_tokens", input_tokens),
            "output_tokens": openai_response.get("usage", {}).get("completion_tokens", 0)
        }
    }


def translate_streaming_chunk(chunk: Dict, is_first: bool = False) -> Generator[Dict, None, None]:
    choices = chunk.get("choices", [{}])
    first_choice = choices[0] if choices else {}
    delta = first_choice.get("delta", {})
    
    if is_first:
        yield {
            "type": "message_start",
            "message": {
                "id": chunk.get("id", f"msg_{hashlib.md5(str(time.time()).encode()).hexdigest()[:24]}"),
                "type": "message",
                "role": "assistant",
                "content": [],
                "model": config.active_model,
                "stop_reason": None,
                "usage": {"input_tokens": 0, "output_tokens": 0}
            }
        }
    
    content = delta.get("content", "")
    if content:
        yield {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": content}
        }
    
    if first_choice.get("finish_reason"):
        yield {"type": "content_block_stop", "index": 0}
        yield {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn"},
            "usage": {"output_tokens": chunk.get("usage", {}).get("completion_tokens", 0) if chunk.get("usage") else 0}
        }
        yield {"type": "message_stop"}


# =============================================================================
# CLIENTE HTTP
# =============================================================================

class ProviderClient:
    def __init__(self, timeout: int = 120):
        self.timeout = timeout
        self.session = requests.Session()
    
    def request(self, endpoint: str, data: Dict, provider: Optional[str] = None, stream: bool = False) -> requests.Response:
        provider = provider or config.active_provider
        provider_cfg = config.get_provider_config(provider)
        
        if not provider_cfg:
            raise ValueError(f"Provedor não configurado: {provider}")
        
        api_key = config.get_api_key(provider)
        if not api_key:
            raise ValueError(f"API Key não configurada para: {provider}")
        
        url = f"{provider_cfg['base_url']}/{endpoint.lstrip('/')}"
        headers = provider_cfg["headers"](api_key)
        
        logger.info(f"Requisição: {provider} -> {endpoint}")
        logger.debug(f"URL: {url}")
        logger.debug(f"Modelo: {data.get('model')}")
        
        response = self.session.post(url, headers=headers, json=data, stream=stream, timeout=self.timeout)
        return response
    
    def test_connection(self, provider: Optional[str] = None) -> Dict:
        provider = provider or config.active_provider
        provider_cfg = config.get_provider_config(provider)
        
        if not provider_cfg:
            return {"success": False, "error": "Provedor não configurado"}
        
        api_key = config.get_api_key(provider)
        if not api_key:
            return {"success": False, "error": "API Key não configurada"}
        
        try:
            url = f"{provider_cfg['base_url']}/{provider_cfg['test_endpoint'].lstrip('/')}"
            headers = provider_cfg["headers"](api_key)
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                model_count = len(data.get("data", []))
                return {"success": True, "message": "Conexão bem sucedida", "model_count": model_count}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text[:200]}"}
                
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Timeout na conexão"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close(self):
        self.session.close()


client = ProviderClient()


# =============================================================================
# FLASK APP
# =============================================================================

app = Flask(__name__)


# =============================================================================
# MIDDLEWARE
# =============================================================================

def require_master_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not config.master_key:
            return f(*args, **kwargs)
        
        auth = request.cookies.get('auth') or request.headers.get('X-Master-Key', '')
        
        if auth != config.master_key:
            if request.path.startswith('/api/'):
                return jsonify({"error": "Unauthorized", "code": 401}), 401
            return redirect(url_for('admin_login'))
        
        return f(*args, **kwargs)
    return decorated


@app.before_request
def before_request():
    config.reload_if_changed()
    logger.debug(f"{request.method} {request.path}")


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Master-Key'
    return response


# =============================================================================
# ROTAS DO PROXY - OPENAI FORMAT
# =============================================================================

@app.route('/v1/chat/completions', methods=['POST', 'OPTIONS'])
@app.route('/api/v1/chat/completions', methods=['POST', 'OPTIONS'])
def chat_completions():
    if request.method == 'OPTIONS':
        return jsonify({})
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body", "code": 400}), 400
        
        data["model"] = config.active_model
        stream = data.get("stream", False)
        
        logger.info(f"Chat completion request - Stream: {stream}")
        
        response = client.request("chat/completions", data, stream=stream)
        
        if response.status_code != 200:
            error_text = response.text[:500]
            logger.error(f"Erro do provedor [{response.status_code}]: {error_text}")
            return jsonify({"error": {"message": error_text, "type": "provider_error", "code": response.status_code}}), response.status_code
        
        if stream:
            def generate():
                try:
                    for line in response.iter_lines():
                        if line:
                            yield line + b'\n'
                except Exception as e:
                    logger.error(f"Erro no streaming: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return Response(generate(), content_type='text/event-stream',
                headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'X-Accel-Buffering': 'no'})
        
        return jsonify(response.json())
    
    except ValueError as e:
        logger.error(f"Erro de configuração: {e}")
        return jsonify({"error": str(e), "code": 400}), 400
    except requests.exceptions.Timeout:
        logger.error("Timeout na requisição ao provedor")
        return jsonify({"error": "Request timeout", "code": 504}), 504
    except Exception as e:
        logger.error(f"Erro interno: {e}", exc_info=True)
        return jsonify({"error": str(e), "code": 500}), 500


# =============================================================================
# ROTAS DO PROXY - ANTHROPIC FORMAT
# =============================================================================

@app.route('/v1/messages', methods=['POST', 'OPTIONS'])
@app.route('/api/v1/messages', methods=['POST', 'OPTIONS'])
def anthropic_messages():
    if request.method == 'OPTIONS':
        return jsonify({})
    
    try:
        anthropic_request = request.get_json()
        if not anthropic_request:
            return jsonify({"error": "Invalid request body", "type": "invalid_request_error"}), 400
        
        openai_request = translate_anthropic_to_openai(anthropic_request)
        stream = openai_request.get("stream", False)
        
        logger.info(f"Anthropic message request - Stream: {stream}")
        
        response = client.request("chat/completions", openai_request, stream=stream)
        
        if response.status_code != 200:
            error_text = response.text[:500]
            logger.error(f"Erro do provedor [{response.status_code}]: {error_text}")
            return jsonify({"error": {"type": "api_error", "message": error_text}}), response.status_code
        
        if stream:
            def generate_anthropic():
                try:
                    is_first = True
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]
                                if data_str == '[DONE]':
                                    yield f"event: message_stop\ndata: {{}}\n\n"
                                else:
                                    try:
                                        chunk = json.loads(data_str)
                                        for anth_chunk in translate_streaming_chunk(chunk, is_first):
                                            is_first = False
                                            yield f"event: {anth_chunk['type']}\ndata: {json.dumps(anth_chunk)}\n\n"
                                    except json.JSONDecodeError:
                                        pass
                except Exception as e:
                    logger.error(f"Erro no streaming Anthropic: {e}")
                    yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            
            return Response(generate_anthropic(), content_type='text/event-stream',
                headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'X-Accel-Buffering': 'no'})
        
        anthropic_response = translate_openai_to_anthropic(
            response.json(),
            input_tokens=len(str(anthropic_request.get("messages", [])))
        )
        return jsonify(anthropic_response)
    
    except ValueError as e:
        logger.error(f"Erro de configuração: {e}")
        return jsonify({"error": {"type": "invalid_request_error", "message": str(e)}}), 400
    except requests.exceptions.Timeout:
        logger.error("Timeout na requisição ao provedor")
        return jsonify({"error": {"type": "timeout_error", "message": "Request timeout"}}), 504
    except Exception as e:
        logger.error(f"Erro interno: {e}", exc_info=True)
        return jsonify({"error": {"type": "internal_error", "message": str(e)}}), 500


# =============================================================================
# MODELOS E HEALTH
# =============================================================================

@app.route('/v1/models', methods=['GET'])
@app.route('/api/v1/models', methods=['GET'])
def list_models():
    """Lista modelos disponíveis com informações detalhadas"""
    models = []
    
    for provider_id, provider_cfg in PROVIDER_CONFIG.items():
        available = config.is_provider_available(provider_id)
        
        for model in provider_cfg["models"]:
            model_info = {
                "id": model,
                "object": "model",
                "created": 1700000000,
                "owned_by": provider_id,
                "provider": provider_cfg["name"],
                "available": available
            }
            
            # Adicionar info extra do models_config
            if USE_MODELS_CONFIG:
                extra_info = get_model_info(model, provider_id)
                if extra_info:
                    model_info["name"] = extra_info.get("name", model)
                    model_info["best_for"] = extra_info.get("best_for", "")
                    model_info["params"] = extra_info.get("params", "")
                    model_info["context"] = extra_info.get("context", "")
                    model_info["recommended"] = extra_info.get("recommended", False)
            
            models.append(model_info)
    
    return jsonify({"object": "list", "data": models})


@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "provider": config.active_provider,
        "model": config.active_model,
        "port": config.proxy_port,
        "available_providers": config.get_available_providers()
    })


# =============================================================================
# PAINEL ADMIN - TEMPLATES
# =============================================================================

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Free - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            padding: 20px;
        }
        .login-container { width: 100%; max-width: 420px; }
        .logo { text-align: center; margin-bottom: 40px; }
        .logo h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .logo p { color: #888; font-size: 0.95em; }
        .login-box {
            background: rgba(255,255,255,0.03);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }
        .error-msg {
            background: rgba(231,76,60,0.15);
            border: 1px solid rgba(231,76,60,0.3);
            color: #e74c3c;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 25px;
            text-align: center;
        }
        .form-group { margin-bottom: 25px; }
        .form-group label { display: block; margin-bottom: 10px; color: #aaa; font-size: 0.9em; }
        .form-group input {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            background: rgba(0,0,0,0.3);
            color: white;
            font-size: 1em;
        }
        .form-group input:focus { outline: none; border-color: #00d4ff; }
        .btn-login {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #00d4ff 0%, #7b2cbf 100%);
            color: white;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-login:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,212,255,0.3); }
        .footer { text-align: center; margin-top: 30px; color: #555; font-size: 0.85em; }
        .footer a { color: #00d4ff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🤖 Claude Free</h1>
            <p>Ambiente AI Gratuito - Painel de Administração</p>
        </div>
        <div class="login-box">
            {% if error %}
            <div class="error-msg">{{ error }}</div>
            {% endif %}
            <form method="POST" action="/admin">
                <div class="form-group">
                    <label>Master Key</label>
                    <input type="password" name="master_key" placeholder="Digite sua Master Key" required autofocus>
                </div>
                <button type="submit" class="btn-login">Entrar</button>
            </form>
        </div>
        <div class="footer">
            <p>Setup Claude Free v2.1.0 | <a href="https://github.com/sistemabritto/free-claude-code-setup">GitHub</a></p>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Free - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #00d4ff;
            --secondary: #7b2cbf;
            --bg-dark: #0f0f23;
            --bg-card: rgba(255,255,255,0.03);
            --text: #fff;
            --text-muted: #888;
            --border: rgba(255,255,255,0.1);
            --success: #2ecc71;
            --warning: #f39c12;
            --danger: #e74c3c;
            --groq: #f55036;
            --nvidia: #76b900;
            --openrouter: #6366f1;
            --zai: #00b4d8;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--bg-dark) 0%, #1a1a3e 50%, #16213e 100%);
            min-height: 100vh;
            color: var(--text);
            padding: 30px 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; position: relative; }
        .header h1 {
            font-size: 2.2em;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .header p { color: var(--text-muted); }
        .logout-btn {
            position: absolute;
            top: 0;
            right: 0;
            background: rgba(255,255,255,0.1);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            font-size: 0.85em;
        }
        .logout-btn:hover { background: rgba(255,255,255,0.15); color: var(--text); }
        
        .card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(20px);
            border: 1px solid var(--border);
        }
        .card h2 {
            color: var(--primary);
            font-size: 1.2em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* Status Grid */
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .status-item {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid transparent;
        }
        .status-item.active {
            border-color: var(--primary);
            background: rgba(0,212,255,0.1);
        }
        .status-item h3 {
            font-size: 0.85em;
            color: var(--text-muted);
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        .status-item .value { font-size: 1.1em; font-weight: 600; }
        .status-item.active .value { color: var(--primary); }
        
        /* Provider Section */
        .provider-section {
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            border-left: 4px solid var(--border);
        }
        .provider-section.groq { border-left-color: var(--groq); }
        .provider-section.nvidia { border-left-color: var(--nvidia); }
        .provider-section.openrouter { border-left-color: var(--openrouter); }
        .provider-section.zai { border-left-color: var(--zai); }
        .provider-section.active { background: rgba(0,212,255,0.05); }
        
        .provider-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .provider-name { font-size: 1.1em; font-weight: 600; }
        .provider-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85em;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }
        .status-dot.configured { background: var(--success); }
        .status-dot.not-configured { background: var(--danger); }
        .status-dot.active { background: var(--primary); box-shadow: 0 0 10px var(--primary); }
        
        /* Model Cards */
        .models-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 12px;
        }
        .model-card {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
        }
        .model-card:hover { background: rgba(0,0,0,0.4); border-color: var(--border); }
        .model-card.active { border-color: var(--primary); background: rgba(0,212,255,0.1); }
        .model-card.disabled { opacity: 0.5; cursor: not-allowed; }
        
        .model-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
        .model-name { font-weight: 600; font-size: 0.95em; }
        .model-badge {
            font-size: 0.7em;
            padding: 3px 8px;
            border-radius: 4px;
            background: rgba(255,255,255,0.1);
        }
        .model-badge.recommended { background: rgba(46,204,113,0.3); color: var(--success); }
        .model-badge.top { background: rgba(243,156,18,0.3); color: var(--warning); }
        
        .model-info { font-size: 0.8em; color: var(--text-muted); margin-bottom: 5px; }
        .model-best-for {
            font-size: 0.85em;
            color: var(--primary);
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid var(--border);
        }
        
        /* Buttons */
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 500;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,212,255,0.3); }
        .btn-secondary { background: rgba(255,255,255,0.1); color: white; border: 1px solid var(--border); }
        .btn-secondary:hover { background: rgba(255,255,255,0.15); }
        .btn-success { background: var(--success); color: white; }
        .btn-danger { background: var(--danger); color: white; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        
        /* Forms */
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: var(--text-muted); font-size: 0.9em; }
        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid var(--border);
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
            color: white;
            font-size: 1em;
        }
        .form-group input:focus { outline: none; border-color: var(--primary); }
        .form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        
        /* API Info */
        .api-info {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 10px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.85em;
            margin-top: 15px;
        }
        .api-info code { color: var(--primary); }
        
        /* Alerts */
        .alert-container { position: fixed; top: 20px; right: 20px; z-index: 1000; }
        .alert {
            padding: 15px 25px;
            border-radius: 10px;
            margin-bottom: 10px;
            animation: slideIn 0.3s ease;
        }
        .alert-success { background: rgba(46,204,113,0.2); border: 1px solid var(--success); }
        .alert-error { background: rgba(231,76,60,0.2); border: 1px solid var(--danger); }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 0.85em;
        }
        .footer a { color: var(--primary); text-decoration: none; }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.8em; }
            .card { padding: 20px; }
            .models-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Claude Free - Dashboard</h1>
            <p>Gerencie seu ambiente AI gratuito</p>
            <a href="/admin/logout" class="logout-btn">Sair</a>
        </div>
        
        <!-- Status -->
        <div class="card">
            <h2>📊 Status Atual</h2>
            <div class="status-grid">
                <div class="status-item active">
                    <h3>Provedor</h3>
                    <div class="value">{{ provider_name }}</div>
                </div>
                <div class="status-item active">
                    <h3>Modelo Ativo</h3>
                    <div class="value">{{ active_model_display }}</div>
                </div>
                <div class="status-item">
                    <h3>Porta</h3>
                    <div class="value">{{ proxy_port }}</div>
                </div>
                <div class="status-item">
                    <h3>Configurados</h3>
                    <div class="value">{{ configured_count }}/{{ total_providers }}</div>
                </div>
            </div>
            
            <div class="api-info">
                <strong>OpenAI:</strong> <code>http://localhost:{{ proxy_port }}/v1/chat/completions</code><br>
                <strong>Anthropic:</strong> <code>http://localhost:{{ proxy_port }}/v1/messages</code>
            </div>
        </div>
        
        <!-- Modelos por Provedor -->
        <div class="card">
            <h2>🤖 Selecionar Modelo</h2>
            
            {% for provider_id in ['groq', 'nvidia', 'openrouter', 'zai'] %}
            {% set provider = providers_info.get(provider_id, {}) %}
            {% set is_configured = provider.get('configured', false) %}
            {% set is_active = (provider_id == active_provider) %}
            
            <div class="provider-section {{ provider_id }} {% if is_active %}active{% endif %}">
                <div class="provider-header">
                    <span class="provider-name">{{ provider.get('name', provider_id|title) }}</span>
                    <span class="provider-status">
                        <span class="status-dot {% if is_configured %}configured{% else %}not-configured{% endif %}"></span>
                        {% if is_configured %}Configurado{% else %}Não configurado{% endif %}
                        {% if is_active %}• <span class="status-dot active"></span> ATIVO{% endif %}
                    </span>
                </div>
                
                {% if provider.get('description') %}
                <p style="font-size: 0.85em; color: var(--text-muted); margin-bottom: 15px;">{{ provider.get('description') }}</p>
                {% endif %}
                
                <div class="models-grid">
                    {% for model_id, model_info in provider.get('models', {}).items() %}
                    {% set is_model_active = (model_id == active_model) %}
                    <div class="model-card {% if is_model_active %}active{% endif %} {% if not is_configured %}disabled{% endif %}"
                         onclick="{% if is_configured %}setModel('{{ provider_id }}', '{{ model_id }}'){% endif %}">
                        <div class="model-header">
                            <span class="model-name">{{ model_info.get('name', model_id) }}</span>
                            {% if model_info.get('top_pick') %}
                            <span class="model-badge top">🏆 TOP</span>
                            {% elif model_info.get('recommended') %}
                            <span class="model-badge recommended">⭐</span>
                            {% endif %}
                        </div>
                        <div class="model-info">
                            {{ model_info.get('params', '') }} | {{ model_info.get('context', '') }} ctx
                            {% if model_info.get('speed') %}| {{ model_info.get('speed') }}{% endif %}
                        </div>
                        {% if model_info.get('best_for') %}
                        <div class="model-best-for">💡 {{ model_info.get('best_for') }}</div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- API Keys -->
        <div class="card">
            <h2>🔑 Configurar API Keys</h2>
            <form id="keys-form">
                <div class="form-row">
                    <div class="form-group">
                        <label>🔑 Groq API Key {% if groq_configured %}✓{% endif %}</label>
                        <input type="password" name="groq_key" placeholder="gsk_..." value="{{ groq_key_preview }}">
                        <small style="color: var(--text-muted); font-size: 0.8em;">Obter em: console.groq.com/keys</small>
                    </div>
                    <div class="form-group">
                        <label>🟢 NVIDIA API Key {% if nvidia_configured %}✓{% endif %}</label>
                        <input type="password" name="nvidia_key" placeholder="nvapi-..." value="{{ nvidia_key_preview }}">
                        <small style="color: var(--text-muted); font-size: 0.8em;">Obter em: build.nvidia.com</small>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>🔵 OpenRouter API Key {% if openrouter_configured %}✓{% endif %}</label>
                        <input type="password" name="openrouter_key" placeholder="sk-or-..." value="{{ openrouter_key_preview }}">
                        <small style="color: var(--text-muted); font-size: 0.8em;">Obter em: openrouter.ai/keys</small>
                    </div>
                    <div class="form-group">
                        <label>🟦 Z.AI API Key {% if zai_configured %}✓{% endif %}</label>
                        <input type="password" name="zai_key" placeholder="" value="{{ zai_key_preview }}">
                        <small style="color: var(--text-muted); font-size: 0.8em;">Obter em: z.ai</small>
                    </div>
                </div>
                <button type="submit" class="btn btn-success">💾 Salvar Chaves</button>
            </form>
        </div>
        
        <!-- Teste de Conexão -->
        <div class="card">
            <h2>🧪 Testar Conexão</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 12px;">
                {% if groq_configured %}
                <button class="btn btn-secondary" onclick="testConnection('groq')">Testar Groq</button>
                {% endif %}
                {% if nvidia_configured %}
                <button class="btn btn-secondary" onclick="testConnection('nvidia')">Testar NVIDIA</button>
                {% endif %}
                {% if openrouter_configured %}
                <button class="btn btn-secondary" onclick="testConnection('openrouter')">Testar OpenRouter</button>
                {% endif %}
                {% if zai_configured %}
                <button class="btn btn-secondary" onclick="testConnection('zai')">Testar Z.AI</button>
                {% endif %}
            </div>
            <div id="test-result" style="margin-top: 15px;"></div>
        </div>
        
        <div class="footer">
            <p>Setup Claude Free v2.1.0 | <a href="https://github.com/sistemabritto/free-claude-code-setup">Documentação no GitHub</a></p>
        </div>
    </div>
    
    <div class="alert-container" id="alert-container"></div>
    
    <script>
        function showAlert(message, type) {
            const container = document.getElementById('alert-container');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            container.appendChild(alert);
            setTimeout(() => {
                alert.style.animation = 'slideIn 0.3s ease reverse';
                setTimeout(() => alert.remove(), 300);
            }, 3000);
        }
        
        function getAuthKey() {
            return document.cookie.split('; ').find(row => row.startsWith('auth='))?.split('=')[1] || '';
        }
        
        async function setModel(provider, model) {
            try {
                const response = await fetch('/api/admin/provider', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Master-Key': getAuthKey()
                    },
                    body: JSON.stringify({ provider, model })
                });
                const data = await response.json();
                
                if (data.success) {
                    showAlert('Modelo alterado: ' + model, 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showAlert(data.error || 'Erro ao alterar modelo', 'error');
                }
            } catch (e) {
                showAlert('Erro de conexão', 'error');
            }
        }
        
        async function testConnection(provider) {
            const resultDiv = document.getElementById('test-result');
            resultDiv.innerHTML = '<p style="color: #888;">Testando conexão...</p>';
            
            try {
                const response = await fetch('/api/admin/test', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Master-Key': getAuthKey()
                    },
                    body: JSON.stringify({ provider })
                });
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `<p style="color: #2ecc71;">✅ Conexão OK! ${data.model_count || 0} modelos disponíveis.</p>`;
                } else {
                    resultDiv.innerHTML = `<p style="color: #e74c3c;">❌ Erro: ${data.error}</p>`;
                }
            } catch (e) {
                resultDiv.innerHTML = `<p style="color: #e74c3c;">❌ Erro de conexão</p>`;
            }
        }
        
        document.getElementById('keys-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                groq_key: formData.get('groq_key'),
                nvidia_key: formData.get('nvidia_key'),
                openrouter_key: formData.get('openrouter_key'),
                zai_key: formData.get('zai_key')
            };
            
            try {
                const response = await fetch('/api/admin/keys', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Master-Key': getAuthKey()
                    },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                
                if (result.success) {
                    showAlert('Chaves salvas com sucesso!', 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showAlert(result.error || 'Erro ao salvar', 'error');
                }
            } catch (e) {
                showAlert('Erro de conexão', 'error');
            }
        });
    </script>
</body>
</html>
'''


# =============================================================================
# ROTAS DO ADMIN
# =============================================================================

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        key = request.form.get('master_key', '')
        if key == config.master_key:
            response = make_response(redirect(url_for('admin_dashboard')))
            response.set_cookie('auth', key, max_age=86400)
            return response
        return render_template_string(LOGIN_TEMPLATE, error="Master Key incorreta")
    
    if not config.master_key:
        return redirect(url_for('admin_dashboard'))
    
    return render_template_string(LOGIN_TEMPLATE, error=None)


@app.route('/admin/dashboard')
@require_master_key
def admin_dashboard():
    # Preparar dados dos provedores
    providers_info = {}
    
    for prov_id, prov_cfg in PROVIDER_CONFIG.items():
        configured = config.is_provider_available(prov_id)
        
        # Obter modelos com info extra
        models_info = {}
        for model_id in prov_cfg["models"]:
            model_data = {"name": model_id}
            
            if USE_MODELS_CONFIG:
                extra = get_model_info(model_id, prov_id)
                if extra:
                    model_data = extra
            
            models_info[model_id] = model_data
        
        providers_info[prov_id] = {
            "name": prov_cfg["name"],
            "description": prov_cfg.get("description", ""),
            "configured": configured,
            "models": models_info
        }
    
    # Nome amigável do modelo ativo
    active_model_display = config.active_model
    if USE_MODELS_CONFIG:
        model_info = get_model_info(config.active_model, config.active_provider)
        if model_info:
            active_model_display = model_info.get("name", config.active_model)
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        provider_name=PROVIDER_CONFIG.get(config.active_provider, {}).get("name", config.active_provider),
        active_model=config.active_model,
        active_model_display=active_model_display,
        active_provider=config.active_provider,
        proxy_port=config.proxy_port,
        configured_count=len(config.get_available_providers()),
        total_providers=len(PROVIDER_CONFIG),
        providers_info=providers_info,
        groq_configured=bool(config.groq_api_key),
        nvidia_configured=bool(config.nvidia_api_key),
        openrouter_configured=bool(config.openrouter_api_key),
        zai_configured=bool(config.zai_api_key),
        groq_key_preview=config.groq_api_key[:8] + "..." if config.groq_api_key else "",
        nvidia_key_preview=config.nvidia_api_key[:8] + "..." if config.nvidia_api_key else "",
        openrouter_key_preview=config.openrouter_api_key[:8] + "..." if config.openrouter_api_key else "",
        zai_key_preview=config.zai_api_key[:8] + "..." if config.zai_api_key else ""
    )


@app.route('/admin/logout')
def admin_logout():
    response = make_response(redirect(url_for('admin_login')))
    response.delete_cookie('auth')
    return response


# =============================================================================
# API ADMIN
# =============================================================================

@app.route('/api/admin/provider', methods=['POST'])
@require_master_key
def api_set_provider():
    data = request.get_json()
    provider = data.get('provider')
    model = data.get('model')
    
    if not provider:
        return jsonify({"success": False, "error": "Provider não especificado"})
    
    if config.set_active_provider(provider, model):
        return jsonify({"success": True, "provider": provider, "model": config.active_model})
    else:
        return jsonify({"success": False, "error": "Falha ao definir provider"})


@app.route('/api/admin/keys', methods=['POST'])
@require_master_key
def api_set_keys():
    data = request.get_json()
    
    if data.get('groq_key'):
        config.groq_api_key = data['groq_key']
    if data.get('nvidia_key'):
        config.nvidia_api_key = data['nvidia_key']
    if data.get('openrouter_key'):
        config.openrouter_api_key = data['openrouter_key']
    if data.get('zai_key'):
        config.zai_api_key = data['zai_key']
    
    config.save_to_env()
    return jsonify({"success": True})


@app.route('/api/admin/test', methods=['POST'])
@require_master_key
def api_test_connection():
    data = request.get_json()
    provider = data.get('provider', config.active_provider)
    result = client.test_connection(provider)
    return jsonify(result)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Inicia o servidor proxy"""
    # Carregar configuração inicial
    config.load_from_env()
    
    # Iniciar thread de hot reload
    hot_reload = HotReloadWorker()
    hot_reload.start()
    
    logger.info(f"Iniciando proxy na porta {config.proxy_port}")
    logger.info(f"Provedor ativo: {config.active_provider}")
    logger.info(f"Modelo ativo: {config.active_model}")
    
    # Iniciar Flask
    app.run(
        host='0.0.0.0',
        port=config.proxy_port,
        debug=False,
        threaded=True
    )


if __name__ == '__main__':
    main()
