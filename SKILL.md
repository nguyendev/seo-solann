---
name: seo-solann
description: >-
  In-house SolannEco SEO data provider and automation engine. Queries Google Ads search volume,
  12-month trends, topic clusters, competitor keywords, and long-tail autocomplete expansions,
  performs bulk Google index verification (Serper BYOK) with Cloud sync, and triggers 1-Click
  Force Indexing. Use this skill when the user asks for keyword research, search volume, competitor
  keyword discovery, long-tail expansion, bulk Google index check, or force indexing.
---

# SEO Solann — Keyword Intelligence & Index Management

Cổng dữ liệu SEO độc quyền của **SolannEco**, cung cấp dữ liệu Google Ads chuẩn xác trực tiếp từ Keyword Planner API, kiểm tra Google Index hàng loạt kèm cơ chế lưu trữ Cloud, và kích hoạt Ép Index 1-Click.

> **Nguyên tắc Kiến trúc:** Mọi xử lý thuật toán, cào dữ liệu, đối soát URL và gọi API được đóng gói hoàn toàn trong các tệp Python độc lập tại thư mục `scripts/`. Tài liệu chuyên sâu được phân tách tại `references/` theo cơ chế Progressive Disclosure để tối ưu hóa context window.

---

## 🛠️ Bộ Công Cụ Scripts Thực Thi (`scripts/`)

Các script viết bằng **100% Python Standard Library** (Zero Dependencies, không cần `pip install`), chạy trực tiếp qua `run_command`:

| Script | Nghiệp Vụ Cốt Lõi | Lệnh Thực Thi Mẫu |
|---|---|---|
| [`keyword_volume.py`](./scripts/keyword_volume.py) | Tra cứu Volume, CPC, Trend 12 tháng, Cào từ khóa đối thủ | `python scripts/keyword_volume.py --keywords "từ khóa" --location "VN"` |
| [`keyword_suggest.py`](./scripts/keyword_suggest.py) | Vét từ khóa đuôi dài Alphabet Soup (a→j) + Enrich Volume | `python scripts/keyword_suggest.py --seed "từ khóa gốc" --max 50` |
| [`check_index.py`](./scripts/check_index.py) | Quét Google Index hàng loạt (Serper BYOK) & Lưu Cloud | `python scripts/check_index.py --file links.txt --save-session --scope 1` |
| [`force_index.py`](./scripts/force_index.py) | Kích hoạt Ép Index 1-Click (120 credit/URL, tự hoàn tiền) | `python scripts/force_index.py --urls "url1,url2" --dry-run` |

---

## 📖 Tài Liệu Tham Chiếu Chuyên Sâu (`references/`)

Đọc các tài liệu tham chiếu chi tiết khi thực hiện quy trình nghiệp vụ tương ứng:

1. **[Nghiên Cứu Từ Khóa & Cào Đối Thủ](./references/keyword-research.md)**: Hướng dẫn chi tiết về cấu trúc dữ liệu trả về, cào URL landing page đối thủ và kỹ thuật vét Alphabet Soup.
2. **[Kiểm Tra Google Index & Lưu Trữ Đám Mây](./references/index-management.md)**: Thuật toán đối soát URLCleaner 5 tầng, phân loại Scope (`Internal`, `Backlink`, `Social`, `Standalone`), gắn Dự án và Tags.
3. **[Ép Index 1-Click & Quản Lý Credit](./references/force-indexing.md)**: Quy trình 4 bước khép kín từ kiểm tra index đến ép index, chính sách trừ điểm và cơ chế Auto-Refund khi lỗi đối tác.
4. **[Tích Hợp Máy Chủ MCP Stdio](./references/mcp-integration.md)**: Hướng dẫn kết nối `mcp_stdio.py` cho Claude Desktop, Cursor IDE theo triết lý Anti-Tool-Bloat.

---

## ⚙️ Cấu Hình Nhanh

Cấu hình API Key tại `config/solann-api.json` hoặc biến môi trường `SOLANN_API_KEY`:

```json
{
  "api_key": "sk-solanneco-your-key-here",
  "base_url": "https://api.solann.io/api/v1",
  "default_location": "VN",
  "default_language": "vi",
  "serper_api_key": "your-serper-key-here"
}
```

*Nếu thiếu API Key*: Báo người dùng đăng ký nhận 7 ngày dùng thử miễn phí tại [solanneco.com](https://solanneco.com) hoặc [app.solann.io](https://app.solann.io).
