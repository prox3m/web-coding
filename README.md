#  Arkanoid Backend + Game

Серверная часть браузерной игры "Арканоид" (Лабораторная работа).
Разработано на Django + Django REST Framework + PostgreSQL.

## 🛠 Стек технологий
- **Backend:** Python 3.11, Django 4.2, DRF
- **Database:** PostgreSQL 15
- **Infrastructure:** Docker, Docker Compose
- **Frontend:** Vanilla JS, Canvas API

##  Запуск проекта

### Вариант 1: Docker (Рекомендуемый)
```bash
docker-compose up --build -d
docker-compose exec web python manage.py createsuperuser

python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver