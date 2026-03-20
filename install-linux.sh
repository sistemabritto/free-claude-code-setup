#!/bin/bash
#===============================================================================
# Setup Claude Free - Instalador TUI para Linux
# Repositório: sistemabritto/free-claude-code-setup
# Versão: 2.3.0 - Claude Code + Proxy Grátis
#===============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Diretórios
INSTALL_DIR="${HOME}/.claude-free"
CONFIG_DIR="${INSTALL_DIR}/config"
LOGS_DIR="${INSTALL_DIR}/logs"
ENV_FILE="${CONFIG_DIR}/.env"
PROXY_PORT=8323

# =============================================================================
# MODELOS E PROVEDORES
# =============================================================================

declare -A PROVIDER_INFO=(
    ["groq"]="Groq|100% GRÁTIS|Inferência ULTRA-RÁPIDA (~460 tok/s)|https://console.groq.com/keys|gsk_"
    ["openrouter"]="OpenRouter|FREE + Low-Cost|Vários modelos gratuitos|https://openrouter.ai/keys|sk-or_"
    ["nvidia"]="NVIDIA NIM|FREE Rate-Limited|189+ modelos disponíveis|https://build.nvidia.com/|nvapi-"
    ["zai"]="Z.AI (GLM)|Free Limitado|Excelente para código|https://z.ai/|glm-"
)

declare -A FREE_MODELS=(
    ["groq"]="llama-4-scout-17b-16e|llama-4-maverick-17b-128e|llama-3.3-70b-versatile|deepseek-r1-distill-llama-70b"
    ["openrouter"]="qwen/qwen3-coder:free|deepseek/deepseek-chat-v3-0324:free|deepseek/deepseek-r1:free|google/gemini-2.0-flash-exp:free"
    ["nvidia"]="moonshotai/kimi-k2-instruct|moonshotai/kimi-k2.5-instruct|minimaxai/minimax-m2.5-250106|meta/llama-3.1-405b-instruct|deepseek-ai/deepseek-r1"
    ["zai"]="glm-4.5-air"
)

declare -A MODEL_NAMES=(
    # GROQ
    ["llama-4-scout-17b-16e"]="Llama 4 Scout 17B (⭐ CÓDIGO)"
    ["llama-4-maverick-17b-128e"]="Llama 4 Maverick 17B"
    ["llama-3.3-70b-versatile"]="Llama 3.3 70B Versatile"
    ["deepseek-r1-distill-llama-70b"]="DeepSeek R1 Distill 70B"
    # OPENROUTER
    ["qwen/qwen3-coder:free"]="Qwen3 Coder 480B (🏆 TOP CÓDIGO)"
    ["deepseek/deepseek-chat-v3-0324:free"]="DeepSeek V3 Chat"
    ["deepseek/deepseek-r1:free"]="DeepSeek R1 Reasoning"
    ["google/gemini-2.0-flash-exp:free"]="Gemini 2.0 Flash"
    # NVIDIA
    ["moonshotai/kimi-k2-instruct"]="Kimi K2 (🏆 CÓDIGO)"
    ["moonshotai/kimi-k2.5-instruct"]="Kimi K2.5 (🏆 CÓDIGO)"
    ["minimaxai/minimax-m2.5-250106"]="MiniMax M2.5 230B"
    ["meta/llama-3.1-405b-instruct"]="Llama 3.1 405B"
    ["deepseek-ai/deepseek-r1"]="DeepSeek R1"
    # Z.AI
    ["glm-4.5-air"]="GLM 4.5 Air"
)

declare -A API_KEY_NAMES=(
    ["groq"]="GROQ_API_KEY"
    ["openrouter"]="OPENROUTER_API_KEY"
    ["nvidia"]="NVIDIA_API_KEY"
    ["zai"]="ZAI_API_KEY"
)

# =============================================================================
# LOG
# =============================================================================

log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[AVISO]${NC} $1"; }
log_erro() { echo -e "${RED}[ERRO]${NC} $1"; }

# =============================================================================
# DEPENDÊNCIAS
# =============================================================================

check_dependencies() {
    local missing=()
    
    command -v whiptail &>/dev/null || missing+=("whiptail")
    command -v python3 &>/dev/null || missing+=("python3")
    command -v pip3 &>/dev/null || command -v pip &>/dev/null || missing+=("python3-pip")
    command -v curl &>/dev/null || missing+=("curl")
    
    if [ ${#missing[@]} -gt 0 ]; then
        whiptail --title "Dependências" --msgbox "Faltando: ${missing[*]}\n\nsudo apt install ${missing[*]}" 12 50
        exit 1
    fi
}

# =============================================================================
# ESTRUTURA
# =============================================================================

create_directories() {
    log_info "Criando diretórios..."
    mkdir -p "${INSTALL_DIR}"/{config,logs,proxy}
    log_ok "Diretórios criados"
}

create_env_file() {
    [ -f "${ENV_FILE}" ] && return
    
    log_info "Criando configuração..."
    cat > "${ENV_FILE}" << 'EOF'
# Setup Claude Free v2.3
ACTIVE_PROVIDER=groq
ACTIVE_MODEL=llama-4-scout-17b-16e

GROQ_API_KEY=
OPENROUTER_API_KEY=
NVIDIA_API_KEY=
ZAI_API_KEY=

PROXY_PORT=8323
MASTER_KEY=
EOF
    log_ok "Config criada"
}

# =============================================================================
# TUI
# =============================================================================

show_welcome() {
    whiptail --title "Setup Claude Free v2.3" --msgbox "\
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🤖 Setup Claude Free - Ambiente AI Gratuito          ║
║                  Versão 2.3 - 2025                        ║
║                                                           ║
║  TOP MODELOS GRATUITOS PARA CÓDIGO:                      ║
║                                                           ║
║  🏆 Qwen3 Coder 480B (OpenRouter)                        ║
║  🏆 Kimi K2.5 (NVIDIA)                                   ║
║  ⭐ Llama 4 Scout (Groq) - ~460 tok/s                    ║
║  ⭐ MiniMax M2.5 230B (NVIDIA)                           ║
║                                                           ║
║  • Proxy local Anthropic ↔ OpenAI                        ║
║  • Painel web em localhost:8323                          ║
║  • Claude Code CLI integrado                             ║
║  • Hot reload de configuração                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝" 24 65
}

configure_providers() {
    while true; do
        local items=()
        
        for provider in groq openrouter nvidia zai; do
            IFS='|' read -r name tier desc url prefix <<< "${PROVIDER_INFO[$provider]}"
            local key_name="${API_KEY_NAMES[$provider]}"
            local status="off"
            
            grep -q "^${key_name}=.\+" "${ENV_FILE}" 2>/dev/null && status="on"
            items+=("$provider" "$name ($tier)" "$status")
        done
        
        local sel
        sel=$(whiptail --title "Provedores" --checklist "\nSelecione para configurar:" 15 60 4 "${items[@]}" 3>&1 1>&2 2>&3)
        
        [ $? -ne 0 ] && break
        
        IFS=' ' read -ra selected <<< "$sel"
        
        for provider in "${selected[@]}"; do
            provider=$(echo "$provider" | tr -d '"')
            IFS='|' read -r name tier desc url prefix <<< "${PROVIDER_INFO[$provider]}"
            
            whiptail --title "$name" --msgbox "\nObtenha sua API Key em:\n$url" 10 60
            
            local key
            key=$(whiptail --title "$name" --passwordbox "Cole sua API Key:" 10 50 3>&1 1>&2 2>&3)
            
            if [ -n "$key" ]; then
                local key_name="${API_KEY_NAMES[$provider]}"
                grep -q "^${key_name}=" "${ENV_FILE}" && \
                    sed -i "s|^${key_name}=.*|${key_name}=${key}|" "${ENV_FILE}" || \
                    echo "${key_name}=${key}" >> "${ENV_FILE}"
                log_ok "$name configurado!"
            fi
        done
        
        whiptail --title "Continuar?" --yesno "Configurar mais provedores?" 8 40 || break
    done
}

select_model() {
    local available=()
    
    for provider in groq openrouter nvidia zai; do
        local key_name="${API_KEY_NAMES[$provider]}"
        grep -q "^${key_name}=.\+" "${ENV_FILE}" 2>/dev/null && available+=("$provider")
    done
    
    if [ ${#available[@]} -eq 0 ]; then
        whiptail --title "Erro" --msgbox "Configure pelo menos um provedor." 10 40
        return 1
    fi
    
    local items=()
    
    for provider in "${available[@]}"; do
        IFS='|' read -ra models <<< "${FREE_MODELS[$provider]}"
        IFS='|' read -r name tier desc url prefix <<< "${PROVIDER_INFO[$provider]}"
        
        for model in "${models[@]}"; do
            local display="${MODEL_NAMES[$model]:-$model}"
            items+=("$provider:$model" "[$name] $display")
        done
    done
    
    local sel
    sel=$(whiptail --title "Modelo Ativo" --menu "\nSelecione:" 20 70 12 "${items[@]}" 3>&1 1>&2 2>&3)
    
    if [ -n "$sel" ]; then
        IFS=':' read -r provider model <<< "$sel"
        sed -i "s|^ACTIVE_PROVIDER=.*|ACTIVE_PROVIDER=${provider}|" "${ENV_FILE}"
        sed -i "s|^ACTIVE_MODEL=.*|ACTIVE_MODEL=${model}|" "${ENV_FILE}"
        log_ok "Modelo: ${MODEL_NAMES[$model]:-$model}"
    fi
}

# =============================================================================
# INSTALAÇÃO
# =============================================================================

install_python_deps() {
    log_info "Instalando dependências Python..."
    pip3 install -q flask requests python-dotenv gunicorn 2>/dev/null || \
    pip install -q flask requests python-dotenv gunicorn 2>/dev/null
    log_ok "Python OK"
}

copy_proxy_files() {
    log_info "Copiando arquivos do proxy..."
    
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    for file in proxy_core.py config_manager.py models_config.py; do
        if [ -f "${script_dir}/${file}" ]; then
            cp "${script_dir}/${file}" "${INSTALL_DIR}/proxy/"
        else
            curl -fsSL "https://raw.githubusercontent.com/sistemabritto/free-claude-code-setup/main/${file}" \
                -o "${INSTALL_DIR}/proxy/${file}"
        fi
    done
    log_ok "Proxy OK"
}

install_claude_code() {
    log_info "Verificando Claude Code..."
    
    if command -v claude &>/dev/null; then
        log_ok "Claude Code já instalado"
        return 0
    fi
    
    # Verificar Node.js
    if command -v node &>/dev/null; then
        local ver=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$ver" -ge 18 ]; then
            log_ok "Node.js $(node -v) encontrado"
            npm install -g @anthropic-ai/claude-code 2>/dev/null && log_ok "Claude Code instalado"
            return 0
        fi
    fi
    
    # Instalar Node.js
    log_info "Instalando Node.js..."
    if command -v apt &>/dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt install -y nodejs
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y nodejs
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm nodejs npm
    fi
    
    npm install -g @anthropic-ai/claude-code 2>/dev/null && log_ok "Claude Code instalado"
}

create_aliases() {
    log_info "Criando aliases..."
    
    local block="
# =============================================================================
# Claude Free - Aliases
# =============================================================================
alias cc-config='python3 ${INSTALL_DIR}/proxy/config_manager.py'
alias cc-status='curl -s http://localhost:8323/health 2>/dev/null | python3 -m json.tool || echo \"Proxy parado\"'
alias cc-stop='pkill -9 -f proxy_core.py 2>/dev/null; echo \"Proxy parado\"'
alias cc-logs='tail -f ${INSTALL_DIR}/logs/proxy.log'
alias cc-restart='cc-stop; sleep 1; cc-start'

cc-start() {
    pkill -9 -f proxy_core.py 2>/dev/null || true
    sleep 1
    nohup python3 ${INSTALL_DIR}/proxy/proxy_core.py > ${INSTALL_DIR}/logs/proxy.log 2>&1 &
    sleep 2
    if curl -s http://localhost:8323/health > /dev/null 2>&1; then
        echo '✅ Proxy iniciado na porta 8323'
    else
        echo '⚠️  Verifique: cc-logs'
    fi
}

claude() {
    if ! curl -s http://localhost:8323/health > /dev/null 2>&1; then
        echo '⚠️  Iniciando proxy...'
        cc-start
        sleep 2
    fi
    ANTHROPIC_BASE_URL=http://localhost:8323 command claude \"\$@\"
}
"
    
    for rc in "${HOME}/.bashrc" "${HOME}/.zshrc"; do
        if [ -f "$rc" ]; then
            grep -q "cc-start" "$rc" 2>/dev/null || echo "$block" >> "$rc"
        fi
    done
    
    log_ok "Aliases criados"
}

create_systemd_service() {
    log_info "Criando serviço systemd..."
    
    mkdir -p "${HOME}/.config/systemd/user"
    
    cat > "${HOME}/.config/systemd/user/claude-free.service" << EOF
[Unit]
Description=Claude Free Proxy
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 ${INSTALL_DIR}/proxy/proxy_core.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
EOF
    
    systemctl --user daemon-reload 2>/dev/null || true
    log_ok "Serviço criado"
}

start_proxy() {
    log_info "Iniciando proxy..."
    
    pkill -9 -f proxy_core.py 2>/dev/null || true
    sleep 1
    
    nohup python3 "${INSTALL_DIR}/proxy/proxy_core.py" > "${INSTALL_DIR}/logs/proxy.log" 2>&1 &
    sleep 2
    
    if curl -s "http://localhost:8323/health" > /dev/null 2>&1; then
        log_ok "Proxy rodando na porta 8323"
    fi
}

show_summary() {
    local model=$(grep "^ACTIVE_MODEL=" "${ENV_FILE}" 2>/dev/null | cut -d'=' -f2)
    local name="${MODEL_NAMES[$model]:-$model}"
    local claude=""
    
    command -v claude &>/dev/null && claude="✅" || claude="❌"
    
    whiptail --title "✅ Pronto!" --msgbox "\
╔═══════════════════════════════════════════════════════════╗
║                 ✅ INSTALAÇÃO CONCLUÍDA!                  ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Modelo: $name
║  Claude Code: $claude
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║  COMANDOS:                                                ║
║    cc-status  → Ver status                                ║
║    cc-config  → Configurar                                ║
║    cc-logs    → Ver logs                                  ║
║    claude     → Iniciar Claude Code                       ║
║                                                           ║
║  Painel: http://localhost:8323/admin                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝" 20 60
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    [ "$EUID" -eq 0 ] && { echo "Não rode como root!"; exit 1; }
    
    check_dependencies
    show_welcome
    create_directories
    create_env_file
    configure_providers
    select_model
    install_python_deps
    copy_proxy_files
    create_aliases
    create_systemd_service
    install_claude_code
    start_proxy
    show_summary
    
    echo -e "${GREEN}✅ Tudo pronto! Use 'claude' para iniciar.${NC}"
}

main "$@"
