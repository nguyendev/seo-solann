#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SolannEco SEO Kit — 1-Click Force Index CLI (part of seo-solann)
Submits un-indexed URLs to the Solann 1-Click Force Indexing engine (Sinbyte/1hPing)
via the SolannEco API (POST /api/v1/force-index).
Deducts 120 RankCredits per URL from your Solann Cloud account with auto-refund on failure.
Zero external dependencies (uses standard library urllib.request).
"""

import argparse
import datetime
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
        # User home directory
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

    if raw_env_key.startswith("${") and raw_env_key.endswith("}"):
        raw_env_key = ""

    config = {
        "base_url": os.environ.get("SOLANN_BASE_URL", "https://api.solann.io/api/v1"),
        "api_key": raw_env_key,
        "default_country": "vn",
        "default_language": "vi"
    }

    if config_path:
        try:
            with open(config_path, "r", encoding="utf-8-sig") as f:
                file_config = json.load(f)
                file_key = file_config.get("api_key", "").strip()
                config.update(file_config)
                if raw_env_key:
                    config["api_key"] = raw_env_key
                elif file_key and file_key != "YOUR_API_KEY_HERE" and file_key != "YOUR_SOLANN_API_KEY_HERE":
                    config["api_key"] = file_key
        except Exception as e:
            sys.stderr.write(f"[WARNING] Could not parse config at {config_path}: {e}\n")

    return config


def submit_force_index(config, urls, project_name=None, dry_run=False):
    base_url = config.get("base_url", "https://api.solann.io/api/v1").rstrip("/")
    endpoint = f"{base_url}/force-index"
    api_key = config.get("api_key", "").strip()

    credit_per_url = 120
    total_urls = len(urls)
    total_credit_required = total_urls * credit_per_url

    if dry_run:
        print(json.dumps({
            "mode": "DRY_RUN",
            "totalUrls": total_urls,
            "creditPerUrl": credit_per_url,
            "totalCreditRequired": total_credit_required,
            "urls": urls,
            "endpoint": endpoint
        }, ensure_ascii=False, indent=2))
        return

    if not api_key or api_key in ("YOUR_API_KEY_HERE", "YOUR_SOLANN_API_KEY_HERE"):
        print(json.dumps({
            "error": "MISSING_API_KEY",
            "message": "Chưa cấu hình API Key. Đăng ký tài khoản tại https://solanneco.com hoặc https://app.solann.io để nhận gói Cloud và nạp credits.",
            "guide": "Điền key vào file config/solann-api.json hoặc thiết lập biến môi trường SOLANN_API_KEY."
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    payload = {
        "urls": urls,
        "projectName": project_name or f"AI Force Index {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "tool": "sinbyte"
    }

    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"))
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", api_key)

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return data
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            parsed_err = json.loads(err_body)
        except Exception:
            parsed_err = {"raw": err_body}

        hint = "Vui lòng kiểm tra lại yêu cầu."
        if e.code == 401:
            hint = "API Key không hợp lệ. Vui lòng kiểm tra lại SOLANN_API_KEY."
        elif e.code == 402:
            hint = f"Số dư không đủ. Cần {total_credit_required} credit cho {total_urls} URLs. Vui lòng nạp thêm credit trên trang quản trị Solann."
        elif e.code == 403:
            hint = "Tài khoản của bạn chưa có gói thuê bao Cloud (Trial 7 ngày hoặc Pro 12 tháng) còn hạn. Vui lòng kích hoạt gói trên web để mở khóa tính năng ép index."
        elif e.code == 502:
            hint = "Nhà cung cấp dịch vụ indexing đang bận hoặc gặp lỗi tạm thời. Toàn bộ credits đã được tự động hoàn lại cho tài khoản của bạn."

        print(json.dumps({
            "error": "FORCE_INDEX_FAILED",
            "statusCode": e.code,
            "details": parsed_err,
            "hint": hint
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": "NETWORK_ERROR",
            "message": str(e)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Solann 1-Click Force Index CLI (seo-solann)")
    parser.add_argument("--urls", type=str, help="Comma-separated URLs to force index", default=None)
    parser.add_argument("--file", type=str, help="Path to text file containing URLs (one per line)", default=None)
    parser.add_argument("--project-name", type=str, help="Name for the indexing batch", default=None)
    parser.add_argument("--api-key", type=str, help="Solann API Key", default=None)
    parser.add_argument("--base-url", type=str, help="Custom Solann API base URL", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Calculate required credits without sending request")

    args = parser.parse_args()

    urls = []
    if args.urls:
        urls.extend([u.strip() for u in args.urls.split(",") if u.strip()])
    if args.file:
        if os.path.exists(args.file):
            with open(args.file, "r", encoding="utf-8") as f:
                for line in f:
                    u = line.strip()
                    if u and not u.startswith("#"):
                        urls.append(u)
        else:
            print(json.dumps({"error": f"File not found: {args.file}"}, ensure_ascii=False))
            sys.exit(1)

    if not urls:
        print(json.dumps({
            "error": "NO_URLS",
            "message": "Vui lòng cung cấp ít nhất 1 URL qua --urls hoặc --file."
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    seen = set()
    deduped_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            deduped_urls.append(u)
    urls = deduped_urls

    config = load_config()
    if args.api_key:
        config["api_key"] = args.api_key.strip()
    if args.base_url:
        config["base_url"] = args.base_url.strip()

    submit_force_index(config, urls, project_name=args.project_name, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
