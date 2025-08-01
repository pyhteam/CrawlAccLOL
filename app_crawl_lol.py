import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime

class CrawlAccLOL:
    def __init__(self):
        self.data_file = "chothuesub_accounts.json"
        self.accounts = []
        self.load_data()
    
    def load_data(self):
        """Load dữ liệu từ file JSON nếu có"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.accounts = json.load(f)
                print(f"Đã load {len(self.accounts)} tài khoản từ file.")
            except:
                self.accounts = []
    
    def save_data(self):
        """Lưu dữ liệu vào file JSON"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, ensure_ascii=False, indent=2)
        print(f"Đã lưu {len(self.accounts)} tài khoản vào file.")
    
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
                "link": link
            }
        except Exception as e:
            print(f"Lỗi khi trích xuất thông tin: {e}")
            return None
    
    def crawl_page(self, page_number):
        """Crawl một trang cụ thể"""
        url = f"https://chothuesub.com/list_accounts?page={page_number}"
        print(f"Đang crawl trang {page_number}: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
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
    
    def crawl_all_pages(self):
        """Crawl tất cả các trang"""
        print("\n" + "="*50)
        print("BẮT ĐẦU CRAWL DỮ LIỆU")
        print("="*50)
        
        self.accounts = []  # Reset dữ liệu cũ
        total_pages = 6
        
        print(f"Sẽ crawl {total_pages} trang từ chothuesub.com")
        print("-" * 50)
        
        for page in range(1, total_pages + 1):
            accounts = self.crawl_page(page)
            self.accounts.extend(accounts)
            
            # Delay giữa các request
            if page < total_pages:
                print(f"Đợi 2 giây trước khi crawl trang tiếp theo...")
                time.sleep(2)
        
        print("-" * 50)
        print(f"Hoàn thành! Tổng cộng crawl được {len(self.accounts)} tài khoản")
        
        # Lưu dữ liệu
        self.save_data()
        
        # Tạo file CSV
        self.export_to_csv()
        
        print("\nNhấn Enter để quay lại menu...")
        input()
    
    def export_to_csv(self):
        """Xuất dữ liệu ra file CSV"""
        import csv
        csv_file = "chothuesub_accounts.csv"
        
        if self.accounts:
            with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.accounts[0].keys())
                writer.writeheader()
                writer.writerows(self.accounts)
            print(f"Đã xuất dữ liệu ra file: {csv_file}")
    
    def view_accounts(self):
        """Xem danh sách tài khoản đã crawl"""
        print("\n" + "="*50)
        print("DANH SÁCH TÀI KHOẢN ĐÃ CRAWL")
        print("="*50)
        
        if not self.accounts:
            print("Chưa có dữ liệu! Vui lòng crawl dữ liệu trước.")
        else:
            print(f"Tổng số tài khoản: {len(self.accounts)}")
            print("-" * 100)
            print(f"{'STT':<5} {'ID Game':<30} {'Rank':<15} {'Tướng':<10} {'Skin':<10} {'Giá':<15}")
            print("-" * 100)
            
            for i, acc in enumerate(self.accounts[:20], 1):  # Hiển thị 20 acc đầu
                id_game = acc['id_game'][:28] + '..' if len(acc['id_game']) > 30 else acc['id_game']
                print(f"{i:<5} {id_game:<30} {acc['rank']:<15} {acc['so_tuong']:<10} {acc['so_skin']:<10} {acc['gia']:<15}")
            
            if len(self.accounts) > 20:
                print(f"\n... và {len(self.accounts) - 20} tài khoản khác")
            
            # Thống kê
            print("\n" + "-" * 50)
            print("THỐNG KÊ:")
            self.show_statistics()
        
        print("\nNhấn Enter để quay lại menu...")
        input()
    
    def show_statistics(self):
        """Hiển thị thống kê"""
        if not self.accounts:
            return
        
        # Thống kê theo rank
        rank_stats = {}
        for acc in self.accounts:
            rank = acc.get('rank', 'Unknown')
            rank_stats[rank] = rank_stats.get(rank, 0) + 1
        
        print("\nThống kê theo Rank:")
        for rank, count in sorted(rank_stats.items()):
            print(f"  {rank}: {count} tài khoản")
        
        # Thống kê giá
        prices = []
        for acc in self.accounts:
            price_str = acc.get('gia', '0')
            price_clean = price_str.replace('VNĐ', '').replace(',', '').strip()
            try:
                price = int(price_clean)
                prices.append(price)
            except:
                pass
        
        if prices:
            print(f"\nGiá thấp nhất: {min(prices):,} VNĐ")
            print(f"Giá cao nhất: {max(prices):,} VNĐ")
            print(f"Giá trung bình: {sum(prices)/len(prices):,.0f} VNĐ")
    
    def sort_by_price(self):
        """Sắp xếp theo giá từ thấp đến cao"""
        print("\n" + "="*50)
        print("DANH SÁCH TÀI KHOẢN SẮP XẾP THEO GIÁ (THẤP -> CAO)")
        print("="*50)
        
        if not self.accounts:
            print("Chưa có dữ liệu! Vui lòng crawl dữ liệu trước.")
        else:
            # Tạo list với giá đã convert sang số
            accounts_with_price = []
            for acc in self.accounts:
                price_str = acc.get('gia', '0')
                price_clean = price_str.replace('VNĐ', '').replace(',', '').strip()
                try:
                    price_num = int(price_clean)
                    accounts_with_price.append((price_num, acc))
                except:
                    pass
            
            # Sắp xếp theo giá
            accounts_with_price.sort(key=lambda x: x[0])
            
            print("-" * 100)
            print(f"{'STT':<5} {'ID Game':<30} {'Rank':<15} {'Tướng':<10} {'Skin':<10} {'Giá':<15}")
            print("-" * 100)
            
            for i, (price, acc) in enumerate(accounts_with_price[:30], 1):  # Hiển thị 30 acc giá thấp nhất
                id_game = acc['id_game'][:28] + '..' if len(acc['id_game']) > 30 else acc['id_game']
                print(f"{i:<5} {id_game:<30} {acc['rank']:<15} {acc['so_tuong']:<10} {acc['so_skin']:<10} {acc['gia']:<15}")
            
            if len(accounts_with_price) > 30:
                print(f"\n... và {len(accounts_with_price) - 30} tài khoản khác")
        
        print("\nNhấn Enter để quay lại menu...")
        input()
    
    def clear_screen(self):
        """Xóa màn hình console"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_menu(self):
        """Hiển thị menu chính"""
        self.clear_screen()
        print("="*50)
        print("CHƯƠNG TRÌNH CRAWL TÀI KHOẢN LOL - CHOTHUESUB.COM")
        print("="*50)
        print(f"Dữ liệu hiện tại: {len(self.accounts)} tài khoản")
        if self.accounts:
            print(f"Lần cập nhật cuối: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("-"*50)
        print("1. Crawl tài khoản mới")
        print("2. Xem danh sách đã crawl")
        print("3. Sắp xếp theo giá (thấp -> cao)")
        print("4. Thoát")
        print("-"*50)
    
    def run(self):
        """Chạy ứng dụng"""
        while True:
            self.show_menu()
            choice = input("Nhập lựa chọn của bạn (1-4): ")
            
            if choice == '1':
                self.crawl_all_pages()
            elif choice == '2':
                self.view_accounts()
            elif choice == '3':
                self.sort_by_price()
            elif choice == '4':
                print("\nCảm ơn bạn đã sử dụng chương trình!")
                print("Tạm biệt!")
                break
            else:
                print("\nLựa chọn không hợp lệ! Vui lòng chọn từ 1-4.")
                print("Nhấn Enter để tiếp tục...")
                input()

if __name__ == "__main__":
    app = CrawlAccLOL()
    app.run()
