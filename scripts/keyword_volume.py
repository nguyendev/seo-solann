#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SolannEco SEO Kit — Keyword Volume & Competitor Research
Connects to SolannEco API (Google Ads Keyword Planner + Topic Clusters)
Zero external dependencies (uses standard library urllib.request).
"""

import argparse
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

def resolve_config_path():
    """Locate solann-api.json from common locations."""
    if os.environ.get("SOLANN_CONFIG") and os.path.exists(os.environ["SOLANN_CONFIG"]):
        return os.environ["SOLANN_CONFIG"]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        # Relative to script: ../config/solann-api.json
        os.path.join(script_dir, "..", "config", "solann-api.json"),
        # Current working directory
        os.path.join(os.getcwd(), "config", "solann-api.json"),
        os.path.join(os.getcwd(), ".agent", "config", "solann-api.json"),
        os.path.join(os.getcwd(), ".agents", "config", "solann-api.json"),
        # User home directory for global setups
        os.path.expanduser("~/.solann/config.json"),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def load_config():
    config_path = resolve_config_path()
    raw_env_key = (
        os.environ.get("SOLANN_API_KEY")
        or os.environ.get("CLAUDE_PLUGIN_OPTION_SOLANN_API_KEY")
        or os.environ.get("CLAUDE_PLUGIN_OPTION_API_KEY")
        or ""
    ).strip()

    # Ignore literal unexpanded template placeholders
    if raw_env_key.startswith("${") and raw_env_key.endswith("}"):
        raw_env_key = ""

    config = {
        "base_url": os.environ.get("SOLANN_BASE_URL", "https://api.solann.io/api/v1"),
        "api_key": raw_env_key,
        "default_location": "VN",
        "default_language": "vi"
    }

    if config_path:
        try:
            with open(config_path, "r", encoding="utf-8-sig") as f:
                file_config = json.load(f)
                file_key = file_config.get("api_key", "").strip()
                config.update(file_config)
                # Keep env key if valid, else keep file key
                if raw_env_key:
                    config["api_key"] = raw_env_key
                elif file_key and file_key != "YOUR_API_KEY_HERE":
                    config["api_key"] = file_key
        except Exception as e:
            sys.stderr.write(f"[WARNING] Could not parse config at {config_path}: {e}\n")

    return config

def fetch_keyword_data(config, url=None, keywords=None, location=None, language=None):
    base_url = config.get("base_url", "https://api.solann.io/api/v1").rstrip("/")
    endpoint = f"{base_url}/keyword-research"
    api_key = config.get("api_key", "").strip()

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print(json.dumps({
            "error": "MISSING_API_KEY",
            "message": "Chưa cấu hình API Key. Đăng ký tài khoản tại https://solanneco.com hoặc https://app.solann.io để nhận 7 ngày dùng thử miễn phí.",
            "guide": "Điền key vào file config/solann-api.json hoặc thiết lập biến môi trường SOLANN_API_KEY."
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    payload = {}
    if url:
        payload["targetUrl"] = url
    if keywords:
        if isinstance(keywords, list):
            payload["keywords"] = keywords
        else:
            payload["keywords"] = [k.strip() for k in keywords.split(",") if k.strip()]

    payload["locationId"] = location or config.get("default_location", "VN")
    payload["languageId"] = language or config.get("default_language", "vi")

    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"))
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", api_key)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return result
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        try:
            parsed_err = json.loads(error_msg)
        except Exception:
            parsed_err = {"raw": error_msg}

        hint = "Vui lòng kiểm tra lại yêu cầu."
        if e.code in (401, 403):
            hint = "API Key không hợp lệ hoặc đã hết hạn dùng thử 7 ngày. Hãy gia hạn gói thuê bao năm tại https://solanneco.com."
        elif e.code == 402:
            hint = "Tài khoản của bạn đã hết Credits cho lượt tra cứu Google Ads này. Vui lòng nạp thêm Credits trên web SolannEco."

        print(json.dumps({
            "error": "API_REQUEST_FAILED",
            "status_code": e.code,
            "details": parsed_err,
            "hint": hint
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": "NETWORK_ERROR", "message": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SolannEco Keyword Volume & Research CLI")
    parser.add_argument("--url", type=str, help="Competitor URL to extract keywords from", default=None)
    parser.add_argument("--keywords", type=str, help="Comma-separated keywords (e.g. 'iphone 16, dien thoai samsung')", default=None)
    parser.add_argument("--location", type=str, help="Location ID or name (default 'VN')", default=None)
    parser.add_argument("--language", type=str, help="Language code or name (default 'vi')", default=None)

    args = parser.parse_args()

    if not args.url and not args.keywords:
        print(json.dumps({
            "error": "INVALID_ARGUMENTS",
            "message": "Phải cung cấp ít nhất --keywords hoặc --url."
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    cfg = load_config()
    fetch_keyword_data(cfg, url=args.url, keywords=args.keywords, location=args.location, language=args.language)
