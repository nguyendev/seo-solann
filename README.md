# SEO Solann — AI Keyword Intelligence Connector

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-success.svg)]()
[![Ecosystem: SolannEco](https://img.shields.io/badge/Ecosystem-SolannEco-orange.svg)](https://solanneco.com)

> **Gói kỹ năng mã nguồn mở chính thức kết nối hệ sinh thái SolannEco.** 
> Cung cấp dữ liệu từ khóa Google Ads chuẩn xác (Search Volume, Xu hướng 12 tháng, Topic Clusters, Cào đối thủ, Vét từ khóa đuôi dài Alphabet Soup) dành cho **Antigravity 2**, **Cursor IDE** và **Claude Desktop**.

---

## 🌟 Tính Năng Nổi Bật

- **Dữ Liệu Chuẩn Google Ads API**: Truy cập trực tiếp Google Ads Keyword Planner — không dùng số liệu ước lượng, không phụ thuộc bên thứ 3 chậm trễ.
- **Biểu Đồ Xu Hướng 12 Tháng (Seasonality)**: Phân tích tính mùa vụ, xác định tháng cao điểm và tháng thoái trào của thị trường.
- **Cào Từ Khóa Đối Thủ Theo URL**: Chỉ cần cung cấp URL landing page của đối thủ, hệ thống tự động trích xuất bộ từ khóa trọng tâm của họ.
- **Vét Từ Khóa Đuôi Dài (Alphabet Soup a→j)**: Kết hợp Google Autocomplete với Google Ads Volume Enrichment trong một lệnh duy nhất.
- **Zero Third-Party Dependency**: 100% Python Standard Library — không cần chạy `pip install requests` hay bất kỳ thư viện ngoài nào.
- **Tiết Kiệm Token Tối Đa**: Chạy theo kiến trúc Agent Skill & Local Stdio — không nhồi nhét tool schema vào context window của AI khi nhàn rỗi.

---

## 💎 Chính Sách Sử Dụng & Bản Quyền

- 🎁 **Dùng thử 7 ngày miễn phí (7-Day Free Trial)**: Tất cả tài khoản mới đăng ký tại [solanneco.com](https://solanneco.com) hoặc [app.solann.io](https://app.solann.io) đều được kích hoạt 7 ngày trải nghiệm toàn bộ tính năng lưu trữ dữ liệu và kết nối AI.
- 📅 **Gói Thuê Bao Năm (Yearly Subscription)**: Gói nền tảng kích hoạt **SolannEco API Key** (`sk-solanneco-...`) với mục đích cốt lõi là **Lưu trữ & Quản lý Dữ liệu SEO** trên hệ thống (quản lý backlink của domain, lưu trữ kết quả check index, lưu trữ & truy xuất lịch sử ranking từ khóa) và kết nối AI IDEs.
- 🪙 **Ví Credits Bổ Sung (Pay-as-you-go)**: Dành riêng cho các tính năng tiêu tốn tài nguyên bên thứ ba (như tra cứu Google Ads Keyword Planner khối lượng lớn vượt hạn ngạch).

> ⚠️ **Lưu ý quan trọng**: SolannEco API Key của `seo-solann` (dạng `sk-solanneco-...`, đăng ký tại `solanneco.com` hoặc `app.solann.io`) **hoàn toàn khác** với License Key của bộ công cụ CLI Antigravity SeoKit (dạng `SK-XXXX-XXXX-XXXX`, bán tại `antigravityseokit.solann.io`).

---

## ⚡ Cài Đặt Siêu Tốc (1-Click Install)

### Bước 1: Clone mã nguồn về máy
```bash
git clone https://github.com/nguyendev/seo-solann.git
cd seo-solann
```

### Bước 2: Chạy trình cài đặt tự động

#### 🔹 Trên Windows (PowerShell):
```powershell
.\install.ps1 -ApiKey "sk-solanneco-your-api-key-here"
```

#### 🔹 Trên macOS / Linux (Bash):
```bash
chmod +x install.sh
./install.sh "sk-solanneco-your-api-key-here"
```

---

## 🔑 Hướng Dẫn Cấu Hình `SOLANN_API_KEY`

Hệ thống hỗ trợ 3 cách cung cấp API Key linh hoạt (ưu tiên theo thứ tự từ trên xuống dưới):

1. **Biến môi trường (Khuyến nghị cho Claude Code & Server)**:
   - **Windows PowerShell**:
     ```powershell
     [System.Environment]::SetEnvironmentVariable('SOLANN_API_KEY', 'sk-solanneco-your-key', 'User')
     ```
   - **macOS / Linux**:
     ```bash
     echo 'export SOLANN_API_KEY="sk-solanneco-your-key"' >> ~/.bashrc && source ~/.bashrc
     ```
2. **File cấu hình `config/solann-api.json`**:
   - Chạy `install.ps1 -ApiKey "sk-solanneco-..."` hoặc sửa trực tiếp file `config/solann-api.json`:
     ```json
     {
       "api_key": "sk-solanneco-your-key",
       "base_url": "https://api.solann.io/api/v1",
       "default_location": "VN",
       "default_language": "vi"
     }
     ```
3. **Thư mục cấu hình toàn cục**: `~/.solann/config.json`.

---

## 🚀 Hướng Dẫn Tích Hợp Chi Tiết Từng Nền Tảng

### 1. Antigravity 2 (Đề xuất ⭐)
- Chạy script cài đặt:
  ```powershell
  .\install.ps1 -ApiKey "sk-solanneco-your-api-key"
  ```
- Trình cài đặt tự động nạp Skill vào `.agents/skills/seo-solann/` (hoặc thư mục toàn cục `~/.gemini/config/skills/seo-solann/`) và cập nhật API Key vào `config/solann-api.json`.
- AI sẽ tự động đọc `SKILL.md` và kích hoạt tra cứu mỗi khi bạn hỏi về SEO/Từ khóa.

### 2. Cursor IDE
- Chạy script `.\install.ps1 -ApiKey "sk-solanneco-..."` sẽ tự động tạo file rule tại `.cursor/rules/seo-solann.mdc` và lưu key vào `config/solann-api.json`.
- Khi bạn chat với Cursor Composer / Agent, chỉ cần gõ yêu cầu nghiên cứu từ khóa, Cursor Agent sẽ tự động chạy script Python để lấy dữ liệu.

### 3. Claude Desktop & Claude Code

#### 🔹 Cách A: Dùng Claude Plugin Marketplace (Mới nhất)
1. Trong Claude, chọn **Add marketplace** (hoặc gõ `/plugin marketplace add https://github.com/nguyendev/seo-solann`).
2. Dán URL: `https://github.com/nguyendev/seo-solann` và nhấn **Sync**.
3. **Cách nhập API Key**:
   - Thiết lập biến môi trường `SOLANN_API_KEY` (xem mục [🔑 Cấu Hình SOLANN_API_KEY](#-hướng-dẫn-cấu-hình-solann_api_key) ở trên).
   - Hoặc thêm vào file `~/.claude/settings.json`:
     ```json
     {
       "env": {
         "SOLANN_API_KEY": "sk-solanneco-your-api-key"
       }
     }
     ```
   - Hoặc điền vào file `config/solann-api.json` ngay trong thư mục repository.

#### 🔹 Cách B: Cài đặt Local MCP cho Claude Desktop (Truyền thống)
Chạy script cài đặt để tự động cấu hình:
```powershell
.\install.ps1 -ApiKey "sk-solanneco-your-api-key" -Target "Claude"
```
File `%APPDATA%\Claude\claude_desktop_config.json` (Windows) hoặc `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) sẽ được tự động cập nhật:
```json
{
  "mcpServers": {
    "seo-solann": {
      "command": "python",
      "args": [
        "C:/path/to/seo-solann/mcp_stdio.py"
      ],
      "env": {
        "SOLANN_API_KEY": "sk-solanneco-your-api-key"
      }
    }
  }
}
```
Khởi động lại Claude Desktop, bạn sẽ thấy biểu tượng 2 Tools sẵn sàng: `google_keyword_research` và `auto_suggest_and_fetch_volume`.

---

## 💬 Mẫu Câu Lệnh Trò Chuyện Với AI

Sau khi cài đặt, bạn chỉ cần trò chuyện tự nhiên với AI:

- *"Hãy nghiên cứu lượng tìm kiếm và CPC của các từ khóa: `máy rửa bát bosch`, `máy rửa bát gia đình`, `giá máy rửa bát`"*
- *"Đối thủ của tôi là `https://tiki.vn/dien-thoai-may-tinh-bang/c1789`, hãy phân tích xem họ đang tập trung vào bộ từ khóa nào."*
- *"Tôi đang muốn viết bài về `nồi chiên không dầu`, hãy mở rộng cho tôi 30 từ khóa đuôi dài kèm search volume để tôi lập dàn ý topic cluster."*
- *"Phân tích tính mùa vụ trong 12 tháng qua của từ khóa `vé máy bay tết`, tháng nào bắt đầu tăng đột biến?"*

---

## 📄 Bản Quyền & Giấy Phép

Phát hành theo giấy phép **MIT License**. Mã nguồn mở tự do sử dụng và đóng góp bởi cộng đồng SEOer & Lập trình viên Việt Nam.

Phát triển bởi đội ngũ **SolannEco** — Nền tảng SEO Automation & Backlink hàng đầu.
