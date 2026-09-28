# -*- coding: utf-8 -*-
import random
import math
import hashlib
import json

SECRET_SALT = "Ural_Telecom_2026_Secret"

class PracticeEngine:
    def __init__(self, student_id: str):
        self.student_id = student_id.strip().upper()
        self.seed = self._generate_seed()
        random.seed(self.seed)

    def _generate_seed(self):
        hash_obj = hashlib.md5(self.student_id.encode())
        return int(hash_obj.hexdigest(), 16)

    def generate_variant(self) -> dict:
        variant = {}
        
        variant['task_1'] = self._task_1_moivre_laplace()
        variant['task_2'] = self._task_2_bernoulli_packets()
        variant['task_3'] = self._task_3_sample_size()
        variant['task_4'] = self._task_4_poisson_survival()
        
        cq_pool = [
            "При каких условиях формула Бернулли заменяется приближенной формулой Пуассона?",
            "Объясните суть интегральной теоремы Муавра-Лапласа. Для чего используется функция Лапласа Ф(x)?",
            "Чем отличается локальная теорема Лапласа от интегральной?",
            "Что такое дискретная случайная величина (ДСВ) и что называется ее законом распределения?",
            "Какими свойствами обладает функция Лапласа Ф(x) (четность/нечетность, предельные значения)?",
            "Запишите формулу математического ожидания и дисперсии для биномиального распределения.",
            "Как вычислить вероятность того, что в n независимых испытаниях событие наступит хотя бы один раз?"
        ]
        
        selected_questions = random.sample(cq_pool, 3)
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(selected_questions)])
        
        variant['task_99'] = {
            'title': 'Контрольные теоретические вопросы (Предельные теоремы и ДСВ)',
            'text': f"ОБЯЗАТЕЛЬНО прикрепите фото с развернутым рукописным ответом на следующие вопросы:\n\n{questions_text}",
            'answer': 'Ручная проверка (Требуется фото)'
        }
        
        return variant

    def _task_1_moivre_laplace(self):
        n = random.choice([100, 144, 225, 400])
        a = random.randint(50, 80)
        sigma = random.randint(8, 15)
        
        x1 = random.choice([-1, -1.5, -2])
        x2 = random.choice([1, 1.5, 2, 2.5])
        
        min_val = int(n * a + math.sqrt(n) * sigma * x1)
        max_val = int(n * a + math.sqrt(n) * sigma * x2)
        
        text = f"Балансировщик нагрузки распределяет {n} независимых потоков видео-трафика. Средний битрейт одного потока a = {a} Мбит/с, а среднеквадратическое отклонение σ = {sigma} Мбит/с. Используя интегральную теорему Муавра-Лапласа, оцените вероятность того, что суммарная нагрузка на магистральный канал будет в пределах от {min_val} до {max_val} Мбит/с. \n(Используйте таблицы значений функции Лапласа Ф(x). Ответ округлите до 4 знаков)."
        
        phi_x1 = math.erf(x1 / math.sqrt(2)) / 2
        phi_x2 = math.erf(x2 / math.sqrt(2)) / 2
        ans = phi_x2 - phi_x1
        
        return {'text': text, 'answer': str(round(ans, 4))}

    def _task_2_bernoulli_packets(self):
        n = 8
        p = round(random.uniform(0.15, 0.35), 2)
        
        text = f"Анализатор перехватывает {n} подозрительных сетевых пакетов. Вероятность того, что пакет содержит сигнатуру вредоносного прокси-трафика, равна p = {p}. Найти вероятности того, что среди перехваченных пакетов окажется: \nа) не менее 6 вредоносных (сработает блокировка IP); \nб) не менее одного вредоносного (сработает базовый алерт).\n\nВ ответе запишите через пробел два числа. (Пример: 0.1234 0.9876. Округляйте до 4 знаков)."
        
        ans_a = sum([math.comb(n, k) * (p**k) * ((1 - p)**(n - k)) for k in range(6, n + 1)])
        ans_b = 1 - ((1 - p)**n)
        
        return {'text': text, 'answer': f"{round(ans_a, 4)} {round(ans_b, 4)}"}

    def _task_3_sample_size(self):
        p_defect = round(random.uniform(0.01, 0.05), 2)
        p_target = round(random.uniform(0.90, 0.98), 2)
        
        text = f"При производстве оптического кабеля доля бракованных сплайс-кассет составляет {int(p_defect*100)}%. Каков должен быть минимальный объем случайной выборки (количество кассет для проверки рефлектометром), чтобы вероятность встретить в ней ХОТЯ БЫ ОДНУ бракованную кассету была не менее {p_target}? (Укажите целое число)."
        
        ans = math.ceil(math.log(1 - p_target) / math.log(1 - p_defect))
        
        return {'text': text, 'answer': str(ans)}

    def _task_4_poisson_survival(self):
        lam = round(random.uniform(1.5, 4.5), 1)
        
        text = f"Модель воздействия космического излучения на ячейки оперативной памяти сервера (без ECC-коррекции). За год через процессор проходит огромное число частиц N, размер транзистора крайне мал. Известно, что среднее число поражений λ (лямбда) равно {lam}. Сервер уходит в Kernel Panic, если поражена хотя бы одна ячейка. \nИспользуя формулу Пуассона, вычислите «выживаемость» сервера за год — вероятность того, что не произойдет НИ ОДНОГО поражения памяти. (Округлите до 4 знаков)."
        
        ans = math.exp(-lam)
        
        return {'text': text, 'answer': str(round(ans, 4))}

    @staticmethod
    def generate_security_hash(student_id: str, student_answers: dict) -> str:
        answers_str = json.dumps(student_answers, sort_keys=True)
        raw_data = f"{student_id}_{answers_str}_{SECRET_SALT}"
        return hashlib.sha256(raw_data.encode('utf-8')).hexdigest()

    def check_answers(self, student_answers: dict) -> dict:
        variant = self.generate_variant()
        correct_count = 0
        total_count = len(variant)
        details = {}

        def is_close(val1, val2, tol=0.005):
            if ' ' in str(val1) and ' ' in str(val2):
                parts1 = str(val1).split()
                parts2 = str(val2).split()
                if len(parts1) == len(parts2):
                    return all(abs(float(p1) - float(p2)) <= tol for p1, p2 in zip(parts1, parts2))
                return False
            try:
                return abs(float(val1) - float(val2)) <= tol
            except ValueError:
                return str(val1).strip().lower() == str(val2).strip().lower()

        for task_key, task_data in variant.items():
            photo_list = student_answers.get(f"{task_key}_photo", [])
            has_photo = bool(photo_list)
            
            student_ans_str = student_answers.get(task_key, "").strip().replace(',', '.')
            correct_ans_str = str(task_data.get('answer', ''))
            
            if task_key == 'task_99':
                if has_photo:
                    is_correct = True
                    correct_count += 1
                    details[task_key] = {
                        'is_correct': True, 'correct_answer': "Фото прикреплено",
                        'student_answer': f"Фото ({len(photo_list)} шт.)"
                    }
                else:
                    details[task_key] = {
                        'is_correct': False, 'correct_answer': "Требуется фото",
                        'student_answer': "Нет фото!"
                    }
                continue

            is_correct = is_close(student_ans_str, correct_ans_str)

            if not has_photo:
                is_correct = False
                student_ans_str = f"{student_ans_str} (Нет фото!)" if student_ans_str else "Нет ответа (Нет фото!)"

            if is_correct: correct_count += 1
            details[task_key] = {'is_correct': is_correct, 'correct_answer': correct_ans_str, 'student_answer': student_ans_str}

        score_percent = (correct_count / total_count) * 100
        if score_percent >= 85: mark = 5
        elif score_percent >= 70: mark = 4
        elif score_percent >= 50: mark = 3
        else: mark = 2

        photos_dict = {k: student_answers.get(f"{k}_photo") for k in variant.keys() if student_answers.get(f"{k}_photo")}

        return {
            'correct_count': correct_count,
            'total_count': total_count,
            'percent': round(score_percent, 1),
            'mark': mark,
            'details': details,
            'photos': photos_dict
        }