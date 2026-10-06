# Hướng Dẫn Kích Hoạt Ép Index (1-Click Force Indexing)

Tài liệu chi tiết về quy trình gửi danh sách URL chưa index sang hệ thống ép index chuyên nghiệp qua `scripts/force_index.py`.

---

## 1. Cơ Chế Hoạt Động & Chi Phí

Script `scripts/force_index.py` kết nối với API Backend SolannEco (`POST /api/v1/force-index`), đẩy các URL sang hệ thống ép index đối tác (Sinbyte / 1hPing).

### Quy định Chi phí & Bảo toàn Credit (P0 Guardrail):
- **Chi phí**: Khấu trừ **120 RankCredits** trên mỗi URL.
- **Yêu cầu gói nền tảng**: Tài khoản người dùng bắt buộc phải sở hữu gói Solann Cloud (`RankSubscription`: Trial 7 ngày hoặc Pro 12 tháng) còn hiệu lực.
- **Cơ chế hoàn trả tự động (Auto-Refund)**: Nếu hệ thống ép index gặp sự cố (`502` hoặc đối tác lỗi mạng), toàn bộ số credits đã khấu trừ sẽ được máy chủ hoàn trả ngay lập tức vào ví tài khoản của bạn.

---

## 2. Các Lệnh Thực Thi Mẫu (`scripts/force_index.py`)

```bash
# 1. Chế độ kiểm tra an toàn (Dry-Run): Tính toán chi phí mà KHÔNG trừ credits
python scripts/force_index.py --urls "https://example.com/bai-chua-index" --dry-run

# 2. Kích hoạt ép index cho danh sách URLs
python scripts/force_index.py --urls "https://example.com/bai-1, https://example.com/bai-2" --project-name "Ép index bài mới tuần 10"

# 3. Kích hoạt ép index từ file văn bản chứa các URL chưa index
python scripts/force_index.py --file not_indexed_urls.txt --project-name "Đợt ép index tổng thể"
```

### Các Cờ Tham Số Chi Tiết:
- `--urls`: Danh sách URLs cần ép index (phân cách bằng dấu phẩy).
- `--file`: File văn bản chứa danh sách URLs (mỗi dòng 1 URL).
- `--project-name`: Tên đợt ép index để theo dõi trong lịch sử thanh toán và báo cáo.
- `--dry-run`: Cờ kiểm tra mô phỏng (tính toán số URL, số credit cần thiết và kiểm tra cú pháp).
- `--api-key`: Solann API Key của Tenant (`sk-solanneco-...`).

---

## 3. Quy Trình Khép Kín 4 Bước Khuyến Nghị

Khi người dùng yêu cầu: *"Hãy kiểm tra các link này và ép index giúp tôi"*:

1. **Bước 1**: Chạy `python scripts/check_index.py --file links.txt --save-session` để quét toàn bộ.
2. **Bước 2**: Đọc trường `notIndexedUrls` trong kết quả JSON trả về.
3. **Bước 3**: Báo cáo tổng kết cho người dùng:
   > *"Đã kiểm tra xong X URLs: Có Y URLs đã index, Z URLs chưa index. Cần Z × 120 credits để ép index."*
4. **Bước 4**: Xác nhận với người dùng rồi chạy `python scripts/force_index.py --urls "..."` để hoàn tất quy trình.
