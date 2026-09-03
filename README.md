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

- 🎁 **Dùng thử 7 ngày miễn phí (7-Day Free Trial)**: Tất cả tài khoản mới đăng ký tại [antigravityseokit.solann.io](https://antigravityseokit.solann.io) hoặc [solanneco.com](https://solanneco.com) đều được kích hoạt 7 ngày trải nghiệm không giới hạn tính năng cơ bản.
- 📅 **Gói Thuê Bao Năm (Yearly Subscription)**: Duy trì kết nối ổn định 24/7 với hệ sinh thái SolannEco API / MCP cho doanh nghiệp và chuyên gia SEO.
- 🪙 **Hệ Thống Credits Linh Hoạt**: Riêng một số tính năng tra cứu chuyên sâu tiêu tốn tài nguyên lớn (như batch volume quy mô lớn, cào đối thủ sâu) sẽ được tính theo số dư Credits của tài khoản.

---

## ⚡ Cài Đặt Siêu Tốc (1-Click Install)

### Bước 1: Clone mã nguồn về máy
```bash
git clone https://github.com/solann-eco/seo-solann.git
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

## 🚀 Hướng Dẫn Tích Hợp Chi Tiết Từng Nền Tảng

### 1. Antigravity 2 (Đề xuất ⭐)
- Chạy script `install.ps1` (hoặc copy cả thư mục này vào `.agents/skills/seo-solann` trong dự án hoặc thư mục toàn cục `~/.gemini/config/skills/seo-solann`).
- Đảm bảo file `config/solann-api.json` đã có API Key của bạn.
- AI sẽ tự động đọc `SKILL.md` và kích hoạt tra cứu mỗi khi bạn hỏi về SEO/Từ khóa.

### 2. Cursor IDE
- Chạy script `install.ps1` sẽ tự động tạo file rule tại `.cursor/rules/seo-solann.mdc`.
- Khi bạn chat với Cursor Composer / Agent, chỉ cần gõ yêu cầu nghiên cứu từ khóa, Cursor Agent sẽ tự động chạy script Python để lấy dữ liệu.

### 3. Claude Desktop
Script cài đặt sẽ tự động cập nhật file `claude_desktop_config.json` của bạn:
```json
{
  "mcpServers": {
    "seo-solann": {
      "command": "python",
      "args": [
        "C:/path/to/seo-solann/mcp_stdio.py"
      ],
      "env": {
        "SOLANN_API_KEY": "sk-solanneco-..."
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
