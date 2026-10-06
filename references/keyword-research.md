# Hướng Dẫn Nghiên Cứu Từ Khóa (Keyword Intelligence)

Tài liệu chi tiết về quy trình tra cứu dữ liệu từ khóa Google Ads chuẩn xác qua `scripts/keyword_volume.py` và `scripts/keyword_suggest.py`.

---

## 1. Tra Cứu Volume & Phân Tích Đối Thủ (`scripts/keyword_volume.py`)

Script kết nối trực tiếp với Google Ads Keyword Planner API thông qua SolannEco Backend (`POST /api/v1/keyword-research`).

### Lệnh thực thi:
```bash
# 1. Tra cứu danh sách từ khóa cụ thể
python scripts/keyword_volume.py --keywords "mua nhà hà nội, bán đất đông anh" --location "VN" --language "vi"

# 2. Cào toàn bộ bộ từ khóa trọng tâm của website đối thủ
python scripts/keyword_volume.py --url "https://tiki.vn" --location "VN" --language "vi"

# 3. Kết hợp cả từ khóa gốc và URL đối thủ (Hybrid Seed)
python scripts/keyword_volume.py --url "https://shopee.vn" --keywords "tai nghe bluetooth"
```

### Các cờ tham số:
- `--keywords`: Danh sách từ khóa phân cách bằng dấu phẩy.
- `--url`: URL trang đích của đối thủ để tự động cào và trích xuất từ khóa.
- `--location`: Quốc gia tìm kiếm (mặc định: `VN`, hỗ trợ `vietnam`, `US`, `UK`,...).
- `--language`: Ngôn ngữ tìm kiếm (mặc định: `vi`, hỗ trợ `tiếng việt`, `en`,...).
- `--api-key`: Solann API Key (nếu không dùng file `config/solann-api.json`).

### Dữ liệu trả về (JSON Standard):
- `avgMonthlySearches`: Lượng tìm kiếm trung bình hàng tháng.
- `competition`: Mức độ cạnh tranh quảng cáo (`LOW`, `MEDIUM`, `HIGH`).
- `competitionIndex`: Điểm số cạnh tranh từ `0` đến `100`.
- `lowTopOfPageBidMicros` / `highTopOfPageBidMicros`: Giá thầu CPC tối thiểu và tối đa (chia $1,000,000$ ra số tiền gốc).
- `monthlySearchVolumes`: Mảng 12 tháng gần nhất (phục vụ biểu đồ tính mùa vụ - Seasonality).
- `topicClusters`: Phân nhóm chủ đề ngữ nghĩa tự động.

---

## 2. Vét Từ Khóa Đuôi Dài Alphabet Soup (`scripts/keyword_suggest.py`)

Script thực hiện kỹ thuật Alphabet Soup (nối từ khóa hạt giống với các ký tự `a` $\rightarrow$ `j`) qua Google Autocomplete, sau đó tự động gửi danh sách sang Solann API để enrich đầy đủ số liệu Search Volume và CPC.

### Lệnh thực thi:
```bash
# Mở rộng từ khóa gốc với Alphabet Soup và enrich metrics tự động
python scripts/keyword_suggest.py --seed "máy lọc nước" --max 30

# Chỉ lấy gợi ý autocomplete cơ bản (không quét Alphabet Soup)
python scripts/keyword_suggest.py --seed "máy lọc nước" --no-alphabet-soup --max 20
```

### Các cờ tham số:
- `--seed`: Từ khóa hạt giống (Bắt buộc).
- `--max`: Số lượng từ khóa tối đa cần lấy (mặc định: 50, tối đa: 100).
- `--no-alphabet-soup`: Tắt chế độ quét bảng chữ cái.
- `--location` / `--language`: Ngôn ngữ và thị trường tra cứu.
