import os
import re
import json
from datetime import datetime
from xml.etree import ElementTree as ET
from django.conf import settings

DATA_DIR = getattr(settings, 'DATA_DIR', os.path.join(settings.BASE_DIR, 'data', 'logs'))
os.makedirs(DATA_DIR, exist_ok=True)

def sanitize_text(text: str) -> str:
    """Оставляет только буквы (кириллица/латиница), цифры, пробелы и дефисы."""
    cleaned = re.sub(r'[^A-Za-zА-Яа-яЁё0-9\s\-]', '', text)
    return cleaned.strip().replace(' ', '_')[:50] or 'data'

def generate_filename(full_name: str, subject: str, ext: str) -> str:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{ts}_{sanitize_text(full_name)}_{sanitize_text(subject)}.{ext}"

def validate_and_parse_json(filepath: str):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        required = {'full_name', 'group_number', 'subject', 'grade', 'date'}
        if not isinstance(data, dict) or not required.issubset(data.keys()):
            return None, "Отсутствуют обязательные поля JSON."
        if not isinstance(data['grade'], int) or not (2 <= data['grade'] <= 5):
            return None, "Оценка должна быть целым числом от 2 до 5."
        data['grade'] = int(data['grade'])
        return data, None
    except json.JSONDecodeError:
        return None, "Файл не является валидным JSON."
    except Exception as e:
        return None, f"Ошибка чтения: {str(e)}"

def validate_and_parse_xml(filepath: str):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        if root.tag != 'student':
            return None, "Корневой тег XML должен быть <student>."
        children = {child.tag: child.text for child in root}
        required = {'full_name', 'group_number', 'subject', 'grade', 'date'}
        if not required.issubset(children.keys()):
            return None, "Отсутствуют обязательные теги XML."
        try:
            grade = int(children['grade'])
            if not (2 <= grade <= 5):
                return None, "Оценка должна быть от 2 до 5."
            children['grade'] = grade
        except ValueError:
            return None, "Оценка должна быть целым числом."
        return children, None
    except ET.ParseError:
        return None, "Файл не является валидным XML."
    except Exception as e:
        return None, f"Ошибка чтения: {str(e)}"