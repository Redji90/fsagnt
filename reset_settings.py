"""Скрипт для сброса настроек бота"""
import os
import shutil
from pathlib import Path

def reset_settings():
    """Сброс всех настроек бота"""
    print("🔄 Сброс настроек бота...\n")
    
    # Директории для очистки
    uploads_dir = Path("uploads")
    analysis_dir = Path("analysis")
    
    # Очищаем директории
    dirs_to_clean = [uploads_dir, analysis_dir]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            try:
                # Удаляем все файлы в директории
                for file in dir_path.iterdir():
                    if file.is_file():
                        file.unlink()
                        print(f"✅ Удален файл: {file}")
                print(f"✅ Директория {dir_path} очищена")
            except Exception as e:
                print(f"❌ Ошибка при очистке {dir_path}: {e}")
        else:
            print(f"ℹ️  Директория {dir_path} не существует")
    
    # Работа с .env файлом
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print(f"\n📝 Файл .env найден")
        response = input("Удалить текущий .env файл? (y/n): ").strip().lower()
        if response == 'y':
            try:
                env_file.unlink()
                print("✅ Файл .env удален")
            except Exception as e:
                print(f"❌ Ошибка при удалении .env: {e}")
        else:
            print("ℹ️  Файл .env сохранен")
    
    # Создаем .env.example если его нет
    if not env_example.exists():
        print(f"\n📝 Создаю файл .env.example...")
        env_example_content = """# Telegram Bot Token
# Получите у @BotFather в Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenAI API Key
# Получите на https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Модель OpenAI (по умолчанию: gpt-4)
OPENAI_MODEL=gpt-4

# Максимальный размер PDF файла в МБ (по умолчанию: 10)
MAX_PDF_SIZE_MB=10
"""
        try:
            env_example.write_text(env_example_content, encoding='utf-8')
            print("✅ Файл .env.example создан")
        except Exception as e:
            print(f"❌ Ошибка при создании .env.example: {e}")
    
    print("\n✨ Сброс настроек завершен!")
    print("\n📋 Следующие шаги:")
    print("1. Если нужно, создайте новый .env файл на основе .env.example")
    print("2. Заполните токены и ключи в .env файле")
    print("3. Запустите бота: python bot.py")


if __name__ == "__main__":
    reset_settings()



