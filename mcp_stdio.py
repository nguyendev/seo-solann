#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SolannEco SEO Kit — Lightweight Local MCP Stdio Server
Enables Claude Desktop (or any stdio MCP client) to connect to SolannEco API
Zero external dependencies (uses standard library only).
"""

import json
import os
import sys
import urllib.request
import urllib.error

# Force UTF-8 encoding on stdin, stdout, stderr for Windows compatibility
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")

# Add current scripts directory to path to reuse functions if needed
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "scripts"))

from keyword_volume import load_config as load_volume_config
from keyword_volume import resolve_config_path

def log_debug(msg):
    sys.stderr.write(f"[seo-solann-mcp] {msg}\n")
    sys.stderr.flush()

def make_api_request(endpoint_path, payload, config):
    base_url = config.get("base_url", "https://api.solann.io/api/v1").rstrip("/")
    endpoint = f"{base_url}/{endpoint_path.lstrip('/')}"
    api_key = config.get("api_key", "").strip()

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return {
            "error": "MISSING_API_KEY",
            "message": "Chưa cấu hình API Key. Đăng ký tài khoản tại https://solanneco.com hoặc https://app.solann.io để nhận 7 ngày dùng thử miễn phí.",
            "guide": "Vui lòng cập nhật file config/solann-api.json hoặc biến môi trường SOLANN_API_KEY."
        }

    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"))
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", api_key)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(error_body)
        except Exception:
            parsed = {"raw": error_body}

        hint = "Vui lòng kiểm tra lại yêu cầu."
        if e.code in (401, 403):
            hint = "API Key không hợp lệ hoặc đã hết hạn dùng thử 7 ngày. Hãy gia hạn gói thuê bao năm tại https://solanneco.com."
        elif e.code == 402:
            hint = "Tài khoản đã hết Credits cho lượt tra cứu Google Ads này. Vui lòng nạp thêm Credits trên web SolannEco."

        return {
            "error": "API_REQUEST_FAILED",
            "status_code": e.code,
            "details": parsed,
            "hint": hint
        }
    except Exception as e:
        return {"error": "NETWORK_ERROR", "message": str(e)}

def get_tools_definition():
    return [
        {
            "name": "google_keyword_research",
            "description": "Tra cứu lượng tìm kiếm chuẩn Google Ads (Search Volume), biểu đồ xu hướng 12 tháng (Trends), CPC và phân cụm chủ đề (Topic Clusters) từ danh sách từ khóa hoặc cào từ website đối thủ.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Danh sách các từ khóa cần tra cứu (ví dụ: ['mua nhà', 'bán đất'])"
                    },
                    "targetUrl": {
                        "type": "string",
                        "description": "URL website đối thủ để hệ thống tự động cào và trích xuất bộ từ khóa của họ"
                    },
                    "location": {
                        "type": "string",
                        "description": "Mã hoặc tên quốc gia (mặc định: 'VN', hỗ trợ 'vietnam', 'US',...)"
                    },
                    "language": {
                        "type": "string",
                        "description": "Mã hoặc tên ngôn ngữ (mặc định: 'vi', hỗ trợ 'tiếng việt', 'en',...)"
                    }
                }
            }
        },
        {
            "name": "auto_suggest_and_fetch_volume",
            "description": "Mở rộng từ khóa hạt giống thành hàng chục từ khóa đuôi dài (Google Autocomplete Alphabet Soup a-j) và tự động làm giàu số liệu Search Volume, CPC từ Google Ads.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "seedKeyword": {
                        "type": "string",
                        "description": "Từ khóa hạt giống cần mở rộng (ví dụ: 'máy lọc nước')"
                    },
                    "location": {
                        "type": "string",
                        "description": "Mã hoặc tên quốc gia (mặc định 'VN')"
                    },
                    "language": {
                        "type": "string",
                        "description": "Mã hoặc tên ngôn ngữ (mặc định 'vi')"
                    },
                    "maxSuggestions": {
                        "type": "integer",
                        "description": "Số lượng từ khóa tối đa cần lấy (1-100, mặc định 50)"
                    },
                    "alphabetSoup": {
                        "type": "boolean",
                        "description": "Có chạy chiến thuật vét bảng chữ cái a-j hay không (mặc định true)"
                    }
                },
                "required": ["seedKeyword"]
            }
        }
    ]

def handle_tool_call(tool_name, arguments, config):
    if tool_name == "google_keyword_research":
        payload = {}
        if "targetUrl" in arguments and arguments["targetUrl"]:
            payload["targetUrl"] = arguments["targetUrl"]
        if "keywords" in arguments and arguments["keywords"]:
            payload["keywords"] = arguments["keywords"]

        payload["locationId"] = arguments.get("location") or config.get("default_location", "VN")
        payload["languageId"] = arguments.get("language") or config.get("default_language", "vi")

        return make_api_request("keyword-research", payload, config)

    elif tool_name == "auto_suggest_and_fetch_volume":
        seed = arguments.get("seedKeyword")
        if not seed:
            return {"error": "INVALID_ARGUMENT", "message": "seedKeyword là bắt buộc."}

        payload = {
            "seedKeyword": seed,
            "locationId": arguments.get("location") or config.get("default_location", "VN"),
            "languageId": arguments.get("language") or config.get("default_language", "vi"),
            "maxSuggestions": min(arguments.get("maxSuggestions", 50), 100),
            "alphabetSoup": arguments.get("alphabetSoup", True)
        }
        return make_api_request("keyword-suggest", payload, config)

    else:
        return {"error": "TOOL_NOT_FOUND", "message": f"Không tìm thấy tool: {tool_name}"}

def send_response(response_dict):
    msg = json.dumps(response_dict, ensure_ascii=False)
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

def main():
    log_debug("Starting seo-solann MCP Stdio server...")
    config = load_volume_config()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue

            req_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            if method == "initialize":
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "seo-solann",
                            "version": "1.0.0"
                        }
                    }
                })

            elif method == "notifications/initialized":
                # Client initialized confirmation — no response needed for notifications
                pass

            elif method == "ping":
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {}
                })

            elif method == "tools/list":
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": get_tools_definition()
                    }
                })

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result_data = handle_tool_call(tool_name, arguments, config)

                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_data, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                })

            else:
                if req_id is not None:
                    send_response({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    })

        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            log_debug(f"Unhandled loop error: {e}")

if __name__ == "__main__":
    main()
