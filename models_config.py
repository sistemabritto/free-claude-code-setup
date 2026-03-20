#!/usr/bin/env python3
"""
Mapeamento de Modelos e Provedores - Setup Claude Free
Atualizado: 2025 - Melhores modelos para CÓDIGO

MODELOS TOP PARA CÓDIGO:
- Qwen3 Coder 480B (OpenRouter FREE) - MELHOR para código
- Kimi K2 / K2.5 (NVIDIA FREE) - Excelente para código
- Llama 4 Scout (Groq FREE) - Rápido + código
- MiniMax M2.5 (NVIDIA FREE) - Especialista código
"""

# =============================================================================
# PROVEDORES E MODELOS - ATUALIZADO 2025
# =============================================================================

PROVIDERS = {
    # =========================================================================
    # GROQ - 100% GRÁTIS (Ultra-rápido)
    # =========================================================================
    "groq": {
        "name": "Groq",
        "description": "Inferência ULTRA-RÁPIDA via LPU. 100% gratuito, sem rate limits.",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_prefix": "gsk_",
        "get_url": "https://console.groq.com/keys",
        "categories": ["free"],
        
        "models": {
            # Llama 4 - Melhor para código na Groq
            "llama-4-scout-17b-16e": {
                "name": "Llama 4 Scout 17B",
                "params": "17B×16 Experts (MoE)",
                "context": "128K",
                "best_for": "🏆 CÓDIGO - Multimodal, Rápido",
                "speed": "~460 tok/s",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            "llama-4-maverick-17b-128e": {
                "name": "Llama 4 Maverick 17B",
                "params": "17B×128 Experts",
                "context": "128K",
                "best_for": "Tarefas complexas, Reasoning",
                "speed": "~300 tok/s",
                "tier": "free",
                "recommended": True
            },
            "llama-3.3-70b-versatile": {
                "name": "Llama 3.3 70B",
                "params": "70B",
                "context": "128K",
                "best_for": "Chat geral, Versátil",
                "speed": "~100 tok/s",
                "tier": "free"
            },
            "deepseek-r1-distill-llama-70b": {
                "name": "DeepSeek R1 Distill 70B",
                "params": "70B",
                "context": "128K",
                "best_for": "Reasoning profundo, Matemática",
                "speed": "~80 tok/s",
                "tier": "free"
            }
        }
    },
    
    # =========================================================================
    # OPENROUTER - Vários modelos FREE
    # =========================================================================
    "openrouter": {
        "name": "OpenRouter",
        "description": "Gateway para múltiplos provedores. Vários modelos FREE.",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_prefix": "sk-or_",
        "get_url": "https://openrouter.ai/keys",
        "categories": ["free", "low_cost"],
        
        "models": {
            # MELHOR MODELO GRÁTIS PARA CÓDIGO
            "qwen/qwen3-coder:free": {
                "name": "Qwen3 Coder 480B",
                "params": "480B total (35B active)",
                "context": "262K",
                "best_for": "CÓDIGO AVANÇADO - TOP!",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            "deepseek/deepseek-chat-v3-0324:free": {
                "name": "DeepSeek V3 Chat",
                "params": "685B MoE",
                "context": "128K",
                "best_for": "Chat geral, Análise",
                "tier": "free",
                "recommended": True
            },
            "deepseek/deepseek-r1:free": {
                "name": "DeepSeek R1",
                "params": "671B MoE",
                "context": "128K",
                "best_for": "Reasoning profundo",
                "tier": "free",
                "recommended": True
            },
            "google/gemini-2.0-flash-exp:free": {
                "name": "Gemini 2.0 Flash",
                "params": "Flash",
                "context": "1M",
                "best_for": "Contexto longo",
                "tier": "free"
            },
            # Low-cost
            "deepseek/deepseek-chat": {
                "name": "DeepSeek V3 (paid)",
                "params": "685B MoE",
                "context": "128K",
                "best_for": "Melhor qualidade",
                "tier": "low_cost",
                "price": "$0.27/$1.10 per 1M"
            }
        }
    },
    
    # =========================================================================
    # NVIDIA NIM - GRATUITO (Rate Limited)
    # =========================================================================
    "nvidia": {
        "name": "NVIDIA NIM",
        "description": "API gratuita com rate limits. 189+ modelos. Ótimo para código.",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_prefix": "nvapi-",
        "get_url": "https://build.nvidia.com/",
        "categories": ["free"],
        
        "models": {
            # KIMI K2 - TOP PARA CÓDIGO
            "moonshotai/kimi-k2-instruct": {
                "name": "Kimi K2",
                "params": "MoE Large (1T params)",
                "context": "128K",
                "best_for": "🏆 CÓDIGO - Excelente raciocínio!",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            # KIMI K2.5 - Versão mais recente
            "moonshotai/kimi-k2.5-instruct": {
                "name": "Kimi K2.5",
                "params": "MoE Large (atualizado)",
                "context": "128K",
                "best_for": "🏆 CÓDIGO - Versão melhorada",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            # MINIMAX M2.5 - Excelente para código
            "minimaxai/minimax-m2.5-250106": {
                "name": "MiniMax M2.5 230B",
                "params": "230B",
                "context": "128K",
                "best_for": "CÓDIGO, Reasoning avançado",
                "tier": "free",
                "recommended": True
            },
            "nvidia/nemotron-4-340b-instruct": {
                "name": "Nemotron 4 340B",
                "params": "340B",
                "context": "4K",
                "best_for": "Chat geral, Síntese",
                "tier": "free"
            },
            "meta/llama-3.1-405b-instruct": {
                "name": "Llama 3.1 405B",
                "params": "405B",
                "context": "128K",
                "best_for": "Máxima qualidade geral",
                "tier": "free",
                "recommended": True
            },
            "meta/llama-3.3-70b-instruct": {
                "name": "Llama 3.3 70B",
                "params": "70B",
                "context": "128K",
                "best_for": "Equilibrado e eficiente",
                "tier": "free"
            },
            "deepseek-ai/deepseek-r1": {
                "name": "DeepSeek R1",
                "params": "671B MoE",
                "context": "128K",
                "best_for": "Reasoning profundo, Matemática",
                "tier": "free",
                "recommended": True
            },
            "qwen/qwen3-235b-a22b-instruct": {
                "name": "Qwen3 235B",
                "params": "235B (22B active)",
                "context": "128K",
                "best_for": "Código, Multimodal",
                "tier": "free",
                "recommended": True
            }
        }
    },
    
    # =========================================================================
    # Z.AI - GRATUITO LIMITADO
    # =========================================================================
    "zai": {
        "name": "Z.AI (GLM)",
        "description": "GLM models. Plano gratuito limitado.",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_prefix": "",
        "get_url": "https://z.ai/",
        "categories": ["free_limited"],
        
        "models": {
            "glm-4.5-air": {
                "name": "GLM 4.5 Air",
                "params": "MoE Compact",
                "context": "128K",
                "best_for": "Código, Agentes",
                "tier": "free_limited",
                "recommended": True
            },
            "glm-4.5": {
                "name": "GLM 4.5",
                "params": "MoE Large",
                "context": "128K",
                "best_for": "Código avançado",
                "tier": "paid",
                "price": "$2.20/$0.45 per 1M"
            }
        }
    }
}

# =============================================================================
# RECOMENDAÇÕES POR CASO DE USO
# =============================================================================

RECOMMENDATIONS = {
    "coding": {
        "title": "Programação e Código",
        "free": [
            ("qwen/qwen3-coder:free", "OpenRouter", "🏆 MELHOR para código - 480B"),
            ("moonshotai/kimi-k2.5-instruct", "NVIDIA", "⭐ Kimi K2.5 - Versão melhorada"),
            ("moonshotai/kimi-k2-instruct", "NVIDIA", "⭐ Kimi K2 - Excelente código"),
            ("llama-4-scout-17b-16e", "Groq", "⚡ Ultra-rápido (~460 tok/s)"),
            ("minimaxai/minimax-m2.5-250106", "NVIDIA", "⭐ MiniMax M2.5 - 230B código"),
        ]
    },
    "reasoning": {
        "title": "Reasoning e Matemática",
        "free": [
            ("deepseek-ai/deepseek-r1", "NVIDIA", "DeepSeek R1 - NVIDIA API"),
            ("deepseek/deepseek-r1:free", "OpenRouter", "DeepSeek R1 - OpenRouter"),
            ("deepseek-r1-distill-llama-70b", "Groq", "R1 rápido na Groq"),
        ]
    },
    "general": {
        "title": "Chat Geral",
        "free": [
            ("deepseek/deepseek-chat-v3-0324:free", "OpenRouter", "Excelente geral - 685B"),
            ("llama-3.3-70b-versatile", "Groq", "Rápido e versátil"),
            ("meta/llama-3.3-70b-instruct", "NVIDIA", "Llama 3.3 via NVIDIA"),
        ]
    },
    "speed": {
        "title": "Velocidade Máxima",
        "free": [
            ("llama-4-scout-17b-16e", "Groq", "~460 tok/s - TOP velocidade"),
            ("llama-4-maverick-17b-128e", "Groq", "~300 tok/s"),
        ]
    }
}

# =============================================================================
# MAPEAMENTO PARA O PROXY
# =============================================================================

PROXY_MODELS = {
    "groq": [
        "llama-4-scout-17b-16e",
        "llama-4-maverick-17b-128e", 
        "llama-3.3-70b-versatile",
        "deepseek-r1-distill-llama-70b"
    ],
    "openrouter": [
        "qwen/qwen3-coder:free",
        "deepseek/deepseek-chat-v3-0324:free",
        "deepseek/deepseek-r1:free",
        "google/gemini-2.0-flash-exp:free"
    ],
    "nvidia": [
        "moonshotai/kimi-k2-instruct",
        "moonshotai/kimi-k2.5-instruct",
        "minimaxai/minimax-m2.5-250106",
        "meta/llama-3.1-405b-instruct",
        "meta/llama-3.3-70b-instruct",
        "deepseek-ai/deepseek-r1",
        "qwen/qwen3-235b-a22b-instruct"
    ],
    "zai": [
        "glm-4.5-air",
        "glm-4.5"
    ]
}

# Headers por provedor
PROVIDER_HEADERS = {
    "groq": lambda key: {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    },
    "openrouter": lambda key: {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://claude-free.local",
        "X-Title": "Claude Free Proxy"
    },
    "nvidia": lambda key: {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    },
    "zai": lambda key: {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
}


# =============================================================================
# UTILITÁRIOS
# =============================================================================

def get_model_info(model_id: str, provider: str = None) -> dict:
    """Retorna informações do modelo"""
    providers_to_search = [provider] if provider else PROVIDERS.keys()
    
    for prov in providers_to_search:
        if prov in PROVIDERS:
            models = PROVIDERS[prov].get("models", {})
            if model_id in models:
                model_info = models[model_id].copy()
                model_info["provider"] = prov
                model_info["provider_name"] = PROVIDERS[prov]["name"]
                model_info["model_id"] = model_id
                return model_info
    
    return None


def get_free_models() -> dict:
    """Retorna todos os modelos gratuitos"""
    free = {}
    for provider_id, provider in PROVIDERS.items():
        free[provider_id] = {
            "name": provider["name"],
            "description": provider["description"],
            "get_url": provider["get_url"],
            "models": {}
        }
        for model_id, model in provider.get("models", {}).items():
            if model.get("tier") in ["free", "free_limited"]:
                free[provider_id]["models"][model_id] = model
    
    return {k: v for k, v in free.items() if v["models"]}


def print_model_table():
    """Imprime tabela de modelos"""
    free = get_free_models()
    
    print("\n" + "="*70)
    print("MODELOS GRATUITOS PARA CÓDIGO - 2025")
    print("="*70)
    
    for provider_id, provider in free.items():
        print(f"\n{'─'*70}")
        print(f"📦 {provider['name']}")
        print(f"   {provider['description']}")
        print(f"   🔑 {provider['get_url']}")
        print(f"{'─'*70}")
        
        for model_id, model in provider["models"].items():
            rec = "⭐ " if model.get("recommended") else "   "
            top = "🏆 " if model.get("top_pick") else ""
            print(f"{rec}{top}{model['name']}")
            print(f"      ID: {model_id}")
            print(f"      {model['params']} | Context: {model['context']}")
            print(f"      Best: {model['best_for']}")
            print()


if __name__ == "__main__":
    print_model_table()
