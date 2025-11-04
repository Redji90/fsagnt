"""Модуль для парсинга PDF файлов с результатами фигурного катания"""
import pdfplumber
import PyPDF2
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Класс для извлечения текста из PDF файлов"""
    
    def __init__(self, pdf_path: str):
        """
        Инициализация парсера
        
        Args:
            pdf_path: Путь к PDF файлу
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF файл не найден: {pdf_path}")
    
    def extract_text(self) -> str:
        """
        Извлекает весь текст из PDF файла
        
        Returns:
            Строка с текстом из PDF
        """
        text_content = []
        
        # Пробуем использовать pdfplumber (лучше для таблиц)
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            if text_content:
                return "\n\n".join(text_content)
        except Exception as e:
            logger.warning(f"Ошибка при использовании pdfplumber: {e}, пробуем PyPDF2")
        
        # Fallback на PyPDF2
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            return "\n\n".join(text_content)
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста из PDF: {e}")
            raise
    
    def extract_tables(self) -> List[Dict]:
        """
        Извлекает таблицы из PDF (если есть)
        
        Returns:
            Список словарей с данными таблиц
        """
        tables = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_tables = page.extract_tables()
                    for table in page_tables:
                        if table:
                            tables.append({
                                'page': page_num,
                                'data': table
                            })
        except Exception as e:
            logger.warning(f"Ошибка при извлечении таблиц: {e}")
        
        return tables
    
    def get_structured_data(self) -> Dict:
        """
        Получает структурированные данные из PDF
        
        Returns:
            Словарь с текстом и таблицами
        """
        return {
            'text': self.extract_text(),
            'tables': self.extract_tables(),
            'filename': self.pdf_path.name
        }




