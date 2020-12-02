import logging
import time
import flask
import telebot
from parser import url
from config import token
import schedule
import threading
import db_question

API_TOKEN = token
WEBHOOK_URL_BASE = url                                                      #https://6dc3bd5fa35c.ngrok.io
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)                                     #/1131808189:AAE5Qp5cSQ3EW7q4h-sj6sOZyGbLd6LT5G4/

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(API_TOKEN)
app = flask.Flask(__name__)
#### Расписание для скриптов #########
def job():
    print("Время 8.00")
    #bot.send_message('561518886', 'Время 8.00')          #561518886 - это chat_id моего телефона
    m = db_question.db_time_querry_sel()                  # m - это словарь типа {'user_id': 'День рождения у Грищенов Сергей, 21.09.1985, 35 лет', ....}
    print('это ответ от бд{}'.format(m))
    for answ in m:
        bot.send_message(answ, m.get(answ))

def send_messages():
    bot.send_message('561518886', 'Привет, ')

schedule.every().day.at('08:00').do(job)
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
@app.route(WEBHOOK_URL_PATH, methods=['POST'])              #WEBHOOK_URL_PATH='/1131808189:AAE5Qp5cSQ3EW7q4h-sj6sOZyGbLd6LT5G4/'
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


# Handle '/start' and '/help'
@bot.message_handler(commands=['info'])
def handle_text(message):
    answer = 'БЛА-БЛА-БЛА.'
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, ты написал мне /start')

@bot.message_handler(commands=['help', 'my_start'])
def send_welcome(message):
    bot.reply_to(message,
                 ("Hi there, I am EchoBot.\n"
                  "I am here to echo your kind words back to you."))



@bot.message_handler(content_types=['text'])
def send_text(message):
    chat_id=message.chat.id
    query=message.text.lower()
    query_list=query.split(',')
    query_list=list(map(lambda x:x.strip(), query_list))                                                                # Убираем пробелы в элементах списка вначале и конце строк
    query_list.append(chat_id)
    #print(query_list)
    if len(query_list)==5 and query_list[0]=='добавить' and query_list[1].count('-')==2:                                # Если добавить, и есть дата вида YYYY-MM-DD
        query_list.pop(0)                                                                                               # Убираем 'Добавить' из списка
        if check_date(query_list[0])==False:                                                                            # Проверяем дату на валидность
            bot.send_message(message.chat.id, 'Событие добавлено')
        else: bot.send_message(message.chat.id, check_date(query_list[0]))                                              # Если дата хреновая, пишем в сообщение, что нам не понравилось
        result=tuple(query_list)                                                                                        # Делаем из списка кортэж с 1 списком
        db_question.db_query(result)
    elif len(query_list)>=2 and query_list[0]=='показать':                           # query_list включает два элемента ['показать', 'день рождения/фамилия']
        bot.send_message(message.chat.id, 'начинаем извлечение из бд')
        db_request=query_list[1]                                             # строка с запросом после 'показать'
        print('Это query list{}', query_list)                                   #['показать', 'день рождения', 561518886]
        if db_request.count('день рождения') or db_request.count('годовщина'):
            key='description'
        else:
            key='full_name'
        query_str = '%' + query_list[1] + '%'
        query_list2 = []
        query_list2.append(query_str)                                       # В пустой список добавляем строку '%....%'
        query_list2.append(chat_id)                                         # В список добавляем строку '......' с chat_id
        result2 = tuple(query_list2)
        print('это result2: {}', result2)                                   # ('%день рождения%', 561518886)
        m=db_question.db_query_select(key, result2)                         #key=description/full_name; result2=(['%Иванов%, '561518886'])
        print('это ответ от бд{}'.format(m))
        for answ in m:
            bot.send_message(message.chat.id, answ)

    elif message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, мой создатель')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Прощай, создатель')
    elif message.text.lower() == 'я тебя люблю':
        bot.send_sticker(message.chat.id, 'CAADAgADZgkAAnlc4gmfCor5YbYYRAI')
    else:
        bot.send_message(message.chat.id, 'Для добавления события делай такой запрос через запятую: Добавить, 2001-01-01, Иванов Иван Иваныч, Годовщина свадьбы')

@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)
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


# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()
time.sleep(1)
# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)        #https://6dc3bd5fa35c.ngrok.io/1131808189:AAE5Qp5cSQ3EW7q4h-sj6sOZyGbLd6LT5G4/

# Start flask server
app.run(debug=True)