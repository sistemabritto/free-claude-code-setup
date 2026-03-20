#!/bin/bash
#===============================================================================
# Bootstrap Script - Setup Claude Free
# Detecta o sistema e executa o instalador correto
# Suporta: Linux, macOS, Windows (via WSL/Git Bash)
#===============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPO_URL="https://github.com/sistemabritto/free-claude-code-setup"
INSTALL_DIR="$HOME/.claude-free"
TEMP_DIR=$(mktemp -d 2>/dev/null || echo "/tmp/claude-free-$$")

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       🤖 Setup Claude Free - Instalador                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Cleanup
cleanup() {
    rm -rf "$TEMP_DIR" 2>/dev/null
}
trap cleanup EXIT

# Detectar sistema
OS="$(uname -s 2>/dev/null || echo 'Unknown')"
ARCH="$(uname -m 2>/dev/null || echo 'unknown')"

case "$OS" in
    Linux*)
        echo -e "${GREEN}✓ Sistema: Linux ($ARCH)${NC}"
        SCRIPT_NAME="install-linux.sh"
        ;;
    Darwin*)
        echo -e "${GREEN}✓ Sistema: macOS ($ARCH)${NC}"
        SCRIPT_NAME="install-mac.sh"
        ;;
    CYGWIN*|MINGW*|MSYS*|Windows_NT)
        echo -e "${YELLOW}⚠ Windows detectado${NC}"
        echo ""
        echo -e "${YELLOW}Para Windows, use PowerShell:${NC}"
        echo ""
        echo "  1. Abra PowerShell como Administrador"
        echo "  2. Execute:"
        echo ""
        echo "     irm https://raw.githubusercontent.com/sistemabritto/free-claude-code-setup/main/install-windows.ps1 | iex"
        echo ""
        echo "  Ou baixe e execute manualmente:"
        echo "  https://github.com/sistemabritto/free-claude-code-setup"
        echo ""
        exit 0
        ;;
    *)
        echo -e "${RED}✗ Sistema não suportado: $OS${NC}"
        echo "  Sistemas suportados: Linux, macOS, Windows"
        exit 1
        ;;
esac

# Baixar repositório
echo ""
echo -e "${CYAN}[1/3]${NC} Baixando Setup Claude Free..."

if command -v git &>/dev/null; then
    if git clone --depth 1 "$REPO_URL" "$TEMP_DIR/repo" 2>/dev/null; then
        echo -e "${GREEN}✓ Repositório baixado${NC}"
    else
        echo -e "${RED}✗ Erro ao clonar repositório${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Git não encontrado. Instale git primeiro.${NC}"
    exit 1
fi

# Instalar arquivos
echo -e "${CYAN}[2/3]${NC} Instalando arquivos..."

mkdir -p "$INSTALL_DIR/proxy"
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/logs"

# Copiar arquivos principais
for file in proxy_core.py config_manager.py models_config.py requirements.txt; do
    if [ -f "$TEMP_DIR/repo/$file" ]; then
        cp "$TEMP_DIR/repo/$file" "$INSTALL_DIR/proxy/"
    fi
done

echo -e "${GREEN}✓ Arquivos em $INSTALL_DIR${NC}"

# Executar instalador
echo -e "${CYAN}[3/3]${NC} Iniciando instalador..."

cd "$TEMP_DIR/repo"

if [ -f "$SCRIPT_NAME" ]; then
    chmod +x "$SCRIPT_NAME" 2>/dev/null
    
    # Para macOS, executar com zsh
    if [ "$OS" = "Darwin" ]; then
        exec zsh "$SCRIPT_NAME"
    else
        exec bash "$SCRIPT_NAME"
    fi
else
    echo -e "${RED}✗ Instalador $SCRIPT_NAME não encontrado${NC}"
    echo "  Arquivos disponíveis:"
    ls -la "$TEMP_DIR/repo/"
    exit 1
fi
