import os
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from xml.etree import ElementTree as ET
from .forms import StudentForm
from . import utils

def home(request):
    if request.method == 'POST':
        if 'save_data' in request.POST:
            form = StudentForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                ext = data.pop('export_format')
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
                        ET.indent(root, space="  ") # Python 3.9+
                        with open(filepath, 'wb') as f:
                            f.write(ET.tostring(root, encoding='utf-8', xml_declaration=True))
                    messages.success(request, f"✅ Данные сохранены: {filename}")
                except Exception as e:
                    messages.error(request, f"❌ Ошибка сохранения: {e}")
                return redirect('home')
            else:
                messages.error(request, "❌ Ошибка валидации формы. Проверьте поля.")
                
        elif 'upload_file' in request.POST:
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                messages.error(request, "❌ Файл не выбран.")
                return redirect('home')
                
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            if ext not in ['.json', '.xml']:
                messages.error(request, "❌ Разрешены только .json и .xml файлы.")
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
                messages.error(request, f"❌ Файл невалиден: {error}. Файл удален.")
            else:
                final_name = utils.generate_filename(parsed_data['full_name'], parsed_data['subject'], ext.lstrip('.'))
                final_path = os.path.join(utils.DATA_DIR, final_name)
                os.rename(temp_path, final_path)
                messages.success(request, f"✅ Файл успешно загружен: {final_name}")
            return redirect('home')
    else:
        form = StudentForm()
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
            
    context = {'files': files_data}
    return render(request, 'grade_app/list.html', context)