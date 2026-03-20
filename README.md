# 🤖 Setup Claude Free - Ambiente AI 100% Gratuito

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platforms: Linux+macOS+Windows](https://img.shields.io/badge/platforms-Linux%20%7C%20macOS%20%7C%20Windows-success.svg)]()

**Instalador completo para ambiente de desenvolvimento AI com os MELHORES modelos gratuitos para código.**

---

## 🚀 Instalação com Um Comando

### Linux
```bash
curl -fsSL https://raw.githubusercontent.com/sistemabritto/free-claude-code-setup/main/bootstrap.sh | bash
```

### macOS
```bash
curl -fsSL https://raw.githubusercontent.com/sistemabritto/free-claude-code-setup/main/bootstrap.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/sistemabritto/free-claude-code-setup/main/install-windows.ps1 | iex
```

---

## 🏆 Top 4 Modelos GRATUITOS para Código

| # | Modelo | Provedor | Params | Velocidade |
|---|--------|----------|--------|------------|
| 🥇 | **Qwen3 Coder 480B** | OpenRouter | 480B MoE | Média |
| 🥈 | **Llama 4 Scout** | Groq | 17B×16E | ~460 tok/s ⚡ |
| 🥉 | **MiniMax M2.5** | NVIDIA | 230B | Média |
| 4 | **DeepSeek R1** | OpenRouter | 671B MoE | Média |

---

## 📦 Provedores

### 🟢 Groq (100% FREE)
- Llama 4 Scout 17B ⭐ **CÓDIGO RÁPIDO**
- Llama 4 Maverick 17B
- Llama 3.3 70B
- DeepSeek R1 Distill 70B

🔗 https://console.groq.com/keys

### 🔵 OpenRouter (FREE + Paid)
- Qwen3 Coder 480B 🏆 **TOP CÓDIGO**
- DeepSeek V3
- DeepSeek R1
- Llama 4 Scout
- GLM 4.5 Air

🔗 https://openrouter.ai/keys

### 🟠 NVIDIA NIM (FREE)
- MiniMax M2.5 230B ⭐
- Nemotron 4 340B
- Llama 3.1 405B

🔗 https://build.nvidia.com/

### 🟣 Z.AI (Free Limitado)
- GLM 4.5 Air

🔗 https://z.ai/

---

## 💻 Requisitos

### Linux
- Ubuntu 20.04+, Debian 11+, Fedora, Arch
- `whiptail` (instalado automaticamente)

### macOS
- macOS 10.15+ (Catalina ou superior)
- Homebrew (opcional)

### Windows
- Windows 10/11
- PowerShell 5.1+
- Python 3.8+ (instalado automaticamente)

---

## 🎮 Comandos

```bash
cc-config    # Menu de configuração
cc-start     # Iniciar proxy
cc-status    # Verificar status
cc-models    # Ver modelos
```

---

## 🌐 Painel Web

```
http://localhost:8323/admin
```

- Trocar modelo com 1 clique
- Gerenciar API Keys
- Testar conexões
- Ver status

---

## 🔧 Clientes AI

### Cursor / Continue / Cline

```json
{
  "models": [{
    "title": "Claude Free",
    "provider": "openai",
    "apiBase": "http://localhost:8323/v1",
    "apiKey": "sk-dummy"
  }]
}
```

### Endpoints

| Formato | URL |
|---------|-----|
| OpenAI | `http://localhost:8323/v1/chat/completions` |
| Anthropic | `http://localhost:8323/v1/messages` |

---

## 📁 Estrutura

```
~/.claude-free/
├── config/.env     # Configuração
├── logs/           # Logs
└── proxy/          # Scripts Python
```

---

## 🔒 Segurança

- API Keys armazenadas localmente
- Painel protegido por Master Key
- Sem dados enviados para terceiros

---

## 📄 Licença

MIT License

---

**Feito com ❤️ por [Sistema Britto](https://github.com/sistemabritto)**
