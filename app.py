# -*- coding: utf-8 -*-
import streamlit as st
import json
import base64
import io
import re
import math
import random
from PIL import Image
from datetime import datetime
import plotly.graph_objects as go

from core import PracticeEngine

st.set_page_config(page_title="Практическая работа №3", layout="centered", page_icon="📊")

def parse_float(val_str):
    try:
        return float(val_str.strip().replace(',', '.'))
    except:
        return None

def parse_int(val_str):
    try:
        return int(val_str.strip())
    except:
        return None

def draw_gauss_simulation(ans_str):
    val = parse_float(ans_str)
    
    # Строим стандартную кривую Гаусса
    x = [i/10.0 for i in range(-35, 36)]
    y = [math.exp(-0.5 * (v**2)) / math.sqrt(2 * math.pi) for v in x]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='rgba(100,150,250,0.8)', width=3), name='Нормальное распределение'))
    
    if val is not None:
        if val < 0 or val > 1:
            # Аномалия - красим всё в красный
            fig.add_trace(go.Scatter(x=x, y=y, fill='tozeroy', mode='none', fillcolor='rgba(255, 0, 0, 0.4)', name='Критическая ошибка'))
        else:
            # Закрашиваем площадь, пропорциональную введенной вероятности (от центра)
            center = len(x) // 2
            limit = int((len(x) / 2) * val)
            fill_x = x[center-limit:center+limit+1]
            fill_y = y[center-limit:center+limit+1]
            if fill_x:
                fig.add_trace(go.Scatter(x=fill_x, y=fill_y, fill='tozeroy', mode='none', fillcolor='rgba(0, 200, 100, 0.5)', name='Ваш расчет'))

    fig.update_layout(
        height=250, margin=dict(l=10, r=10, t=30, b=10),
        title="Симуляция нагрузки канала (Гаусс)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    st.plotly_chart(fig, use_container_width=True)

def draw_reliability_simulation(ans_str, task_text):
    val = parse_int(ans_str)
    
    # Вытаскиваем параметры из текста задачи с помощью регулярных выражений
    match_def = re.search(r'составляет (\d+)%', task_text)
    p_def = int(match_def.group(1)) / 100.0 if match_def else 0.02
    
    match_tgt = re.search(r'не менее (0\.\d+)', task_text)
    p_tgt = float(match_tgt.group(1)) if match_tgt else 0.95

    max_n = max(val + 50 if val else 150, int(math.log(1-p_tgt)/math.log(1-p_def)) * 2)
    n_vals = list(range(1, max_n, max(1, max_n//50)))
    p_vals = [1 - (1 - p_def)**n for n in n_vals]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=n_vals, y=p_vals, mode='lines', line=dict(color='gray'), name='Вероятность обнаружения'))
    fig.add_hline(y=p_tgt, line_dash="dash", line_color="green", annotation_text="Целевой порог надежности")

    if val is not None and val > 0:
        student_p = 1 - (1 - p_def)**val
        color = 'green' if student_p >= p_tgt else 'red'
        fig.add_trace(go.Scatter(x=[val], y=[student_p], mode='markers', marker=dict(color=color, size=14, line=dict(width=2, color='white')), name='Ваш объем выборки'))

    fig.update_layout(
        height=250, margin=dict(l=10, r=10, t=30, b=10),
        title="Динамика выборки (Асимптота)"
    )
    st.plotly_chart(fig, use_container_width=True)

def draw_poisson_heatmap(ans_str):
    val = parse_float(ans_str)
    
    # Сетка 10x10 ячеек памяти
    z = [[0 for _ in range(10)] for _ in range(10)]
    
    if val is not None:
        if val < 0 or val > 1:
            z = [[1 for _ in range(10)] for _ in range(10)] # Перегрузка (всё красное)
        else:
            errors = int((1 - val) * 100) # Чем ниже вероятность выживания, тем больше ошибок
            rng = random.Random(42) # Фиксированный сид, чтобы карта не мерцала при вводе
            coords = [(r, c) for r in range(10) for c in range(10)]
            error_coords = rng.sample(coords, min(100, max(0, errors)))
            for r, c in error_coords:
                z[r][c] = 1

    fig = go.Figure(data=go.Heatmap(z=z, colorscale=[[0, 'rgba(0,200,100,0.6)'], [1, 'rgba(255,0,0,0.8)']], showscale=False, xgap=2, ygap=2))
    fig.update_layout(
        height=250, margin=dict(l=10, r=10, t=30, b=10),
        title="Тепловая карта сбоев (Пуассон)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    st.plotly_chart(fig, use_container_width=True)


if 'started' not in st.session_state:
    st.session_state.started = False
    st.session_state.student_id = ""
    st.session_state.start_time = None
    st.session_state.report_json = None
    st.session_state.filename = ""

if not st.session_state.started:
    st.title("📚 Практическая работа №3 - ТВиМС")
    st.write("Числовые характеристики ДСВ и предельные теоремы")
    
    with st.container():
        st.info("Введите номер вашей зачетной книжки. От этого номера зависит ваш уникальный вариант.")
        student_id_input = st.text_input("Номер зачетной книжки:", placeholder="Например: 220156")
        
        if st.button("🚀 Начать практику", use_container_width=True):
            if student_id_input.strip():
                st.session_state.student_id = student_id_input.strip()
                st.session_state.started = True
                st.session_state.start_time = datetime.now()
                st.rerun()
            else:
                st.error("Поле не может быть пустым!")

elif st.session_state.started and st.session_state.report_json is None:
    st.title(f"🎓 Практика №3 | Зачетка: {st.session_state.student_id}")
    
    engine = PracticeEngine(st.session_state.student_id)
    variant = engine.generate_variant()
    
    st.warning("⚠️ Для зачета каждой задачи ОБЯЗАТЕЛЬНО необходимо прикрепить фотографию рукописного решения! Можно прикреплять несколько фото.")
    
    # Словари для хранения ответов
    if 'student_answers' not in st.session_state:
        st.session_state.student_answers = {}
    if 'student_photos' not in st.session_state:
        st.session_state.student_photos = {}

    for task_key, task_data in variant.items():
        st.divider()
        if task_key == 'task_99':
            st.markdown(f"### 📝 {task_data['title']}")
            st.write(task_data['text'])
            ans = st.text_input("Краткий комментарий (необязательно):", key=f"ans_{task_key}")
            st.session_state.student_answers[task_key] = ans
            photos = st.file_uploader("📸 Прикрепить фото с ответами (можно несколько)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=f"photo_{task_key}")
            st.session_state.student_photos[task_key] = photos
        else:
            task_num = task_key.split('_')[1]
            st.markdown(f"### 🔹 Задача {task_num}")
            st.write(task_data['text'])
            
            ans = st.text_input("Ваш ответ:", key=f"ans_{task_key}")
            st.session_state.student_answers[task_key] = ans
            
            # Отрисовка интерактивных симуляторов
            if task_key == 'task_1':
                draw_gauss_simulation(ans)
            elif task_key == 'task_3':
                draw_reliability_simulation(ans, task_data['text'])
            elif task_key == 'task_4':
                draw_poisson_heatmap(ans)
                
            photos = st.file_uploader("📸 Прикрепить решение (можно несколько фото)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=f"photo_{task_key}")
            st.session_state.student_photos[task_key] = photos
        
    st.divider()
    if st.button("✅ Завершить и сформировать отчет", use_container_width=True, type="primary"):
        delta = datetime.now() - st.session_state.start_time
        mins = int(delta.total_seconds() // 60)
        secs = int(delta.total_seconds() % 60)
        time_spent_str = f"{mins} мин. {secs} сек."
        
        student_answers_raw = {}
        encrypted_answers = {}
        
        # Сбор текстовых ответов
        for k, text_val in st.session_state.student_answers.items():
            raw_val = text_val.strip().replace(',', '.')
            student_answers_raw[k] = raw_val
            encrypted_answers[k] = base64.b64encode(raw_val[::-1].encode('utf-8')).decode('utf-8')
            
        # Сбор и сжатие фотографий
        for k, file_list in st.session_state.student_photos.items():
            if file_list: 
                compressed_photos = []
                encrypted_photos = []
                for file in file_list:
                    img = Image.open(file).convert("RGB")
                    img.thumbnail((1200, 1200))
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG", quality=75)
                    b64_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    compressed_photos.append(b64_str)
                    encrypted_photos.append(base64.b64encode(b64_str[::-1].encode('utf-8')).decode('utf-8'))
                
                student_answers_raw[f"{k}_photo"] = compressed_photos
                encrypted_answers[f"{k}_photo"] = encrypted_photos
                
        security_hash = engine.generate_security_hash(engine.student_id, student_answers_raw)
        
        report_data = {
            "student_id": engine.student_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "time_spent": time_spent_str,
            "answers": encrypted_answers,
            "verification_key": security_hash
        }
        
        st.session_state.report_json = json.dumps(report_data, ensure_ascii=False, indent=4)
        st.session_state.filename = f"Отчет_Практика3_{engine.student_id}.json"
        st.rerun()

if st.session_state.get('report_json') is not None:
    st.title("🎉 Работа успешно завершена!")
    st.success("Отчет зашифрован и сформирован. Скачайте файл и отправьте его преподавателю.")
    st.download_button(
        label="📥 СКАЧАТЬ ФАЙЛ ОТЧЕТА (.json)",
        data=st.session_state.report_json,
        file_name=st.session_state.filename,
        mime="application/json",
        use_container_width=True
    )
    if st.button("Выйти на главную"):
        st.session_state.started = False
        st.session_state.report_json = None
        st.rerun()
