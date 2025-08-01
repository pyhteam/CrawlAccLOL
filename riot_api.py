import requests
import time
from datetime import datetime

class RiotAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://vn2.api.riotgames.com"
        
    def get_summoner_by_name(self, summoner_name):
        """Lấy thông tin summoner từ tên"""
        # Xử lý tên summoner (loại bỏ tag)
        if '#' in summoner_name:
            game_name, tag_line = summoner_name.split('#')
        else:
            game_name = summoner_name
            tag_line = 'VN2'  # Default tag cho server VN
            
        # API endpoint mới của Riot (Account-V1)
        url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        headers = {"X-Riot-Token": self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                account_data = response.json()
                puuid = account_data.get('puuid')
                
                # Lấy summoner data từ PUUID
                summoner_url = f"{self.base_url}/lol/summoner/v4/summoners/by-puuid/{puuid}"
                summoner_response = requests.get(summoner_url, headers=headers)
                
                if summoner_response.status_code == 200:
                    return summoner_response.json()
            elif response.status_code == 404:
                print(f"Không tìm thấy tài khoản: {summoner_name}")
            elif response.status_code == 429:
                print("Rate limit exceeded. Đợi một chút...")
                time.sleep(10)
            else:
                print(f"Lỗi API: {response.status_code}")
        except Exception as e:
            print(f"Lỗi khi gọi API: {e}")
        
        return None
    
    def get_match_history(self, puuid, count=5):
        """Lấy lịch sử trận đấu"""
        url = f"https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        headers = {"X-Riot-Token": self.api_key}
        params = {"start": 0, "count": count}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("Rate limit exceeded. Đợi một chút...")
                time.sleep(10)
        except Exception as e:
            print(f"Lỗi khi lấy match history: {e}")
        
        return []
    
    def get_match_detail(self, match_id):
        """Lấy chi tiết một trận đấu"""
        url = f"https://sea.api.riotgames.com/lol/match/v5/matches/{match_id}"
        headers = {"X-Riot-Token": self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Lỗi khi lấy match detail: {e}")
        
        return None
    
    def get_last_match_time(self, summoner_name):
        """Lấy thời gian trận đấu gần nhất của một summoner"""
        summoner = self.get_summoner_by_name(summoner_name)
        if not summoner:
            return None
            
        puuid = summoner.get('puuid')
        if not puuid:
            return None
            
        # Lấy danh sách match gần nhất
        match_ids = self.get_match_history(puuid, 1)
        if not match_ids:
            return None
            
        # Lấy chi tiết match gần nhất
        match_detail = self.get_match_detail(match_ids[0])
        if not match_detail:
            return None
            
        # Lấy timestamp của trận đấu (milliseconds)
        game_end_timestamp = match_detail['info']['gameEndTimestamp']
        
        # Chuyển đổi sang datetime
        game_end_time = datetime.fromtimestamp(game_end_timestamp / 1000)
        
        # Tính khoảng thời gian từ bây giờ
        time_diff = datetime.now() - game_end_time
        
        # Format thời gian
        if time_diff.days > 30:
            months = time_diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif time_diff.days > 0:
            return f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            minutes = time_diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
