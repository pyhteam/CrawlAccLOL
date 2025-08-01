# HƯỚNG DẪN SỬ DỤNG CHƯƠNG TRÌNH CRAWL TÀI KHOẢN LOL - MULTI SHOP

## Tổng quan
Chương trình này cho phép crawl dữ liệu tài khoản League of Legends từ nhiều shop khác nhau:
- **ChothuesuB.com**: Shop bán tài khoản LOL phổ biến
- **VnToolGame.com**: Shop game tool và tài khoản LOL

## Cài đặt và chạy chương trình

### 1. Cài đặt thư viện cần thiết
```bash
pip install requests beautifulsoup4 pandas
```

### 2. Chạy chương trình
```bash
python app_crawl_lol.py
```

## Các tính năng chính

### 1. Crawl tài khoản mới (Option 1)
Khi chọn option 1, bạn sẽ thấy menu con:
- **1. ChothuesuB.com**: Crawl chỉ từ chothuesub.com (6 trang)
- **2. VnToolGame.com**: Crawl chỉ từ vntoolgame.com (6 trang)
- **3. Crawl cả 2 shop**: Crawl từ cả hai shop
- **4. Quay lại menu chính**

### 2. Xem danh sách đã crawl (Option 2)
- Hiển thị tất cả tài khoản đã crawl
- Bao gồm thống kê theo rank và giá
- Hiển thị phân bố theo shop

### 3. Sắp xếp theo giá (Option 3)
- Sắp xếp tất cả tài khoản từ thấp đến cao
- Hiển thị đầy đủ thông tin: ID Game, Rank, Tướng, Skin, Giá

### 4. Cập nhật thời gian trận đấu (Option 4)
- Sử dụng Riot API để lấy thời gian trận đấu gần nhất
- Cần có Riot API Key (miễn phí tại https://developer.riotgames.com/)
- API Key sẽ được lưu tự động cho lần sau

### 5. Xem tài khoản theo thời gian hoạt động (Option 5)
- Hiển thị tài khoản theo thời gian hoạt động gần nhất
- Cần chạy option 4 trước để có dữ liệu thời gian

## Dữ liệu được lưu

### File JSON (all_accounts.json)
Chứa tất cả dữ liệu tài khoản với cấu trúc:
```json
{
  "id_game": "Tên tài khoản",
  "rank": "Rank hiện tại",
  "so_tuong": "Số tướng",
  "so_skin": "Số skin",
  "gia": "Giá bán",
  "link": "Link chi tiết",
  "shop": "Tên shop",
  "last_match_time": "Thời gian trận gần nhất",
  "last_update": "Thời gian cập nhật"
}
```

### File CSV (all_accounts.csv)
Dữ liệu dạng bảng để mở bằng Excel

## Lưu ý quan trọng

### 1. Về Crawling
- Có delay 2 giây giữa các trang để tránh bị chặn
- Có delay 3 giây giữa các shop khi crawl cả 2
- Dữ liệu mới sẽ được thêm vào dữ liệu cũ (không ghi đè)

### 2. Về Riot API
- Cần đăng ký tài khoản tại https://developer.riotgames.com/
- API Key miễn phí có giới hạn 20 requests/giây
- Chương trình tự động delay 1.2 giây giữa các request

### 3. Về dữ liệu
- Dữ liệu từ VnToolGame có thêm trường "level" và "account_id"
- Dữ liệu từ ChothuesuB có cấu trúc chuẩn hóa
- Tất cả đều có trường "shop" để phân biệt nguồn

## Xử lý lỗi thường gặp

### 1. Lỗi kết nối
- Kiểm tra kết nối internet
- Thử lại sau vài phút nếu website bận

### 2. Lỗi Riot API
- Kiểm tra API Key còn hiệu lực
- Đảm bảo không vượt quá rate limit

### 3. Lỗi dữ liệu
- File JSON bị lỗi: Xóa file và crawl lại
- Dữ liệu không đầy đủ: Kiểm tra cấu trúc HTML của website

## Cấu trúc file

```
CrawlAccLOL/
├── app_crawl_lol.py          # File chính
├── vntoolgame_crawler.py     # Module crawl VnToolGame
├── riot_api.py               # Module Riot API
├── all_accounts.json         # Dữ liệu JSON
├── all_accounts.csv          # Dữ liệu CSV
├── riot_api_key.txt          # API Key (tự động tạo)
└── HUONG_DAN_MULTI_SHOP.md   # File hướng dẫn này
```

## Liên hệ hỗ trợ
Nếu gặp vấn đề, vui lòng kiểm tra:
1. Phiên bản Python >= 3.6
2. Các thư viện đã được cài đặt đầy đủ
3. Kết nối internet ổn định
4. Website nguồn vẫn hoạt động bình thường
