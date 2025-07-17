#!/usr/bin/env python3
"""
Скрипт для тестирования GitHub Actions локально
Проверяет все необходимые файлы и зависимости перед запуском Actions
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Проверяет существование файла"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - НЕ НАЙДЕН")
        return False

def check_python_version():
    """Проверяет версию Python"""
    version = sys.version_info
    print(f"🐍 Python версия: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Версия Python подходит (3.8+)")
        return True
    else:
        print("❌ Требуется Python 3.8+")
        return False

def check_python_packages():
    """Проверяет установленные Python пакеты"""
    required_packages = [
        'PIL', 'pymem', 'dclimplode', 'numpy', 'cv2', 'tkinter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'cv2':
                import cv2
            elif package == 'PIL':
                import PIL
            elif package == 'pymem':
                import pymem
            elif package == 'dclimplode':
                import dclimplode
            elif package == 'numpy':
                import numpy
                
            print(f"✅ {package} - установлен")
        except ImportError:
            print(f"❌ {package} - НЕ УСТАНОВЛЕН")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_github_workflows():
    """Проверяет наличие GitHub Actions файлов"""
    workflows_dir = Path(".github/workflows")
    required_workflows = [
        "build-installer.yml",
        "build-installer-chocolatey.yml", 
        "build-installer-simple.yml"
    ]
    
    all_exist = True
    
    if not workflows_dir.exists():
        print(f"❌ Директория {workflows_dir} не найдена")
        return False
    
    for workflow in required_workflows:
        workflow_path = workflows_dir / workflow
        if workflow_path.exists():
            print(f"✅ GitHub Action: {workflow}")
        else:
            print(f"❌ GitHub Action: {workflow} - НЕ НАЙДЕН")
            all_exist = False
    
    return all_exist

def check_build_scripts():
    """Проверяет наличие скриптов сборки"""
    required_scripts = [
        ("build_exe.py", "Скрипт сборки EXE"),
        ("build_installer.py", "Скрипт сборки инсталлера"),
        ("download_dependencies.py", "Скрипт загрузки зависимостей"),
        ("installer.nsi", "NSIS скрипт инсталлера")
    ]
    
    all_exist = True
    
    for script, description in required_scripts:
        if check_file_exists(script, description):
            pass
        else:
            all_exist = False
    
    return all_exist

def check_application_files():
    """Проверяет наличие файлов приложения"""
    required_files = [
        ("sourcehold_converter_gui.py", "GUI приложение"),
        ("sourcehold_converter_cli.py", "CLI приложение"),
        ("requirements.txt", "Зависимости Python")
    ]
    
    all_exist = True
    
    for file, description in required_files:
        if check_file_exists(file, description):
            pass
        else:
            all_exist = False
    
    return all_exist

def check_dependencies_directory():
    """Проверяет директорию зависимостей"""
    deps_dir = Path("dependencies")
    
    if deps_dir.exists():
        print(f"✅ Директория зависимостей: {deps_dir}")
        
        # Проверяем наличие файлов зависимостей
        required_deps = [
            "python-3.11.8-amd64.exe",
            "vc_redist.x64.exe"
        ]
        
        for dep in required_deps:
            dep_path = deps_dir / dep
            if dep_path.exists():
                size_mb = dep_path.stat().st_size / (1024 * 1024)
                print(f"  ✅ {dep} ({size_mb:.1f} MB)")
            else:
                print(f"  ❌ {dep} - НЕ НАЙДЕН")
        
        return True
    else:
        print(f"❌ Директория зависимостей: {deps_dir} - НЕ НАЙДЕНА")
        return False

def check_git_status():
    """Проверяет статус Git репозитория"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            print("⚠️  Есть несохраненные изменения в Git:")
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        else:
            print("✅ Git репозиторий чист")
        
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка при проверке Git статуса")
        return False
    except FileNotFoundError:
        print("⚠️  Git не установлен или не найден")
        return False

def check_github_token():
    """Проверяет наличие GitHub токена"""
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    
    if token:
        print("✅ GitHub токен найден")
        return True
    else:
        print("⚠️  GitHub токен не найден (GITHUB_TOKEN или GH_TOKEN)")
        print("   Это нормально для локального тестирования")
        return True

def run_build_test():
    """Запускает тестовую сборку"""
    print("\n🔨 Запуск тестовой сборки...")
    
    try:
        # Тестируем сборку EXE
        print("1. Тестирование сборки EXE...")
        result = subprocess.run(
            [sys.executable, "build_exe.py", "--test"],
            capture_output=True,
            text=True,
            timeout=300  # 5 минут
        )
        
        if result.returncode == 0:
            print("✅ Тестовая сборка EXE прошла успешно")
        else:
            print(f"❌ Ошибка тестовой сборки EXE:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Тестовая сборка превысила лимит времени")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестовой сборке: {e}")
        return False
    
    return True

def main():
    """Основная функция проверки"""
    print("🚀 Проверка готовности к GitHub Actions")
    print("=" * 50)
    
    checks = []
    
    # Проверки
    checks.append(("Python версия", check_python_version()))
    checks.append(("Python пакеты", check_python_packages()))
    checks.append(("GitHub Actions", check_github_workflows()))
    checks.append(("Скрипты сборки", check_build_scripts()))
    checks.append(("Файлы приложения", check_application_files()))
    checks.append(("Директория зависимостей", check_dependencies_directory()))
    checks.append(("Git статус", check_git_status()))
    checks.append(("GitHub токен", check_github_token()))
    
    print("\n" + "=" * 50)
    print("📊 Результаты проверки:")
    
    passed = 0
    total = len(checks)
    
    for check_name, result in checks:
        status = "✅ ПРОЙДЕНА" if result else "❌ ПРОВАЛЕНА"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nИтого: {passed}/{total} проверок пройдено")
    
    if passed == total:
        print("\n🎉 Все проверки пройдены! GitHub Actions готов к запуску.")
        
        # Спрашиваем о тестовой сборке
        try:
            response = input("\nЗапустить тестовую сборку? (y/N): ").lower().strip()
            if response in ['y', 'yes']:
                if run_build_test():
                    print("\n🎉 Тестовая сборка прошла успешно!")
                else:
                    print("\n❌ Тестовая сборка завершилась с ошибками")
        except KeyboardInterrupt:
            print("\n\nТестовая сборка отменена")
            
    else:
        print(f"\n⚠️  {total - passed} проверок не пройдено.")
        print("Исправьте ошибки перед запуском GitHub Actions.")
        
        # Показываем рекомендации
        print("\n📋 Рекомендации:")
        if not check_python_version():
            print("- Установите Python 3.8+")
        if not check_python_packages():
            print("- Установите недостающие Python пакеты: pip install -r requirements.txt")
        if not check_github_workflows():
            print("- Убедитесь, что файлы .github/workflows/ существуют")
        if not check_build_scripts():
            print("- Убедитесь, что все скрипты сборки присутствуют")
        if not check_application_files():
            print("- Убедитесь, что все файлы приложения присутствуют")
        if not check_dependencies_directory():
            print("- Запустите download_dependencies.py для загрузки зависимостей")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)