import requests
from bs4 import BeautifulSoup
import time

class ChothuesubCrawler:
    def __init__(self):
        self.base_url = "https://chothuesub.com/list_accounts"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_account_info(self, account_div):
        """Trích xuất thông tin từ một account div"""
        try:
            # Lấy tên ID Game
            name_element = account_div.find('h3', class_='acc_name')
            id_game = name_element.text.strip() if name_element else ""
            
            # Lấy thông tin từ phần mô tả
            desc_element = account_div.find('p', class_='acc_description')
            if desc_element:
                desc_text = desc_element.text.strip()
                lines = desc_text.split('\n')
                
                # Parse thông tin
                rank = lines[0].strip() if len(lines) > 0 else ""
                
                # Số tướng
                so_tuong = ""
                for line in lines:
                    if "Số Tướng:" in line:
                        so_tuong = line.replace("Số Tướng:", "").strip()
                        break
                
                # Số skin
                so_skin = ""
                for line in lines:
                    if "Số Skin:" in line:
                        so_skin = line.replace("Số Skin:", "").strip()
                        break
                
                # Giá
                gia = ""
                price_span = desc_element.find('span', class_='text-primary')
                if price_span:
                    gia = price_span.text.strip()
            else:
                rank = so_tuong = so_skin = gia = ""
            
            # Lấy link chi tiết
            link_element = account_div.find('a', href=True)
            link = link_element['href'] if link_element else ""
            if link and not link.startswith('http'):
                link = f"https://chothuesub.com{link}"
            
            return {
                "id_game": id_game,
                "rank": rank,
                "so_tuong": so_tuong,
                "so_skin": so_skin,
                "gia": gia,
                "link": link,
                "shop": "chothuesub.com"
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
            
            # Tìm tất cả các account items
            account_divs = soup.find_all('div', class_='acc-item-bounder')
            
            accounts = []
            for div in account_divs:
                account_info = self.extract_account_info(div)
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
        
        print(f"Sẽ crawl {max_pages} trang từ chothuesub.com")
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
            print("⚠️  CẢNH BÁO: Không thể crawl được dữ liệu từ chothuesub.com")
            print("   Có thể website đang bảo trì hoặc thay đổi cấu trúc")
            print("   Vui lòng thử lại sau hoặc sử dụng các shop khác")
        
        return all_accounts
