# CrawlAccLOL v2.0.0

Tool crawl và quản lý tài khoản LOL từ nhiều shop, với giao diện Fluent UI (Windows 11 style).

## Cấu trúc dự án

```
CrawlAccLOL/
├── main.py                  # Entry point chính
├── build.bat                # Build ra EXE (có hỏi nâng version)
├── requirements.txt         # Dependencies
├── data/                    # Thư mục dữ liệu (auto-created)
│   └── accounts.json        # Dữ liệu tài khoản (JSON)
├── src/
│   ├── __init__.py          # Package info + version
│   ├── config.py            # Cấu hình ứng dụng
│   ├── models.py            # Data models (Account)
│   ├── storage.py           # Lưu trữ JSON
│   ├── riot_api.py          # Riot Games API client
│   ├── crawlers/
│   │   ├── __init__.py
│   │   ├── base.py          # Base crawler (abstract)
│   │   ├── chothuesub.py    # Crawler chothuesub.com
│   │   ├── vntoolgame.py    # Crawler thuetool.com
│   │   └── thuetoolhay.py   # Crawler thuetoolhay.com
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py   # FluentWindow chính
│       └── pages/
│           ├── __init__.py
│           ├── dashboard.py # Trang tổng quan
│           ├── accounts.py  # Quản lý tài khoản
│           ├── crawl.py     # Crawl dữ liệu
│           └── settings.py  # Cài đặt
```

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy

```bash
python main.py
```

## Build EXE

```bash
build.bat
```

Build script sẽ:
1. Hỏi bạn có muốn nâng version không
2. Cho chọn kiểu nâng: Patch / Minor / Major / Thủ công
3. Build ra file EXE trong thư mục `dist/`

## Tính năng

- **Dashboard**: Thống kê tổng quan (tổng tài khoản, phân bố shop, giá)
- **Quản lý tài khoản**: Bảng dữ liệu với tìm kiếm, lọc theo Shop/Rank, sắp xếp
- **Crawl**: Chọn shop, cấu hình số trang, crawl với progress bar real-time
- **Cài đặt**: Riot API Key, delay, timeout
- **Fluent UI**: Giao diện Windows 11 style (dark mode)
