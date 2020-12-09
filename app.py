import logging
import time
import datetime
import flask
import telebot
from parser import url
from config import token
import schedule
import threading
import db_question

API_TOKEN = token
WEBHOOK_URL_BASE = url                                                      #https://6dc3bd5fa35c.ngrok.io
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)                                     #/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(API_TOKEN)
app = flask.Flask(__name__)
#### Расписание для скриптов #########
def job():
    print("Время 8.00")
    time_now = datetime.date.today()
    time_now = time_now.strftime('%Y-%m-%d')                    # Строка вида '2020-12-01'
    #time_now='2020-03-21'
    print(time_now)
    #funktion принимает 2 аргумента query и id=False, возвращает список словарей
    m = db_question.funktion(query=time_now)                  # m - это словарь типа {'user_id': 'День рождения у Иванов Иван, 01.01.1111, 35 лет', ....}
    print('это ответ от бд{}'.format(m))
    for elem in m:
        print('elem', elem)
        for key, value in elem.items():                         # key = chat_id , value = '1999-12-12 день рождения у Иванов Иван Иваныч - 34 года
            print('key', key)
            print('value', value)
            bot.send_message(key, value)

def send_messages():
    bot.send_message('561518886', 'Привет, ')

schedule.every(1).minutes.do(job)
#schedule.every().day.at('08:00').do(job)
#schedule.every(1).minutes.do(send_messages)
def go():
    while 1:
        schedule.run_pending()
        time.sleep(1)
t = threading.Thread(target=go, name="тест")
t.start()
### Конец блока расписание для скриптов ###


@app.route('/html', methods=['GET', 'POST'])
def html():
    return 'это моя страница'


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''

# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])              #WEBHOOK_URL_PATH='/xxxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/'
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@bot.message_handler(content_types=['text'])
def send_text(message):
    chat_id=message.chat.id
    query=message.text.lower()
    query_list=query.split(',')
    query_list=list(map(lambda x:x.strip(), query_list))                                                                # Убираем пробелы в элементах списка вначале и конце строк
    query_list.append(chat_id)
    print(query_list)
    if len(query_list)==5 and query_list[0]=='добавить' and query_list[1].count('-')==2:                                # Если добавить, и есть дата вида YYYY-MM-DD
        query_list.pop(0)                                                                                               # Убираем 'Добавить' из списка
        if check_date(query_list[0])==False:                                                                            # Проверяем дату на валидность
            db_question.funktion(query, chat_id)
            bot.send_message(message.chat.id, 'Событие добавлено')
        else: bot.send_message(message.chat.id, check_date(query_list[0]))                                              # Если дата хреновая, пишем в сообщение, что нам не понравилось

    elif len(query_list)>=2 and query_list[0]=='показать':                                                              # query_list включает два элемента ['показать', 'день рождения/фамилия']
        #bot.send_message(message.chat.id, 'начинаем извлечение из бд')                                                                                        # строка с запросом после 'показать'
        #print('Это query list{}', query_list)                                                                           #['показать', 'день рождения', xchat_idx]
        m=db_question.funktion(query, chat_id)                         # m = [{chat_id:['День рождения у ...',
        print('это ответ от бд{}'.format(m))
        for elem in m:
            for key, answ in elem.items():
                for elem_2 in answ:
                    bot.send_message(message.chat.id, elem_2)

    elif message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, мой создатель')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Прощай, создатель')
    else:
        bot.send_message(message.chat.id, 'Для добавления события делай такой запрос через запятую: Добавить, 2001-01-01, Иванов Иван Иваныч, Годовщина свадьбы')


def check_date(valid_date):                         #'1985.03.21'
    valid_list_date=valid_date.split('-')           #['1985', '03', '21']
    print(valid_list_date)
    if len(valid_list_date)!=3:
        return 'Формат даты:ГГГГ-ММ-ДД'
    elif len(valid_list_date[0])!=4:
        return 'Год должен состоять из 4 цифр и быть вначале даты!'
    elif int(valid_list_date[1]) > 12 or len(str(valid_list_date[1]))!=2:
        return 'Месяц должен состоять из 2 цифр и быть вторым в дате!'
    elif int(valid_list_date[2]) > 31 or len(str(valid_list_date[2]))!=2:
        return 'День должен состоять из двух цифр и быть последним в дате'
    else: return False



# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()
time.sleep(1)
# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)        #https://6dc3bd5fa35c.ngrok.io/xxxxxxxxxxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/

# Start flask server
app.run(debug=True)