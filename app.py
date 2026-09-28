# -*- coding: utf-8 -*-
import streamlit as st
import json
import base64
import io
from PIL import Image
from datetime import datetime
import requests
import plotly.express as px
import math
import random
import time

from core import PracticeEngine

st.set_page_config(page_title="Практическая работа №3", layout="centered", page_icon="📈")

st.markdown("""
    <style>
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #6366f1;
        background-color: #1f2937;
        color: white;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
        background: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        opacity: 0.95;
        transform: translateY(-2px);
    }
    .task-card {
        padding: 24px;
        border-radius: 16px;
        background: linear-gradient(145deg, #161e2e 0%, #1f2937 100%);
        border: 1px solid #374151;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    .header-card {
        padding: 24px;
        border-radius: 16px;
        background: linear-gradient(135deg, #1e1b4b 100%, #312e81 0%);
        border: 1px solid #4338ca;
        margin-bottom: 24px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

def upload_to_google_drive(file_content, filename):
    try:
        web_app_url = "https://script.google.com/macros/s/AKfycbzZZVu9AaYHPKKGEXQ4C0QeTYMm1U0HdHQcq3sc6cLHFz9f5P3Ivdj_Wj3XgdrItzq5/exec"
        payload = {
            "filename": filename,
            "content": file_content,
            "practice_num": "3"
        }
        response = requests.post(web_app_url, json=payload, timeout=45)
        if not response.text:
            return False
        res_data = response.json()
        return res_data.get("status") == "success"
    except Exception:
        return False

if 'started' not in st.session_state:
    st.session_state.started = False
    st.session_state.student_id = ""
    st.session_state.start_time = None
    st.session_state.report_json = None
    st.session_state.filename = ""
    st.session_state.sent_to_cloud = False

if not st.session_state.started:
    st.markdown("""
        <div class="header-card">
            <h1 style="color: #818cf8; margin-bottom: 5px;">📈 Практическая работа №3</h1>
            <p style="color: #94a3b8; font-size: 1.1rem;">Предельные теоремы и закон Пуассона в ИКТ</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="task-card">', unsafe_allow_html=True)
        student_id_input = st.text_input("🔑 Введите номер вашей зачетной книжки:", placeholder="Например: 220156")
        if st.button("🚀 Начать выполнение практики", use_container_width=True):
            if student_id_input.strip():
                st.session_state.student_id = student_id_input.strip()
                st.session_state.started = True
                st.session_state.start_time = datetime.now()
                st.balloons()
                st.rerun()
            else:
                st.error("Поле не может быть пустым!")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.started and st.session_state.report_json is None:
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; background: #1f2937; padding: 15px 20px; border-radius: 12px; border: 1px solid #374151; margin-bottom: 20px;">
            <span>🎓 <b>Студент:</b> {st.session_state.student_id}</span>
            <span style="color: #38bdf8;">📈 Практика №3 (ТВиМС)</span>
        </div>
    """, unsafe_allow_html=True)

    engine = PracticeEngine(st.session_state.student_id)
    variant = engine.generate_variant()
    
    st.warning("⚠️ Для зачета каждой задачи обязательно прикрепите фотографию рукописного решения!")
    
    if 'student_answers' not in st.session_state:
        st.session_state.student_answers = {}
    if 'student_photos' not in st.session_state:
        st.session_state.student_photos = {}

    total_tasks = len(variant)
    answered_tasks = sum(1 for k in variant.keys() if st.session_state.student_answers.get(k, "").strip())
    st.progress(answered_tasks / total_tasks, text=f"Прогресс выполнения: {answered_tasks} из {total_tasks} заданий заполнено")
    st.write("")

    for task_key, task_data in variant.items():
        st.markdown('<div class="task-card">', unsafe_allow_html=True)
        if task_key == 'task_99':
            st.markdown(f"### 📝 {task_data['title']}")
            st.markdown(task_data['text'])
            ans = st.text_input("Ваш комментарий / пояснение:", key=f"ans_{task_key}")
            st.session_state.student_answers[task_key] = ans
            photos = st.file_uploader("📸 Прикрепить фото рукописного ответа", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=f"photo_{task_key}")
            st.session_state.student_photos[task_key] = photos
        else:
            task_num = task_key.split('_')[1]
            st.markdown(f"### 🔹 Задача {task_num}")
            st.markdown(task_data['text'])
            
            # Поле ввода ответа сразу под текстом задачи
            ans = st.text_input("Ваш ответ:", key=f"ans_{task_key}")
            st.session_state.student_answers[task_key] = ans
            
            # ИНТЕРАКТИВНАЯ АНИМИРОВАННАЯ ПРОВЕРКА ВВЕДЕННОГО ОТВЕТА
            with st.expander(f"🎬 Проверить мой ответ с помощью живой симуляции"):
                st.write("Введите ответ выше, затем нажмите кнопку запуска — симуляция проверит вашу вероятность на практике:")
                if st.button(f"▶ Запустить тест для задачи {task_num}", key=f"anim_btn_{task_key}"):
                    user_val_str = st.session_state.get(f"ans_{task_key}", "").strip().replace(',', '.')
                    try:
                        target_p = float(user_val_str)
                        if not (0 <= target_p <= 1):
                            st.error("Значение вероятности должно быть в пределах от 0 до 1!")
                        else:
                            chart_ph = st.empty()
                            prog_ph = st.progress(0)
                            
                            steps = 25
                            x_vals, y_vals = [], []
                            succ, trials = 0, 0
                            
                            for s in range(1, steps + 1):
                                for _ in range(20):
                                    trials += 1
                                    if random.random() < target_p:
                                        succ += 1
                                
                                freq = succ / trials
                                x_vals.append(trials)
                                y_vals.append(freq)
                                
                                fig = px.line(x=x_vals, y=y_vals, labels={'x': 'Испытания', 'y': 'Частота'})
                                fig.add_hline(y=target_p, line_dash="dash", line_color="#4ade80", annotation_text="Ваш ответ")
                                fig.update_layout(
                                    template="plotly_dark",
                                    margin=dict(l=10, r=10, t=10, b=10),
                                    height=200,
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)'
                                )
                                chart_ph.plotly_chart(fig, use_container_width=True)
                                prog_ph.progress(s / steps)
                                time.sleep(0.03)
                            
                            diff = abs(y_vals[-1] - target_p)
                            if diff < 0.05:
                                st.success(f"🎯 Отлично! Эмпирическая частота ({y_vals[-1]:.4f}) отлично сошлась с вашим ответом ({target_p}).")
                            else:
                                st.info(f"📊 Эксперимент завершен. Частота: {y_vals[-1]:.4f}. Сравните с вашим расчетом.")
                    except ValueError:
                        st.warning("⚠️ Сначала введите числовой ответ в поле «Ваш ответ», чтобы симуляция знала, что проверять!")

            photos = st.file_uploader("📸 Прикрепить решение (фото)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=f"photo_{task_key}")
            st.session_state.student_photos[task_key] = photos
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.divider()
    if st.button("✅ Завершить и отправить отчет преподавателю", use_container_width=True, type="primary"):
        delta = datetime.now() - st.session_state.start_time
        mins = int(delta.total_seconds() // 60)
        secs = int(delta.total_seconds() % 60)
        time_spent_str = f"{mins} мин. {secs} сек."
        
        student_answers_raw = {}
        encrypted_answers = {}
        
        for k, text_val in st.session_state.student_answers.items():
            raw_val = text_val.strip().replace(',', '.')
            student_answers_raw[k] = raw_val
            encrypted_answers[k] = base64.b64encode(raw_val[::-1].encode('utf-8')).decode('utf-8')
            
        for k, file_list in st.session_state.student_photos.items():
            if file_list: 
                compressed_photos, encrypted_photos = [], []
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
        time_tag = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        st.session_state.filename = f"Practice_3_Student_{engine.student_id}_{time_tag}.json"
        st.rerun()

if st.session_state.get('report_json') is not None:
    st.balloons()
    st.markdown("""
        <div class="header-card">
            <h1 style="color: #4ade80;">🎉 Работа успешно завершена!</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get('sent_to_cloud', False):
        with st.spinner("⏳ Идет отправка отчета на Google Диск преподавателя..."):
            success = upload_to_google_drive(st.session_state.report_json, st.session_state.filename)
            if success:
                st.session_state.sent_to_cloud = True
                st.rerun()
                
    if st.session_state.get('sent_to_cloud', False):
        st.success("✅ Отчет успешно доставлен преподавателю в облако! Все данные и фотографии зафиксированы.")
        st.snow()
        st.info("Вы можете закрыть эту вкладку браузера.")
        
    if st.button("🔄 Пройти заново / Сменить зачетку"):
        st.session_state.started = False
        st.session_state.report_json = None
        st.session_state.sent_to_cloud = False
        st.rerun()
