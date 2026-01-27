# Excel fayllar bilan ishlash moduli
import pandas as pd
import os
import json
from typing import Dict, List, Optional
from config import EXCEL_FILES_DIR, EXCEL_COLUMNS

class ExcelHandler:
    """Excel fayllar bilan ishlash uchun klass"""
    
    def __init__(self):
        self.excel_files = []
        self.cached_data = {}
        self.load_existing_files()
    
    def load_existing_files(self):
        """Mavjud Excel fayllarini yuklash"""
        if not os.path.exists(EXCEL_FILES_DIR):
            os.makedirs(EXCEL_FILES_DIR)
            return
        
        for file in os.listdir(EXCEL_FILES_DIR):
            if file.endswith('.xlsx'):
                self.excel_files.append(file)
                self.cache_excel_data(file)
    
    def cache_excel_data(self, filename: str):
        """Excel fayl ma'lumotlarini keshga yuklash"""
        try:
            file_path = os.path.join(EXCEL_FILES_DIR, filename)
            df = pd.read_excel(file_path)
            
            # ID ustunini string formatiga o'tkazish
            if 'ID' in df.columns:
                df['ID'] = df['ID'].astype(str)
            
            self.cached_data[filename] = df
            print(f"✅ {filename} fayli keshlandi")
        except Exception as e:
            print(f"❌ {filename} faylini keshlashda xatolik: {e}")
    
    def add_excel_file(self, file_path: str) -> bool:
        """Yangi Excel fayl qo'shish"""
        try:
            filename = os.path.basename(file_path)
            
            # Faylni tekshirish
            if not filename.endswith('.xlsx'):
                return False
            
            # Fayl papkaga ko'chirish
            destination = os.path.join(EXCEL_FILES_DIR, filename)
            import shutil
            shutil.move(file_path, destination)
            
            # Fayl ro'yxatiga qo'shish
            if filename not in self.excel_files:
                self.excel_files.append(filename)
            
            # Keshlash
            self.cache_excel_data(filename)
            
            return True
        except Exception as e:
            print(f"❌ Excel faylni qo'shishda xatolik: {e}")
            return False
    
    def search_by_id(self, user_id: str) -> Optional[Dict]:
        """Barcha Excel fayllaridan ID bo'yicha qidiruv"""
        user_id = str(user_id).zfill(6)  # 6 xonali qilish
        
        for filename, df in self.cached_data.items():
            if 'ID' in df.columns:
                # ID bo'yicha qidiruv
                result = df[df['ID'] == user_id]
                if not result.empty:
                    row = result.iloc[0]
                    return {
                        'ID': str(row.get('ID', '')),
                        'Ism': str(row.get('Ism', '')),
                        'Familiya': str(row.get('Familiya', '')),
                        'Fan': str(row.get('Fan', '')),
                        'Sana': str(row.get('Sana', '')),
                        'Xona': str(row.get('Xona', '')),
                        'source_file': filename
                    }
        
        return None
    
    def get_file_list(self) -> List[str]:
        """Excel fayllar ro'yxatini olish"""
        return self.excel_files.copy()
    
    def remove_file(self, filename: str) -> bool:
        """Excel faylni o'chirish"""
        try:
            if filename in self.excel_files:
                self.excel_files.remove(filename)
            
            if filename in self.cached_data:
                del self.cached_data[filename]
            
            file_path = os.path.join(EXCEL_FILES_DIR, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"❌ Faylni o'chirishda xatolik: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Statistika olish"""
        total_records = 0
        for df in self.cached_data.values():
            total_records += len(df)
        
        return {
            'files_count': len(self.excel_files),
            'total_records': total_records,
            'files': self.excel_files
        }
