# ==============================================================================
# SolannEco SEO Kit — 1-Click Installer (Windows PowerShell)
# Hỗ trợ tự động thiết lập cho: Antigravity 2, Cursor IDE, Claude Desktop
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
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       SolannEco SEO Kit — Trình Cài Đặt Tự Động          " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Kiểm tra / Nhập API Key
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    Write-Host "[?] Nhập SolannEco API Key của bạn (nhấn Enter nếu muốn cấu hình sau):" -ForegroundColor Yellow
    $InputKey = Read-Host "    API Key (sk-solanneco-...)"
    if (-not [string]::IsNullOrWhiteSpace($InputKey)) {
        $ApiKey = $InputKey.Trim()
    }
}

# 2. Tạo file config/solann-api.json
$ConfigDir = Join-Path $ScriptDir "config"
if (-not (Test-Path $ConfigDir)) {
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
}

$ConfigFile = Join-Path $ConfigDir "solann-api.json"
$ConfigData = @{
    api_key = if ($ApiKey) { $ApiKey } else { "YOUR_API_KEY_HERE" }
    base_url = "https://api.solann.io/api/v1"
    default_location = "VN"
    default_language = "vi"
}

$ConfigData | ConvertTo-Json -Depth 4 | Set-Content -Path $ConfigFile -Encoding UTF8
Write-Host "[OK] Đã tạo file cấu hình: $ConfigFile" -ForegroundColor Green

# 3. Thiết lập cho từng Client
$InstalledTargets = @()

# ── A. Antigravity IDE (Global hoặc Local Workspace)
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
    
    Write-Host "[OK] Đã cài đặt Skill vào Antigravity IDE tại: $TargetAntigravity" -ForegroundColor Green
    $InstalledTargets += "Antigravity IDE"
}

# ── B. Cursor IDE
if ($Target -in @("Auto", "Cursor", "All")) {
    $CursorRulesDir = Join-Path (Get-Location) ".cursor\rules"
    if (Test-Path (Join-Path (Get-Location) ".cursor") -or $Target -eq "Cursor") {
        if (-not (Test-Path $CursorRulesDir)) {
            New-Item -ItemType Directory -Path $CursorRulesDir -Force | Out-Null
        }
        $CursorRuleSrc = Join-Path $ScriptDir "templates\cursor_rule.mdc"
        $CursorRuleDst = Join-Path $CursorRulesDir "seo-solann.mdc"
        Copy-Item -Path $CursorRuleSrc -Destination $CursorRuleDst -Force
        Write-Host "[OK] Đã tạo Cursor Rule tại: $CursorRuleDst" -ForegroundColor Green
        $InstalledTargets += "Cursor IDE"
    }
}

# ── C. Claude Desktop
if ($Target -in @("Auto", "Claude", "All")) {
    $ClaudeConfigPath = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
    $ClaudeConfigDir = Split-Path -Parent $ClaudeConfigPath

    if (Test-Path $ClaudeConfigDir -or $Target -in @("Claude", "All")) {
        if (-not (Test-Path $ClaudeConfigDir)) {
            New-Item -ItemType Directory -Path $ClaudeConfigDir -Force | Out-Null
        }

        $McpScriptPath = (Join-Path $ScriptDir "mcp_stdio.py").Replace("\", "/")
        
        $CurrentJson = @{}
        if (Test-Path $ClaudeConfigPath) {
            try {
                $CurrentJson = Get-Content -Path $ClaudeConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
            } catch {
                $CurrentJson = @{}
            }
        }

        if (-not $CurrentJson.ContainsKey("mcpServers")) {
            $CurrentJson["mcpServers"] = @{}
        }

        $CurrentJson["mcpServers"]["seo-solann"] = @{
            command = "python"
            args = @($McpScriptPath)
            env = @{
                SOLANN_API_KEY = if ($ApiKey) { $ApiKey } else { "YOUR_API_KEY_HERE" }
            }
        }

        $CurrentJson | ConvertTo-Json -Depth 6 | Set-Content -Path $ClaudeConfigPath -Encoding UTF8
        Write-Host "[OK] Đã cập nhật cấu hình Claude Desktop tại: $ClaudeConfigPath" -ForegroundColor Green
        $InstalledTargets += "Claude Desktop"
    }
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "                Cài Đặt Hoàn Tất Thành Công!              " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Đã hỗ trợ: $($InstalledTargets -join ', ')" -ForegroundColor White
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    Write-Host "Lưu ý: Đừng quên cập nhật API Key trong file config/solann-api.json" -ForegroundColor Yellow
    Write-Host "Đăng ký nhận 7 ngày dùng thử miễn phí tại https://antigravityseokit.solann.io" -ForegroundColor Yellow
}
Write-Host ""
