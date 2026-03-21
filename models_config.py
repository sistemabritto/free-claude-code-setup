#!/usr/bin/env python3
"""
Mapeamento de Modelos e Provedores - Setup Claude Free
Atualizado: Março 2026

LEGENDA:
  🟢 GRÁTIS   = free tier sem cartão
  🟡 BARATO   = < $0.50/M tokens
  🔴 PAGO     = > $0.50/M tokens

DEFAULT: OpenRouter → Qwen3 Coder 480B (262K ctx, sem problema de max_tokens)
"""

COLOR_FREE     = "\033[92m"
COLOR_LOW_COST = "\033[93m"
COLOR_PAID     = "\033[91m"
COLOR_RESET    = "\033[0m"

TIER_BADGE = {
    "free":     "🟢 GRÁTIS",
    "low_cost": "🟡 BARATO",
    "paid":     "🔴 PAGO",
}

# =============================================================================
# OPENROUTER — PRIMEIRO (padrão do sistema)
# 20 req/min, 200 req/dia por modelo, zero cartão
# Melhor para código: 262K ctx, sem limite problemático de max_tokens
# =============================================================================
PROVIDERS = {
    "openrouter": {
        "name": "OpenRouter",
        "description": "27 modelos FREE. Melhor contexto. 200 req/dia grátis.",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_prefix": "sk-or",
        "get_url": "https://openrouter.ai/keys",
        "tier": "free",
        "rate_limits": "20 req/min | 200 req/dia | sem cartão",

        "models": {
            "qwen/qwen3-coder:free": {
                "name": "Qwen3 Coder 480B",
                "params": "480B MoE (35B ativos)",
                "context": "262K",
                "max_output": 32768,
                "best_for": "🏆 MELHOR CÓDIGO FREE — 262K ctx | ⚠️ rate limit upstream",
                "speed": "~80 tok/s",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            "nvidia/nemotron-3-super-120b-a12b:free": {
                "name": "Nemotron 3 Super 120B",
                "params": "120B MoE (12B ativos)",
                "context": "1M",
                "max_output": 32768,
                "best_for": "⭐ 1M context — projetos enormes",
                "speed": "~150 tok/s",
                "tier": "free",
                "recommended": True
            },
            "google/gemini-2.0-flash-exp:free": {
                "name": "Gemini 2.0 Flash",
                "params": "N/A",
                "context": "1M",
                "max_output": 32768,
                "best_for": "1M context, multimodal, rápido",
                "speed": "~200 tok/s",
                "tier": "free"
            },
            "stepfun/step-3.5-flash:free": {
                "name": "Step 3.5 Flash",
                "params": "196B MoE (11B ativos)",
                "context": "256K",
                "max_output": 32768,
                "best_for": "256K ctx, rápido, geral",
                "speed": "~250 tok/s",
                "tier": "free"
            },
            "deepseek/deepseek-chat-v3-0324:free": {
                "name": "DeepSeek V3 Chat",
                "params": "671B MoE",
                "context": "128K",
                "max_output": 32768,
                "best_for": "Chat, código, análise",
                "speed": "~60 tok/s",
                "tier": "free"
            },
            "deepseek/deepseek-r1:free": {
                "name": "DeepSeek R1",
                "params": "671B MoE",
                "context": "128K",
                "max_output": 32768,
                "best_for": "🧠 Reasoning profundo | ⚠️ instável upstream",
                "speed": "~40 tok/s",
                "tier": "free"
            },
            "meta-llama/llama-4-maverick:free": {
                "name": "Llama 4 Maverick",
                "params": "17B×128E",
                "context": "128K",
                "max_output": 32768,
                "best_for": "Chat, raciocínio",
                "speed": "~100 tok/s",
                "tier": "free"
            },
            "meta-llama/llama-3.3-70b-instruct:free": {
                "name": "Llama 3.3 70B",
                "params": "70B",
                "context": "128K",
                "max_output": 32768,
                "best_for": "Chat geral, versátil",
                "speed": "~80 tok/s",
                "tier": "free"
            },
            "openrouter/free": {
                "name": "Auto-Router FREE",
                "params": "Varia",
                "context": "200K",
                "max_output": 32768,
                "best_for": "Seleção automática do melhor free disponível",
                "speed": "Varia",
                "tier": "free",
                "is_router": True
            },
        }
    },

    # =========================================================================
    # GROQ — Free tier, ultra-rápido mas max_tokens limitado
    # ⚠️  Scout: max_output = 8.192 (proxy faz cap automático)
    # 30 req/min | 500K tok/dia | sem cartão
    # =========================================================================
    "groq": {
        "name": "Groq",
        "description": "Ultra-rápido (LPU). Free tier. ⚠️ max_output limitado por modelo.",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_prefix": "gsk_",
        "get_url": "https://console.groq.com/keys",
        "tier": "free",
        "rate_limits": "30 req/min | 500K tok/dia | sem cartão",

        "models": {
            "meta-llama/llama-4-scout-17b-16e-instruct": {
                "name": "Llama 4 Scout 17B",
                "params": "17B×16E MoE",
                "context": "128K",
                "max_output": 8192,
                "best_for": "⚡ MAIS RÁPIDO (~460 tok/s) — ⚠️ max 8K output",
                "speed": "~460 tok/s",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            "openai/gpt-oss-120b": {
                "name": "GPT-OSS 120B",
                "params": "120B MoE",
                "context": "128K",
                "max_output": 32768,
                "best_for": "🧠 Reasoning, substitui Maverick",
                "speed": "~200 tok/s",
                "tier": "free",
                "recommended": True
            },
            "openai/gpt-oss-20b": {
                "name": "GPT-OSS 20B",
                "params": "20B",
                "context": "128K",
                "max_output": 32768,
                "best_for": "Rápido, código e chat",
                "speed": "~400 tok/s",
                "tier": "free"
            },
            "moonshotai/kimi-k2.5": {
                "name": "Kimi K2.5",
                "params": "1T MoE (multimodal)",
                "context": "256K",
                "max_output": 8192,
                "best_for": "⭐ Visão + código + agentes — 256K ctx",
                "speed": "~100 tok/s",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            "moonshotai/kimi-k2-instruct": {
                "name": "Kimi K2",
                "params": "MoE",
                "context": "128K",
                "max_output": 16384,
                "best_for": "Código, agentes",
                "speed": "~200 tok/s",
                "tier": "free"
            },
            "qwen/qwen3-32b": {
                "name": "Qwen3 32B",
                "params": "32B",
                "context": "128K",
                "max_output": 32768,
                "best_for": "Código, raciocínio",
                "speed": "~150 tok/s",
                "tier": "free"
            },
            "llama-3.3-70b-versatile": {
                "name": "Llama 3.3 70B",
                "params": "70B",
                "context": "128K",
                "max_output": 32768,
                "best_for": "Chat geral, versátil",
                "speed": "~100 tok/s",
                "tier": "free"
            },
            "deepseek-r1-distill-llama-70b": {
                "name": "DeepSeek R1 Distill 70B",
                "params": "70B",
                "context": "128K",
                "max_output": 16384,
                "best_for": "Reasoning, matemática",
                "speed": "~80 tok/s",
                "tier": "free"
            },
        }
    },

    # =========================================================================
    # NVIDIA NIM — Free tier via build.nvidia.com
    # Rate limited mas gratuito para desenvolvimento
    # =========================================================================
    "nvidia": {
        "name": "NVIDIA NIM",
        "description": "Modelos NVIDIA. Free tier para dev. build.nvidia.com",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_prefix": "nvapi-",
        "get_url": "https://build.nvidia.com/explore/discover",
        "tier": "free",
        "rate_limits": "Rate limited | sem cartão | para dev",

        "models": {
            "nvidia/nemotron-3-super-120b-a12b": {
                "name": "Nemotron 3 Super 120B",
                "params": "120B MoE (12B ativos)",
                "context": "1M",
                "max_output": 32768,
                "best_for": "⭐ 1M context — agentes, projetos enormes",
                "speed": "~150 tok/s",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            "nvidia/nemotron-3-nano-30b-a3b": {
                "name": "Nemotron 3 Nano 30B",
                "params": "30B MoE (3B ativos)",
                "context": "256K",
                "max_output": 32768,
                "best_for": "Agentes leves, eficiente",
                "speed": "~300 tok/s",
                "tier": "free",
                "recommended": True
            },
            "nvidia/nemotron-nano-12b-v2-vl": {
                "name": "Nemotron Nano 12B VL",
                "params": "12B",
                "context": "256K",
                "max_output": 32768,
                "best_for": "Visão + texto, documentos",
                "speed": "~200 tok/s",
                "tier": "free"
            },
            "moonshotai/kimi-k2.5": {
                "name": "Kimi K2.5",
                "params": "1T MoE (multimodal)",
                "context": "256K",
                "max_output": 8192,
                "best_for": "⭐ Visão + código + agentes — 256K ctx",
                "speed": "~100 tok/s",
                "tier": "free",
                "recommended": True,
                "top_pick": True
            },
            "moonshotai/kimi-k2-instruct": {
                "name": "Kimi K2",
                "params": "MoE",
                "context": "128K",
                "max_output": 16384,
                "best_for": "Código, agentes",
                "speed": "~200 tok/s",
                "tier": "free"
            },
            "meta/llama-3.1-405b-instruct": {
                "name": "Llama 3.1 405B",
                "params": "405B",
                "context": "128K",
                "max_output": 32768,
                "best_for": "Qualidade máxima",
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
        "description": "Modelos GLM. Free limitado.",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_prefix": "glm-",
        "get_url": "https://z.ai/",
        "tier": "free",
        "rate_limits": "Limitado | ver z.ai",

        "models": {
            "glm-4.5-air": {
                "name": "GLM 4.5 Air",
                "params": "N/A",
                "context": "128K",
                "max_output": 32768,
                "best_for": "Código, agentes",
                "speed": "~150 tok/s",
                "tier": "free",
                "recommended": True
            },
        }
    },
}

# Padrão do sistema
DEFAULT_PROVIDER = "openrouter"
DEFAULT_MODEL    = "qwen/qwen3-coder:free"

BEST_FREE_FOR_CODE = [
    ("openrouter", "qwen/qwen3-coder:free"),
    ("nvidia",     "nvidia/nemotron-3-super-120b-a12b"),
    ("groq",       "meta-llama/llama-4-scout-17b-16e-instruct"),
    ("openrouter", "deepseek/deepseek-chat-v3-0324:free"),
]
BEST_FREE_FOR_REASONING = [
    ("openrouter", "deepseek/deepseek-r1:free"),
    ("groq",       "openai/gpt-oss-120b"),
    ("groq",       "deepseek-r1-distill-llama-70b"),
]
BEST_FREE_GENERAL = [
    ("openrouter", "openrouter/free"),
    ("groq",       "llama-3.3-70b-versatile"),
    ("openrouter", "google/gemini-2.0-flash-exp:free"),
]

RECOMMENDATIONS = {
    "code":      BEST_FREE_FOR_CODE,
    "reasoning": BEST_FREE_FOR_REASONING,
    "general":   BEST_FREE_GENERAL,
}

PROVIDER_HEADERS = {
    "openrouter": lambda k: {
        "Authorization": f"Bearer {k}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://claude-free.local",
        "X-Title": "Claude Free Proxy"
    },
    "groq":   lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
    "nvidia": lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
    "zai":    lambda k: {"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
}

def get_model_info(model_id: str, provider_id: str = None) -> dict:
    if provider_id and provider_id in PROVIDERS:
        if model_id in PROVIDERS[provider_id]["models"]:
            return PROVIDERS[provider_id]["models"][model_id]
    for prov in PROVIDERS.values():
        if model_id in prov.get("models", {}):
            return prov["models"][model_id]
    return {}

def get_free_models(provider_id: str = None) -> list:
    result = []
    providers = {provider_id: PROVIDERS[provider_id]} if provider_id and provider_id in PROVIDERS else PROVIDERS
    for prov_id, prov in providers.items():
        for model_id, model in prov.get("models", {}).items():
            if model.get("tier") == "free":
                result.append({"provider": prov_id, "model_id": model_id, **model})
    return result

def get_tier_color(tier): 
    return {"free": "\033[92m", "low_cost": "\033[93m", "paid": "\033[91m"}.get(tier, "\033[0m")

def get_tier_badge(tier):
    return TIER_BADGE.get(tier, tier)

if __name__ == "__main__":
    models = get_free_models()
    print(f"\n🟢 {len(models)} modelos free disponíveis\n")
    print(f"✅ Padrão: {DEFAULT_PROVIDER} → {DEFAULT_MODEL}\n")
