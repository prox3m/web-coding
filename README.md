# ☕ Coffee Shop REST API

RESTful API для интернет-магазина кофе, реализованное на Django + Django Rest Framework.

## 🚀 Требования
- Python 3.10+
- PostgreSQL (или SQLite для разработки)
- pip

## 🛠 Установка и запуск
```bash
# 1. Клонировать репозиторий и перейти в папку
git clone <your-repo-url>
cd coffee_api

# 2. Создать виртуальное окружение и активировать
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить переменные окружения
cp .env.example .env
# Отредактируйте .env, при необходимости измените SECRET_KEY

# 5. Применить миграции
python manage.py migrate

# 6. Создать суперпользователя (для админки)
python manage.py createsuperuser

# 7. Запустить сервер
python manage.py runserver