#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SolannEco SEO Kit — Keyword Suggest & Long-tail Expansion
Connects to SolannEco API (Autocomplete Alphabet Soup + Volume Enrichment)
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
        os.path.join(script_dir, "..", "config", "solann-api.json"),
        os.path.join(os.getcwd(), "config", "solann-api.json"),
        os.path.join(os.getcwd(), ".agent", "config", "solann-api.json"),
        os.path.join(os.getcwd(), ".agents", "config", "solann-api.json"),
        os.path.expanduser("~/.solann/config.json"),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def load_config():
    config_path = resolve_config_path()
    config = {
        "base_url": os.environ.get("SOLANN_BASE_URL", "https://api.solann.io/api/v1"),
        "api_key": os.environ.get("SOLANN_API_KEY", ""),
        "default_location": "VN",
        "default_language": "vi"
    }

    if config_path:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            sys.stderr.write(f"[WARNING] Could not parse config at {config_path}: {e}\n")

    return config

def fetch_keyword_suggestions(config, seed_keyword, location=None, language=None, max_suggestions=50, alphabet_soup=True):
    base_url = config.get("base_url", "https://api.solann.io/api/v1").rstrip("/")
    endpoint = f"{base_url}/keyword-suggest"
    api_key = config.get("api_key", "").strip()

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print(json.dumps({
            "error": "MISSING_API_KEY",
            "message": "Chưa cấu hình API Key. Đăng ký tài khoản tại https://antigravityseokit.solann.io hoặc https://solanneco.com để nhận 7 ngày dùng thử miễn phí.",
            "guide": "Điền key vào file config/solann-api.json hoặc thiết lập biến môi trường SOLANN_API_KEY."
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    payload = {
        "seedKeyword": seed_keyword,
        "locationId": location or config.get("default_location", "VN"),
        "languageId": language or config.get("default_language", "vi"),
        "maxSuggestions": min(max_suggestions, 100),
        "alphabetSoup": alphabet_soup
    }

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
            hint = "API Key không hợp lệ hoặc đã hết hạn dùng thử 7 ngày. Hãy gia hạn gói thuê bao năm tại https://antigravityseokit.solann.io."
        elif e.code == 402:
            hint = "Tài khoản đã hết Credits cho lượt mở rộng từ khóa này. Vui lòng nạp thêm Credits trên web SolannEco."

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
    parser = argparse.ArgumentParser(description="SolannEco Keyword Suggest & Expansion CLI")
    parser.add_argument("--seed", type=str, required=True, help="Seed keyword to expand (e.g. 'may loc nuoc')")
    parser.add_argument("--location", type=str, help="Location ID or name (default 'VN')", default=None)
    parser.add_argument("--language", type=str, help="Language code or name (default 'vi')", default=None)
    parser.add_argument("--max", type=int, help="Max suggestions (1-100, default 50)", default=50)
    parser.add_argument("--no-alphabet-soup", action="store_true", help="Disable Alphabet Soup expansion")

    args = parser.parse_args()

    cfg = load_config()
    fetch_keyword_suggestions(
        cfg,
        seed_keyword=args.seed,
        location=args.location,
        language=args.language,
        max_suggestions=args.max,
        alphabet_soup=not args.no_alphabet_soup
    )
