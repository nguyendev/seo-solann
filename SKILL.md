---
name: seo-solann
description: Tra cứu dữ liệu từ khóa Google Ads chính xác (Search volume, 12-month trends, topic clusters, competitor keywords, long-tail expansion). Kết nối qua SolannEco API.
when_to_use: "Khi người dùng yêu cầu nghiên cứu từ khóa, kiểm tra lượng tìm kiếm (search volume), phân tích tính mùa vụ, phân tích từ khóa đối thủ qua URL, hoặc mở rộng bộ từ khóa đuôi dài (long-tail keywords)."
allowed-tools: run_command
---

# SEO Solann — Keyword Intelligence & Research

Kỹ năng này kết nối trực tiếp với dịch vụ dữ liệu SEO cao cấp của **SolannEco**, cung cấp số liệu tìm kiếm chuẩn xác trực tiếp từ **Google Ads Keyword Planner API** và **Google Autocomplete**.

---

## 🎯 Khi Nào Kích Hoạt Kỹ Năng Này?

Kích hoạt kỹ năng này khi người dùng có các nhu cầu:
1. **Nghiên cứu từ khóa (Keyword Research)**: Tìm kiếm lượng volume, CPC, độ cạnh tranh của một hoặc nhiều từ khóa.
2. **Phân tích đối thủ (Competitor Keyword Discovery)**: Người dùng cung cấp URL website của đối thủ và muốn biết đối thủ đang nhắm vào những từ khóa nào.
3. **Mở rộng từ khóa đuôi dài (Long-Tail Expansion)**: Muốn mở rộng từ một từ khóa hạt giống (seed keyword) ra hàng chục góc nhìn ngách thông qua kỹ thuật Alphabet Soup.
4. **Phân tích tính mùa vụ (Seasonality Analysis)**: Cần xem biểu đồ biến động tìm kiếm trong 12 tháng qua để lên lịch đăng bài đón đầu xu hướng.
5. **Gom cụm chủ đề (Topic Clustering)**: Phân nhóm từ khóa theo ngữ nghĩa tự nhiên.

---

## 🛠️ Bộ Công Cụ Scripts

Kỹ năng cung cấp 2 script CLI viết bằng Python thuần (không cần cài thêm thư viện):

### 1. `scripts/keyword_volume.py` — Tra Cứu Volume & Cào Đối Thủ
Sử dụng khi đã có danh sách từ khóa hoặc có URL đối thủ.

```bash
# Tra cứu volume cho danh sách từ khóa (cách nhau bởi dấu phẩy)
python scripts/keyword_volume.py --keywords "mua nhà hà nội, bán đất đông anh" --location "VN" --language "vi"

# Cào bộ từ khóa từ website đối thủ
python scripts/keyword_volume.py --url "https://tiki.vn" --location "VN" --language "vi"

# Kết hợp cả hai (Hybrid Seed)
python scripts/keyword_volume.py --url "https://shopee.vn" --keywords "tai nghe bluetooth"
```

**Tham số:**
- `--keywords`: Danh sách từ khóa (ngăn cách bằng dấu phẩy).
- `--url`: URL website/landing page đối thủ.
- `--location`: Mã hoặc tên quốc gia (mặc định: `VN`, hỗ trợ `vietnam`, `US`, `japan`,...).
- `--language`: Mã ngôn ngữ (mặc định: `vi`, hỗ trợ `en`, `tiếng việt`,...).

---

### 2. `scripts/keyword_suggest.py` — Mở Rộng Từ Khóa Đuôi Dài (Alphabet Soup)
Sử dụng khi người dùng đưa ra 1 từ khóa chung chung (short-tail) và cần tìm tất cả các biến thể tìm kiếm thực tế của người dùng.

```bash
# Mở rộng từ khóa gốc với chiến thuật Alphabet Soup (a→j) và tự động enrich Volume
python scripts/keyword_suggest.py --seed "máy lọc nước" --max 30

# Tắt Alphabet Soup (chỉ lấy autocomplete cơ bản)
python scripts/keyword_suggest.py --seed "máy lọc nước" --no-alphabet-soup
```

**Tham số:**
- `--seed`: Từ khóa hạt giống bắt buộc.
- `--max`: Số lượng từ khóa tối đa cần lấy (1 - 100, mặc định: 50).
- `--no-alphabet-soup`: Tắt mở rộng a→j nếu chỉ cần gợi ý cơ bản.

---

## 📊 Hướng Dẫn Trình Bày Dữ Liệu Cho Người Dùng

Khi nhận được dữ liệu JSON trả về từ script, hãy luôn format câu trả lời chuyên nghiệp theo cấu trúc:

### 1. Bảng Tổng Hợp Từ Khóa (Sắp xếp theo Search Volume giảm dần)
| Từ khóa | Volume/tháng | Cạnh tranh (0-100) | CPC ước tính (VNĐ) | Phân cụm chủ đề |
|---|---|---|---|---|
| `{keyword}` | `{avgMonthlySearches}` | `{competition}` (`{competitionIndex}`) | `{lowTopOfPageBidMicros/10^6}` - `{highTopOfPageBidMicros/10^6}` | `{topicClusters}` |

### 2. Nhận Xét Xu Hướng & Tính Mùa Vụ (Seasonality Insights)
- Dựa vào trường `monthlySearchVolumes` (mảng 12 tháng), hãy chỉ ra:
  - Tháng có lượng tìm kiếm đạt đỉnh (Peak Month).
  - Tháng có lượng tìm kiếm chạm đáy (Low Season).
  - Xu hướng chung đang tăng trưởng (Trending Up) hay bão hòa/suy giảm.

### 3. Đề Xuất Chiến Lược Nội Dung (Actionable Advice)
- **Top Cơ Hội (Quick Wins)**: Những từ khóa có Volume khá, mức cạnh tranh `LOW` hoặc `competitionIndex < 30`.
- **Phân nhóm Search Intent**: Phân loại rõ từ khóa nào là **Thông tin (Informational)** dùng viết bài blog, từ khóa nào là **Thương mại/Giao dịch (Commercial/Transactional)** dùng làm trang bán hàng/landing page.

---

## ⚠️ Xử Lý Sự Cố (Troubleshooting)

- **Lỗi `MISSING_API_KEY`**: Nhắc người dùng tạo file `config/solann-api.json` hoặc set biến `SOLANN_API_KEY`. Cung cấp link đăng ký nhận **7 ngày dùng thử miễn phí** tại `https://antigravityseokit.solann.io` hoặc `https://solanneco.com`.
- **Lỗi 401/403 (Hết hạn)**: Nhắc người dùng gia hạn gói năm hoặc nâng cấp gói bản quyền.
- **Lỗi 402 (Hết Credits)**: Thông báo tài khoản đã dùng hết credits cho lượt gọi Google Ads và hướng dẫn nạp thêm credits trên web.
