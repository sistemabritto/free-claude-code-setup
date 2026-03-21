#!/bin/bash
#===============================================================================
# Setup Claude Free - Instalador TUI para Ambiente AI Gratuito
# Repositório: sistemabritto/setup-claude-free
# Versão: 2.0.0 - Atualizado com melhores modelos gratuitos 2025
#===============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Diretórios
INSTALL_DIR="${HOME}/.claude-free"
CONFIG_DIR="${INSTALL_DIR}/config"
LOGS_DIR="${INSTALL_DIR}/logs"
ENV_FILE="${CONFIG_DIR}/.env"
PROXY_PORT=8323

# =============================================================================
# MODELOS E PROVEDORES (ATUALIZADO 2025)
# =============================================================================

# Categorias: FREE (100% grátis), LOW_COST (barato), PAID (precisa de créditos)

declare -A PROVIDER_INFO=(
    ["groq"]="Groq|100% GRÁTIS|Inferência ULTRA-RÁPIDA (~460 tok/s)|https://console.groq.com/keys|gsk_"
    ["openrouter"]="OpenRouter|FREE + Low-Cost|Vários modelos gratuitos|https://openrouter.ai/keys|sk-or_"
    ["nvidia"]="NVIDIA NIM|FREE Rate-Limited|182+ modelos disponíveis|https://build.nvidia.com/|nvapi-"
    ["zai"]="Z.AI (GLM)|Free Limitado|Excelente para código|https://z.ai/|glm-"
)

# Modelos GRATUITOS por provedor
declare -A FREE_MODELS=(
    # GROQ - 100% GRÁTIS (Melhor velocidade)
    ["groq"]="llama-4-scout-17b-16e|llama-4-maverick-17b-128e|llama-3.3-70b-versatile|llama-3.1-8b-instant|deepseek-r1-distill-llama-70b"
    
    # OPENROUTER - Vários modelos FREE
    ["openrouter"]="qwen/qwen3-coder:free|deepseek/deepseek-chat-v3-0324:free|deepseek/deepseek-r1:free|meta-llama/llama-4-scout:free|z-ai/glm-4.5-air:free|google/gemini-2.0-flash-exp:free"
    
    # NVIDIA NIM - Rate limited FREE
    ["nvidia"]="minimaxai/minimax-m2.5|nvidia/nemotron-4-340b-instruct|meta/llama-3.1-405b-instruct"
    
    # Z.AI - Free limitado
    ["zai"]="glm-4.5-air"
)

# Nomes amigáveis dos modelos
declare -A MODEL_NAMES=(
    # GROQ
    ["llama-4-scout-17b-16e"]="Llama 4 Scout 17B (⭐ CÓDIGO)"
    ["llama-4-maverick-17b-128e"]="Llama 4 Maverick 17B"
    ["llama-3.3-70b-versatile"]="Llama 3.3 70B Versatile"
    ["llama-3.1-8b-instant"]="Llama 3.1 8B Instant"
    ["deepseek-r1-distill-llama-70b"]="DeepSeek R1 Distill 70B"
    
    # OPENROUTER
    ["qwen/qwen3-coder:free"]="Qwen3 Coder 480B (🏆 TOP CÓDIGO)"
    ["deepseek/deepseek-chat-v3-0324:free"]="DeepSeek V3 Chat"
    ["deepseek/deepseek-r1:free"]="DeepSeek R1 Reasoning"
    ["meta-llama/llama-4-scout:free"]="Llama 4 Scout"
    ["z-ai/glm-4.5-air:free"]="GLM 4.5 Air"
    ["google/gemini-2.0-flash-exp:free"]="Gemini 2.0 Flash"
    
    # NVIDIA
    ["minimaxai/minimax-m2.5"]="MiniMax M2.5 230B (⭐ CÓDIGO)"
    ["nvidia/nemotron-4-340b-instruct"]="Nemotron 4 340B"
    ["meta/llama-3.1-405b-instruct"]="Llama 3.1 405B"
    
    # Z.AI
    ["glm-4.5-air"]="GLM 4.5 Air"
)

# Modelos recomendados para CÓDIGO
declare -A CODING_MODELS=(
    ["qwen/qwen3-coder:free"]="OpenRouter|480B params, 262K context"
    ["llama-4-scout-17b-16e"]="Groq|~460 tok/s, multimodal"
    ["minimaxai/minimax-m2.5"]="NVIDIA|230B, especializado código"
    ["deepseek/deepseek-r1:free"]="OpenRouter|Reasoning + código"
)

# Base URLs
declare -A PROVIDER_BASE_URLS=(
    ["groq"]="https://api.groq.com/openai/v1"
    ["openrouter"]="https://openrouter.ai/api/v1"
    ["nvidia"]="https://integrate.api.nvidia.com/v1"
    ["zai"]="https://open.bigmodel.cn/api/paas/v4"
)

# API Key env names
declare -A API_KEY_NAMES=(
    ["groq"]="GROQ_API_KEY"
    ["openrouter"]="OPENROUTER_API_KEY"
    ["nvidia"]="NVIDIA_API_KEY"
    ["zai"]="ZAI_API_KEY"
)

# =============================================================================
# FUNÇÕES DE LOG
# =============================================================================

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_highlight() {
    echo -e "${MAGENTA}★${NC} $1"
}

# =============================================================================
# VERIFICAÇÕES
# =============================================================================

check_dependencies() {
    log_info "Verificando e instalando dependências do sistema..."
    
    local missing_deps=()
    
    command -v whiptail &>/dev/null || missing_deps+=("whiptail")
    command -v python3  &>/dev/null || missing_deps+=("python3" "python3-pip" "python3-dev" "build-essential")
    { command -v pip3 &>/dev/null || command -v pip &>/dev/null; } || missing_deps+=("python3-pip")
    command -v git  &>/dev/null || missing_deps+=("git")
    command -v curl &>/dev/null || missing_deps+=("curl")
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_info "Instalando: ${missing_deps[*]}"
        sudo apt-get update -qq
        sudo apt-get install -y "${missing_deps[@]}"
        log_success "Dependências instaladas!"
    fi
    
    # Instalar Node.js 20 via NodeSource se não existir ou for antigo
    if ! command -v node &>/dev/null || [ "$(node -v 2>/dev/null | cut -dv -f2 | cut -d. -f1)" -lt 18 ]; then
        log_info "Instalando Node.js 20 (LTS)..."
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - 2>/dev/null
        sudo apt-get install -y nodejs
        log_success "Node.js $(node -v) instalado!"
    else
        log_info "Node.js $(node -v) já instalado."
    fi
}

# =============================================================================
# CRIAÇÃO DE ESTRUTURA
# =============================================================================

create_directories() {
    log_info "Criando estrutura de diretórios..."
    mkdir -p "${INSTALL_DIR}"
    mkdir -p "${CONFIG_DIR}"
    mkdir -p "${LOGS_DIR}"
    mkdir -p "${INSTALL_DIR}/proxy"
    log_success "Diretórios criados em ${INSTALL_DIR}"
}

create_env_file() {
    if [ ! -f "${ENV_FILE}" ]; then
        log_info "Criando arquivo de configuração inicial..."
        cat > "${ENV_FILE}" << 'EOF'
# =============================================================================
# Configuração do Setup Claude Free v2.0
# Atualizado: 2025 - Melhores modelos gratuitos
# =============================================================================

# Provedor ativo: groq, openrouter, nvidia, zai
ACTIVE_PROVIDER=openrouter

# Modelo ativo (recomendado para código: llama-4-scout-17b-16e)
ACTIVE_MODEL=qwen/qwen3-coder:free

# API Keys (configure conforme necessário)
GROQ_API_KEY=
OPENROUTER_API_KEY=
NVIDIA_API_KEY=
ZAI_API_KEY=

# Configuração do Proxy
PROXY_PORT=8323
MASTER_KEY=

# Hot Reload (segundos)
CONFIG_RELOAD_INTERVAL=10

# Logs
LOG_LEVEL=INFO

# Categoria de modelos: free, low_cost, paid
MODEL_TIER=free
EOF
        log_success "Arquivo .env criado em ${ENV_FILE}"
    else
        log_info "Arquivo .env já existe, mantendo configurações atuais"
    fi
}

# =============================================================================
# INTERFACE TUI
# =============================================================================

show_welcome() {
    whiptail --title "Setup Claude Free v2.0 - Ambiente AI Gratuito" \
        --msgbox "\
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🤖 Setup Claude Free - Ambiente AI Gratuito           ║
║                     Versão 2.0 - 2025                        ║
║                                                              ║
║  MELHORES MODELOS GRATUITOS PARA CÓDIGO:                    ║
║                                                              ║
║  🏆 Qwen3 Coder 480B (OpenRouter) - TOP código              ║
║  ⭐ Llama 4 Scout (Groq) - Ultra-rápido ~460 tok/s          ║
║  ⭐ MiniMax M2.5 230B (NVIDIA) - Especialista código        ║
║  ⭐ DeepSeek R1 (OpenRouter) - Reasoning avançado           ║
║                                                              ║
║  Recursos:                                                   ║
║  • Proxy local com tradução Anthropic ↔ OpenAI              ║
║  • Painel web de administração                              ║
║  • Gerenciamento via terminal (cc-config)                   ║
║  • Hot reload de configuração                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝\

Pressione OK para continuar..." \
        26 70
}

show_provider_info() {
    local provider=$1
    IFS='|' read -r name tier desc url prefix <<< "${PROVIDER_INFO[$provider]}"
    
    whiptail --title "Provedor: $name" \
        --msgbox "\
╔══════════════════════════════════════════════════════════════╗
║  $name
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Tipo: $tier
║  $desc
║                                                              ║
║  Obter API Key: $url
║                                                              ║
╚══════════════════════════════════════════════════════════════╝\

Pressione OK para configurar..." \
        15 70
}

configure_api_keys() {
    local providers=("groq" "openrouter" "nvidia" "zai")
    local selected_providers=()
    
    while true; do
        # Criar lista de checkboxes com status
        local checklist_items=()
        
        for provider in "${providers[@]}"; do
            IFS='|' read -r name tier desc url prefix <<< "${PROVIDER_INFO[$provider]}"
            local key_name="${API_KEY_NAMES[$provider]}"
            local status="off"
            
            # Verificar se já configurado
            if grep -q "^${key_name}=.\+" "${ENV_FILE}" 2>/dev/null; then
                status="on"
            fi
            
            checklist_items+=("$provider" "$name ($tier)" "$status")
        done
        
        local selections
        selections=$(whiptail --title "Configurar Provedores" \
            --checklist "\nSelecione os provedores para configurar:\nMarcados = já configurados\n\nUse ESPAÇO para marcar, ENTER para confirmar:" \
            18 65 4 "${checklist_items[@]}" \
            3>&1 1>&2 2>&3)
        
        local exit_status=$?
        if [ $exit_status -ne 0 ]; then
            break
        fi
        
        # Processar seleções
        IFS=' ' read -ra selected_providers <<< "$selections"
        
        if [ ${#selected_providers[@]} -eq 0 ]; then
            if whiptail --title "Nenhum Provedor Selecionado" \
                --yesno "Nenhum provedor selecionado. Deseja sair?" 10 50; then
                break
            fi
            continue
        fi
        
        # Para cada provedor selecionado, pedir a chave
        for provider in "${selected_providers[@]}"; do
            provider=$(echo "$provider" | tr -d '"')
            
            # Mostrar info do provedor
            show_provider_info "$provider"
            
            IFS='|' read -r name tier desc url prefix <<< "${PROVIDER_INFO[$provider]}"
            local key_name="${API_KEY_NAMES[$provider]}"
            local current_key=""
            
            # Obter chave atual se existir
            current_key=$(grep "^${key_name}=" "${ENV_FILE}" 2>/dev/null | cut -d'=' -f2-)
            
            local api_key
            api_key=$(whiptail --title "API Key - $name" \
                --passwordbox "\nDigite sua API Key para $name:\n\nPrefixo esperado: $prefix\n\nA chave será armazenada em:\n${ENV_FILE}" \
                14 65 "${current_key}" \
                3>&1 1>&2 2>&3)
            
            if [ $? -eq 0 ] && [ -n "$api_key" ]; then
                # Atualizar ou adicionar a chave no .env
                if grep -q "^${key_name}=" "${ENV_FILE}"; then
                    sed -i "s|^${key_name}=.*|${key_name}=${api_key}|" "${ENV_FILE}"
                else
                    echo "${key_name}=${api_key}" >> "${ENV_FILE}"
                fi
                log_success "Chave $name configurada!"
            fi
        done
        
        if ! whiptail --title "Continuar?" \
            --yesno "Provedores configurados: ${#selected_providers[@]}\n\nDeseja configurar mais algum?" 10 50; then
            break
        fi
    done
}

select_active_model() {
    # Verificar quais provedores têm chaves configuradas
    local available_providers=()
    
    for provider in groq openrouter nvidia zai; do
        local key_name="${API_KEY_NAMES[$provider]}"
        if grep -q "^${key_name}=.\+" "${ENV_FILE}" 2>/dev/null; then
            available_providers+=("$provider")
        fi
    done
    
    if [ ${#available_providers[@]} -eq 0 ]; then
        whiptail --title "Nenhum Provedor Configurado" \
            --msgbox "Nenhum provedor possui API Key configurada.\nConfigure pelo menos um provedor primeiro." 12 50
        return 1
    fi
    
    # Criar lista de modelos disponíveis
    local model_options=()
    local current_model=$(grep "^ACTIVE_MODEL=" "${ENV_FILE}" 2>/dev/null | cut -d'=' -f2)
    
    # Adicionar modelos recomendados primeiro
    model_options+=("recommend" "🏆 RECOMENDADO PARA CÓDIGO (melhor disponível)")
    
    for provider in "${available_providers[@]}"; do
        IFS='|' read -ra models <<< "${FREE_MODELS[$provider]}"
        IFS='|' read -r name tier desc url prefix <<< "${PROVIDER_INFO[$provider]}"
        
        for model in "${models[@]}"; do
            local display_name="${MODEL_NAMES[$model]:-$model}"
            local selected=""
            
            if [ "$model" == "$current_model" ]; then
                selected=" ✓"
            fi
            
            model_options+=("$provider:$model" "[$name] $display_name$selected")
        done
    done
    
    local selected
    selected=$(whiptail --title "Selecionar Modelo Ativo" \
        --menu "\nEscolha o modelo para suas requisicoes:\n" \
        25 100 15 "${model_options[@]}" \
        3>&1 1>&2 2>&3)
    
    if [ $? -eq 0 ] && [ -n "$selected" ]; then
        if [ "$selected" == "recommend" ]; then
            # Selecionar melhor modelo disponível para código
            select_best_coding_model
        else
            IFS=':' read -r provider model <<< "$selected"
            
            sed -i "s|^ACTIVE_PROVIDER=.*|ACTIVE_PROVIDER=${provider}|" "${ENV_FILE}"
            sed -i "s|^ACTIVE_MODEL=.*|ACTIVE_MODEL=${model}|" "${ENV_FILE}"
            
            local model_name="${MODEL_NAMES[$model]:-$model}"
            log_success "Modelo ativo: $model_name"
        fi
    fi
}

select_best_coding_model() {
    # Prioridade de melhores modelos para código
    local priority_models=(
        "openrouter:qwen/qwen3-coder:free"
        "groq:llama-4-scout-17b-16e"
        "nvidia:minimaxai/minimax-m2.5"
        "openrouter:deepseek/deepseek-r1:free"
    )
    
    for model_entry in "${priority_models[@]}"; do
        IFS=':' read -r provider model <<< "$model_entry"
        local key_name="${API_KEY_NAMES[$provider]}"
        
        if grep -q "^${key_name}=.\+" "${ENV_FILE}" 2>/dev/null; then
            sed -i "s|^ACTIVE_PROVIDER=.*|ACTIVE_PROVIDER=${provider}|" "${ENV_FILE}"
            sed -i "s|^ACTIVE_MODEL=.*|ACTIVE_MODEL=${model}|" "${ENV_FILE}"
            
            local model_name="${MODEL_NAMES[$model]:-$model}"
            log_success "Modelo recomendado selecionado: $model_name"
            return 0
        fi
    done
    
    whiptail --title "Nenhum Modelo Recomendado Disponível" \
        --msgbox "Configure pelo menos um destes provedores para usar o modelo recomendado:\n\n• OpenRouter (Qwen3 Coder)\n• Groq (Llama 4 Scout)\n• NVIDIA (MiniMax M2.5)" 14 60
}

configure_master_key() {
    local master_key
    master_key=$(whiptail --title "Configurar Master Key" \
        --passwordbox "\nDefina uma senha para o painel admin web.\n\nDeixe vazio para desabilitar proteção.\n\nPainel: http://localhost:${PROXY_PORT}/admin" \
        14 60 \
        3>&1 1>&2 2>&3)
    
    if [ $? -eq 0 ]; then
        if grep -q "^MASTER_KEY=" "${ENV_FILE}"; then
            sed -i "s|^MASTER_KEY=.*|MASTER_KEY=${master_key}|" "${ENV_FILE}"
        else
            echo "MASTER_KEY=${master_key}" >> "${ENV_FILE}"
        fi
        log_success "Master Key configurada!"
    fi
}

install_antigravity() {
    if whiptail --title "Instalar Antigravity IDE" \
        --yesno "\nDeseja instalar o Antigravity IDE (Google)?\n\nIDE gratuito com agentes de IA.\nRequer login com conta Google.\n\n(Recomendado)" 14 60; then
        
        log_info "Adicionando repositório do Antigravity..."
        
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg | \
            sudo gpg --dearmor -o /etc/apt/keyrings/antigravity-repo-key.gpg
        
        echo "deb [signed-by=/etc/apt/keyrings/antigravity-repo-key.gpg] https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev/ antigravity-debian main" | \
            sudo tee /etc/apt/sources.list.d/antigravity.list > /dev/null
        
        log_info "Instalando Antigravity..."
        sudo apt-get update -qq
        sudo apt-get install -y antigravity
        
        log_success "Antigravity instalado! Abra pelo menu de aplicativos."
        log_info "  Configure: ANTHROPIC_BASE_URL=http://localhost:${PROXY_PORT}"
    else
        log_info "Antigravity: instale quando quiser em https://antigravity.google/download/linux"
    fi
}

# =============================================================================
# INSTALAÇÃO DOS ARQUIVOS
# =============================================================================

install_proxy_files() {
    log_info "Instalando arquivos do proxy..."
    
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Copiar arquivos principais
    for file in proxy_core.py config_manager.py models_config.py requirements.txt; do
        if [ -f "${script_dir}/${file}" ]; then
            cp "${script_dir}/${file}" "${INSTALL_DIR}/proxy/"
        fi
    done
    
    # Criar requirements se não existir
    if [ ! -f "${INSTALL_DIR}/proxy/requirements.txt" ]; then
        cat > "${INSTALL_DIR}/proxy/requirements.txt" << 'EOF'
flask>=3.0.0
requests>=2.31.0
python-dotenv>=1.0.0
gunicorn>=21.0.0
EOF
    fi
    
    log_success "Arquivos do proxy instalados"
}

install_python_deps() {
    log_info "Instalando dependências Python..."
    pip3 install -q flask requests python-dotenv gunicorn 2>/dev/null || \
    pip install -q flask requests python-dotenv gunicorn 2>/dev/null
    log_success "Dependências Python instaladas"
}

create_aliases() {
    log_info "Criando aliases..."
    
    local bashrc="${HOME}/.bashrc"
    local zshrc="${HOME}/.zshrc"
    
    local alias_block="
# Claude Free - Comandos
alias cc-config='python3 ${INSTALL_DIR}/proxy/config_manager.py'
cc-start() {
    # Matar qualquer processo na porta 8323
    pkill -9 -f proxy_core.py 2>/dev/null || true
    local pid=$(lsof -ti:8323 2>/dev/null)
    [ -n "$pid" ] && kill -9 $pid 2>/dev/null || true
    sleep 1
    
    nohup python3 ${INSTALL_DIR}/proxy/proxy_core.py > ${INSTALL_DIR}/logs/proxy.log 2>&1 &
    sleep 2
    
    if curl -s http://localhost:8323/health > /dev/null 2>&1; then
        echo "✅ Proxy rodando em http://localhost:8323"
    else
        echo "⚠️  Erro ao iniciar. Logs: cc-logs"
    fi
}
alias cc-status='curl -s http://localhost:8323/health | python3 -m json.tool'
alias cc-models='python3 ${INSTALL_DIR}/proxy/models_config.py'
"
    
    for rc in "$bashrc" "$zshrc"; do
        if [ -f "$rc" ] && ! grep -q "cc-config" "$rc" 2>/dev/null; then
            echo "$alias_block" >> "$rc"
        fi
    done
    
    log_success "Aliases criados (reinicie o terminal)"
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
    systemctl --user enable claude-free.service 2>/dev/null || true
    systemctl --user start claude-free.service 2>/dev/null || true
    log_success "Serviço systemd criado e iniciado"
}

# =============================================================================
# INSTALAÇÃO DO CLAUDE CODE CLI
# =============================================================================

install_claude_code() {
    log_info "Verificando Claude Code CLI..."
    
    if command -v claude &>/dev/null; then
        log_info "Claude Code já instalado: $(claude --version 2>/dev/null | head -1 || echo OK)"
        return 0
    fi
    
    log_info "Instalando Claude Code via instalador oficial..."
    
    # Tentar instalador oficial
    if curl -fsSL https://claude.ai/install.sh 2>/dev/null | bash; then
        log_success "Claude Code instalado!"
        return 0
    fi
    
    # Fallback: npm global
    log_info "Tentando via npm..."
    if npm install -g @anthropic-ai/claude-code 2>/dev/null; then
        log_success "Claude Code instalado via npm!"
        return 0
    fi
    
    log_warning "Não foi possível instalar o Claude Code automaticamente."
    log_warning "Tente manualmente: npm install -g @anthropic-ai/claude-code"
    return 1
}

configure_claude_proxy() {
    log_info "Configurando Claude Code para usar proxy..."
    
    mkdir -p "${HOME}/.claude"
    
    local bashrc="${HOME}/.bashrc"
    local master_key=$(grep "^MASTER_KEY=" "${ENV_FILE}" 2>/dev/null | cut -d'=' -f2)
    [ -z "$master_key" ] && master_key="sk-free-proxy"
    
    # Fix PATH para ~/.local/bin
    if ! grep -q 'HOME/.local/bin' "$bashrc" 2>/dev/null; then
        echo "" >> "$bashrc"
        echo "# Claude Code - PATH" >> "$bashrc"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$bashrc"
    fi
    
    # Variáveis do proxy
    if ! grep -q "ANTHROPIC_BASE_URL" "$bashrc" 2>/dev/null; then
        echo "" >> "$bashrc"
        echo "# Claude Free - Proxy local" >> "$bashrc"
        echo "export ANTHROPIC_BASE_URL=http://localhost:${PROXY_PORT}" >> "$bashrc"
        echo "export ANTHROPIC_AUTH_TOKEN=${master_key}" >> "$bashrc"
        echo 'export ANTHROPIC_API_KEY=""' >> "$bashrc"
    fi
    
    # Aplicar imediatamente
    export PATH="$HOME/.local/bin:$PATH"
    export ANTHROPIC_BASE_URL="http://localhost:${PROXY_PORT}"
    export ANTHROPIC_AUTH_TOKEN="${master_key}"
    export ANTHROPIC_API_KEY=""
    
    # Criar settings.json com proxy configurado
    cat > "${HOME}/.claude/settings.json" << EOF
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:${PROXY_PORT}",
    "ANTHROPIC_AUTH_TOKEN": "${master_key}",
    "ANTHROPIC_API_KEY": ""
  }
}
EOF
    
    # Criar ~/.claude.json para pular tela de login no primeiro uso
    # (bug conhecido no Claude Code 2.0.65+: fresh install ignora settings.json)
    if [ ! -f "${HOME}/.claude.json" ]; then
        cat > "${HOME}/.claude.json" << EOF
{
  "hasCompletedOnboarding": true,
  "primaryApiKeySource": "bedrock"
}
EOF
    fi
    
    log_success "Claude Code configurado para usar proxy na porta ${PROXY_PORT}!"
}


# =============================================================================
# RESUMO FINAL
# =============================================================================

show_summary() {
    # Iniciar proxy antes do resumo
    log_info "Iniciando proxy..."
    pkill -f proxy_core.py 2>/dev/null || true
    sleep 1
    nohup python3 "${INSTALL_DIR}/proxy/proxy_core.py" > "${INSTALL_DIR}/logs/proxy.log" 2>&1 &
    sleep 3
    
    if curl -s "http://localhost:${PROXY_PORT}/health" > /dev/null 2>&1; then
        log_success "Proxy rodando em http://localhost:${PROXY_PORT}"
    else
        log_warning "Proxy pode demorar alguns segundos. Use: cc-start"
    fi
    
    local configured_providers=()
    local active_provider=$(grep "^ACTIVE_PROVIDER=" "${ENV_FILE}" 2>/dev/null | cut -d'=' -f2)
    local active_model=$(grep "^ACTIVE_MODEL=" "${ENV_FILE}" 2>/dev/null | cut -d'=' -f2)
    
    for provider in groq openrouter nvidia zai; do
        local key_name="${API_KEY_NAMES[$provider]}"
        if grep -q "^${key_name}=.\+" "${ENV_FILE}" 2>/dev/null; then
            IFS='|' read -r name tier desc url prefix <<< "${PROVIDER_INFO[$provider]}"
            configured_providers+=("$name")
        fi
    done
    
    local model_name="${MODEL_NAMES[$active_model]:-$active_model}"
    
    whiptail --title "✓ Instalação Concluída!" \
        --msgbox "\
╔══════════════════════════════════════════════════════════════╗
║                  ✓ INSTALAÇÃO CONCLUÍDA!                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Diretório: ${INSTALL_DIR}
║  Config:    ${ENV_FILE}
║                                                              ║
║  Provedores Configurados: ${configured_providers[*]:-Nenhum}
║  Modelo Ativo: ${model_name:-Não definido}
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                    COMANDOS:                                 ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  cc-config    Menu de configuração                           ║
║  cc-start     Iniciar o proxy                                ║
║  cc-status    Verificar status                               ║
║  cc-models    Ver modelos disponíveis                        ║
║                                                              ║
║  Painel Web:  http://localhost:${PROXY_PORT}/admin
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                  PRÓXIMOS PASSOS:                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Reinicie o terminal: source ~/.bashrc                    ║
║  2. Inicie o proxy: cc-start                                 ║
║  3. Configure seu cliente para:                              ║
║     http://localhost:${PROXY_PORT}/v1/chat/completions
║                                                              ║
╚══════════════════════════════════════════════════════════════╝\

Pressione OK para finalizar..." \
        28 70
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    if [ "$EUID" -eq 0 ]; then
        whiptail --title "Aviso" --msgbox "Execute como usuário normal, não como root." 10 50
        exit 1
    fi
    
    check_dependencies
    show_welcome
    create_directories
    create_env_file
    configure_api_keys
    select_active_model
    configure_master_key
    install_antigravity
    install_proxy_files
    install_python_deps
    create_aliases
    create_systemd_service
    install_claude_code
    configure_claude_proxy
    show_summary
    
    log_success "Instalacao concluida!"
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ TUDO PRONTO!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  Proxy: ${CYAN}http://localhost:${PROXY_PORT}${NC}"
    echo -e "  Modelo: ${CYAN}${active_model}${NC}"
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════${NC}"
    
    # Aplicar PATH
    export PATH="$HOME/.local/bin:$PATH"
    export ANTHROPIC_BASE_URL="http://localhost:${PROXY_PORT}"
    
    echo ""
    echo -e "${GREEN}  Abrindo Antigravity...${NC}"
    echo ""
    
    # Abrir Antigravity se instalado, senão Claude Code
    if command -v antigravity &>/dev/null; then
        antigravity . &
        echo -e "${GREEN}  ✅ Antigravity aberto!${NC}"
        echo -e "${CYAN}  Proxy: http://localhost:${PROXY_PORT}${NC}"
    elif command -v claude &>/dev/null; then
        echo -e "${YELLOW}  Antigravity não encontrado. Abrindo Claude Code...${NC}"
        exec claude
    else
        echo -e "${YELLOW}  Instalação concluída!${NC}"
        echo -e "${CYAN}  Proxy: http://localhost:${PROXY_PORT}${NC}"
        echo -e "${CYAN}  Claude Code: source ~/.bashrc && claude${NC}"
        echo -e "${CYAN}  Antigravity: https://antigravity.dev${NC}"
    fi
}

main "$@"
