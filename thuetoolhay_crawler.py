import requests
from bs4 import BeautifulSoup
import re
import time

class ThueToolHayCrawler:
    def __init__(self):
        self.base_url = "https://thuetoolhay.com/acc-rac-random-50k"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_account_info(self, article):
        """Trích xuất thông tin từ một article element"""
        try:
            # Lấy link chi tiết
            link_element = article.find('a', class_='link_detail')
            link = link_element['href'] if link_element else ""
            if link and not link.startswith('http'):
                link = f"https://thuetoolhay.com{link}"
            
            # Lấy giá
            price_element = article.find('span', class_='text_price_cate')
            gia = ""
            if price_element:
                price_text = price_element.get_text(strip=True)
                # Loại bỏ icon và lấy số tiền
                price_match = re.search(r'([\d,]+)', price_text)
                if price_match:
                    gia = f"{price_match.group(1)} VNĐ"
            
            # Lấy ID từ more-detail
            id_element = article.find('span', class_='more-detail')
            account_id = ""
            if id_element:
                id_text = id_element.get_text(strip=True)
                # Ví dụ: "#68495: Acc Rác Full Thông Tin"
                id_match = re.search(r'#(\d+):', id_text)
                if id_match:
                    account_id = id_match.group(1)
            
            # Lấy thông tin chi tiết từ section info-line
            info_section = article.find('section', class_='text-sm info-line font-weight-bold')
            
            id_game = ""
            rank_don = ""
            so_tuong = ""
            so_skin = ""
            
            if info_section:
                info_text = info_section.get_text()
                
                # Tìm InGame
                ingame_match = re.search(r'✓\s*InGame:\s*([^\n\r]+)', info_text)
                if ingame_match:
                    id_game = ingame_match.group(1).strip()
                
                # Tìm Rank
                rank_match = re.search(r'✓\s*Rank:\s*([^\n\r]+)', info_text)
                if rank_match:
                    rank_don = rank_match.group(1).strip()
                
                # Tìm Tướng
                tuong_match = re.search(r'✓\s*Tướng:\s*([^\n\r]+)', info_text)
                if tuong_match:
                    so_tuong = tuong_match.group(1).strip()
                
                # Tìm Skin
                skin_match = re.search(r'✓\s*Skin:\s*([^\n\r]+)', info_text)
                if skin_match:
                    so_skin = skin_match.group(1).strip()
            
            return {
                "id_game": id_game,
                "rank": rank_don,
                "so_tuong": so_tuong,
                "so_skin": so_skin,
                "gia": gia,
                "link": link,
                "shop": "thuetoolhay.com",
                "account_id": account_id
            }
            
        except Exception as e:
            print(f"Lỗi khi trích xuất thông tin: {e}")
            return None
    
    def crawl_page(self, page_number):
        """Crawl một trang cụ thể"""
        url = f"{self.base_url}?page={page_number}"
        print(f"Đang crawl trang {page_number}: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm tất cả các article elements
            articles = soup.find_all('article', class_='col-lg-3 col-sm-4 col-6')
            
            accounts = []
            for article in articles:
                account_info = self.extract_account_info(article)
                if account_info:
                    accounts.append(account_info)
            
            print(f"Tìm thấy {len(accounts)} tài khoản ở trang {page_number}")
            return accounts
            
        except requests.RequestException as e:
            print(f"Lỗi khi crawl trang {page_number}: {e}")
            return []
        except Exception as e:
            print(f"Lỗi không xác định khi crawl trang {page_number}: {e}")
            return []
    
    def crawl_all_pages(self, max_pages=6):
        """Crawl tất cả các trang"""
        all_accounts = []
        
        print(f"Sẽ crawl {max_pages} trang từ thuetoolhay.com")
        print("Lưu ý: Nếu website không phản hồi, sẽ bỏ qua sau 30 giây")
        print("-" * 50)
        
        success_count = 0
        for page in range(1, max_pages + 1):
            accounts = self.crawl_page(page)
            if accounts:  # Chỉ đếm thành công nếu có dữ liệu
                success_count += 1
                all_accounts.extend(accounts)
            
            # Delay giữa các request
            if page < max_pages:
                print(f"Đợi 2 giây trước khi crawl trang tiếp theo...")
                time.sleep(2)
        
        if success_count == 0:
            print("⚠️  CẢNH BÁO: Không thể crawl được dữ liệu từ thuetoolhay.com")
            print("   Có thể website đang bảo trì hoặc thay đổi cấu trúc")
            print("   Vui lòng thử lại sau hoặc sử dụng các shop khác")
        
        return all_accounts
