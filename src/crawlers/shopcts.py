"""
ShopCTS Crawler - Crawl dữ liệu từ shopcts.pro
"""

import re
from typing import List
from bs4 import BeautifulSoup

from src.crawlers.base import BaseCrawler
from src.models import Account


class ShopCTSCrawler(BaseCrawler):
    """Crawler cho shopcts.pro"""

    @property
    def shop_name(self) -> str:
        return "shopcts.pro"

    @property
    def base_url(self) -> str:
        return "https://shopcts.pro/acc-rac-lien-minh"

    def parse_page(self, html_content: str) -> List[Account]:
        """Parse HTML từ shopcts.pro"""
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
            link_element = article.find("a", class_="more-detail")
            if not link_element:
                link_element = article.find("a", href=True)
            link = link_element["href"] if link_element else ""
            if link and not link.startswith("http"):
                link = f"https://shopcts.pro{link}"

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
            id_element = article.find("a", class_="more-detail")
            if id_element:
                id_text = id_element.get_text(strip=True)
                id_match = re.search(r"#(\d+):", id_text)
                if id_match:
                    account_id = id_match.group(1)

            # Lấy thông tin chi tiết từ product-details
            info_section = article.find("div", class_="product-details")

            id_game = rank = so_tuong = so_skin = ""

            if info_section:
                info_divs = info_section.find_all("div", class_="mb-2")
                for div in info_divs:
                    text = div.get_text(separator=" ", strip=True)
                    badge = div.find("span", class_="badge")
                    badge_val = badge.get_text(strip=True) if badge else ""

                    if "Ingame" in text:
                        ingame_text = text.split("Ingame")[-1].strip()
                        ingame_text = re.sub(r"^[:\s✓]+", "", ingame_text).strip()
                        if badge_val:
                            id_game = badge_val
                        elif ingame_text:
                            id_game = ingame_text
                    elif "Rank" in text and "Linh" not in text:
                        rank_text = text.split("Rank")[-1].strip()
                        rank_text = re.sub(r"^[:\s✓]+", "", rank_text).strip()
                        if badge_val:
                            rank = badge_val
                        elif rank_text:
                            rank = rank_text
                    elif "Tướng" in text:
                        if badge_val:
                            so_tuong = badge_val
                        else:
                            tuong_match = re.search(r"(\d+)", text)
                            if tuong_match:
                                so_tuong = tuong_match.group(1)
                    elif "Skin" in text:
                        if badge_val:
                            so_skin = badge_val
                        else:
                            skin_match = re.search(r"(\d+)", text)
                            if skin_match:
                                so_skin = skin_match.group(1)

            return Account(
                id_game=id_game,
                rank=rank,
                so_tuong=so_tuong,
                so_skin=so_skin,
                gia=gia,
                link=link,
                shop=self.shop_name,
                account_id=account_id,
            )

        except Exception as e:
            print(f"[{self.shop_name}] Lỗi parse: {e}")
            return None
