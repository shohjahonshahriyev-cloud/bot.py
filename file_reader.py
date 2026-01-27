import pandas as pd
from docx import Document
import PyPDF2
import pdfplumber
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

class FileReader:
    """Fayllarni o'qish va ID orqali ma'lumot qidirish uchun klass"""
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.docx', '.pdf']
    
    def read_excel(self, file_path: str) -> Dict[str, Any]:
        """Excel faylidan ma'lumotlarni o'qish"""
        try:
            df = pd.read_excel(file_path)
            return {
                'type': 'excel',
                'data': df.to_dict('records'),
                'columns': df.columns.tolist(),
                'shape': df.shape
            }
        except Exception as e:
            return {'error': f"Excel faylini o'qishda xatolik: {str(e)}"}
    
    def read_word(self, file_path: str) -> Dict[str, Any]:
        """Word faylidan ma'lumotlarni o'qish"""
        try:
            doc = Document(file_path)
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text.strip())
            
            return {
                'type': 'word',
                'data': paragraphs,
                'paragraphs_count': len(paragraphs)
            }
        except Exception as e:
            return {'error': f"Word faylini o'qishda xatolik: {str(e)}"}
    
    def read_pdf(self, file_path: str) -> Dict[str, Any]:
        """PDF faylidan ma'lumotlarni o'qish"""
        try:
            text_content = []
            
            # PdfPlumber bilan o'qish (yaxshi natija beradi)
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
            except:
                pass
            
            # Agar pdfplumber ishlamasa, PyPDF2 dan foydalanamiz
            if not text_content:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
            
            return {
                'type': 'pdf',
                'data': text_content,
                'pages_count': len(text_content)
            }
        except Exception as e:
            return {'error': f"PDF faylini o'qishda xatolik: {str(e)}"}
    
    def search_by_id(self, file_path: str, search_id: str) -> Dict[str, Any]:
        """Faylda ID orqali ma'lumot qidirish"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in self.supported_formats:
            return {'error': f"Qo'llab-quvvatlanmaydigan fayl formati: {file_ext}"}
        
        # Fayl turiga qarab o'qish
        if file_ext in ['.xlsx', '.xls']:
            result = self.read_excel(file_path)
            if 'error' in result:
                return result
            
            # Excel da ID qidirish
            matches = []
            for row in result['data']:
                for key, value in row.items():
                    if str(value).strip() == str(search_id).strip():
                        matches.append(row)
                        break
            
            return {
                'file_type': 'excel',
                'search_id': search_id,
                'matches': matches,
                'matches_count': len(matches)
            }
        
        elif file_ext == '.docx':
            result = self.read_word(file_path)
            if 'error' in result:
                return result
            
            # Word da ID qidirish
            matches = []
            for i, paragraph in enumerate(result['data']):
                if str(search_id).strip() in paragraph:
                    matches.append({
                        'paragraph_index': i + 1,
                        'text': paragraph
                    })
            
            return {
                'file_type': 'word',
                'search_id': search_id,
                'matches': matches,
                'matches_count': len(matches)
            }
        
        elif file_ext == '.pdf':
            result = self.read_pdf(file_path)
            if 'error' in result:
                return result
            
            # PDF da ID qidirish
            matches = []
            for i, page_text in enumerate(result['data']):
                if str(search_id).strip() in page_text:
                    # ID atrofidagi matnni olish
                    lines = page_text.split('\n')
                    for j, line in enumerate(lines):
                        if str(search_id).strip() in line:
                            matches.append({
                                'page': i + 1,
                                'line': j + 1,
                                'text': line.strip()
                            })
            
            return {
                'file_type': 'pdf',
                'search_id': search_id,
                'matches': matches,
                'matches_count': len(matches)
            }
    
    def search_in_directory(self, directory_path: str, search_id: str) -> Dict[str, Any]:
        """Papkadagi barcha fayllarda ID qidirish"""
        directory = Path(directory_path)
        if not directory.exists():
            return {'error': f"Papka mavjud emas: {directory_path}"}
        
        all_results = {}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                result = self.search_by_id(str(file_path), search_id)
                if 'matches' in result and result['matches']:
                    all_results[str(file_path)] = result
        
        return {
            'directory': directory_path,
            'search_id': search_id,
            'total_files_with_matches': len(all_results),
            'results': all_results
        }
