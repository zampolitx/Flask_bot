#!/usr/bin/python3
import datetime
import sqlite3
import re
import os
db_filename='bot.db'
def db_query(result):

    db_exists=os.path.exists(db_filename)
    print('dbexist=', db_exists)
    conn=sqlite3.connect(db_filename)
    print(type(conn))
    schema_filename='db_create.sql'
    print('schema filename=', schema_filename)
    if not db_exists:
        print('Creating schema')
        with open (schema_filename, 'r') as f:
            schema=f.read()
        conn.executescript(schema)
        print('Done')
    else:
        print('Database is exists!')
    print('inserting')
    query='insert into birthday (date_bd, full_name, description, user_id) VALUES (?, ?, ?, ?)'
    conn.execute(query, result)
    #conn.execute(query, result) ## executemany нужен если передается список кортэжей
    conn.commit()

# Запрос на извлечение данных из таблицы
def funktion(query, id=False):              # В функцию работы с базой данных передается два аргумента (query - 
    conn= sqlite3.connect(db_filename)
    user_id=id
    print('chat_id=', user_id)
    query=str(query.lower())
    glogal_list=[]
    resp_list=[]
    print('query=', query)
    if query.count('-')!=2 and user_id!=False:     # Если в запросе нет даты м есть chat_id
        print('Значит запрос от Пользователя')
        if query.count('день') or query.count('годовщина'):     # Если показать события
            for row in conn.execute("select * from birthday where user_id=? and description like ?", (user_id, query+'%')):
                #print(row)
                mystr="{} у {}, {}".format(row[1], row[3], row[2])
                resp_list.append(mystr)
            resp_dict = {}
            resp_dict[user_id]=resp_list
            glogal_list.append(resp_dict)
            return glogal_list
        else:                           # Если не события, то ФИО
            for row in conn.execute("select * from birthday where user_id=? and full_name like ?", (user_id, query+'%')):
                #print(row)
                mystr = "{} у {}, {}".format(row[3], row[1], row[2])
                resp_list.append(mystr)
            resp_dict = {}
            resp_dict[user_id] = resp_list
            #print('resp_dict=', resp_dict)
            glogal_list.append(resp_dict)
            return glogal_list

    elif query.count('-')==2 and user_id==False:   # Если в запросе есть дата
        #print('Значит запрос от планировщика')
        date_planirovshik=query.split('-')          # Получили список вида ['2020', '12', '12']
        date_planirovshik_str='%' + date_planirovshik[1]+'-'+date_planirovshik[2]     # Строка вида '%12-12'
        #print('это date_planirovshik_str=', date_planirovshik_str)
        for row in conn.execute('select * from birthday where date_bd LIKE ?', (date_planirovshik_str, )):
            user_year=row[1]
            user_year=user_year.split('-')
            user_year=int(user_year[0])
            #print('user_year', user_year)
            #print('date_planirovshik', date_planirovshik[0])
            user_old=int(date_planirovshik[0]) - user_year
            goda = ''
            user_old_str=str(user_old)
            #print('user_old_str', user_old_str[-1:])
            if user_old_str[-1:] == '1' or user_old_str[-1:] == '2' or user_old_str[-1:] == '3' or user_old_str[-1:] == '4':
                goda='года'
            else: goda='лет'
            #print(row)
            mystr = "{} {} у {} - {} {}".format(row[1], row[3], row[2], user_old, goda)
            #print(mystr)
            resp_dict = {}
            resp_dict[row[4]] = mystr
            resp_list.append(resp_dict)
        return resp_list

    else:
        return "Строка не подходит. Для добавления события ... Для просмотра события ..."

#Мы должны возвращать не список а словарь {'user_id': 'День рождения у Грищенов Сергей, 21.09.1985, 35 лет', ....}
# select * from birthday where date_bd like '%09-27' and user_id='561518886'

