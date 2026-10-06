#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SolannEco SEO Kit — Anti-Tool-Bloat Local MCP Stdio Server
Enables Claude Desktop / Cursor / Antigravity to connect to SolannEco API
Zero external dependencies (uses standard library only).

Architecture Principle (Anti-Tool-Bloat):
Exposes only generic gateway tools to prevent context window saturation.
Heavy computational and bulk operations (e.g., checking hundreds of URLs via Serper,
Alphabet Soup scraping) are delegated to the 'seo-solann' Skill using Python scripts.
"""

import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

# Force UTF-8 encoding on stdin, stdout, stderr for Windows compatibility
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")

# Add current scripts directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "scripts"))

from keyword_volume import load_config as load_volume_config
from keyword_volume import resolve_config_path


def log_debug(msg):
    sys.stderr.write(f"[seo-solann-mcp] {msg}\n")
    sys.stderr.flush()


def make_api_request(endpoint_path, payload, config, method="POST"):
    base_url = config.get("base_url", "https://api.solann.io/api/v1").rstrip("/")
    endpoint = f"{base_url}/{endpoint_path.lstrip('/')}"
    api_key = config.get("api_key", "").strip()

    if not api_key or api_key in ("YOUR_API_KEY_HERE", "YOUR_SOLANN_API_KEY_HERE"):
        return {
            "error": "MISSING_API_KEY",
            "message": "Chưa cấu hình API Key. Đăng ký tài khoản tại https://solanneco.com hoặc https://app.solann.io để nhận 7 ngày dùng thử miễn phí.",
            "guide": "Vui lòng cập nhật file config/solann-api.json hoặc biến môi trường SOLANN_API_KEY."
        }

    if method.upper() == "GET" or payload is None:
        req = urllib.request.Request(endpoint, method="GET")
    else:
        req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), method=method.upper())
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
        if "Host not in allowlist" in error_body or "network egress" in error_body.lower():
            hint = "Môi trường sandbox của Claude đang chặn kết nối mạng tới api.solann.io. Vui lòng vào Claude Settings -> Capabilities -> Bật 'Allow network egress' và thêm 'api.solann.io' vào Domain allowlist."
        elif e.code in (401, 403):
            hint = "API Key không hợp lệ hoặc đã hết hạn dùng thử 7 ngày. Hãy gia hạn gói thuê bao năm tại https://solanneco.com."
        elif e.code == 402:
            hint = "Tài khoản đã hết Credits cho lượt gọi API này. Vui lòng nạp thêm Credits trên web SolannEco."

        return {
            "error": "API_REQUEST_FAILED",
            "status_code": e.code,
            "details": parsed,
            "hint": hint
        }
    except Exception as e:
        return {"error": "NETWORK_ERROR", "message": str(e)}


def get_tools_definition():
    """Returns concise, anti-tool-bloat tool definitions."""
    return [
        {
            "name": "solann_api_request",
            "description": "Cổng gửi yêu cầu chung đến mọi API của hệ sinh thái SolannEco (ví dụ: 'keyword-research', 'keyword-suggest', 'index-check-sessions', 'force-index'). Giúp AI linh hoạt kết nối dữ liệu mà không làm tràn context window với quá nhiều tool rời rạc. Với các tác vụ kiểm tra hàng loạt nặng (hàng trăm URLs qua Serper), hãy kích hoạt Skill 'seo-solann' để chạy script Python qua terminal.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "Tên endpoint API (ví dụ: 'keyword-research', 'keyword-suggest', 'index-check-sessions', 'force-index')"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE"],
                        "description": "Phương thức HTTP (mặc định 'POST')"
                    },
                    "payload": {
                        "type": "object",
                        "description": "Dữ liệu JSON gửi kèm trong body (đối với POST/PUT)"
                    },
                    "queryParams": {
                        "type": "object",
                        "description": "Các tham số query key-value nối vào URL"
                    }
                },
                "required": ["endpoint"]
            }
        },
        {
            "name": "solann_get_project_data",
            "description": "Truy vấn nhanh dữ liệu lưu trữ SEO trên Solann Cloud: Danh sách phiên kiểm tra Google Index, các URL chưa index (NotIndexed/Error) theo Dự án hoặc Tên miền để AI nắm bắt ngữ cảnh.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list_sessions", "get_unindexed_urls", "get_session_detail"],
                        "description": "Hành động: 'list_sessions' (liệt kê phiên), 'get_unindexed_urls' (lấy link chưa index), 'get_session_detail' (chi tiết 1 phiên)"
                    },
                    "projectId": {
                        "type": "string",
                        "description": "ID Guid của dự án SEO"
                    },
                    "targetDomain": {
                        "type": "string",
                        "description": "Tên miền mục tiêu (ví dụ: solannseo.com)"
                    },
                    "scope": {
                        "type": "integer",
                        "description": "Loại link: 0=Standalone, 1=Internal, 2=Backlink, 3=SocialEntity"
                    },
                    "sessionId": {
                        "type": "string",
                        "description": "ID Guid của phiên kiểm tra (khi action='get_session_detail' hoặc 'get_unindexed_urls')"
                    },
                    "take": {
                        "type": "integer",
                        "description": "Số lượng bản ghi tối đa (mặc định 20, tối đa 100)"
                    }
                },
                "required": ["action"]
            }
        }
    ]


def handle_tool_call(tool_name, arguments, config):
    if tool_name == "solann_api_request":
        endpoint = arguments.get("endpoint", "").strip().lstrip("/")
        if not endpoint:
            return {"error": "INVALID_ARGUMENT", "message": "endpoint là bắt buộc."}

        method = arguments.get("method", "POST").upper()
        payload = arguments.get("payload")
        query_params = arguments.get("queryParams")

        if query_params and isinstance(query_params, dict):
            query_str = urllib.parse.urlencode({k: v for k, v in query_params.items() if v is not None})
            if query_str:
                endpoint = f"{endpoint}?{query_str}"

        return make_api_request(endpoint, payload, config, method=method)

    elif tool_name == "solann_get_project_data":
        action = arguments.get("action", "list_sessions")

        if action == "list_sessions":
            params = []
            if arguments.get("projectId"):
                params.append(f"projectId={urllib.parse.quote(str(arguments['projectId']))}")
            if arguments.get("targetDomain"):
                params.append(f"targetDomain={urllib.parse.quote(str(arguments['targetDomain']))}")
            if arguments.get("scope") is not None:
                params.append(f"scope={arguments['scope']}")
            take = min(arguments.get("take", 20), 100)
            params.append(f"take={take}")
            query_str = "&".join(params)
            endpoint = f"index-check-sessions{('?' + query_str) if query_str else ''}"
            return make_api_request(endpoint, None, config, method="GET")

        elif action == "get_unindexed_urls":
            params = []
            if arguments.get("projectId"):
                params.append(f"projectId={urllib.parse.quote(str(arguments['projectId']))}")
            if arguments.get("targetDomain"):
                params.append(f"targetDomain={urllib.parse.quote(str(arguments['targetDomain']))}")
            if arguments.get("scope") is not None:
                params.append(f"scope={arguments['scope']}")
            if arguments.get("sessionId"):
                params.append(f"sessionId={urllib.parse.quote(str(arguments['sessionId']))}")
            query_str = "&".join(params)
            endpoint = f"index-check-sessions/unindexed-urls{('?' + query_str) if query_str else ''}"
            return make_api_request(endpoint, None, config, method="GET")

        elif action == "get_session_detail":
            sess_id = arguments.get("sessionId")
            if not sess_id:
                return {"error": "INVALID_ARGUMENT", "message": "sessionId là bắt buộc đối với action get_session_detail."}
            return make_api_request(f"index-check-sessions/{sess_id}", None, config, method="GET")

        else:
            return {"error": "INVALID_ACTION", "message": f"Hành động không hợp lệ: {action}"}

    # Backward compatibility fallbacks
    elif tool_name in ("google_keyword_research", "keyword_research"):
        return make_api_request("keyword-research", arguments, config, method="POST")

    elif tool_name in ("auto_suggest_and_fetch_volume", "keyword_suggest"):
        return make_api_request("keyword-suggest", arguments, config, method="POST")

    elif tool_name == "force_google_index":
        return make_api_request("force-index", arguments, config, method="POST")

    else:
        return {
            "error": "TOOL_NOT_FOUND",
            "message": f"Không tìm thấy tool: {tool_name}. Vui lòng sử dụng 'solann_api_request' hoặc kích hoạt Skill 'seo-solann' để chạy script Python qua terminal."
        }


def send_response(response_dict):
    msg = json.dumps(response_dict, ensure_ascii=False)
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def main():
    log_debug("Starting seo-solann Anti-Tool-Bloat MCP Stdio server...")
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

            msg_id = request.get("id")
            method = request.get("method")

            if method == "initialize":
                send_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "seo-solann",
                            "version": "2.0.0"
                        }
                    }
                })

            elif method == "tools/list":
                send_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"tools": get_tools_definition()}
                })

            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                result_data = handle_tool_call(tool_name, arguments, config)

                send_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_data, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                })

            elif method == "notifications/initialized":
                pass

            else:
                if msg_id is not None:
                    send_response({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    })

        except Exception as e:
            log_debug(f"Unhandled exception in MCP loop: {e}")


if __name__ == "__main__":
    main()
