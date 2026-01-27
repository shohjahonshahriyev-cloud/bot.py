# Ma'lumotlar bazasi bilan ishlash moduli
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from config import USERS_DB, STATS_FILE

class Database:
    """Foydalanuvchilar va statistika ma'lumotlarini saqlash uchun klass"""
    
    def __init__(self):
        self.users = {}
        self.stats = {
            'total_users': 0,
            'total_searches': 0,
            'total_files': 0,
            'daily_searches': {},
            'user_activity': {}
        }
        self.load_data()
    
    def load_data(self):
        """Ma'lumotlarni fayldan yuklash"""
        try:
            # Foydalanuvchilar ma'lumotlari
            if os.path.exists(USERS_DB):
                with open(USERS_DB, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            
            # Statistika ma'lumotlari
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
        except Exception as e:
            print(f"❌ Ma'lumotlarni yuklashda xatolik: {e}")
    
    def save_data(self):
        """Ma'lumotlarni faylga saqlash"""
        try:
            # Papkalar yaratish
            os.makedirs(os.path.dirname(USERS_DB), exist_ok=True)
            os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
            
            # Foydalanuvchilar ma'lumotlari
            with open(USERS_DB, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            
            # Statistika ma'lumotlari
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ma'lumotlarni saqlashda xatolik: {e}")
    
    def add_user(self, user_id: int, username: str = None, full_name: str = None):
        """Yangi foydalanuvchi qo'shish"""
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                'username': username,
                'full_name': full_name,
                'joined_date': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat(),
                'search_count': 0
            }
            self.stats['total_users'] = len(self.users)
            self.save_data()
    
    def update_user_activity(self, user_id: int):
        """Foydalanuvchi faoliyatini yangilash"""
        if str(user_id) in self.users:
            self.users[str(user_id)]['last_active'] = datetime.now().isoformat()
            self.save_data()
    
    def increment_search_count(self, user_id: int):
        """Qidiruv sonini oshirish"""
        if str(user_id) in self.users:
            self.users[str(user_id)]['search_count'] += 1
        
        # Umumiy statistikani yangilash
        self.stats['total_searches'] += 1
        
        # Kunlik statistika
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.stats['daily_searches']:
            self.stats['daily_searches'][today] = 0
        self.stats['daily_searches'][today] += 1
        
        self.save_data()
    
    def get_all_users(self) -> List[int]:
        """Barcha foydalanuvchi IDlarini olish"""
        return [int(uid) for uid in self.users.keys()]
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchi ma'lumotlarini olish"""
        return self.users.get(str(user_id))
    
    def update_files_count(self, count: int):
        """Fayllar sonini yangilash"""
        self.stats['total_files'] = count
        self.save_data()
    
    def get_stats(self) -> Dict:
        """Statistikani olish"""
        return self.stats.copy()
    
    def get_daily_stats(self, days: int = 7) -> Dict:
        """Oxirgi kunlar statistikasi"""
        from datetime import timedelta
        
        daily_stats = {}
        end_date = datetime.now()
        
        for i in range(days):
            date = (end_date - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_stats[date] = self.stats['daily_searches'].get(date, 0)
        
        return daily_stats
