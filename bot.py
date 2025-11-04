"""Основной файл телеграм-бота для анализа результатов фигурного катания"""
import logging
import os
from pathlib import Path
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ChatAction

from config import (
    TELEGRAM_BOT_TOKEN,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    MAX_PDF_SIZE_BYTES,
    UPLOAD_DIR,
    ANALYSIS_DIR
)
from pdf_parser import PDFParser
from llm_analyzer import FigureSkatingAnalyzer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация анализатора
analyzer = FigureSkatingAnalyzer(OPENAI_API_KEY, OPENAI_MODEL)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_message = """
🏅 Добро пожаловать в бота для анализа результатов фигурного катания!

Этот бот может анализировать PDF файлы с результатами соревнований по фигурному катанию.

📋 Доступные команды:
/start - Начать работу с ботом
/help - Показать справку
/analyze - Инструкция по анализу файлов

📎 Как использовать:
1. Отправьте PDF файл с результатами соревнований
2. Бот автоматически извлечет данные и проанализирует их
3. Получите подробный анализ результатов

Приятного использования! ⛸️
"""
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
📖 Справка по использованию бота:

1. Отправьте PDF файл с результатами соревнований по фигурному катанию
2. Бот автоматически:
   - Извлечет текст и таблицы из PDF
   - Проанализирует результаты через LLM
   - Предоставит подробный анализ

⚠️ Требования к файлу:
- Формат: PDF
- Максимальный размер: 10 МБ
- Файл должен содержать результаты соревнований

💡 Примеры того, что бот может проанализировать:
- Протоколы соревнований
- Результаты чемпионатов
- Итоговые таблицы
- Оценочные ведомости

Для начала работы отправьте PDF файл!
"""
    await update.message.reply_text(help_text)


async def analyze_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /analyze"""
    info_text = """
📊 Инструкция по анализу:

1. Подготовьте PDF файл с результатами
2. Отправьте файл боту
3. Дождитесь обработки (может занять 10-30 секунд)
4. Получите подробный анализ

Бот анализирует:
✅ Название и дату соревнований
✅ Категории и дисциплины
✅ Топ-3 спортсменов
✅ Достижения и рекорды
✅ Ключевые моменты

Отправьте PDF файл для начала анализа!
"""
    await update.message.reply_text(info_text)


async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик получения PDF файла"""
    user = update.effective_user
    message = update.message
    
    if not message.document:
        await message.reply_text("❌ Пожалуйста, отправьте PDF файл.")
        return
    
    # Проверяем тип файла
    if not message.document.mime_type or "pdf" not in message.document.mime_type.lower():
        await message.reply_text("❌ Файл должен быть в формате PDF.")
        return
    
    # Проверяем размер файла
    if message.document.file_size > MAX_PDF_SIZE_BYTES:
        await message.reply_text(
            f"❌ Файл слишком большой. Максимальный размер: {MAX_PDF_SIZE_BYTES / 1024 / 1024:.1f} МБ"
        )
        return
    
    # Отправляем сообщение о начале обработки
    status_message = await message.reply_text("⏳ Обрабатываю PDF файл...")
    
    try:
        # Скачиваем файл
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
        
        file = await context.bot.get_file(message.document.file_id)
        file_path = Path(UPLOAD_DIR) / f"{message.document.file_id}.pdf"
        
        await file.download_to_drive(file_path)
        
        await status_message.edit_text("📄 Извлекаю данные из PDF...")
        
        # Парсим PDF
        parser = PDFParser(str(file_path))
        pdf_data = parser.get_structured_data()
        
        if not pdf_data['text'] or len(pdf_data['text'].strip()) < 50:
            await status_message.edit_text(
                "❌ Не удалось извлечь текст из PDF. Убедитесь, что файл содержит текст (не только изображения)."
            )
            file_path.unlink()  # Удаляем файл
            return
        
        await status_message.edit_text("🤖 Анализирую результаты через AI...")
        
        # Анализируем через LLM
        analysis = analyzer.analyze_results(
            pdf_data['text'],
            pdf_data['tables']
        )
        
        # Сохраняем анализ
        analysis_path = Path(ANALYSIS_DIR) / f"{message.document.file_id}.txt"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            f.write(f"Анализ файла: {pdf_data['filename']}\n\n")
            f.write(analysis)
        
        # Отправляем результат
        result_message = f"""
✅ Анализ завершен!

📄 Файл: {pdf_data['filename']}

📊 Результаты анализа:

{analysis}

---
💾 Полный анализ сохранен локально.
"""
        
        # Разбиваем на части если сообщение слишком длинное
        max_length = 4000
        if len(result_message) > max_length:
            # Отправляем первую часть
            await status_message.edit_text(result_message[:max_length])
            # Отправляем остальные части
            remaining = result_message[max_length:]
            while remaining:
                await message.reply_text(remaining[:max_length])
                remaining = remaining[max_length:]
        else:
            await status_message.edit_text(result_message)
        
        # Удаляем временный файл
        file_path.unlink()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке PDF: {e}", exc_info=True)
        await status_message.edit_text(
            f"❌ Произошла ошибка при обработке файла: {str(e)}\n\n"
            "Попробуйте еще раз или проверьте формат файла."
        )
        
        # Удаляем файл в случае ошибки
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    await update.message.reply_text(
        "📎 Отправьте PDF файл с результатами соревнований для анализа.\n\n"
        "Используйте /help для получения справки."
    )


def main():
    """Основная функция запуска бота"""
    logger.info("Запуск бота...")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze_info))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Запускаем бота
    logger.info("Бот запущен и готов к работе!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()




