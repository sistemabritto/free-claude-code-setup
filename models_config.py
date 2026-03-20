#!/usr/bin/env python3
"""
Mapeamento de Modelos e Provedores - Setup Claude Free
Atualizado: Março 2026

LEGENDA DE CORES NO PAINEL:
  🟢 VERDE  = 100% gratuito (free tier)
  🟡 AMARELO = Baixo custo (< $0.50/M tokens)
  🔴 VERMELHO = Pago (> $0.50/M tokens)

MODELOS FREE TOP PARA CÓDIGO (Março 2026):
  🏆 Qwen3 Coder 480B   (OpenRouter :free) — MELHOR código
  ⭐ Nemotron 3 Super   (OpenRouter :free) — 120B, 1M context
  ⚡ Llama 4 Scout      (Groq free tier)   — mais rápido
  🧠 GPT-OSS 120B       (Groq free tier)   — melhor reasoning
"""

# Cores para terminal e painel web
COLOR_FREE = "\033[92m"      # Verde
COLOR_LOW_COST = "\033[93m"  # Amarelo
COLOR_PAID = "\033[91m"      # Vermelho
COLOR_RESET = "\033[0m"

TIER_BADGE = {
    "free":     "🟢 GRÁTIS",
    "low_cost": "🟡 BAIXO CUSTO",
    "paid":     "🔴 PAGO",
}

PROVIDERS = {

    # =========================================================================
    # GROQ — Free tier com rate limits
    # Todos os modelos abaixo são acessíveis no free tier
    # Rate limits: ~30 req/min, ~1000 req/dia dependendo do modelo
    # =========================================================================
    "groq": {
        "name": "Groq",
        "description": "Inferência ULTRA-RÁPIDA via LPU. Free tier disponível.",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_prefix": "gsk_",
        "get_url": "https://console.groq.com/keys",
        "tier": "free",

        "models": {
            # --- RECOMENDADOS PARA CÓDIGO ---
            "meta-llama/llama-4-scout-17b-16e-instruct": {
                "name": "Llama 4 Scout 17B",
                "params": "17B×16E MoE",
                "context": "128K",
                "best_for": "🏆 CÓDIGO — Multimodal, Ultra-rápido",
                "speed": "~460 tok/s",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            "openai/gpt-oss-120b": {
                "name": "GPT-OSS 120B",
                "params": "120B MoE",
                "context": "128K",
                "best_for": "🧠 REASONING — Substitui Maverick",
                "speed": "~200 tok/s",
                "tier": "free",
                "recommended": True
            },
            "openai/gpt-oss-20b": {
                "name": "GPT-OSS 20B",
                "params": "20B",
                "context": "128K",
                "best_for": "Rápido, código e chat",
                "speed": "~400 tok/s",
                "tier": "free"
            },
            "qwen/qwen3-32b": {
                "name": "Qwen3 32B",
                "params": "32B",
                "context": "128K",
                "best_for": "Código, raciocínio",
                "speed": "~150 tok/s",
                "tier": "free"
            },
            "moonshotai/kimi-k2-instruct": {
                "name": "Kimi K2",
                "params": "MoE",
                "context": "128K",
                "best_for": "Código, agentes",
                "speed": "~200 tok/s",
                "tier": "free"
            },
            "llama-3.3-70b-versatile": {
                "name": "Llama 3.3 70B",
                "params": "70B",
                "context": "128K",
                "best_for": "Chat geral, versátil",
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
            },
            # --- DESCONTINUADOS (não usar) ---
            # "llama-4-maverick-17b-128e" → DEPRECADO fev/2026, use gpt-oss-120b
        }
    },

    # =========================================================================
    # OPENROUTER — 27 modelos free (sufixo :free), zero custo
    # Rate limits: 20 req/min, 200 req/dia (grátis) | 1000/dia com $10 de crédito
    # =========================================================================
    "openrouter": {
        "name": "OpenRouter",
        "description": "27 modelos FREE. Use sufixo :free. 200 req/dia grátis.",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_prefix": "sk-or",
        "get_url": "https://openrouter.ai/keys",
        "tier": "free",

        "models": {
            # --- TOP CÓDIGO FREE ---
            "qwen/qwen3-coder:free": {
                "name": "Qwen3 Coder 480B",
                "params": "480B MoE (35B ativos)",
                "context": "262K",
                "best_for": "🏆 MELHOR CÓDIGO FREE — Agentes, tool use",
                "speed": "~80 tok/s",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            "nvidia/nemotron-3-super-120b-a12b:free": {
                "name": "Nemotron 3 Super 120B",
                "params": "120B MoE (12B ativos)",
                "context": "1M",
                "best_for": "⭐ Agentes complexos, 1M context",
                "speed": "~150 tok/s",
                "tier": "free",
                "recommended": True
            },
            "nvidia/nemotron-3-nano-30b-a3b:free": {
                "name": "Nemotron 3 Nano 30B",
                "params": "30B MoE (3B ativos)",
                "context": "256K",
                "best_for": "Agentes leves, eficiente",
                "speed": "~300 tok/s",
                "tier": "free"
            },
            "nvidia/nemotron-nano-12b-v2-vl:free": {
                "name": "Nemotron Nano 12B VL",
                "params": "12B",
                "context": "256K",
                "best_for": "Visão + texto, documentos",
                "speed": "~200 tok/s",
                "tier": "free"
            },
            "openai/gpt-oss-120b:free": {
                "name": "GPT-OSS 120B",
                "params": "120B MoE",
                "context": "128K",
                "best_for": "Reasoning, código",
                "speed": "~150 tok/s",
                "tier": "free"
            },
            "deepseek/deepseek-chat-v3-0324:free": {
                "name": "DeepSeek V3 Chat",
                "params": "671B MoE",
                "context": "128K",
                "best_for": "Chat geral, código",
                "speed": "~60 tok/s",
                "tier": "free"
            },
            "deepseek/deepseek-r1:free": {
                "name": "DeepSeek R1",
                "params": "671B MoE",
                "context": "128K",
                "best_for": "Reasoning profundo",
                "speed": "~40 tok/s",
                "tier": "free"
            },
            "meta-llama/llama-4-maverick:free": {
                "name": "Llama 4 Maverick",
                "params": "17B×128E",
                "context": "128K",
                "best_for": "Chat, reasoning",
                "speed": "~100 tok/s",
                "tier": "free"
            },
            "meta-llama/llama-3.3-70b-instruct:free": {
                "name": "Llama 3.3 70B",
                "params": "70B",
                "context": "128K",
                "best_for": "Chat geral, versátil",
                "speed": "~80 tok/s",
                "tier": "free"
            },
            "google/gemini-2.0-flash-exp:free": {
                "name": "Gemini 2.0 Flash",
                "params": "N/A",
                "context": "1M",
                "best_for": "1M context, multimodal",
                "speed": "~200 tok/s",
                "tier": "free"
            },
            "stepfun/step-3.5-flash:free": {
                "name": "Step 3.5 Flash",
                "params": "196B MoE (11B ativos)",
                "context": "256K",
                "best_for": "Rápido, geral",
                "speed": "~250 tok/s",
                "tier": "free"
            },
            "qwen/qwen3-next-80b-a3b-instruct:free": {
                "name": "Qwen3 Next 80B",
                "params": "80B MoE (3B ativos)",
                "context": "262K",
                "best_for": "Código, raciocínio, agentic",
                "speed": "~200 tok/s",
                "tier": "free"
            },
            "z-ai/glm-4.5-air:free": {
                "name": "GLM 4.5 Air",
                "params": "N/A",
                "context": "128K",
                "best_for": "Agentes, chat",
                "speed": "~150 tok/s",
                "tier": "free"
            },
            # Router automático — seleciona o melhor free disponível
            "openrouter/free": {
                "name": "Auto-Router FREE",
                "params": "Varia",
                "context": "200K",
                "best_for": "Seleção automática do melhor free",
                "speed": "Varia",
                "tier": "free",
                "is_router": True
            },
        }
    },

    # =========================================================================
    # NVIDIA NIM — Free tier via build.nvidia.com
    # Rate limited mas gratuito para desenvolvimento
    # =========================================================================
    "nvidia": {
        "name": "NVIDIA NIM",
        "description": "Modelos NVIDIA. Free tier para desenvolvimento via build.nvidia.com.",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_prefix": "nvapi-",
        "get_url": "https://build.nvidia.com/explore/discover",
        "tier": "free",

        "models": {
            "nvidia/nemotron-3-super-120b-a12b": {
                "name": "Nemotron 3 Super 120B",
                "params": "120B MoE (12B ativos)",
                "context": "1M",
                "best_for": "⭐ Agentes, multi-step, 1M context",
                "speed": "~150 tok/s",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            "nvidia/nemotron-3-nano-30b-a3b": {
                "name": "Nemotron 3 Nano 30B",
                "params": "30B MoE (3B ativos)",
                "context": "256K",
                "best_for": "Agentes leves, eficiente",
                "speed": "~300 tok/s",
                "tier": "free",
                "recommended": True
            },
            "nvidia/nemotron-nano-12b-v2-vl": {
                "name": "Nemotron Nano 12B VL",
                "params": "12B",
                "context": "256K",
                "best_for": "Visão + texto",
                "speed": "~200 tok/s",
                "tier": "free"
            },
            "moonshotai/kimi-k2-instruct": {
                "name": "Kimi K2",
                "params": "MoE",
                "context": "128K",
                "best_for": "Código, agentes",
                "speed": "~200 tok/s",
                "tier": "free"
            },
            "meta/llama-3.1-405b-instruct": {
                "name": "Llama 3.1 405B",
                "params": "405B",
                "context": "128K",
                "best_for": "Qualidade máxima, raciocínio",
                "speed": "~50 tok/s",
                "tier": "free"
            },
        }
    },

    # =========================================================================
    # Z.AI — Free limitado
    # =========================================================================
    "zai": {
        "name": "Z.AI (GLM)",
        "description": "Modelos GLM. Free limitado. Excelente para código.",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_prefix": "glm-",
        "get_url": "https://z.ai/",
        "tier": "free",

        "models": {
            "glm-4.5-air": {
                "name": "GLM 4.5 Air",
                "params": "N/A",
                "context": "128K",
                "best_for": "Código, agentes",
                "speed": "~150 tok/s",
                "tier": "free",
                "recommended": True
            },
        }
    },
}

# =============================================================================
# MELHORES MODELOS FREE POR CATEGORIA (para seleção automática)
# =============================================================================

BEST_FREE_FOR_CODE = [
    ("openrouter", "qwen/qwen3-coder:free"),
    ("groq", "meta-llama/llama-4-scout-17b-16e-instruct"),
    ("openrouter", "nvidia/nemotron-3-super-120b-a12b:free"),
    ("groq", "openai/gpt-oss-120b"),
    ("openrouter", "deepseek/deepseek-chat-v3-0324:free"),
]

BEST_FREE_FOR_REASONING = [
    ("groq", "openai/gpt-oss-120b"),
    ("openrouter", "deepseek/deepseek-r1:free"),
    ("groq", "deepseek-r1-distill-llama-70b"),
    ("openrouter", "openai/gpt-oss-120b:free"),
]

BEST_FREE_GENERAL = [
    ("groq", "llama-3.3-70b-versatile"),
    ("openrouter", "meta-llama/llama-3.3-70b-instruct:free"),
    ("openrouter", "google/gemini-2.0-flash-exp:free"),
]

# Modelo padrão recomendado
DEFAULT_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
DEFAULT_PROVIDER = "groq"


def get_tier_color(tier):
    """Retorna código de cor ANSI para o tier."""
    return {
        "free": COLOR_FREE,
        "low_cost": COLOR_LOW_COST,
        "paid": COLOR_PAID,
    }.get(tier, COLOR_RESET)


def get_tier_badge(tier):
    """Retorna badge visual para o tier."""
    return TIER_BADGE.get(tier, tier)


def list_free_models():
    """Lista todos os modelos gratuitos disponíveis."""
    result = []
    for provider_id, provider in PROVIDERS.items():
        for model_id, model in provider["models"].items():
            if model.get("tier") == "free":
                result.append({
                    "provider": provider_id,
                    "model_id": model_id,
                    "name": model["name"],
                    "best_for": model.get("best_for", ""),
                    "context": model.get("context", ""),
                    "top_pick": model.get("top_pick", False),
                })
    return result


if __name__ == "__main__":
    print(f"\n{COLOR_FREE}{'='*60}")
    print("  MODELOS FREE DISPONÍVEIS — Março 2026")
    print(f"{'='*60}{COLOR_RESET}\n")

    for provider_id, provider in PROVIDERS.items():
        print(f"\n📦 {provider['name']} — {provider['description']}")
        print(f"   Chave: {provider['get_url']}\n")

        for model_id, model in provider["models"].items():
            tier = model.get("tier", "paid")
            color = get_tier_color(tier)
            badge = get_tier_badge(tier)
            pick = " ⭐ TOP PICK" if model.get("top_pick") else ""
            print(f"  {color}{badge}{COLOR_RESET}{pick}")
            print(f"    ID: {model_id}")
            print(f"    {model['name']} | {model.get('context','?')} ctx | {model.get('best_for','')}")
            print()


# =============================================================================
# COMPATIBILIDADE COM proxy_core.py
# =============================================================================

# Headers por provedor (necessário pelo proxy_core.py)
PROVIDER_HEADERS = {
    "groq": lambda k: {
        "Authorization": f"Bearer {k}",
        "Content-Type": "application/json"
    },
    "openrouter": lambda k: {
        "Authorization": f"Bearer {k}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://claude-free.local",
        "X-Title": "Claude Free Proxy"
    },
    "nvidia": lambda k: {
        "Authorization": f"Bearer {k}",
        "Content-Type": "application/json"
    },
    "zai": lambda k: {
        "Authorization": f"Bearer {k}",
        "Content-Type": "application/json"
    },
}


def get_model_info(model_id: str, provider_id: str = None) -> dict:
    """Retorna info de um modelo específico."""
    if provider_id and provider_id in PROVIDERS:
        models = PROVIDERS[provider_id].get("models", {})
        if model_id in models:
            return models[model_id]
    # Busca em todos os provedores
    for prov in PROVIDERS.values():
        if model_id in prov.get("models", {}):
            return prov["models"][model_id]
    return {}


def get_free_models(provider_id: str = None) -> list:
    """Retorna lista de modelos gratuitos."""
    result = []
    providers = {provider_id: PROVIDERS[provider_id]} if provider_id and provider_id in PROVIDERS else PROVIDERS
    for prov_id, prov in providers.items():
        for model_id, model in prov.get("models", {}).items():
            if model.get("tier") == "free":
                result.append({"provider": prov_id, "model_id": model_id, **model})
    return result


# Recomendações para seleção automática
RECOMMENDATIONS = {
    "code": BEST_FREE_FOR_CODE,
    "reasoning": BEST_FREE_FOR_REASONING,
    "general": BEST_FREE_GENERAL,
}
