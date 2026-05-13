"""
VnToolGame Crawler - Crawl dữ liệu từ thuetool.com
"""

import re
from typing import List
from bs4 import BeautifulSoup

from src.crawlers.base import BaseCrawler
from src.models import Account


class VnToolGameCrawler(BaseCrawler):
    """Crawler cho thuetool.com (VnToolGame)"""

    @property
    def shop_name(self) -> str:
        return "thuetool.com"

    @property
    def base_url(self) -> str:
        return "https://thuetool.com/acc-rac-full-thong-tin"

    def parse_page(self, html_content: str) -> List[Account]:
        """Parse HTML từ thuetool.com"""
        soup = BeautifulSoup(html_content, "html.parser")
        articles = soup.find_all("article", class_="col-lg-3 col-sm-4 col-6")

        accounts = []
        for article in articles:
            account = self._extract_account(article)
            if account:
                accounts.append(account)

        return accounts

    def _extract_account(self, article) -> Account | None:
        """Trích xuất thông tin từ một article element"""
        try:
            # Lấy link chi tiết
            link_element = article.find("a", class_="link_detail")
            link = link_element["href"] if link_element else ""
            if link and not link.startswith("http"):
                link = f"https://thuetool.com{link}"

            # Lấy giá
            gia = ""
            price_element = article.find("span", class_="text_price_cate")
            if price_element:
                price_text = price_element.get_text(strip=True)
                price_match = re.search(r"([\d,]+)", price_text)
                if price_match:
                    gia = f"{price_match.group(1)} VNĐ"

            # Lấy account ID
            account_id = ""
            id_element = article.find("span", class_="more-detail")
            if id_element:
                id_text = id_element.get_text(strip=True)
                id_match = re.search(r"#(\d+):", id_text)
                if id_match:
                    account_id = id_match.group(1)

            # Lấy thông tin chi tiết
            info_section = article.find("section", class_="info-line font-weight-bold")

            id_game = rank = so_tuong = so_skin = level = ""

            if info_section:
                info_text = info_section.get_text()

                ingame_match = re.search(r"✓\s*Ingame:\s*([^\n\r]+)", info_text)
                if ingame_match:
                    id_game = ingame_match.group(1).strip()

                rank_match = re.search(r"✓\s*Rank Đơn:\s*([^\n\r]+)", info_text)
                if rank_match:
                    rank = rank_match.group(1).strip()

                tuong_match = re.search(r"✓\s*Tướng:\s*([^\n\r]+)", info_text)
                if tuong_match:
                    so_tuong = tuong_match.group(1).strip()

                skin_match = re.search(r"✓\s*Skin:\s*([^\n\r]+)", info_text)
                if skin_match:
                    so_skin = skin_match.group(1).strip()

                level_match = re.search(r"✓\s*Level:\s*([^\n\r]+)", info_text)
                if level_match:
                    level = level_match.group(1).strip()

            return Account(
                id_game=id_game,
                rank=rank,
                so_tuong=so_tuong,
                so_skin=so_skin,
                gia=gia,
                link=link,
                shop=self.shop_name,
                account_id=account_id,
                level=level,
            )

        except Exception as e:
            print(f"[{self.shop_name}] Lỗi parse: {e}")
            return None
