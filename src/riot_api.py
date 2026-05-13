"""
Riot API module - Tương tác với Riot Games API
Hỗ trợ multi-key pool để tăng tốc (mỗi key có rate limit riêng)
"""

import time
import requests
from datetime import datetime
from typing import Optional, Tuple, List
from threading import Lock
from itertools import cycle

from src.config import AppConfig


class RiotAPI:
    """Client cho Riot Games API - tối ưu rate limit per key"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": self.api_key})

        # Rate limit tracking per key
        self._request_times: List[float] = []
        self._lock = Lock()

    def _rate_limit_wait(self):
        """Đợi nếu cần để không vượt rate limit (20/s, 100/2min)"""
        with self._lock:
            now = time.time()
            # Xóa requests cũ hơn 2 phút
            self._request_times = [t for t in self._request_times if now - t < 120]

            # Check 100 req / 2 min
            if len(self._request_times) >= 95:
                oldest = self._request_times[0]
                wait_time = 120 - (now - oldest) + 0.5
                if wait_time > 0:
                    time.sleep(wait_time)

            # Check 20 req / 1 sec
            recent = [t for t in self._request_times if now - t < 1.0]
            if len(recent) >= 18:
                time.sleep(0.1)

            self._request_times.append(time.time())

    def _get(self, url: str, params: dict = None, timeout: int = 10) -> Optional[requests.Response]:
        """GET request với rate limit handling"""
        self._rate_limit_wait()

        try:
            response = self.session.get(url, params=params, timeout=timeout)

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 10))
                time.sleep(retry_after + 1)
                return self._get(url, params, timeout)

            if response.status_code == 200:
                return response

        except requests.RequestException:
            pass

        return None

    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> Optional[dict]:
        """Lấy thông tin account từ Riot ID"""
        url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        resp = self._get(url)
        return resp.json() if resp else None

    def get_lol_match_ids(self, puuid: str, count: int = 1) -> list:
        """Lấy LOL match IDs"""
        url = f"https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"start": 0, "count": count}
        resp = self._get(url, params=params)
        return resp.json() if resp else []

    def get_lol_match_detail(self, match_id: str) -> Optional[dict]:
        """Lấy chi tiết LOL match"""
        url = f"https://sea.api.riotgames.com/lol/match/v5/matches/{match_id}"
        resp = self._get(url)
        return resp.json() if resp else None

    def get_tft_match_ids(self, puuid: str, count: int = 1) -> list:
        """Lấy TFT match IDs"""
        url = f"https://sea.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids"
        params = {"start": 0, "count": count}
        resp = self._get(url, params=params)
        return resp.json() if resp else []

    def get_tft_match_detail(self, match_id: str) -> Optional[dict]:
        """Lấy chi tiết TFT match"""
        url = f"https://sea.api.riotgames.com/tft/match/v1/matches/{match_id}"
        resp = self._get(url)
        return resp.json() if resp else None

    @staticmethod
    def _format_time_ago(timestamp_ms: int) -> str:
        """Format timestamp thành 'X thời gian trước'"""
        game_end_time = datetime.fromtimestamp(timestamp_ms / 1000)
        time_diff = datetime.now() - game_end_time

        if time_diff.days > 365:
            years = time_diff.days // 365
            return f"{years} năm trước"
        elif time_diff.days > 30:
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

    def get_last_match_times(self, summoner_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Lấy thời gian trận đấu gần nhất cho cả LOL và TFT.
        Returns: (lol_time, tft_time)
        """
        # Parse Riot ID
        if "#" in summoner_name:
            game_name, tag_line = summoner_name.split("#", 1)
        else:
            game_name = summoner_name
            tag_line = "VN2"

        # Lấy account (1 request)
        account = self.get_account_by_riot_id(game_name, tag_line)
        if not account:
            return None, None

        puuid = account.get("puuid")
        if not puuid:
            return None, None

        lol_time = None
        tft_time = None

        # LOL match (1-2 requests)
        lol_match_ids = self.get_lol_match_ids(puuid, 1)
        if lol_match_ids:
            match_detail = self.get_lol_match_detail(lol_match_ids[0])
            if match_detail:
                try:
                    ts = match_detail["info"]["gameEndTimestamp"]
                    lol_time = self._format_time_ago(ts)
                except (KeyError, TypeError):
                    pass

        # TFT match (1-2 requests)
        tft_match_ids = self.get_tft_match_ids(puuid, 1)
        if tft_match_ids:
            match_detail = self.get_tft_match_detail(tft_match_ids[0])
            if match_detail:
                try:
                    ts = match_detail["info"]["game_datetime"]
                    tft_time = self._format_time_ago(ts)
                except (KeyError, TypeError):
                    pass

        return lol_time, tft_time


class RiotAPIPool:
    """
    Pool nhiều Riot API keys - round-robin để tăng tốc.
    Mỗi key có rate limit riêng (20/s, 100/2min),
    nên N keys = N lần throughput.
    """

    def __init__(self, api_keys: List[str]):
        self.clients: List[RiotAPI] = [RiotAPI(key) for key in api_keys if key.strip()]
        self._cycle = cycle(range(len(self.clients))) if self.clients else None
        self._lock = Lock()

    @classmethod
    def load_from_file(cls) -> Optional["RiotAPIPool"]:
        """Load API keys từ file (mỗi dòng 1 key)"""
        if AppConfig.API_KEY_FILE.exists():
            try:
                content = AppConfig.API_KEY_FILE.read_text().strip()
                keys = [k.strip() for k in content.splitlines() if k.strip()]
                if keys:
                    return cls(keys)
            except IOError:
                pass
        return None

    @property
    def key_count(self) -> int:
        """Số lượng keys"""
        return len(self.clients)

    def _next_client(self) -> Optional[RiotAPI]:
        """Lấy client tiếp theo (round-robin)"""
        if not self._cycle:
            return None
        with self._lock:
            idx = next(self._cycle)
            return self.clients[idx]

    def get_last_match_times(self, summoner_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Lấy thời gian match gần nhất, dùng key tiếp theo trong pool"""
        client = self._next_client()
        if not client:
            return None, None
        return client.get_last_match_times(summoner_name)

    def save_keys(self):
        """Lưu tất cả keys vào file"""
        AppConfig.ensure_dirs()
        keys_text = "\n".join(client.api_key for client in self.clients)
        AppConfig.API_KEY_FILE.write_text(keys_text)
