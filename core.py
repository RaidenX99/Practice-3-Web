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
        rng = random.Random(self.seed)
        pool = []

        # 1
        n1 = rng.choice([500, 1000, 1500])
        p1 = rng.choice([0.002, 0.003, 0.004])
        lam1 = n1 * p1
        k1 = rng.choice([2, 3, 4])
        ans1 = ( (lam1 ** k1) / math.factorial(k1) ) * math.exp(-lam1)
        pool.append({
            'text': f"Коммутатор обрабатывает пакетов в сутки: $n = {n1}$. Вероятность сбоя отдельного пакета равна $p = {p1}$. Найти вероятность того, что за сутки произойдет ровно $k = {k1}$ сбоев. (Округление до 4 знаков).",
            'answer': str(round(ans1, 4))
        })

        # 2
        n2 = 1000
        p2 = 0.003
        lam2 = n2 * p2
        k2 = 2
        ans2 = ( (lam2 ** k2) / math.factorial(k2) ) * math.exp(-lam2)
        pool.append({
            'text': f"На линии связи протяженностью в $n = {n2}$ км вероятность обрыва на 1 км равна $p = {p2}$. Найти вероятность ровно $k = {k2}$ обрывов на всей линии. (Округление до 4 знаков).",
            'answer': str(round(ans2, 4))
        })

        # 3
        n3 = 800
        p3 = 0.0025
        lam3 = n3 * p3
        k3 = 1
        ans3 = ( (lam3 ** k3) / math.factorial(k3) ) * math.exp(-lam3)
        pool.append({
            'text': f"В дата-центре зафиксировано $n = {n3}$ обращений к защищенному модулю, вероятность критической ошибки для каждого равна $p = {p3}$. Найти вероятность ровно $k = {k3}$ ошибки. (Округление до 4 знаков).",
            'answer': str(round(ans3, 4))
        })

        # 4
        n4 = 500
        p4 = 0.004
        lam4 = n4 * p4
        ans4 = math.exp(-lam4)
        pool.append({
            'text': f"В системе из $n = {n4}$ независимых датчиков вероятность отказа каждого за смену составляет $p = {p4}$. Найти вероятность того, что за смену не откажет ни один датчик ($k = 0$). (Округление до 4 знаков).",
            'answer': str(round(ans4, 4))
        })

        # 5
        n5 = 600
        p5 = 0.005
        lam5 = n5 * p5
        ans5 = 1 - math.exp(-lam5)
        pool.append({
            'text': f"На узле связи обрабатывается $n = {n5}$ запросов, вероятность сбоя каждого равна $p = {p5}$. Найти вероятность того, что произойдет хотя бы один сбой ($k \ge 1$). (Округление до 4 знаков).",
            'answer': str(round(ans5, 4))
        })

        # 6
        pool.append({
            'text': f"В серверную стойку устанавливается 100 блоков. Оценить вероятность того, что их суммарный вес будет в пределах от 6900 до 7200 кг, если средний вес одного блока составляет $a = 70$ кг, а среднеквадратичное отклонение $\sigma = 10$ кг. (Ответ округлите до 5 знаков).",
            'answer': "0.81859"
        })

        # 7
        pool.append({
            'text': f"В некотором обществе имеется 1% абонентов с нестандартной конфигурацией оборудования. Каков должен быть минимальный объем выборки (с возвращением), чтобы вероятность встретить в ней хотя бы одного такого абонента была не менее 0.957?",
            'answer': "300"
        })

        # 8
        lam8 = 2.5
        k8 = 3
        ans8 = ( (lam8 ** k8) / math.factorial(k8) ) * math.exp(-lam8)
        pool.append({
            'text': f"Интенсивность поступления заявок на сервер составляет $\\lambda = {lam8}$ заявок в минуту. Найти вероятность поступления ровно $k = {k8}$ заявок за минуту. (Округление до 4 знаков).",
            'answer': str(round(ans8, 4))
        })

        # 9
        lam9 = 1.5
        ans9 = math.exp(-lam9)
        pool.append({
            'text': f"Среднее число сетевых атак на шлюз за час составляет $\\lambda = {lam9}$. Найти вероятность того, что за час не будет ни одной атаки ($k = 0$). (Округление до 4 знаков).",
            'answer': str(round(ans9, 4))
        })

        # 10
        lam10 = 3.0
        k10 = 2
        ans10 = ( (lam10 ** k10) / math.factorial(k10) ) * math.exp(-lam10)
        pool.append({
            'text': f"В среднем за сеанс связи происходит $\\lambda = {lam10}$ переподключений. Найти вероятность ровно $k = {k10}$ переподключений за сеанс. (Округление до 4 знаков).",
            'answer': str(round(ans10, 4))
        })

        # 11-20
        for i in range(11, 21):
            n_val = rng.choice([10, 15, 20])
            p_val = round(rng.uniform(0.2, 0.4), 2)
            k_val = rng.randint(2, 5)
            ans_val = math.comb(n_val, k_val) * (p_val ** k_val) * ((1 - p_val) ** (n_val - k_val))
            pool.append({
                'text': f"В серии из $n = {n_val}$ независимых проверок сетевого узла вероятность успешного отклика равна $p = {p_val}$. Найти вероятность ровно $k = {k_val}$ успешных откликов. (Округление до 4 знаков).",
                'answer': str(round(ans_val, 4))
            })

        rng.shuffle(pool)

        variant = {}
        for idx, task_item in enumerate(pool):
            task_num = idx + 1
            variant[f"task_{task_num}"] = task_item

        cq_pool = [
            "При каких условиях формулу Пуассона используют вместо формулы Бернулли? Напишите ее математическое выражение[cite: 6].",
            "В чем суть приближения вероятностей суммы независимых случайных величин через функцию Лапласа в предельных теоремах?",
            "Как определяется параметр $\\lambda$ в формуле Пуассона для потока редких событий в телекоммуникациях[cite: 6]?"
        ]
        variant['task_99'] = {
            'title': 'Контрольный теоретический вопрос',
            'text': f"ОБЯЗАТЕЛЬНО прикрепите фото с развернутым рукописным ответом на вопрос:\n\n{rng.choice(cq_pool)}",
            'answer': 'Ручная проверка (Требуется фото)'
        }
        
        return variant

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

        def is_close(val1, val2, tol=0.01):
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
                    details[task_key] = {'is_correct': True, 'correct_answer': "Фото прикреплено", 'student_answer': f"Фото ({len(photo_list)} шт.)"}
                else:
                    details[task_key] = {'is_correct': False, 'correct_answer': "Требуется фото", 'student_answer': "Нет фото!"}
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
