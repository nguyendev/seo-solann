#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SolannEco SEO Kit — Google Index Checker CLI (part of seo-solann)
Checks Google index status for URLs via Serper Google Search (BYOK)
with URLCleaner parity matching SolannSerperWorker / Serper.js,
and optionally saves the session to Solann Cloud (POST /api/v1/index-check-sessions).
Zero external dependencies (uses standard library urllib.request).
"""

import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Force UTF-8 encoding on stdin, stdout, stderr for Windows compatibility
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


class URLCleaner:
    INDEX_FILES = ['/index.htm', '/index.html', '/index.php', '/default.aspx', '/default.htm']

    @staticmethod
    def strip_tracking_params(url: str) -> str:
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            if not parsed.query:
                return url
            qs = parse_qs(parsed.query, keep_blank_values=True)
            filtered_qs = {
                k: v for k, v in qs.items()
                if k.lower() != 'srsltid' and not k.lower().startswith('utm_') and k.lower() not in ('gclid', 'fbclid')
            }
            new_query = urlencode(filtered_qs, doseq=True)
            return urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
        except Exception:
            cleaned = re.sub(r'([?&])srsltid=[^&#]*(&?)', lambda m: '&' if m.group(1) == '&' and m.group(2) else ('?' if m.group(2) else ''), url)
            return cleaned.rstrip('?&')

    @staticmethod
    def clean_url(url: str, remove_protocol_and_query: bool = True) -> str:
        if not url:
            return ""
        url = url.strip()
        url = URLCleaner.strip_tracking_params(url)

        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            path = parsed.path.lower()

            for idx_file in URLCleaner.INDEX_FILES:
                if path.endswith(idx_file):
                    path = path[:-len(idx_file)]
                    break

            path = path.rstrip('/')

            if remove_protocol_and_query:
                return f"{netloc}{path}"

            scheme = parsed.scheme.lower() if parsed.scheme else "https"
            query_part = f"?{parsed.query}" if parsed.query else ""
            return f"{scheme}://{netloc}{path}{query_part}"
        except Exception:
            cleaned = re.sub(r'^https?://', '', url, flags=re.I)
            cleaned = cleaned.split('#')[0]
            if remove_protocol_and_query:
                cleaned = cleaned.split('?')[0]
            return cleaned.lower().rstrip('/')

    @staticmethod
    def is_url_match(original_url: str, result_url: str, ignore_slash_errors: bool = True) -> bool:
        if not original_url or not result_url:
            return False

        clean_orig = URLCleaner.clean_url(original_url)
        clean_res = URLCleaner.clean_url(result_url)

        if clean_orig == clean_res:
            return True

        norm_orig = clean_orig.replace("www.", "")
        norm_res = clean_res.replace("www.", "")

        if norm_orig == norm_res:
            return True

        if ignore_slash_errors:
            if norm_orig.rstrip('/') == norm_res.rstrip('/'):
                return True

        # Check subpath matching if both share netloc
        try:
            orig_parsed = urlparse(f"https://{norm_orig}")
            res_parsed = urlparse(f"https://{norm_res}")
            if orig_parsed.netloc == res_parsed.netloc:
                if orig_parsed.path.rstrip('/') == res_parsed.path.rstrip('/'):
                    return True
        except Exception:
            pass

        return False


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
    raw_solann_key = (
        os.environ.get("SOLANN_API_KEY")
        or os.environ.get("CLAUDE_PLUGIN_OPTION_SOLANN_API_KEY")
        or os.environ.get("CLAUDE_PLUGIN_OPTION_API_KEY")
        or ""
    ).strip()
    if raw_solann_key.startswith("${") and raw_solann_key.endswith("}"):
        raw_solann_key = ""

    raw_serper_key = (
        os.environ.get("SERPER_API_KEY")
        or ""
    ).strip()

    config = {
        "base_url": os.environ.get("SOLANN_BASE_URL", "https://api.solann.io/api/v1"),
        "api_key": raw_solann_key,
        "serper_api_key": raw_serper_key,
        "default_country": "vn",
        "default_language": "vi"
    }

    if config_path:
        try:
            with open(config_path, "r", encoding="utf-8-sig") as f:
                file_config = json.load(f)
                config.update(file_config)
                if raw_solann_key:
                    config["api_key"] = raw_solann_key
                if raw_serper_key:
                    config["serper_api_key"] = raw_serper_key
        except Exception as e:
            sys.stderr.write(f"[WARNING] Could not parse config at {config_path}: {e}\n")

    return config


def query_serper_api(query: str, serper_api_key: str, country: str = "vn") -> dict:
    endpoint = "https://google.serper.dev/search"
    payload = {
        "q": query,
        "gl": country,
        "num": 10
    }
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"))
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-KEY", serper_api_key)

    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check_url_via_serper(url: str, serper_api_key: str, country: str = "vn") -> dict:
    """
    Executes full index check pipeline matching SolannSerperWorker / Serper.js:
    1. Query site:<clean_url>
    2. If matched -> Indexed
    3. If not matched -> Query <clean_url> directly
    """
    url = url.strip()
    if not url:
        return None

    clean_url_query = URLCleaner.clean_url(url, remove_protocol_and_query=True)

    try:
        # Step 1: site:URL search
        query1 = f"site:{clean_url_query}"
        data1 = query_serper_api(query1, serper_api_key, country)
        organic1 = data1.get("organic", [])

        for item in organic1:
            link = item.get("link", "")
            if URLCleaner.is_url_match(url, link):
                return {
                    "url": url,
                    "status": 1,
                    "statusText": "Indexed",
                    "googleUrl": link,
                    "googleTitle": item.get("title"),
                    "snippet": item.get("snippet"),
                    "errorMessage": None
                }

        # Step 2: direct clean URL search if site: didn't match
        query2 = clean_url_query
        data2 = query_serper_api(query2, serper_api_key, country)
        organic2 = data2.get("organic", [])

        for item in organic2:
            link = item.get("link", "")
            if URLCleaner.is_url_match(url, link):
                return {
                    "url": url,
                    "status": 1,
                    "statusText": "Indexed",
                    "googleUrl": link,
                    "googleTitle": item.get("title"),
                    "snippet": item.get("snippet"),
                    "errorMessage": None
                }

        # If organic1 had results and first result is close
        if organic1:
            first = organic1[0]
            return {
                "url": url,
                "status": 1,
                "statusText": "Indexed",
                "googleUrl": first.get("link"),
                "googleTitle": first.get("title"),
                "snippet": first.get("snippet"),
                "errorMessage": None
            }

        return {
            "url": url,
            "status": 2,
            "statusText": "NotIndexed",
            "googleUrl": None,
            "googleTitle": None,
            "snippet": None,
            "errorMessage": None
        }
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        return {
            "url": url,
            "status": 3,
            "statusText": "Error",
            "googleUrl": None,
            "googleTitle": None,
            "snippet": None,
            "errorMessage": f"Serper HTTP {e.code}: {err_body}"
        }
    except Exception as e:
        return {
            "url": url,
            "status": 3,
            "statusText": "Error",
            "googleUrl": None,
            "googleTitle": None,
            "snippet": None,
            "errorMessage": str(e)
        }


def save_session_to_cloud(config, session_name, items, country="vn", language="vi", project_id=None, target_domain=None, scope=0, tags=None):
    base_url = config.get("base_url", "https://api.solann.io/api/v1").rstrip("/")
    endpoint = f"{base_url}/index-check-sessions"
    api_key = config.get("api_key", "").strip()

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return {
            "saved": False,
            "error": "MISSING_API_KEY",
            "message": "Không có SOLANN_API_KEY để lưu vào Cloud."
        }

    formatted_items = []
    for idx, it in enumerate(items, start=1):
        formatted_items.append({
            "orderNumber": idx,
            "url": it["url"],
            "status": it["status"],
            "googleUrl": it.get("googleUrl"),
            "googleTitle": it.get("googleTitle"),
            "snippet": it.get("snippet"),
            "errorMessage": it.get("errorMessage"),
            "checkedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })

    payload = {
        "sessionName": session_name,
        "engine": "SerperBYOK",
        "country": country,
        "language": language,
        "items": formatted_items,
        "projectId": project_id,
        "targetDomain": target_domain,
        "scope": scope,
        "tags": tags or []
    }

    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"))
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", api_key)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"saved": True, "data": data}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        return {"saved": False, "status_code": e.code, "error": err_body}
    except Exception as e:
        return {"saved": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Solann Google Index Checker CLI (seo-solann)")
    parser.add_argument("--urls", type=str, help="Comma-separated URLs to check (e.g. 'https://solanneco.com, https://app.solann.io')", default=None)
    parser.add_argument("--file", type=str, help="Path to text file containing URLs (one per line)", default=None)
    parser.add_argument("--serper-key", type=str, help="Serper.dev API Key (BYOK)", default=None)
    parser.add_argument("--country", type=str, help="Country code (default 'vn')", default=None)
    parser.add_argument("--save-session", action="store_true", help="Save results to Solann Cloud (requires Solann API Key)")
    parser.add_argument("--session-name", type=str, help="Custom name for saved Cloud session", default=None)
    parser.add_argument("--project-id", type=str, help="SEO Project ID (Guid) to associate with this session", default=None)
    parser.add_argument("--target-domain", type=str, help="Target domain (e.g. solannseo.com)", default=None)
    parser.add_argument("--scope", type=int, help="Scope: 0=Standalone, 1=Internal, 2=Backlink, 3=SocialEntity", default=0)
    parser.add_argument("--tags", type=str, help="Comma-separated tags (e.g. 'dot-1,pr-bao-chi')", default=None)
    parser.add_argument("--delay", type=float, help="Delay between checks in seconds (default 0.2)", default=0.2)

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
    serper_key = args.serper_key or config.get("serper_api_key", "").strip()
    country = args.country or config.get("default_country", "vn")

    if not serper_key or serper_key == "YOUR_SERPER_API_KEY_HERE":
        print(json.dumps({
            "error": "MISSING_SERPER_KEY",
            "message": "Chưa cấu hình Serper API Key (BYOK). Hãy tạo tài khoản miễn phí (2,500 queries) tại https://serper.dev.",
            "guide": "Truyền --serper-key <key>, set biến môi trường SERPER_API_KEY, hoặc lưu vào file config/solann-api.json."
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    results = []
    for idx, u in enumerate(urls, start=1):
        item_res = check_url_via_serper(u, serper_key, country=country)
        item_res["orderNumber"] = idx
        results.append(item_res)
        if idx < len(urls) and args.delay > 0:
            time.sleep(args.delay)

    total = len(results)
    indexed = [r for r in results if r["status"] == 1]
    not_indexed = [r for r in results if r["status"] == 2]
    errors = [r for r in results if r["status"] == 3]

    output = {
        "summary": {
            "total": total,
            "indexed": len(indexed),
            "notIndexed": len(not_indexed),
            "error": len(errors),
            "indexRatePercent": round((len(indexed) / total * 100), 1) if total > 0 else 0
        },
        "notIndexedUrls": [r["url"] for r in not_indexed],
        "results": results
    }

    if args.save_session or args.session_name:
        sess_name = args.session_name or f"Kiểm tra Index CLI {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} ({total} URLs)"
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        cloud_res = save_session_to_cloud(
            config,
            sess_name,
            results,
            country=country,
            project_id=args.project_id,
            target_domain=args.target_domain,
            scope=args.scope,
            tags=tags
        )
        output["cloudSync"] = cloud_res

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
