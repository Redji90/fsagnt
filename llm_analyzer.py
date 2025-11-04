"""Модуль для анализа результатов фигурного катания через LLM"""
from openai import OpenAI
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class FigureSkatingAnalyzer:
    """Класс для анализа результатов фигурного катания с помощью LLM"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Инициализация анализатора
        
        Args:
            api_key: OpenAI API ключ
            model: Модель для использования
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def analyze_results(self, pdf_text: str, tables: list = None) -> str:
        """
        Анализирует результаты фигурного катания из PDF
        
        Args:
            pdf_text: Текст, извлеченный из PDF
            tables: Список таблиц из PDF (опционально)
        
        Returns:
            Строка с анализом результатов
        """
        # Формируем промпт для анализа
        prompt = self._create_analysis_prompt(pdf_text, tables)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по фигурному катанию. Твоя задача - анализировать результаты соревнований и предоставлять подробный анализ."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content
            return analysis
        
        except Exception as e:
            logger.error(f"Ошибка при анализе через LLM: {e}")
            raise
    
    def _create_analysis_prompt(self, pdf_text: str, tables: list = None) -> str:
        """
        Создает промпт для анализа
        
        Args:
            pdf_text: Текст из PDF
            tables: Таблицы из PDF
        
        Returns:
            Сформированный промпт
        """
        prompt = """Проанализируй результаты соревнований по фигурному катанию, представленные ниже.

Текст из PDF:
{}

""".format(pdf_text[:4000])  # Ограничиваем длину для экономии токенов
        
        if tables:
            prompt += "\n\nДополнительно найдены таблицы с результатами:\n"
            for idx, table in enumerate(tables[:3], 1):  # Берем первые 3 таблицы
                prompt += f"\nТаблица {idx} (страница {table.get('page', '?')}):\n"
                if table.get('data'):
                    # Показываем первые строки таблицы
                    for row in table['data'][:5]:
                        prompt += str(row) + "\n"
        
        prompt += """

Пожалуйста, предоставь подробный анализ, включающий:
1. Название соревнования и дату (если указаны)
2. Категории и дисциплины (мужское/женское одиночное, парное, танцы на льду)
3. Топ-3 спортсмена/пары в каждой категории
4. Основные достижения и рекорды
5. Ключевые моменты и интересные факты
6. Сравнение с предыдущими результатами (если есть информация)

Анализ должен быть структурированным и легко читаемым."""
        
        return prompt
    
    def get_summary(self, pdf_text: str) -> str:
        """
        Получает краткое резюме результатов
        
        Args:
            pdf_text: Текст из PDF
        
        Returns:
            Краткое резюме
        """
        prompt = f"""Дай краткое резюме (2-3 предложения) результатов соревнований по фигурному катанию:

{pdf_text[:2000]}

Резюме должно включать: тип соревнования, главных победителей, основные результаты."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты эксперт по фигурному катанию."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Ошибка при получении резюме: {e}")
            raise




