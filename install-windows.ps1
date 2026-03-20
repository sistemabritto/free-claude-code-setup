<#
.SYNOPSIS
    Instalador Windows - Setup Claude Free
.DESCRIPTION
    Baixe e execute este script para instalar o Claude Free
.EXAMPLE
    irm https://raw.githubusercontent.com/sistemabritto/free-claude-code-setup/main/install-windows.ps1 | iex
#>

# Configurações
$InstallDir = "$env:USERPROFILE\.claude-free"
$RepoUrl = "https://github.com/sistemabritto/free-claude-code-setup"

# Cores
function Write-Info { Write-Host "  " -NoNewline; Write-Host "[INFO] " -f Cyan -NoNewline; Write-Host $args }
function Write-OK { Write-Host "  " -NoNewline; Write-Host "[OK] " -f Green -NoNewline; Write-Host $args }
function Write-Warn { Write-Host "  " -NoNewline; Write-Host "[AVISO] " -f Yellow -NoNewline; Write-Host $args }
function Write-Erro { Write-Host "  " -NoNewline; Write-Host "[ERRO] " -f Red -NoNewline; Write-Host $args }

# Banner
Clear-Host
Write-Host ""
Write-Host "  ═════════════════════════════════════════════════════════" -f Cyan
Write-Host "  🤖 Setup Claude Free - Windows" -f Cyan
Write-Host "  ═════════════════════════════════════════════════════════" -f Cyan
Write-Host ""

# Verificar Python
Write-Info "Verificando Python..."
$python = Get-Command python -EA SilentlyContinue
if (-not $python) {
    Write-Warn "Python não encontrado"
    Write-Info "Instalando Python via winget..."
    winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}
Write-OK "Python OK"

# Criar diretórios
Write-Info "Criando diretórios..."
@(
    $InstallDir
    "$InstallDir\config"
    "$InstallDir\logs"
    "$InstallDir\proxy"
) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}
Write-OK "Diretórios criados"

# Baixar arquivos
Write-Info "Baixando arquivos..."
$files = @(
    "proxy_core.py"
    "config_manager.py"
    "models_config.py"
    "requirements.txt"
)

$baseUrl = "https://raw.githubusercontent.com/sistemabritto/free-claude-code-setup/main"

foreach ($file in $files) {
    $url = "$baseUrl/$file"
    $dest = "$InstallDir\proxy\$file"
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
    } catch {
        Write-Erro "Falha ao baixar: $file"
    }
}
Write-OK "Arquivos baixados"

# Criar .env
$envFile = "$InstallDir\config\.env"
if (-not (Test-Path $envFile)) {
    Write-Info "Criando configuração..."
    @"
# Setup Claude Free - Windows
ACTIVE_PROVIDER=groq
ACTIVE_MODEL=llama-4-scout-17b-16e

GROQ_API_KEY=
OPENROUTER_API_KEY=
NVIDIA_API_KEY=
ZAI_API_KEY=

PROXY_PORT=8323
MASTER_KEY=
"@ | Out-File -FilePath $envFile -Encoding UTF8
    Write-OK "Config criado"
}

# Instalar deps Python
Write-Info "Instalando dependências..."
pip install flask requests python-dotenv --quiet 2>$null
Write-OK "Dependências OK"

# Criar script de início
$startBat = @"
@echo off
title Claude Free Proxy
cd /d "$InstallDir"
python proxy\proxy_core.py
pause
"@
$startBat | Out-File -FilePath "$InstallDir\start.bat" -Encoding ASCII

# Criar atalho
$WshShell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcut = $WshShell.CreateShortcut("$desktop\Claude Free.lnk")
$shortcut.TargetPath = "$InstallDir\start.bat"
$shortcut.WorkingDirectory = $InstallDir
$shortcut.Description = "Claude Free Proxy"
$shortcut.Save()

Write-OK "Atalho criado na área de trabalho"

# Resumo
Write-Host ""
Write-Host "  ═════════════════════════════════════════════════════════" -f Green
Write-Host "  ✅ INSTALAÇÃO CONCLUÍDA!" -f Green
Write-Host "  ═════════════════════════════════════════════════════════" -f Green
Write-Host ""
Write-Host "  📁 Diretório: $InstallDir"
Write-Host "  ⚙️  Config:    $InstallDir\config\.env"
Write-Host ""
Write-Host "  Para iniciar:"
Write-Host "    • Clique no atalho 'Claude Free' na área de trabalho"
Write-Host "    • Ou execute: $InstallDir\start.bat"
Write-Host ""
Write-Host "  Painel: http://localhost:8323/admin"
Write-Host ""
Write-Host "  ═════════════════════════════════════════════════════════" -f Green
Write-Host ""

# Abrir config
Write-Host "  Deseja abrir o arquivo de configuração agora? (S/N): " -NoNewline
$open = Read-Host
if ($open -eq 'S' -or $open -eq 's') {
    notepad "$InstallDir\config\.env"
}

Write-Host ""
Write-Host "  Adicione suas API Keys ao arquivo .env"
Write-Host "  Depois execute start.bat para iniciar o proxy"
Write-Host ""
