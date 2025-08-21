#!/usr/bin/env python3
"""
Скрипт для публикации пакета в PyPI
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Выполнение команды с описанием"""
    print(f"🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - успешно")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} - ошибка")
        if result.stderr:
            print(result.stderr)
        return False
    
    return True


def check_requirements():
    """Проверка требований для публикации"""
    print("📋 Проверка требований...")
    
    required_files = ["README.md", "LICENSE", "setup.py", "pyproject.toml"]
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    print("✅ Все необходимые файлы найдены")
    return True


def build_package():
    """Сборка пакета"""
    if not run_command("python -m build", "Сборка пакета"):
        return False
    
    # Проверяем созданные файлы
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ Директория dist не создана")
        return False
    
    wheel_files = list(dist_dir.glob("*.whl"))
    tar_files = list(dist_dir.glob("*.tar.gz"))
    
    if not wheel_files or not tar_files:
        print("❌ Не все файлы дистрибуции созданы")
        return False
    
    print(f"✅ Созданы файлы:")
    for file in wheel_files + tar_files:
        print(f"  - {file.name}")
    
    return True


def test_package():
    """Тестирование пакета"""
    print("🧪 Тестирование пакета...")
    
    test_script = '''
import requests_ai_validator
session = requests_ai_validator.AISession()
print("✅ Пакет импортируется корректно")
'''
    
    return run_command(f'python -c "{test_script}"', "Тестирование импорта")


def publish_to_test_pypi():
    """Публикация в Test PyPI"""
    print("📤 Публикация в Test PyPI...")
    
    cmd = "python -m twine upload --repository testpypi dist/*"
    print(f"Команда: {cmd}")
    print("Вам потребуется логин для Test PyPI")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def publish_to_pypi():
    """Публикация в PyPI"""
    print("📤 Публикация в PyPI...")
    
    confirm = input("Вы уверены, что хотите опубликовать в PyPI? (yes/no): ")
    if confirm.lower() != "yes":
        print("❌ Публикация отменена")
        return False
    
    cmd = "python -m twine upload dist/*"
    print(f"Команда: {cmd}")
    print("Вам потребуется логин для PyPI")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    """Главная функция"""
    print("📦 Публикация requests-ai-validator в PyPI")
    print("=" * 60)
    
    # Проверяем зависимости для публикации
    try:
        import build
        import twine
    except ImportError:
        print("❌ Установите зависимости для публикации:")
        print("pip install build twine")
        return
    
    print("Выберите действие:")
    print("1. Проверить пакет")
    print("2. Собрать пакет")
    print("3. Тестировать пакет")
    print("4. Опубликовать в Test PyPI")
    print("5. Опубликовать в PyPI")
    print("6. Полный цикл (1-4)")
    print("0. Выход")
    
    while True:
        choice = input("\nВведите номер (0-6): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            check_requirements()
        elif choice == "2":
            if check_requirements():
                build_package()
        elif choice == "3":
            test_package()
        elif choice == "4":
            if Path("dist").exists():
                publish_to_test_pypi()
            else:
                print("❌ Сначала соберите пакет (опция 2)")
        elif choice == "5":
            if Path("dist").exists():
                publish_to_pypi()
            else:
                print("❌ Сначала соберите пакет (опция 2)")
        elif choice == "6":
            if (check_requirements() and 
                build_package() and 
                test_package()):
                print("\n🎯 Готов к публикации в Test PyPI")
                if input("Опубликовать в Test PyPI? (y/n): ").lower() == 'y':
                    publish_to_test_pypi()
        else:
            print("❌ Неверный выбор")


if __name__ == "__main__":
    main()
