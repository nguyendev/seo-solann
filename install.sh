#!/usr/bin/env bash
# ==============================================================================
# SolannEco SEO Kit — 1-Click Installer (macOS / Linux Bash)
# Hỗ trợ tự động thiết lập cho: Antigravity 2, Cursor IDE, Claude Desktop
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_KEY="${1:-}"

echo ""
echo "=========================================================="
echo "       SolannEco SEO Kit — Trình Cài Đặt Tự Động          "
echo "=========================================================="
echo ""

if [ -z "$API_KEY" ]; then
    echo "[?] Nhập SolannEco API Key của bạn (nhấn Enter nếu muốn cấu hình sau):"
    read -r -p "    API Key (sk-solanneco-...): " INPUT_KEY
    if [ -n "$INPUT_KEY" ]; then
        API_KEY="$INPUT_KEY"
    fi
fi

# 1. Tạo file config/solann-api.json
mkdir -p "$SCRIPT_DIR/config"
CONFIG_FILE="$SCRIPT_DIR/config/solann-api.json"
cat <<EOF > "$CONFIG_FILE"
{
  "api_key": "${API_KEY:-YOUR_API_KEY_HERE}",
  "base_url": "https://api.solann.io/api/v1",
  "default_location": "VN",
  "default_language": "vi"
}
EOF
echo "[OK] Đã tạo file cấu hình: $CONFIG_FILE"

# 2. Cài đặt vào Antigravity IDE
ANTIGRAVITY_DIR="$HOME/.gemini/config/skills/seo-solann"
if [ -d "$PWD/.agents" ]; then
    ANTIGRAVITY_DIR="$PWD/.agents/skills/seo-solann"
fi
mkdir -p "$ANTIGRAVITY_DIR"
cp -f "$SCRIPT_DIR/SKILL.md" "$ANTIGRAVITY_DIR/"
cp -rf "$SCRIPT_DIR/scripts" "$ANTIGRAVITY_DIR/"
cp -rf "$SCRIPT_DIR/config" "$ANTIGRAVITY_DIR/"
echo "[OK] Đã cài đặt Skill vào Antigravity IDE tại: $ANTIGRAVITY_DIR"

# 3. Cài đặt vào Cursor IDE (nếu có .cursor trong thư mục hiện tại)
if [ -d "$PWD/.cursor" ]; then
    mkdir -p "$PWD/.cursor/rules"
    cp -f "$SCRIPT_DIR/templates/cursor_rule.mdc" "$PWD/.cursor/rules/seo-solann.mdc"
    echo "[OK] Đã tạo Cursor Rule tại: $PWD/.cursor/rules/seo-solann.mdc"
fi

# 4. Cài đặt vào Claude Desktop (macOS)
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
if [ -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "[INFO] Đang cấu hình Claude Desktop..."
    MCP_PATH="$SCRIPT_DIR/mcp_stdio.py"
    # Create or update JSON using python
    python3 -c "
import json, os
cfg_path = '$CLAUDE_CONFIG_FILE'
data = {}
if os.path.exists(cfg_path):
    try:
        with open(cfg_path, 'r') as f: data = json.load(f)
    except: data = {}
if 'mcpServers' not in data: data['mcpServers'] = {}
data['mcpServers']['seo-solann'] = {
    'command': 'python3',
    'args': ['$MCP_PATH'],
    'env': {'SOLANN_API_KEY': '${API_KEY:-YOUR_API_KEY_HERE}'}
}
with open(cfg_path, 'w') as f: json.dump(data, f, indent=2)
"
    echo "[OK] Đã cập nhật cấu hình Claude Desktop: $CLAUDE_CONFIG_FILE"
fi

echo ""
echo "=========================================================="
echo "                Cài Đặt Hoàn Tất Thành Công!              "
echo "=========================================================="
if [ -z "$API_KEY" ]; then
    echo -e "\033[1;33mLưu ý: Đừng quên cập nhật API Key trong file config/solann-api.json\033[0m"
fi
echo "Đăng ký nhận 7 ngày dùng thử miễn phí tại https://solanneco.com hoặc https://app.solann.io"
echo ""
