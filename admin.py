# -*- coding: utf-8 -*-
import streamlit as st
import json
import base64
from core import PracticeEngine

st.set_page_config(page_title="Панель проверки", layout="wide", page_icon="🛡️")

st.title("🛡️ Панель преподавателя - Проверка ТВиМС")

if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False
    
if not st.session_state.admin_auth:
    st.info("Доступ только для преподавателя.")
    pwd = st.text_input("Введите секретный пароль доступа:", type="password")
    if st.button("Войти"):
        if pwd == "urtisi": 
            st.session_state.admin_auth = True
            st.rerun()
        else:
            st.error("Неверный пароль!")
else:
    if st.button("🚪 Выйти из панели"):
        st.session_state.admin_auth = False
        st.rerun()
        
    st.write("Загрузите файлы отчетов студентов (.json), чтобы проверить их. Фотографии решений отобразятся автоматически.")
    uploaded_files = st.file_uploader("Выберите файлы", type=["json"], accept_multiple_files=True)
    
    if uploaded_files:
        for file in uploaded_files:
            try:
                data = json.load(file)
                student_id = data.get("student_id", "Неизвестно")
                encrypted_answers = data.get("answers", {})
                file_hash = data.get("verification_key", "")
                
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
                
                with st.expander(f"Студент: {student_id} | Время решения: {data.get('time_spent', 'Н/Д')}", expanded=True):
                    if expected_hash != file_hash:
                        st.error("🚨 ОШИБКА АНТИЧИТА: Файл был изменен вручную! Хэш-ключ не совпадает.")
                    else:
                        result = engine.check_answers(decrypted_answers)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Оценка", result['mark'])
                        col2.metric("Выполнено", f"{result['percent']}%")
                        col3.metric("Верно", f"{result['correct_count']} из {result['total_count']}")
                        
                        st.write("---")
                        st.write("### Детализация и фото решений:")
                        
                        sorted_tasks = sorted(result['details'].items(), key=lambda x: int(x[0].split('_')[1]) if x[0] != 'task_99' else 99)
                        
                        for task_key, details in sorted_tasks:
                            status_emoji = "✅" if details['is_correct'] else "❌"
                            
                            if task_key == 'task_99':
                                st.write(f"{status_emoji} **Контрольные вопросы:** {details['student_answer']}")
                            else:
                                task_num = task_key.split('_')[1]
                                st.write(f"{status_emoji} **Задача {task_num}:** Ввел: `{details['student_answer']}` | Правильно: `{details['correct_answer']}`")
                            
                            photo_b64_list = result.get('photos', {}).get(task_key)
                            if photo_b64_list and isinstance(photo_b64_list, list):
                                for idx, photo_b64 in enumerate(photo_b64_list):
                                    try:
                                        img_bytes = base64.b64decode(photo_b64)
                                        st.image(img_bytes, caption=f"Фото решения {idx+1} (Задача {task_key.split('_')[1] if task_key != 'task_99' else 'Теория'})", width=500)
                                    except:
                                        st.error(f"Не удалось отобразить фото {idx+1}")
                            st.write("---")
                            
            except Exception as e:
                st.error(f"Не удалось прочитать файл {file.name}: {str(e)}")