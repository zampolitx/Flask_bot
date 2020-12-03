import db_question
import datetime
time_now = datetime.date.today()
time_now = time_now.strftime('%Y-%m-%d')                    # Строка вида '2020-11-30'
time_now='2020-05-26'
zampros='грищенов'
#print(time_now)
#funktion принимает 2 аргумента query и id=False, возвращает список словарей
m = db_question.funktion(query=zampros, id =561518886)                  # m - это словарь типа {'user_id': 'День рождения у Грищенов Сергей, 21.09.1985, 35 лет', ....}
#print('это ответ от бд{}'.format(m))
for answ in m:
    print('это answ', answ)