import os
import subprocess
import shutil


def run_command(cmd):
    """Запускает команду и выводит результат"""
    print(f"🚀 Выполняю: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ Успешно")
            if result.stdout:
                print(f"   Вывод: {result.stdout[:200]}")
        else:
            print(f"❌ Ошибка: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  Исключение: {e}")
        return False


def main():
    print("=" * 60)
    print("ИСПРАВЛЕНИЕ GIT ДЛЯ GITHUB")
    print("=" * 60)

    # 1. Создаем .gitignore
    print("\n1. 📝 Создаем .gitignore...")
    gitignore_content = """# Большие данные (НЕ ЗАГРУЖАТЬ В GITHUB)
data/osm_real/
data/raw/
models/
*.pkl
*.geojson
*.xlsx
*.h5

# OSM кэш
.osm_cache/
__pycache__/
*.py[cod]
*$py.class

# Виртуальное окружение
venv/
.env/
.venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Системные файлы
.DS_Store
Thumbs.db
*.log

# Временные файлы
*.tmp
temp/
tmp/

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Но оставляем тестовые данные
!data/zones_test/
!data/osm_test/
!data/train_test/
!data/zones/perm_points.geojson
!data/zones/sverdlovsk_points.geojson"""

    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✅ .gitignore создан")

    # 2. Удаляем большие файлы из индекса Git
    print("\n2. 🗑️ Удаляем большие файлы из Git...")

    # Удаляем папку osm_real из Git (но оставляем локально)
    run_command('git rm -r --cached data/osm_real/')

    # Удаляем raw файлы
    run_command('git rm --cached data/raw/Пермский край - Население.xlsx')
    run_command('git rm --cached data/raw/Свердловская область - Население.xlsx')

    # Удаляем модели
    run_command('git rm --cached models/*.pkl')

    # 3. Добавляем нужные файлы
    print("\n3. 📦 Добавляем нужные файлы...")

    run_command('git add .gitignore')
    run_command('git add scripts/')
    run_command('git add data/zones/')
    run_command('git add data/zones_test/')
    run_command('git add data/osm_test/')
    run_command('git add data/train_test/')
    run_command('git add *.py')
    run_command('git add *.md')
    run_command('git add requirements.txt')

    # 4. Коммит
    print("\n4. 💾 Создаем коммит...")
    run_command(
        'git commit -m "Remove large files and add .gitignore for GitHub"')

    # 5. Force push
    print("\n5. 🚀 Загружаем на GitHub...")
    response = input("Выполнить force push? (y/n): ")
    if response.lower() == 'y':
        run_command('git push origin main --force')
    else:
        print("⚠️  Пропускаем push. Вы можете сделать это позже:")
        print("   git push origin main --force")

    print("\n" + "=" * 60)
    print("✅ ГОТОВО!")
    print("\nТеперь репозиторий должен загрузиться без ошибок.")
    print("Большие файлы останутся у вас локально, но не будут на GitHub.")


if __name__ == "__main__":
    main()
