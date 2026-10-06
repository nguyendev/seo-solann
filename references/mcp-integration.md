# Hướng Dẫn Tích Hợp MCP Stdio Server (Anti-Tool-Bloat Architecture)

Tài liệu hướng dẫn kết nối máy chủ MCP chuẩn Stdio (`mcp_stdio.py`) dành cho Claude Desktop, Cursor IDE và Antigravity AI.

---

## 1. Triết Lý Thiết Kế: Chống Tràn Tool (Anti-Tool-Bloat)

Trong các hệ thống AI Agents hiện đại, việc khai báo quá nhiều tool con chi tiết (như tool loop từng URL, tool quét volume, tool vét alphabet soup) sẽ làm **tràn context window** và gây suy giảm chất lượng suy luận của mô hình:
- Mỗi tool schema ngốn từ 300 - 800 tokens ở **mỗi lượt prompt**.
- Quá nhiều tool khiến LLM dễ bị nhầm lẫn và chọn sai công cụ.

### Phân Định Trách Nhiệm Chuẩn:
1. **MCP Server (`mcp_stdio.py`)**: Chỉ cung cấp **các Tool Chung (Generic Gateway Tools)**:
   - `solann_api_request`: Cổng gửi yêu cầu chung đến mọi endpoint của SolannEco API (`keyword-research`, `index-check-sessions`, `force-index`).
   - `solann_get_project_data`: Cổng truy vấn dữ liệu dự án, phiên kiểm tra và danh sách URL chưa index trên Cloud.
2. **Skill `seo-solann`**: Chịu trách nhiệm thực thi các tác vụ nặng, lặp lại hoặc xử lý file lớn:
   - AI sử dụng `run_command` để chạy các script độc lập trong `scripts/` (`keyword_volume.py`, `keyword_suggest.py`, `check_index.py`, `force_index.py`).
   - Script chạy trực tiếp trong OS: đa luồng, nhanh hơn 10x, không lo bị timeout và không làm rác context window của AI.

---

## 2. Cấu Hình Tích Hợp Claude Desktop

Mở file cấu hình Claude Desktop:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Thêm cấu hình máy chủ MCP:
```json
{
  "mcpServers": {
    "seo-solann": {
      "command": "python",
      "args": [
        "h:/solanneco/SolannEco/src/seo-solann/mcp_stdio.py"
      ],
      "env": {
        "SOLANN_API_KEY": "sk-solanneco-your-api-key-here"
      }
    }
  }
}
```

---

## 3. Cấu Hình Tích Hợp Cursor IDE

Tạo hoặc cập nhật file `.cursor/rules/seo-solann.mdc` trong thư mục gốc của dự án:
```markdown
---
description: Hướng dẫn gọi Solann Keyword Intelligence và Check Index
globs: *
---
Mỗi khi người dùng yêu cầu nghiên cứu từ khóa, kiểm tra index hoặc ép index:
- Sử dụng các script Python tại `src/seo-solann/scripts/` thông qua terminal.
- Đọc tài liệu chi tiết tại `src/seo-solann/references/`.
```

---

## 4. Kiểm Thử Trực Tiếp MCP Stdio Server

Bạn có thể chạy kiểm tra máy chủ Stdio trực tiếp trên terminal:
```bash
python mcp_stdio.py
```
Gửi yêu cầu JSON-RPC mẫu:
```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
```
Máy chủ sẽ phản hồi danh sách các tool chung hợp nhất với mã hóa UTF-8 chuẩn.
