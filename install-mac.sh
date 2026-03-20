#!/bin/zsh
#===============================================================================
# Setup Claude Free - Instalador para macOS
# Repositório: sistemabritto/free-claude-code-setup
# Versão: 2.1.0
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
ENV_FILE="${CONFIG_DIR}/.env"
PROXY_PORT=8323

# =============================================================================
# MELHORES MODELOS PARA CÓDIGO 2025
# =============================================================================

PROVIDERS=("groq" "openrouter" "nvidia" "zai")

provider_name() {
    case "$1" in
        groq) echo "Groq" ;;
        openrouter) echo "OpenRouter" ;;
        nvidia) echo "NVIDIA NIM" ;;
        zai) echo "Z.AI" ;;
    esac
}

provider_tier() {
    case "$1" in
        groq) echo "100% FREE" ;;
        openrouter) echo "FREE + Paid" ;;
        nvidia) echo "FREE Rate-Limit" ;;
        zai) echo "Free Limitado" ;;
    esac
}

provider_url() {
    case "$1" in
        groq) echo "https://console.groq.com/keys" ;;
        openrouter) echo "https://openrouter.ai/keys" ;;
        nvidia) echo "https://build.nvidia.com/" ;;
        zai) echo "https://z.ai/" ;;
    esac
}

provider_key_name() {
    case "$1" in
        groq) echo "GROQ_API_KEY" ;;
        openrouter) echo "OPENROUTER_API_KEY" ;;
        nvidia) echo "NVIDIA_API_KEY" ;;
        zai) echo "ZAI_API_KEY" ;;
    esac
}

# MELHORES MODELOS PARA CÓDIGO
provider_models_str() {
    case "$1" in
        # Groq - Llama 4 é excelente para código
        groq) echo "llama-4-scout-17b-16e|llama-4-maverick-17b-128e|llama-3.3-70b-versatile|deepseek-r1-distill-llama-70b" ;;
        # OpenRouter - Qwen3 Coder 480B é TOP
        openrouter) echo "qwen/qwen3-coder:free|deepseek/deepseek-chat-v3-0324:free|deepseek/deepseek-r1:free|google/gemini-2.0-flash-exp:free" ;;
        # NVIDIA - Kimi K2 é excelente + MiniMax M2.5
        nvidia) echo "moonshotai/kimi-k2-instruct|minimaxai/minimax-m2.5|meta/llama-3.1-405b-instruct" ;;
        # Z.AI - GLM 4.5
        zai) echo "glm-4.5-air" ;;
    esac
}

model_display() {
    case "$1" in
        # Groq
        llama-4-scout-17b-16e) echo "Llama 4 Scout 🏆 CÓDIGO" ;;
        llama-4-maverick-17b-128e) echo "Llama 4 Maverick" ;;
        llama-3.3-70b-versatile) echo "Llama 3.3 70B" ;;
        deepseek-r1-distill-llama-70b) echo "DeepSeek R1 Distill" ;;
        # OpenRouter
        "qwen/qwen3-coder:free") echo "Qwen3 Coder 480B 🏆 TOP CÓDIGO" ;;
        "deepseek/deepseek-chat-v3-0324:free") echo "DeepSeek V3 Chat" ;;
        "deepseek/deepseek-r1:free") echo "DeepSeek R1 Reasoning" ;;
        "google/gemini-2.0-flash-exp:free") echo "Gemini 2.0 Flash" ;;
        # NVIDIA
        "moonshotai/kimi-k2-instruct") echo "Kimi K2 🏆 CÓDIGO" ;;
        minimaxai/minimax-m2.5) echo "MiniMax M2.5 230B" ;;
        "meta/llama-3.1-405b-instruct") echo "Llama 3.1 405B" ;;
        # Z.AI
        glm-4.5-air) echo "GLM 4.5 Air" ;;
        *) echo "$1" ;;
    esac
}

# =============================================================================
# UTILITÁRIOS
# =============================================================================

log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[AVISO]${NC} $1"; }
log_erro() { echo -e "${RED}[ERRO]${NC} $1"; }

mac_alert() {
    osascript -e "display alert \"$1\" message \"$2\"" 2>/dev/null
}

mac_input() {
    local hidden="${4:-false}"
    if [ "$hidden" = "true" ]; then
        osascript -e "text returned of (display dialog \"$2\" with title \"$1\" default answer \"${3:-}\" with hidden answer)" 2>/dev/null
    else
        osascript -e "text returned of (display dialog \"$2\" with title \"$1\" default answer \"${3:-}\")" 2>/dev/null
    fi
}

mac_choose() {
    local title="$1"
    local prompt="$2"
    shift 2
    local opts=("$@")
    
    local script="choose from list {"
    for o in "${opts[@]}"; do
        script+="\"$o\", "
    done
    script="${script%, }} with prompt \"$prompt\" with title \"$title\""
    
    local result=$(osascript -e "$script" 2>/dev/null)
    [ "$result" = "false" ] && echo "" || echo "$result"
}

count_configured() {
    local count=0
    for p in "${PROVIDERS[@]}"; do
        local key=$(provider_key_name "$p")
        grep -q "^${key}=.\+" "$ENV_FILE" 2>/dev/null && ((count++))
    done
    echo $count
}

# =============================================================================
# ESTRUTURA
# =============================================================================

check_deps() {
    log_info "Verificando dependências..."
    
    command -v python3 &>/dev/null || { log_erro "Python3 não encontrado"; exit 1; }
    command -v pip3 &>/dev/null || { log_erro "pip3 não encontrado"; exit 1; }
    
    log_ok "Dependências OK"
}

create_dirs() {
    log_info "Criando diretórios..."
    mkdir -p "$INSTALL_DIR"/{config,logs,proxy}
    log_ok "Diretórios criados"
}

create_env() {
    [ -f "$ENV_FILE" ] && return
    
    log_info "Criando configuração..."
    cat > "$ENV_FILE" << 'EOF'
# Setup Claude Free v2.1
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
# CONFIGURAÇÃO
# =============================================================================

configure_providers() {
    log_info "Configurando provedores..."
    
    while true; do
        local cnt=$(count_configured)
        
        echo ""
        echo -e "${CYAN}══════════════════════════════════════════════${NC}"
        echo -e "${CYAN}  PROVEDORES ($cnt configurados)${NC}"
        echo -e "${CYAN}══════════════════════════════════════════════${NC}"
        
        for p in "${PROVIDERS[@]}"; do
            local name=$(provider_name "$p")
            local tier=$(provider_tier "$p")
            local key=$(provider_key_name "$p")
            local conf="❌"
            
            grep -q "^${key}=.\+" "$ENV_FILE" 2>/dev/null && conf="✅"
            
            printf "  %-12s %-18s %s\n" "$name" "($tier)" "$conf"
        done
        
        echo ""
        
        local choices=()
        for p in "${PROVIDERS[@]}"; do
            choices+=("$(provider_name "$p")")
        done
        choices+=("➡️  Continuar")
        
        local sel=$(mac_choose "Provedores" "Selecione para configurar ou continue:" "${choices[@]}")
        
        if [ -z "$sel" ] || [ "$sel" = "➡️  Continuar" ]; then
            break
        fi
        
        for p in "${PROVIDERS[@]}"; do
            if [ "$(provider_name "$p")" = "$sel" ]; then
                configure_provider "$p"
                break
            fi
        done
    done
}

configure_provider() {
    local p="$1"
    local name=$(provider_name "$p")
    local url=$(provider_url "$p")
    local key=$(provider_key_name "$p")
    
    mac_alert "$name" "Será aberto:\n$url\n\nObtenha sua API Key e cole no próximo diálogo."
    open "$url"
    
    local api_key=$(mac_input "$name" "Cole sua API Key:" "" "true")
    
    if [ -n "$api_key" ]; then
        if grep -q "^${key}=" "$ENV_FILE"; then
            sed -i '' "s|^${key}=.*|${key}=${api_key}|" "$ENV_FILE"
        else
            echo "${key}=${api_key}" >> "$ENV_FILE"
        fi
        log_ok "$name configurado!"
    fi
}

select_model() {
    log_info "Selecionando modelo..."
    
    local available=()
    for p in "${PROVIDERS[@]}"; do
        local key=$(provider_key_name "$p")
        grep -q "^${key}=.\+" "$ENV_FILE" 2>/dev/null && available+=("$p")
    done
    
    if [ ${#available[@]} -eq 0 ]; then
        mac_alert "Aviso" "Configure pelo menos um provedor."
        return 1
    fi
    
    local models=()
    
    for p in "${available[@]}"; do
        local pname=$(provider_name "$p")
        local models_str=$(provider_models_str "$p")
        
        local old_ifs="$IFS"
        IFS='|'
        local mlist=($(echo "$models_str"))
        IFS="$old_ifs"
        
        for m in "${mlist[@]}"; do
            local disp=$(model_display "$m")
            models+=("[$pname] $disp|$p|$m")
        done
    done
    
    local show_models=()
    for m in "${models[@]}"; do
        show_models+=("${m%%|*}")
    done
    
    local sel=$(mac_choose "Modelo" "Selecione o modelo ativo:" "${show_models[@]}")
    
    if [ -n "$sel" ]; then
        for m in "${models[@]}"; do
            if [[ "$m" == "$sel|"* ]]; then
                local parts=(${(s/|/)m})
                local prov="${parts[2]}"
                local mod="${parts[3]}"
                
                sed -i '' "s|^ACTIVE_PROVIDER=.*|ACTIVE_PROVIDER=${prov}|" "$ENV_FILE"
                sed -i '' "s|^ACTIVE_MODEL=.*|ACTIVE_MODEL=${mod}|" "$ENV_FILE"
                
                log_ok "Modelo: $(model_display "$mod")"
                break
            fi
        done
    fi
}

configure_master() {
    local key=$(mac_input "Master Key" "Senha para o painel admin:\n(vazio = sem proteção)" "" "true")
    
    if [ $? -eq 0 ]; then
        if grep -q "^MASTER_KEY=" "$ENV_FILE"; then
            sed -i '' "s|^MASTER_KEY=.*|MASTER_KEY=${key}|" "$ENV_FILE"
        else
            echo "MASTER_KEY=${key}" >> "$ENV_FILE"
        fi
        log_ok "Master Key configurada"
    fi
}

# =============================================================================
# INSTALAÇÃO
# =============================================================================

install_deps() {
    log_info "Instalando dependências Python..."
    pip3 install -q flask requests python-dotenv gunicorn 2>/dev/null || \
    pip install -q flask requests python-dotenv gunicorn 2>/dev/null
    log_ok "Python deps OK"
}

copy_proxy_files() {
    log_info "Copiando arquivos do proxy..."
    
    # Se rodando do repositório git
    if [ -f "${0:A:h}/proxy_core.py" ]; then
        cp "${0:A:h}/proxy_core.py" "${INSTALL_DIR}/proxy/"
        cp "${0:A:h}/models_config.py" "${INSTALL_DIR}/proxy/"
        cp "${0:A:h}/config_manager.py" "${INSTALL_DIR}/proxy/"
    elif [ -f "./proxy_core.py" ]; then
        cp "./proxy_core.py" "${INSTALL_DIR}/proxy/"
        cp "./models_config.py" "${INSTALL_DIR}/proxy/"
        cp "./config_manager.py" "${INSTALL_DIR}/proxy/"
    else
        # Baixar do GitHub
        log_info "Baixando arquivos do GitHub..."
        curl -fsSL "https://raw.githubusercontent.com/sistemabritto/free-claude-code-setup/main/proxy_core.py" -o "${INSTALL_DIR}/proxy/proxy_core.py"
        curl -fsSL "https://raw.githubusercontent.com/sistemabritto/free-claude-code-setup/main/models_config.py" -o "${INSTALL_DIR}/proxy/models_config.py"
        curl -fsSL "https://raw.githubusercontent.com/sistemabritto/free-claude-code-setup/main/config_manager.py" -o "${INSTALL_DIR}/proxy/config_manager.py"
    fi
    
    log_ok "Arquivos do proxy copiados"
}

create_aliases() {
    log_info "Criando aliases..."
    
    local zshrc="${HOME}/.zshrc"
    local zprofile="${HOME}/.zprofile"
    
    # Bloco de aliases - cc-start inicia em background
    local block="
# =============================================================================
# Claude Free - Aliases
# =============================================================================
alias cc-config='python3 ${INSTALL_DIR}/proxy/config_manager.py'
alias cc-status='curl -s http://localhost:8323/health 2>/dev/null | python3 -m json.tool || echo \"Proxy não está rodando\"'
alias cc-stop='pkill -9 -f proxy_core.py 2>/dev/null; echo \"Proxy parado\"'
alias cc-logs='tail -f ${INSTALL_DIR}/logs/proxy.log'
alias cc-restart='cc-stop; sleep 1; cc-start'

# cc-start - Inicia proxy em background
cc-start() {
    pkill -9 -f proxy_core.py 2>/dev/null || true
    sleep 1
    nohup python3 ${INSTALL_DIR}/proxy/proxy_core.py > ${INSTALL_DIR}/logs/proxy.log 2>&1 &
    sleep 2
    if curl -s http://localhost:8323/health > /dev/null 2>&1; then
        echo '✅ Proxy iniciado na porta 8323'
    else
        echo '⚠️  Verifique logs: cc-logs'
    fi
}

# Claude CLI com proxy
claude() {
    if ! curl -s http://localhost:8323/health > /dev/null 2>&1; then
        echo '⚠️  Proxy não está rodando. Iniciando...'
        cc-start
        sleep 2
    fi
    ANTHROPIC_BASE_URL=http://localhost:8323 command claude \"\$@\"
}
"
    
    # Criar .zshrc se não existir
    if [ ! -f "$zshrc" ]; then
        touch "$zshrc"
        log_ok "Arquivo .zshrc criado"
    fi
    
    # Remover aliases antigos se existirem e adicionar novos
    if grep -q "cc-start" "$zshrc" 2>/dev/null; then
        # Remover bloco antigo
        sed -i '' '/^# =.*Claude Free/,/^# =.*[^=]$/d' "$zshrc" 2>/dev/null || true
        sed -i '' '/^alias cc-/,/^}$/d' "$zshrc" 2>/dev/null || true
    fi
    
    echo "$block" >> "$zshrc"
    log_ok "Aliases criados em .zshrc"
    
    # Criar .zprofile para aliases em sessões de login
    if [ ! -f "$zprofile" ]; then
        touch "$zprofile"
    fi
    
    if ! grep -q "cc-start" "$zprofile" 2>/dev/null; then
        echo "$block" >> "$zprofile"
        log_ok "Aliases também em .zprofile"
    fi
}

create_launch() {
    log_info "Criando LaunchAgent..."
    
    local plist="${HOME}/Library/LaunchAgents/com.claudefree.proxy.plist"
    
    cat > "$plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claudefree.proxy</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${INSTALL_DIR}/proxy/proxy_core.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>${INSTALL_DIR}/logs/proxy.log</string>
    <key>StandardErrorPath</key>
    <string>${INSTALL_DIR}/logs/proxy.log</string>
</dict>
</plist>
EOF
    log_ok "LaunchAgent criado"
}

start_proxy() {
    log_info "Iniciando proxy..."
    
    # Matar processo existente na porta - MÉTODO AGRESSIVO
    pkill -9 -f proxy_core.py 2>/dev/null || true
    sleep 1
    
    # Tentar liberar porta com lsof também
    local pid=$(lsof -ti:8323 2>/dev/null)
    if [ -n "$pid" ]; then
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi
    
    # Iniciar em background
    nohup python3 "${INSTALL_DIR}/proxy/proxy_core.py" > "${INSTALL_DIR}/logs/proxy.log" 2>&1 &
    
    sleep 2
    
    # Verificar se iniciou
    if curl -s "http://localhost:8323/health" > /dev/null 2>&1; then
        log_ok "Proxy iniciado na porta 8323"
    else
        log_warn "Proxy pode ter demorado para iniciar. Verifique os logs."
    fi
}

install_claude_code() {
    log_info "Verificando Claude Code CLI..."
    
    # Verificar se já está instalado
    if command -v claude &>/dev/null; then
        log_ok "Claude Code já instalado: $(claude --version 2>/dev/null | head -1 || echo 'OK')"
        return 0
    fi
    
    # Verificar Node.js 18+ - USAR SISTEMA PRIMEIRO
    if command -v node &>/dev/null; then
        local node_version=$(node -v 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$node_version" -ge 18 ]; then
            log_ok "Node.js $(node -v) encontrado no sistema"
            install_claude_code_npm
            return 0
        else
            log_warn "Node.js $node_version muito antigo. Necessário 18+."
        fi
    fi
    
    # Node.js não encontrado ou antigo - NÃO usar Homebrew em macOS antigo
    local macos_version=$(sw_vers -productVersion | cut -d'.' -f1,2)
    local major=$(echo "$macos_version" | cut -d'.' -f1)
    
    if [ "$major" -lt 11 ]; then
        # macOS 10.x (Catalina ou mais antigo)
        log_erro "================================================"
        log_erro "  macOS $macos_version detectado"
        log_erro "  Homebrew NÃO é recomendado (compilação lenta)"
        log_erro "================================================"
        echo ""
        echo -e "${YELLOW}Instale Node.js manualmente:${NC}"
        echo ""
        echo "  1. Baixe: https://nodejs.org/dist/v20.18.0/node-v20.18.0.pkg"
        echo "  2. Instale o .pkg"
        echo "  3. Rode novamente: curl ... | zsh"
        echo ""
        echo -e "${CYAN}Ou via linha de comando:${NC}"
        echo "  curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0.pkg -o /tmp/node.pkg"
        echo "  sudo installer -pkg /tmp/node.pkg -target /"
        echo ""
        return 1
    fi
    
    # macOS 11+ - pode usar Homebrew
    log_info "Instalando Node.js via Homebrew..."
    if command -v brew &>/dev/null; then
        brew install node
        install_claude_code_npm
    else
        log_erro "Homebrew não encontrado. Instale Node.js manualmente."
        return 1
    fi
}

install_claude_code_npm() {
    log_info "Instalando Claude Code via npm..."
    
    # Tentar instalador oficial primeiro
    if curl -fsSL https://claude.ai/install.sh 2>/dev/null | bash; then
        log_ok "Claude Code instalado via instalador oficial!"
        return 0
    fi
    
    # Fallback via npm
    if npm install -g @anthropic-ai/claude-code 2>/dev/null; then
        log_ok "Claude Code instalado via npm!"
        return 0
    fi
    
    log_erro "Falha ao instalar Claude Code"
    return 1
}

create_claude_config() {
    log_info "Configurando Claude Code para usar proxy..."
    
    # Criar diretório de config do Claude
    local claude_dir="${HOME}/.claude"
    mkdir -p "$claude_dir"
    
    # Criar arquivo de configuração para usar proxy
    cat > "${claude_dir}/settings.json" << 'EOF'
{
  "apiProvider": "anthropic",
  "apiBaseUrl": "http://localhost:8323",
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:8323"
  }
}
EOF
    
    # Atualizar aliases para incluir config
    local zshrc="${HOME}/.zshrc"
    if ! grep -q "ANTHROPIC_BASE_URL" "$zshrc" 2>/dev/null; then
        echo "" >> "$zshrc"
        echo "# Claude Code - Usar proxy local" >> "$zshrc"
        echo "export ANTHROPIC_BASE_URL=http://localhost:8323" >> "$zshrc"
    fi
    
    log_ok "Claude Code configurado para usar proxy!"
}

show_summary() {
    local active=$(grep "^ACTIVE_MODEL=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2)
    local model=$(model_display "$active")
    local cnt=$(count_configured)
    local claude_installed=""
    
    command -v claude &>/dev/null && claude_installed="✅" || claude_installed="❌"
    
    mac_alert "✅ Pronto!" "Setup Claude Free instalado!\n\n📁 $INSTALL_DIR\n🤖 $model\n📦 $cnt provedores\n\nClaude Code: $claude_installed\n\nTudo pronto! Use 'claude' para iniciar."
    
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ INSTALAÇÃO CONCLUÍDA!${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════${NC}"
    echo ""
    echo "  Modelo: $model"
    echo "  Provedores: $cnt configurados"
    echo "  Claude Code CLI: $claude_installed"
    echo ""
    echo -e "${GREEN}  🚀 TUDO PRONTO!${NC}"
    echo ""
    echo "  Comandos:"
    echo "    cc-status  → Ver status do proxy"
    echo "    cc-config  → Configurar modelos"
    echo "    claude     → Iniciar Claude Code"
    echo ""
    echo "  Painel: http://localhost:8323/admin"
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════${NC}"
    
    # Carregar aliases automaticamente no ambiente atual
    source "$HOME/.zshrc" 2>/dev/null || true
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  🤖 Setup Claude Free - macOS${NC}"
    echo -e "${CYAN}  v2.2.0 - Claude Code + Proxy Grátis${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════${NC}"
    echo ""
    
    [ "$(uname -s)" != "Darwin" ] && { log_erro "Use apenas no macOS"; exit 1; }
    
    check_deps
    create_dirs
    create_env
    configure_providers
    select_model
    configure_master
    install_deps
    copy_proxy_files
    create_aliases
    create_launch
    install_claude_code
    create_claude_config
    start_proxy
    show_summary
}

main "$@"
