"""
Riot API module - Tương tác với Riot Games API
"""

import time
import requests
from datetime import datetime
from typing import Optional

from src.config import AppConfig


class RiotAPI:
    """Client cho Riot Games API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://vn2.api.riotgames.com"
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": self.api_key})

    @classmethod
    def load_from_file(cls) -> Optional["RiotAPI"]:
        """Load API key từ file"""
        if AppConfig.API_KEY_FILE.exists():
            try:
                api_key = AppConfig.API_KEY_FILE.read_text().strip()
                if api_key:
                    return cls(api_key)
            except IOError:
                pass
        return None

    def save_key(self):
        """Lưu API key vào file"""
        AppConfig.ensure_dirs()
        AppConfig.API_KEY_FILE.write_text(self.api_key)

    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> Optional[dict]:
        """Lấy thông tin account từ Riot ID"""
        url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                time.sleep(10)
                return self.get_account_by_riot_id(game_name, tag_line)
        except requests.RequestException:
            pass
        return None

    def get_summoner_by_puuid(self, puuid: str) -> Optional[dict]:
        """Lấy summoner data từ PUUID"""
        url = f"{self.base_url}/lol/summoner/v4/summoners/by-puuid/{puuid}"

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def get_match_history(self, puuid: str, count: int = 1) -> list:
        """Lấy lịch sử trận đấu"""
        url = f"https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"start": 0, "count": count}

        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                time.sleep(10)
                return self.get_match_history(puuid, count)
        except requests.RequestException:
            pass
        return []

    def get_match_detail(self, match_id: str) -> Optional[dict]:
        """Lấy chi tiết trận đấu"""
        url = f"https://sea.api.riotgames.com/lol/match/v5/matches/{match_id}"

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def get_last_match_time(self, summoner_name: str) -> Optional[str]:
        """Lấy thời gian trận đấu gần nhất"""
        # Parse Riot ID
        if "#" in summoner_name:
            game_name, tag_line = summoner_name.split("#", 1)
        else:
            game_name = summoner_name
            tag_line = "VN2"

        # Lấy account
        account = self.get_account_by_riot_id(game_name, tag_line)
        if not account:
            return None

        puuid = account.get("puuid")
        if not puuid:
            return None

        # Lấy match gần nhất
        match_ids = self.get_match_history(puuid, 1)
        if not match_ids:
            return None

        # Lấy chi tiết
        match_detail = self.get_match_detail(match_ids[0])
        if not match_detail:
            return None

        # Tính thời gian
        try:
            game_end_ts = match_detail["info"]["gameEndTimestamp"]
            game_end_time = datetime.fromtimestamp(game_end_ts / 1000)
            time_diff = datetime.now() - game_end_time

            if time_diff.days > 30:
                months = time_diff.days // 30
                return f"{months} tháng trước"
            elif time_diff.days > 0:
                return f"{time_diff.days} ngày trước"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                return f"{hours} giờ trước"
            else:
                minutes = max(1, time_diff.seconds // 60)
                return f"{minutes} phút trước"
        except (KeyError, TypeError):
            return None
