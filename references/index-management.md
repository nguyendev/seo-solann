# Hướng Dẫn Quản Lý & Kiểm Tra Google Index (Index Management)

Tài liệu chi tiết về quy trình kiểm tra trạng thái lập chỉ mục Google Index hàng loạt và lưu trữ đám mây qua `scripts/check_index.py`.

---

## 1. Nguyên Lý Kiểm Tra (Serper BYOK & URLCleaner 5 Tầng)

Script `scripts/check_index.py` sử dụng Serper Search API với tài khoản cá nhân của người dùng (BYOK - 2,500 truy vấn miễn phí) để gửi truy vấn toán tử `site:<url>`.

### Thuật toán URLCleaner 5 Tầng:
Để tránh tình trạng Google trả về link trang chủ hoặc link biến thể URL dẫn đến kết quả sai (false positive), script áp dụng bộ lọc đối soát 5 tầng:
1. **Loại bỏ tham số theo dõi**: Lọc sạch `srsltid`, `utm_*`, `gclid`, `fbclid`.
2. **Loại bỏ Index Files**: Tự động lược bỏ `/index.html`, `/index.php`, `/default.aspx`.
3. **Chuẩn hóa Trailing Slash**: Chuẩn hóa dấu gạch chéo cuối URL.
4. **So khớp Exact Host & Path**: So khớp chính xác giữa URL truy vấn và URL trả về trong kết quả Organic của Google.
5. **Phân loại Trạng thái**:
   - `1` (`Indexed`): URL đã được Google lập chỉ mục chính thức.
   - `2` (`NotIndexed`): Không tìm thấy kết quả hoặc không khớp URL.
   - `3` (`Error`): Lỗi gọi Serper API (quá hạn ngạch hoặc mạng ngắt quãng).

---

## 2. Các Lệnh Thực Thi Mẫu (`scripts/check_index.py`)

```bash
# 1. Kiểm tra danh sách URLs qua dòng lệnh
python scripts/check_index.py --urls "https://solanneco.com, https://app.solann.io"

# 2. Kiểm tra danh sách lớn từ file văn bản (mỗi dòng 1 URL)
python scripts/check_index.py --file links.txt

# 3. Kiểm tra và tự động lưu phiên vào Solann Cloud (gắn Dự án và Phân loại Scope)
python scripts/check_index.py --file links.txt --save-session --session-name "Quét bài viết mới đợt 1" --target-domain "solannseo.com" --scope 1 --tags "dot-1,internal"
```

### Các Cờ Tham Số Chi Tiết:
- `--urls`: Danh sách URLs phân cách bằng dấu phẩy.
- `--file`: Đường dẫn file text chứa URLs.
- `--serper-key`: Khóa Serper.dev API cá nhân (tùy chọn nếu đã lưu trong `config/solann-api.json` hoặc biến `SERPER_API_KEY`).
- `--country`: Mã quốc gia tìm kiếm (mặc định: `vn`).
- `--delay`: Khoảng nghỉ giữa các request (giây, mặc định: 0.2s).
- `--save-session`: Cờ kích hoạt gửi kết quả lưu trữ vào Solann Cloud.
- `--session-name`: Tên phiên kiểm tra trên Cloud.
- `--project-id`: GUID của Dự án SEO (`RankProject`) trên Solann Cloud.
- `--target-domain`: Tên miền mục tiêu được thụ hưởng (ví dụ: `solannseo.com`).
- `--scope`: Phân loại loại link:
  - `0`: Độc lập / Khác (`Standalone`)
  - `1`: Link nội bộ website (`Internal`)
  - `2`: Backlink trỏ về (`Backlink`)
  - `3`: Social Entity / Profile (`SocialEntity`)
- `--tags`: Nhãn gắn kèm phân loại (ví dụ: `"dot-1,pr-bao-chi"`).

---

## 3. Cấu Trúc Kết Quả JSON Trả Về

```json
{
  "summary": {
    "total": 100,
    "indexed": 85,
    "notIndexed": 15,
    "error": 0,
    "indexRatePercent": 85.0
  },
  "notIndexedUrls": [
    "https://example.com/bai-chua-index-1",
    "https://example.com/bai-chua-index-2"
  ],
  "results": [ ... ],
  "cloudSync": {
    "saved": true,
    "data": { "id": "...", "sessionName": "..." }
  }
}
```
*Ghi chú:* Trường `notIndexedUrls` được sinh ra tự động để AI hoặc người dùng có thể truyền thẳng sang `scripts/force_index.py` mà không phải lọc thủ công!
