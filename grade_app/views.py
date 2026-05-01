import os
import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from xml.etree import ElementTree as ET
from .forms import StudentForm
from .models import StudentGrade
from . import utils

def home(request):
    form = StudentForm()
    if request.method == 'POST':
        if 'save_data' in request.POST:
            form = StudentForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                storage = data.pop('storage_type')
                if storage == 'database':
                    if StudentGrade.objects.filter(
                        full_name__iexact=data['full_name'],
                        subject__iexact=data['subject'],
                        date=data['date']
                    ).exists():
                        messages.warning(request, "️ Такая запись уже есть в базе данных.")
                    else:
                        try:
                            StudentGrade.objects.create(**data)
                            messages.success(request, "✅ Данные сохранены в базу данных.")
                        except IntegrityError:
                            messages.error(request, "❌ Ошибка БД: запись уже существует.")
                else:
                    ext = 'json' if storage == 'file_json' else 'xml'
                    filename = utils.generate_filename(data['full_name'], data['subject'], ext)
                    filepath = os.path.join(utils.DATA_DIR, filename)
                    try:
                        if ext == 'json':
                            with open(filepath, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                        else:
                            root = ET.Element('student')
                            for k, v in data.items():
                                el = ET.SubElement(root, k)
                                el.text = str(v)
                            ET.indent(root, space="  ")
                            with open(filepath, 'wb') as f:
                                f.write(ET.tostring(root, encoding='utf-8', xml_declaration=True))
                        messages.success(request, f"✅ Данные сохранены в файл: {filename}")
                    except Exception as e:
                        messages.error(request, f"❌ Ошибка сохранения: {e}")
                return redirect('home')
            else:
                messages.error(request, " Ошибка валидации формы.")

        elif 'upload_file' in request.POST:
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                messages.error(request, " Файл не выбран.")
                return redirect('home')
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            if ext not in ['.json', '.xml']:
                messages.error(request, "❌ Разрешены только .json и .xml.")
                return redirect('home')
            temp_name = f"temp_{utils.generate_filename('upload', 'file', ext.lstrip('.'))}"
            temp_path = os.path.join(utils.DATA_DIR, temp_name)
            with open(temp_path, 'wb+') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            validator = utils.validate_and_parse_json if ext == '.json' else utils.validate_and_parse_xml
            parsed_data, error = validator(temp_path)
            if error:
                os.remove(temp_path)
                messages.error(request, f"❌ Файл невалиден: {error}. Удалён.")
            else:
                final_name = utils.generate_filename(parsed_data['full_name'], parsed_data['subject'], ext.lstrip('.'))
                final_path = os.path.join(utils.DATA_DIR, final_name)
                os.rename(temp_path, final_path)
                messages.success(request, f"✅ Файл загружен: {final_name}")
            return redirect('home')
    return render(request, 'grade_app/home.html', {'form': form})

def file_list(request):
    os.makedirs(utils.DATA_DIR, exist_ok=True)
    files_data = []
    for fname in os.listdir(utils.DATA_DIR):
        if not fname.endswith(('.json', '.xml')) or fname.startswith('temp_'):
            continue
        fpath = os.path.join(utils.DATA_DIR, fname)
        validator = utils.validate_and_parse_json if fname.endswith('.json') else utils.validate_and_parse_xml
        data, err = validator(fpath)
        if data and not err:
            data['filename'] = fname
            data['format'] = 'JSON' if fname.endswith('.json') else 'XML'
            files_data.append(data)
    return render(request, 'grade_app/list.html', {'files': files_data, 'source_type': 'file'})

def db_list(request):
    queryset = StudentGrade.objects.all().order_by('-created_at')
    paginator = Paginator(queryset, 10)
    page = request.GET.get('page', 1)
    records = paginator.get_page(page)
    return render(request, 'grade_app/list.html', {'records': records, 'source_type': 'database'})

@require_http_methods(["GET"])
def ajax_search(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': [], 'message': 'Минимум 2 символа'})
    results = StudentGrade.objects.filter(
        Q(full_name__icontains=query) | Q(group_number__icontains=query) | Q(subject__icontains=query)
    ).values('id', 'full_name', 'group_number', 'subject', 'grade', 'date')[:20]
    return JsonResponse({'results': list(results), 'count': len(results)})

def edit_record(request, pk):
    record = get_object_or_404(StudentGrade, pk=pk)
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        group_number = request.POST.get('group_number', '').strip()
        subject = request.POST.get('subject', '').strip()
        grade = request.POST.get('grade')
        date = request.POST.get('date', '').strip()
        errors = []
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-]+$', full_name): errors.append("ФИО: недопустимые символы.")
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', date): errors.append("Дата: ДД-ММ-ГГГГ.")
        try:
            grade = int(grade)
            if not (2 <= grade <= 5): errors.append("Оценка: 2-5.")
        except (ValueError, TypeError): errors.append("Оценка: целое число.")
        if errors:
            for e in errors: messages.error(request, f"❌ {e}")
            return redirect('db_list')
        if StudentGrade.objects.exclude(pk=pk).filter(full_name__iexact=full_name, subject__iexact=subject, date=date).exists():
            messages.warning(request, "⚠️ Такая запись уже существует.")
            return redirect('db_list')
        record.full_name, record.group_number, record.subject, record.grade, record.date = full_name, group_number, subject, grade, date
        record.save()
        messages.success(request, "✅ Запись обновлена.")
        return redirect('db_list')
    return render(request, 'grade_app/edit.html', {'record': record})

def delete_record(request, pk):
    record = get_object_or_404(StudentGrade, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, "🗑️ Запись удалена.")
    return redirect('db_list')