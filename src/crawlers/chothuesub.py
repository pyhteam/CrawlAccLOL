"""
Chothuesub Crawler - Crawl dữ liệu từ chothuesub.com
"""

from typing import List
from bs4 import BeautifulSoup

from src.crawlers.base import BaseCrawler
from src.models import Account


class ChothuesubCrawler(BaseCrawler):
    """Crawler cho chothuesub.com"""

    @property
    def shop_name(self) -> str:
        return "chothuesub.com"

    @property
    def base_url(self) -> str:
        return "https://chothuesub.com/list_accounts"

    def parse_page(self, html_content: str) -> List[Account]:
        """Parse HTML từ chothuesub.com"""
        soup = BeautifulSoup(html_content, "html.parser")
        account_divs = soup.find_all("div", class_="acc-item-bounder")

        accounts = []
        for div in account_divs:
            account = self._extract_account(div)
            if account:
                accounts.append(account)

        return accounts

    def _extract_account(self, div) -> Account | None:
        """Trích xuất thông tin từ một account div"""
        try:
            # Lấy tên ID Game
            name_element = div.find("h3", class_="acc_name")
            id_game = name_element.text.strip() if name_element else ""

            # Lấy thông tin từ phần mô tả
            desc_element = div.find("p", class_="acc_description")
            rank = so_tuong = so_skin = gia = ""

            if desc_element:
                desc_text = desc_element.text.strip()
                lines = desc_text.split("\n")

                # Parse thông tin
                rank = lines[0].strip() if lines else ""

                for line in lines:
                    if "Số Tướng:" in line:
                        so_tuong = line.replace("Số Tướng:", "").strip()
                    elif "Số Skin:" in line:
                        so_skin = line.replace("Số Skin:", "").strip()

                # Giá
                price_span = desc_element.find("span", class_="text-primary")
                if price_span:
                    gia = price_span.text.strip()

            # Lấy link chi tiết
            link_element = div.find("a", href=True)
            link = link_element["href"] if link_element else ""
            if link and not link.startswith("http"):
                link = f"https://chothuesub.com{link}"

            return Account(
                id_game=id_game,
                rank=rank,
                so_tuong=so_tuong,
                so_skin=so_skin,
                gia=gia,
                link=link,
                shop=self.shop_name,
            )

        except Exception as e:
            print(f"[{self.shop_name}] Lỗi parse: {e}")
            return None
