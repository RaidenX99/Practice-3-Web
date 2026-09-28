# -*- coding: utf-8 -*-
import streamlit as st
import json
import base64
import io
from PIL import Image
from datetime import datetime
from core import PracticeEngine

st.set_page_config(page_title="Практическая работа №3", layout="centered", page_icon="📊")

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
    
    with st.form("practice_form"):
        answers = {}
        photos = {}
        
        for task_key, task_data in variant.items():
            if task_key == 'task_99':
                st.markdown(f"### 📝 {task_data['title']}")
                st.write(task_data['text'])
                answers[task_key] = st.text_input("Краткий комментарий (необязательно):", key=f"ans_{task_key}")
                photos[task_key] = st.file_uploader("📸 Прикрепить фото с ответами (можно несколько)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=f"photo_{task_key}")
            else:
                task_num = task_key.split('_')[1]
                st.markdown(f"### 🔹 Задача {task_num}")
                st.write(task_data['text'])
                answers[task_key] = st.text_input("Ответ:", key=f"ans_{task_key}")
                photos[task_key] = st.file_uploader("📸 Прикрепить решение (можно несколько фото)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=f"photo_{task_key}")
            
            st.divider()
            
        submitted = st.form_submit_button("✅ Завершить и сформировать отчет", use_container_width=True)
        
        if submitted:
            delta = datetime.now() - st.session_state.start_time
            mins = int(delta.total_seconds() // 60)
            secs = int(delta.total_seconds() % 60)
            time_spent_str = f"{mins} мин. {secs} сек."
            
            student_answers_raw = {}
            encrypted_answers = {}
            
            for k, text_val in answers.items():
                raw_val = text_val.strip().replace(',', '.')
                student_answers_raw[k] = raw_val
                encrypted_answers[k] = base64.b64encode(raw_val[::-1].encode('utf-8')).decode('utf-8')
                
            for k, file_list in photos.items():
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