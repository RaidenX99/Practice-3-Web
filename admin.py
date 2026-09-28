# -*- coding: utf-8 -*-
import streamlit as st
import json
import base64
from core import PracticeEngine

st.set_page_config(page_title="Панель проверки - Практика 3", layout="wide", page_icon="🛡️")

st.title("🛡️ Панель преподавателя - Практическая работа №3")
st.write("Проверка отчетов студентов, верификация хэшей античита и просмотр рукописных решений (формула Пуассона и предельные теоремы).")

if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False
    
if not st.session_state.admin_auth:
    st.divider()
    col1, col2 = st.columns([1, 2])
    with col1:
        pwd = st.text_input("Введите секретный пароль доступа:", type="password")
        if st.button("Войти", use_container_width=True):
            if pwd == "urtisi": 
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Неверный пароль!")
else:
    if st.button("🚪 Выйти из панели"):
        st.session_state.admin_auth = False
        st.rerun()
        
    st.divider()
    uploaded_files = st.file_uploader("📂 Загрузите файлы отчетов (.json) для проверки", type=["json"], accept_multiple_files=True)
    
    if uploaded_files:
        st.success(f"Загружено отчетов для проверки: {len(uploaded_files)}")
        st.divider()
        
        for file in uploaded_files:
            try:
                data = json.load(file)
                student_id = data.get("student_id", "Неизвестно")
                encrypted_answers = data.get("answers", {})
                file_hash = data.get("verification_key", "")
                timestamp = data.get("timestamp", "Н/Д")
                time_spent = data.get("time_spent", "Н/Д")
                
                # Дешифровка ответов и фотографий
                decrypted_answers = {}
                for k, v in encrypted_answers.items():
                    if isinstance(v, list):
                        decrypted_list = []
                        for photo_v in v:
                            try:
                                decrypted_list.append(base64.b64decode(photo_v.encode('utf-8')).decode('utf-8')[::-1])
                            except Exception:
                                pass
                        decrypted_answers[k] = decrypted_list
                    else:
                        try:
                            decrypted_answers[k] = base64.b64decode(v.encode('utf-8')).decode('utf-8')[::-1]
                        except Exception:
                            decrypted_answers[k] = ""
                        
                engine = PracticeEngine(student_id)
                expected_hash = engine.generate_security_hash(student_id, decrypted_answers)
                
                with st.expander(f"🎓 Студент: {student_id} | Время сдачи: {timestamp} | Затрачено: {time_spent}", expanded=True):
                    if expected_hash != file_hash:
                        st.error("🚨 ВНИМАНИЕ! Обнаружена попытка подделки: файл отчета был изменен вручную!")
                    else:
                        result = engine.check_answers(decrypted_answers)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Итоговая оценка", result['mark'])
                        col2.metric("Процент выполнения", f"{result['percent']}%")
                        col3.metric("Правильных задач", f"{result['correct_count']} из {result['total_count']}")
                        
                        st.write("---")
                        st.markdown("#### 📋 Детализированные результаты по задачам:")
                        
                        for task_key, details in sorted(result['details'].items(), key=lambda x: int(x[0].split('_')[1]) if x[0] != 'task_99' else 99):
                            status = "✅" if details['is_correct'] else "❌"
                            if task_key == 'task_99':
                                st.write(f"{status} **Теоретический вопрос:** {details['student_answer']}")
                            else:
                                st.write(f"{status} **Задача {task_key.split('_')[1]}:** Ответ студента: `{details['student_answer']}` | Правильный ответ: `{details['correct_answer']}`")
                            
                            photos_list = result.get('photos', {}).get(task_key, [])
                            if photos_list:
                                st.markdown(f"*Прикрепленные фото к задаче ({len(photos_list)} шт.):*")
                                cols = st.columns(min(len(photos_list), 3))
                                for idx, photo_b64 in enumerate(photos_list):
                                    with cols[idx % len(cols)]:
                                        st.image(base64.b64decode(photo_b64), caption=f"Решение {idx+1}", use_container_width=True)
                            st.write("---")
            except Exception as e:
                st.error(f"Ошибка при разборе файла {file.name}: {e}")
