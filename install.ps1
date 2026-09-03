# ==============================================================================
# SolannEco SEO Kit - 1-Click Installer (Windows PowerShell)
# Ho tro tu dong thiet lap cho: Antigravity 2, Cursor IDE, Claude Desktop
# ==============================================================================

[CmdletBinding()]
param (
    [Parameter(Mandatory=$false)]
    [string]$ApiKey = "",

    [Parameter(Mandatory=$false)]
    [ValidateSet("Auto", "Antigravity", "Cursor", "Claude", "All")]
    [string]$Target = "Auto"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $ScriptDir) {
    $ScriptDir = (Get-Location).Path
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       SolannEco SEO Kit -- Trinh Cai Dat Tu Dong         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Kiem tra / Nhap API Key
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    Write-Host "[?] Nhap SolannEco API Key cua ban (hoac nhan Enter de cau hinh sau):" -ForegroundColor Yellow
    $InputKey = Read-Host "    API Key (sk-solanneco-...)"
    if (-not [string]::IsNullOrWhiteSpace($InputKey)) {
        $ApiKey = $InputKey.Trim()
    }
}

# 2. Tao file config/solann-api.json
$ConfigDir = Join-Path $ScriptDir "config"
if (-not (Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
}

$ConfigFile = Join-Path $ConfigDir "solann-api.json"
$EffectiveKey = if ($ApiKey) { $ApiKey } else { "YOUR_API_KEY_HERE" }

$ConfigData = @{
    api_key = $EffectiveKey
    base_url = "https://api.solann.io/api/v1"
    default_location = "VN"
    default_language = "vi"
}
$ConfigData | ConvertTo-Json -Depth 4 | Set-Content -Path $ConfigFile -Encoding UTF8
Write-Host "[OK] Da tao file cau hinh: $ConfigFile" -ForegroundColor Green

# 3. Thiet lap cho tung Client
$InstalledTargets = @()

# -- A. Antigravity IDE (Global hoac Local Workspace)
$AntigravityGlobal = Join-Path $HOME ".gemini\config\skills\seo-solann"
$AntigravityLocal = Join-Path (Get-Location) ".agents\skills\seo-solann"

if ($Target -in @("Auto", "Antigravity", "All")) {
    $TargetAntigravity = if (Test-Path (Join-Path (Get-Location) ".agents")) { $AntigravityLocal } else { $AntigravityGlobal }
    
    if (-not (Test-Path $TargetAntigravity)) {
        New-Item -ItemType Directory -Path $TargetAntigravity -Force | Out-Null
    }
    
    Copy-Item -Path (Join-Path $ScriptDir "SKILL.md") -Destination $TargetAntigravity -Force
    Copy-Item -Path (Join-Path $ScriptDir "scripts") -Destination $TargetAntigravity -Recurse -Force
    Copy-Item -Path (Join-Path $ScriptDir "config") -Destination $TargetAntigravity -Recurse -Force
    if (Test-Path (Join-Path $ScriptDir "mcp_stdio.py")) {
        Copy-Item -Path (Join-Path $ScriptDir "mcp_stdio.py") -Destination $TargetAntigravity -Force
    }
    
    Write-Host "[OK] Da cai dat Skill vao Antigravity IDE tai: $TargetAntigravity" -ForegroundColor Green
    $InstalledTargets += "Antigravity IDE (Skill)"
}

# -- B. Cursor IDE
if ($Target -in @("Auto", "Cursor", "All")) {
    $CursorRulesDir = Join-Path (Get-Location) ".cursor\rules"
    if ((Test-Path (Join-Path (Get-Location) ".cursor")) -or ($Target -eq "Cursor")) {
        if (-not (Test-Path $CursorRulesDir)) {
            New-Item -ItemType Directory -Path $CursorRulesDir -Force | Out-Null
        }
        $CursorRuleSrc = Join-Path $ScriptDir "templates\cursor_rule.mdc"
        $CursorRuleDst = Join-Path $CursorRulesDir "seo-solann.mdc"
        Copy-Item -Path $CursorRuleSrc -Destination $CursorRuleDst -Force
        Write-Host "[OK] Da tao Cursor Rule tai: $CursorRuleDst" -ForegroundColor Green
        $InstalledTargets += "Cursor IDE"
    }
}

# -- C. Claude Desktop
if ($Target -in @("Auto", "Claude", "All")) {
    $ClaudeConfigPath = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
    $ClaudeConfigDir = Split-Path -Parent $ClaudeConfigPath

    if ((Test-Path $ClaudeConfigDir) -or ($Target -in @("Claude", "All"))) {
        if (-not (Test-Path $ClaudeConfigDir)) {
            New-Item -ItemType Directory -Path $ClaudeConfigDir -Force | Out-Null
        }

        $McpScriptPath = (Join-Path $ScriptDir "mcp_stdio.py").Replace("\", "/")
        $ClaudeKey = if ($ApiKey) { $ApiKey } else { "YOUR_API_KEY_HERE" }

        python -c @"
import json, os
cfg_path = r'$ClaudeConfigPath'
data = {}
if os.path.exists(cfg_path):
    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}
if not isinstance(data, dict):
    data = {}
if 'mcpServers' not in data or not isinstance(data['mcpServers'], dict):
    data['mcpServers'] = {}

data['mcpServers']['seo-solann'] = {
    'command': 'python',
    'args': [r'$McpScriptPath'],
    'env': {
        'SOLANN_API_KEY': '$ClaudeKey'
    }
}
os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
with open(cfg_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
"@
        Write-Host "[OK] Da cap nhat cau hinh Claude Desktop tai: $ClaudeConfigPath" -ForegroundColor Green
        $InstalledTargets += "Claude Desktop"
    }
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "                Cai Dat Hoan Tat Thanh Cong!              " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Da ho tro: $($InstalledTargets -join ', ')" -ForegroundColor White
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    Write-Host "Luu y: Dung quen cap nhat API Key trong file config/solann-api.json" -ForegroundColor Yellow
    Write-Host "Dang ky nhan 7 ngay dung thu mien phi tai https://solanneco.com" -ForegroundColor Yellow
}
Write-Host ""
