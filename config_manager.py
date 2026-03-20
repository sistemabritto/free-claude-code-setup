#!/usr/bin/env python3
"""
Config Manager - Gerenciador de Configuração via TUI
Comando: cc-config

Este script fornece uma interface TUI (Terminal User Interface) para
gerenciar as configurações do Claude Free Proxy, incluindo:
- Troca de modelo ativo
- Adição/edição de chaves API
- Desabilitação de provedores
- Visualização de status
- Teste de conexão

Repositório: sistemabritto/setup-claude-free
Versão: 1.0.0
"""

import os
import sys
import subprocess
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple, Any


# =============================================================================
# MAPEAMENTO RÍGIDO DE PROVEDORES E MODELOS
# =============================================================================

PROVIDERS: Dict[str, Dict[str, Any]] = {
    "groq": {
        "name": "Groq (Llama 3.1)",
        "models": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant"],
        "env_key": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "description": "Inferência ultra-rápida com Llama 3.1"
    },
    "nvidia": {
        "name": "NVIDIA NIM (Kimi K2)",
        "models": ["moonshotai/kimi-k2-instruct"],
        "env_key": "NVIDIA_API_KEY",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "description": "Kimi K2 Instruct via NVIDIA NIM"
    },
    "openrouter": {
        "name": "OpenRouter (DeepSeek/Qwen)",
        "models": ["deepseek/deepseek-chat", "qwen/qwen-2.5-coder-32b-instruct"],
        "env_key": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "description": "DeepSeek V3 e Qwen Coder 32B"
    }
}

# Caminho do arquivo .env
ENV_FILE = Path(os.path.expanduser("~/.claude-free/config/.env"))
INSTALL_DIR = Path(os.path.expanduser("~/.claude-free"))


# =============================================================================
# CLASSE DE CONFIGURAÇÃO
# =============================================================================

class ConfigManager:
    """Gerenciador de configuração do Claude Free"""
    
    def __init__(self):
        self.config: Dict[str, str] = {}
        self.load()
    
    def load(self) -> None:
        """Carrega configuração do arquivo .env"""
        self.config = {}
        
        if not ENV_FILE.exists():
            self._create_default()
            return
        
        try:
            with open(ENV_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.config[key.strip()] = value.strip()
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
    
    def save(self) -> None:
        """Salva configuração no arquivo .env"""
        try:
            # Garantir que o diretório existe
            ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            content = f"""# =============================================================================
# Configuração do Setup Claude Free
# Atualizado em: {datetime.now().isoformat()}
# =============================================================================

# Provedor ativo: groq, nvidia, openrouter
ACTIVE_PROVIDER={self.config.get('ACTIVE_PROVIDER', 'groq')}

# Modelo ativo (específico do provedor)
ACTIVE_MODEL={self.config.get('ACTIVE_MODEL', 'llama-3.1-70b-versatile')}

# API Keys - Configure conforme necessário
GROQ_API_KEY={self.config.get('GROQ_API_KEY', '')}
NVIDIA_API_KEY={self.config.get('NVIDIA_API_KEY', '')}
OPENROUTER_API_KEY={self.config.get('OPENROUTER_API_KEY', '')}

# Configuração do Proxy
PROXY_PORT={self.config.get('PROXY_PORT', '8323')}
MASTER_KEY={self.config.get('MASTER_KEY', '')}

# Hot Reload (segundos)
CONFIG_RELOAD_INTERVAL={self.config.get('CONFIG_RELOAD_INTERVAL', '10')}

# Logs
LOG_LEVEL={self.config.get('LOG_LEVEL', 'INFO')}
"""
            with open(ENV_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Configuração salva em {ENV_FILE}")
            
        except Exception as e:
            print(f"✗ Erro ao salvar configuração: {e}")
    
    def _create_default(self) -> None:
        """Cria arquivo de configuração padrão"""
        self.config = {
            'ACTIVE_PROVIDER': 'groq',
            'ACTIVE_MODEL': 'llama-3.1-70b-versatile',
            'GROQ_API_KEY': '',
            'NVIDIA_API_KEY': '',
            'OPENROUTER_API_KEY': '',
            'PROXY_PORT': '8323',
            'MASTER_KEY': '',
            'CONFIG_RELOAD_INTERVAL': '10',
            'LOG_LEVEL': 'INFO'
        }
        self.save()
    
    def get(self, key: str, default: str = '') -> str:
        """Obtém valor de configuração"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: str) -> None:
        """Define valor de configuração"""
        self.config[key] = value
    
    def get_available_providers(self) -> List[str]:
        """Retorna lista de provedores com API key configurada"""
        available = []
        for provider_id, provider_info in PROVIDERS.items():
            if self.config.get(provider_info['env_key']):
                available.append(provider_id)
        return available
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Retorna API key do provedor"""
        if provider in PROVIDERS:
            return self.config.get(PROVIDERS[provider]['env_key'], '')
        return None
    
    def is_provider_configured(self, provider: str) -> bool:
        """Verifica se provedor está configurado"""
        return bool(self.get_api_key(provider))


# Instância global
config = ConfigManager()


# =============================================================================
# FUNÇÕES DE INTERFACE TUI (WHIPTAIL)
# =============================================================================

def check_whiptail() -> bool:
    """Verifica se whiptail está instalado"""
    try:
        subprocess.run(
            ['which', 'whiptail'],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def whiptail_msgbox(title: str, message: str, height: int = 15, width: int = 60) -> None:
    """Exibe uma caixa de mensagem"""
    try:
        subprocess.run([
            'whiptail', '--title', title,
            '--msgbox', message,
            str(height), str(width)
        ], check=True)
    except subprocess.CalledProcessError:
        print(f"\n=== {title} ===\n{message}\n")


def whiptail_menu(
    title: str,
    options: List[Tuple[str, str]],
    height: int = 20,
    width: int = 60,
    menu_height: int = 10
) -> Optional[str]:
    """Exibe um menu de seleção"""
    cmd = [
        'whiptail', '--title', title,
        '--menu', '\nSelecione uma opção:\n',
        str(height), str(width), str(menu_height)
    ]
    
    for tag, item in options:
        cmd.extend([tag, item])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except subprocess.CalledProcessError:
        return None


def whiptail_input(
    title: str,
    prompt: str,
    default: str = "",
    password: bool = False,
    height: int = 10,
    width: int = 60
) -> Optional[str]:
    """Exibe uma caixa de entrada"""
    cmd = ['whiptail', '--title', title]
    
    if password:
        cmd.append('--passwordbox')
    else:
        cmd.append('--inputbox')
    
    cmd.extend([prompt, str(height), str(width), default])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except subprocess.CalledProcessError:
        return None


def whiptail_yesno(title: str, prompt: str, height: int = 10, width: int = 60) -> bool:
    """Exibe uma pergunta sim/não"""
    try:
        result = subprocess.run([
            'whiptail', '--title', title,
            '--yesno', prompt,
            str(height), str(width)
        ])
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False


def whiptail_radiolist(
    title: str,
    prompt: str,
    options: List[Tuple[str, str, bool]],
    height: int = 20,
    width: int = 70,
    list_height: int = 10
) -> Optional[str]:
    """Exibe uma lista de seleção única"""
    cmd = [
        'whiptail', '--title', title,
        '--radiolist', prompt,
        str(height), str(width), str(list_height)
    ]
    
    for tag, item, selected in options:
        status = 'ON' if selected else 'OFF'
        cmd.extend([tag, item, status])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except subprocess.CalledProcessError:
        return None


def whiptail_checklist(
    title: str,
    prompt: str,
    options: List[Tuple[str, str, bool]],
    height: int = 20,
    width: int = 70,
    list_height: int = 10
) -> List[str]:
    """Exibe uma lista de seleção múltipla"""
    cmd = [
        'whiptail', '--title', title,
        '--checklist', prompt,
        str(height), str(width), str(list_height)
    ]
    
    for tag, item, selected in options:
        status = 'ON' if selected else 'OFF'
        cmd.extend([tag, item, status])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            # Parse result (items are quoted)
            selections = result.stdout.strip()
            return [s.strip('"') for s in selections.split() if s]
        return []
    except subprocess.CalledProcessError:
        return []


# =============================================================================
# MENUS E FUNCIONALIDADES
# =============================================================================

def menu_change_model() -> None:
    """Menu para trocar modelo ativo"""
    available = config.get_available_providers()
    
    if not available:
        whiptail_msgbox(
            "Nenhum Provedor",
            "Nenhum provedor possui API Key configurada.\n\n"
            "Configure uma chave primeiro usando a opção\n"
            "'Adicionar/Editar Chave API'.",
            12, 55
        )
        return
    
    # Criar lista de modelos disponíveis
    options = []
    current_model = config.get('ACTIVE_MODEL', '')
    
    for provider_id in available:
        provider = PROVIDERS[provider_id]
        for model in provider['models']:
            display = f"{provider['name']} - {model}"
            selected = (model == current_model)
            options.append((f"{provider_id}:{model}", display, selected))
    
    if not options:
        whiptail_msgbox("Erro", "Nenhum modelo disponível.", 10, 40)
        return
    
    selection = whiptail_radiolist(
        "Trocar Modelo Ativo",
        "Selecione o modelo que deseja usar como padrão:",
        options
    )
    
    if selection:
        provider, model = selection.split(':', 1)
        
        config.set('ACTIVE_PROVIDER', provider)
        config.set('ACTIVE_MODEL', model)
        config.save()
        
        provider_name = PROVIDERS[provider]['name']
        whiptail_msgbox(
            "Sucesso",
            f"Modelo alterado com sucesso!\n\n"
            f"Provedor: {provider_name}\n"
            f"Modelo:   {model}",
            12, 55
        )


def menu_edit_key() -> None:
    """Menu para adicionar/editar chaves API"""
    while True:
        options = []
        for provider_id, provider_info in PROVIDERS.items():
            has_key = config.is_provider_configured(provider_id)
            status = "✓ configurado" if has_key else "✗ não configurado"
            options.append((
                provider_id,
                f"{provider_info['name']} - {status}"
            ))
        
        options.append(("0", "← Voltar"))
        
        selection = whiptail_menu(
            "Adicionar/Editar Chave API",
            options,
            16, 65
        )
        
        if not selection or selection == "0":
            break
        
        provider = PROVIDERS[selection]
        current_key = config.get_api_key(selection) or ''
        
        # Preview da chave atual (primeiros caracteres)
        preview = current_key[:8] + '...' if len(current_key) > 8 else current_key
        
        new_key = whiptail_input(
            f"API Key - {provider['name']}",
            f"Digite a API Key para {provider['name']}:\n\n"
            f"{provider['description']}\n\n"
            f"(Cole a chave completa)",
            preview,
            password=True,
            height=14
        )
        
        if new_key is not None:
            # Se o usuário deixou vazio, manter a chave atual
            if new_key:
                config.set(provider['env_key'], new_key)
                config.save()
                
                whiptail_msgbox(
                    "Sucesso",
                    f"API Key atualizada com sucesso!\n\n"
                    f"Provedor: {provider['name']}",
                    10, 50
                )


def menu_disable_provider() -> None:
    """Menu para desabilitar provedor"""
    available = config.get_available_providers()
    
    if not available:
        whiptail_msgbox(
            "Nenhum Provedor",
            "Nenhum provedor está configurado.",
            10, 50
        )
        return
    
    options = [(p, PROVIDERS[p]['name']) for p in available]
    options.append(("0", "← Voltar"))
    
    selection = whiptail_menu(
        "Desabilitar Provedor",
        options,
        15, 60
    )
    
    if not selection or selection == "0":
        return
    
    provider_name = PROVIDERS[selection]['name']
    
    if whiptail_yesno(
        "Confirmar",
        f"Deseja realmente remover a API Key de {provider_name}?\n\n"
        f"Esta ação não pode ser desfeita.",
        12, 55
    ):
        config.set(PROVIDERS[selection]['env_key'], '')
        config.save()
        
        whiptail_msgbox(
            "Sucesso",
            f"API Key de {provider_name} removida.",
            10, 50
        )


def menu_view_status() -> None:
    """Menu para visualizar status do sistema"""
    active_provider = config.get('ACTIVE_PROVIDER', 'não definido')
    active_model = config.get('ACTIVE_MODEL', 'não definido')
    proxy_port = config.get('PROXY_PORT', '8323')
    
    provider_name = PROVIDERS.get(active_provider, {}).get('name', active_provider)
    
    # Verificar status das chaves
    key_status = []
    for provider_id, provider_info in PROVIDERS.items():
        has_key = config.is_provider_configured(provider_id)
        status = "✓ Configurado" if has_key else "✗ Não configurado"
        key_status.append(f"  {provider_info['name']}: {status}")
    
    status_msg = f"""
┌──────────────────────────────────────────────────┐
│       STATUS DO PROXY CLAUDE FREE                │
├──────────────────────────────────────────────────┤
│                                                  │
│  Provedor Ativo:  {active_provider:<30} │
│  Nome:            {provider_name:<30} │
│  Modelo Ativo:    {active_model:<30} │
│  Porta Proxy:     {proxy_port:<30} │
│                                                  │
├──────────────────────────────────────────────────┤
│  CHAVES API:                                     │
│                                                  │
{chr(10).join(key_status)}
│                                                  │
├──────────────────────────────────────────────────┤
│  ARQUIVO DE CONFIGURAÇÃO:                        │
│  {str(ENV_FILE):<46} │
│                                                  │
└──────────────────────────────────────────────────┘
"""
    
    whiptail_msgbox("Status do Sistema", status_msg, 22, 55)


def menu_test_connection() -> None:
    """Menu para testar conexão com provedor"""
    available = config.get_available_providers()
    
    if not available:
        whiptail_msgbox(
            "Nenhum Provedor",
            "Nenhum provedor possui API Key configurada.",
            10, 50
        )
        return
    
    options = [(p, PROVIDERS[p]['name']) for p in available]
    options.append(("0", "← Voltar"))
    
    selection = whiptail_menu(
        "Testar Conexão",
        options,
        15, 60
    )
    
    if not selection or selection == "0":
        return
    
    provider = PROVIDERS[selection]
    api_key = config.get_api_key(selection)
    
    whiptail_msgbox(
        "Testando...",
        f"Testando conexão com {provider['name']}...\n\nAguarde...",
        10, 50
    )
    
    result = test_provider_connection(selection, api_key)
    
    if result['success']:
        whiptail_msgbox(
            "Sucesso!",
            f"✓ Conexão bem sucedida!\n\n"
            f"Provedor: {provider['name']}\n"
            f"Modelos disponíveis: {result.get('model_count', 'N/A')}",
            12, 55
        )
    else:
        whiptail_msgbox(
            "Erro de Conexão",
            f"✗ Falha ao conectar:\n\n{result['error']}",
            12, 55
        )


def test_provider_connection(provider_id: str, api_key: str) -> Dict[str, Any]:
    """Testa conexão com o provedor via HTTP"""
    if provider_id not in PROVIDERS:
        return {"success": False, "error": "Provedor inválido"}
    
    provider = PROVIDERS[provider_id]
    url = f"{provider['base_url']}/models"
    
    try:
        request = urllib.request.Request(url)
        request.add_header('Authorization', f'Bearer {api_key}')
        request.add_header('Content-Type', 'application/json')
        
        # Headers adicionais para OpenRouter
        if provider_id == 'openrouter':
            request.add_header('HTTP-Referer', 'https://claude-free.local')
            request.add_header('X-Title', 'Claude Free Proxy')
        
        response = urllib.request.urlopen(request, timeout=15)
        data = json.loads(response.read().decode('utf-8'))
        
        model_count = len(data.get('data', []))
        
        return {
            "success": True,
            "message": "Conexão bem sucedida",
            "model_count": model_count
        }
    
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        return {
            "success": False,
            "error": f"HTTP {e.code}: {error_body[:200]}"
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"Erro de rede: {e.reason}"
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Resposta inválida do servidor"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def menu_advanced_settings() -> None:
    """Menu de configurações avançadas"""
    while True:
        options = [
            ("1", "Alterar Porta do Proxy"),
            ("2", "Configurar Master Key"),
            ("3", "Alterar Intervalo de Hot Reload"),
            ("0", "← Voltar")
        ]
        
        selection = whiptail_menu(
            "Configurações Avançadas",
            options,
            15, 55
        )
        
        if not selection or selection == "0":
            break
        
        elif selection == "1":
            current_port = config.get('PROXY_PORT', '8323')
            new_port = whiptail_input(
                "Porta do Proxy",
                "Digite a nova porta para o proxy:\n\n"
                "(Valor entre 1024 e 65535)",
                current_port
            )
            
            if new_port:
                try:
                    port = int(new_port)
                    if 1024 <= port <= 65535:
                        config.set('PROXY_PORT', str(port))
                        config.save()
                        whiptail_msgbox(
                            "Sucesso",
                            f"Porta alterada para {port}\n\n"
                            "Reinicie o proxy para aplicar.",
                            10, 45
                        )
                    else:
                        whiptail_msgbox(
                            "Erro",
                            "Porta deve estar entre 1024 e 65535",
                            10, 45
                        )
                except ValueError:
                    whiptail_msgbox("Erro", "Valor inválido", 10, 40)
        
        elif selection == "2":
            current_key = config.get('MASTER_KEY', '')
            preview = '••••••••' if current_key else ''
            
            new_key = whiptail_input(
                "Master Key",
                "Digite a nova Master Key para o painel admin:\n\n"
                "(Deixe vazio para remover proteção)",
                preview,
                password=True
            )
            
            if new_key is not None:
                config.set('MASTER_KEY', new_key)
                config.save()
                
                if new_key:
                    whiptail_msgbox(
                        "Sucesso",
                        "Master Key configurada.\n\n"
                        "O painel admin agora requer autenticação.",
                        10, 50
                    )
                else:
                    whiptail_msgbox(
                        "Sucesso",
                        "Master Key removida.\n\n"
                        "O painel admin está acessível sem autenticação.",
                        10, 50
                    )
        
        elif selection == "3":
            current_interval = config.get('CONFIG_RELOAD_INTERVAL', '10')
            new_interval = whiptail_input(
                "Intervalo de Hot Reload",
                "Digite o intervalo em segundos:\n\n"
                "(Determina a frequência de verificação\n"
                " de mudanças no arquivo .env)",
                current_interval
            )
            
            if new_interval:
                try:
                    interval = int(new_interval)
                    if 1 <= interval <= 300:
                        config.set('CONFIG_RELOAD_INTERVAL', str(interval))
                        config.save()
                        whiptail_msgbox(
                            "Sucesso",
                            f"Intervalo alterado para {interval} segundos",
                            10, 45
                        )
                    else:
                        whiptail_msgbox(
                            "Erro",
                            "Intervalo deve estar entre 1 e 300 segundos",
                            10, 50
                        )
                except ValueError:
                    whiptail_msgbox("Erro", "Valor inválido", 10, 40)


def menu_about() -> None:
    """Menu sobre o sistema"""
    about_msg = f"""
┌──────────────────────────────────────────────────┐
│        CLAUDE FREE - AMBIENTE AI GRATUITO        │
├──────────────────────────────────────────────────┤
│                                                  │
│  Versão: 1.0.0                                   │
│  Repositório: sistemabritto/setup-claude-free    │
│                                                  │
├──────────────────────────────────────────────────┤
│  PROVEDORES SUPORTADOS:                          │
│                                                  │
│  • Groq (Llama 3.1 70B/8B)                       │
│    - Inferência ultra-rápida                     │
│                                                  │
│  • NVIDIA NIM (Kimi K2)                          │
│    - Modelo de linguagem avançado                │
│                                                  │
│  • OpenRouter (DeepSeek V3 / Qwen Coder)         │
│    - Modelos de código e chat                    │
│                                                  │
├──────────────────────────────────────────────────┤
│  RECURSOS:                                       │
│                                                  │
│  • Proxy local com tradução de APIs              │
│  • Suporte a formatos OpenAI e Anthropic         │
│  • Hot reload de configuração                    │
│  • Painel web de administração                   │
│  • Gerenciamento via terminal                    │
│                                                  │
├──────────────────────────────────────────────────┤
│  COMANDOS DISPONÍVEIS:                           │
│                                                  │
│  cc-config  → Este menu de configuração          │
│  cc-start   → Iniciar o proxy                    │
│  cc-status  → Verificar status do proxy          │
│                                                  │
└──────────────────────────────────────────────────┘
"""
    whiptail_msgbox("Sobre", about_msg, 28, 55)


# =============================================================================
# MENU PRINCIPAL
# =============================================================================

def main_menu() -> None:
    """Menu principal do gerenciador de configuração"""
    while True:
        # Contar provedores configurados
        configured = len(config.get_available_providers())
        
        options = [
            ("1", "🔄 Trocar Modelo Ativo"),
            ("2", "🔑 Adicionar/Editar Chave API"),
            ("3", "❌ Desabilitar Provedor"),
            ("4", "📊 Ver Status"),
            ("5", "🧪 Testar Conexão"),
            ("6", "⚙️  Configurações Avançadas"),
            ("7", "ℹ️  Sobre"),
            ("0", "🚪 Sair")
        ]
        
        selection = whiptail_menu(
            f"Claude Free - Gerenciador ({configured}/3 provedores)",
            options,
            18, 55
        )
        
        if not selection or selection == "0":
            break
        
        elif selection == "1":
            menu_change_model()
        elif selection == "2":
            menu_edit_key()
        elif selection == "3":
            menu_disable_provider()
        elif selection == "4":
            menu_view_status()
        elif selection == "5":
            menu_test_connection()
        elif selection == "6":
            menu_advanced_settings()
        elif selection == "7":
            menu_about()


# =============================================================================
# ENTRY POINT
# =============================================================================

def main() -> None:
    """Função principal"""
    print("\n🤖 Claude Free - Gerenciador de Configuração\n")
    
    # Verificar se whiptail está instalado
    if not check_whiptail():
        print("✗ Erro: whiptail não está instalado.")
        print("\nInstale com um dos comandos:")
        print("  Ubuntu/Debian: sudo apt install whiptail")
        print("  Fedora: sudo dnf install newt")
        print("  Arch: sudo pacman -S libnewt")
        sys.exit(1)
    
    # Verificar se o diretório de configuração existe
    if not INSTALL_DIR.exists():
        print(f"Criando diretório de configuração: {INSTALL_DIR}")
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Carregar configuração
    config.load()
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
    
    print("\nAté mais! 🤖\n")


if __name__ == '__main__':
    main()
