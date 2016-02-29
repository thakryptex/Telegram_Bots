# -*- coding: utf-8 -*-

import re
import sys
sys.path.insert(0,'..')
import time
import config
import telebot # https://github.com/eternnoir/pyTelegramBotAPI
import idoit_bot.SQLighter as db
from threading import Thread
from datetime import datetime, time as time2, timedelta
from idoit_bot.SQLighter import SQLighter


bot = telebot.TeleBot(config.token_idoitbot)


@bot.message_handler(commands=['help', 'start'])
def helper(message):
    bot.send_message(message.chat.id, "Как работать с I Do It Bot:\n1. Установите часовой пояс своего региона командой: /timezone\n2. Добавьте текущие задачи командой: /addtask\n3. Установите напоминания о своих задачах: /setreminder\n\nСписок всех команд можно посмотреть, нажав на значок [ / ] внизу экрана.\n\nБота можно использовать для хранения заметок, поскольку он не отвечает на обычные сообщения, а только на команды.")
    db.add_user(message.from_user)
    
    
@bot.message_handler(commands=['timezone'])
def timezone(message):
    text = message.text[9:].strip()
    utc = 0
    try:
        utc = int(text)
        date = datetime.now() + timedelta(hours=utc)
        bot.send_message(message.chat.id, "Часовой пояс установлен.\nВаше время сейчас: %02d%s%02d\n" % (date.hour, ':', date.minute))
        db.update_utc(message.from_user, utc)
    except ValueError:
        bot.send_message(message.chat.id, "Часовой пояс введён некорректно.\nВведите в формате: '/timezone +3' (это московское время)")


@bot.message_handler(commands=['reminders'])
def reminders(message):
    text = db.show_reminders(message.from_user)
    if text is None:
        bot.send_message(message.chat.id, "У вас нет напоминалок.")
    else:
        bot.send_message(message.chat.id, text)
    

@bot.message_handler(commands=['setreminder'])
def setreminder(message):
    text = message.text[12:].strip()
    timer = re.split('[:-]', text)
    time = None
    if len(timer) == 2:
        try:
            hour = int(timer[0])
            minute = int(timer[1])
            if (hour > 23 and hour < 0) or (minute > 59 and minute < 0):
                raise ValueError
            time = time2(hour=hour, minute=minute)
            bot.send_message(message.chat.id, "Время напоминания установлено.\nНапоминание будет в %02d%s%02d\n" % (hour, ':', minute))
            db.set_reminder(message.from_user, time)
        except ValueError:
            bot.send_message(message.chat.id, "Время указано некорректно.\nВведите в формате: '/setreminder 10:30'")
    else:
        bot.send_message(message.chat.id, "Время указано некорректно.\nВведите в формате: '/setreminder 10:30'")
    
    
@bot.message_handler(commands=['delreminder'])
def delreminder(message):
    text = message.text[12:].strip()
    timer = re.split('[:-]', text)
    time = None
    if len(timer) == 2:
        try:
            hour = int(timer[0])
            minute = int(timer[1])
            if (hour > 23 and hour < 0) or (minute > 59 and minute < 0):
                raise ValueError
            time = time2(hour=hour, minute=minute)
            bot.send_message(message.chat.id, "Напоминание удалено.")
            db.del_reminder(message.from_user, time)
        except ValueError:
            bot.send_message(message.chat.id, "Время указано некорректно.\nВведите в формате: '/delreminder 10:30'")
    else:
        bot.send_message(message.chat.id, "Время указано некорректно.\nВведите в формате: '/delreminder 10:30'")
    
    
@bot.message_handler(commands=['clearrems'])
def clearrems(message):
    text = message.text[10:].strip().lower()
    if text == "yes":
        db.clear_rems(message.from_user)
        bot.send_message(message.chat.id, "Ваши напоминания удалены.")
    else:
        bot.send_message(message.chat.id, "Напишите слово 'yes' после команды /clearrems, чтобы избежать случайного удаления задач.")


@bot.message_handler(commands=['tasks'])
def tasks(message):
    text = db.show_tasks(message.from_user)
    if text is None:
        bot.send_message(message.chat.id, "У вас нет задач.")
    else:
        bot.send_message(message.chat.id, text)
    

@bot.message_handler(commands=['addtask'])
def addtask(message):
    text = message.text[8:].strip()
    if len(text) > 1 and len(text) < 100:
        bot.send_message(message.chat.id, "Задача \"" + text + "\" добавлена.")
        db.add_task(message.from_user, text)
    else:
        bot.send_message(message.chat.id, "Пишите через пробел после команды /addtask.\n1 символ < текст задачи < 100 символов.")
    
    
@bot.message_handler(commands=['removetask'])
def removetask(message):
    text = message.text[11:].strip()
    if len(text) > 0 and len(text) < 20:
        try:
            db.remove_task(message.from_user, int(text))
            bot.send_message(message.chat.id, "Задача удалена.")
        except ValueError:
            bot.send_message(message.chat.id, "Порядковый номер задачи указан неверно.")
    else:
        bot.send_message(message.chat.id, "Формат:\n/removetask 3 - удалит задачу с порядковым номером 3.")
        
        
@bot.message_handler(commands=['cleartasks'])
def cleartasks(message):
    text = message.text[11:].strip().lower()
    if text == "yes":
        db.clear_tasks(message.from_user)
        bot.send_message(message.chat.id, "Ваши задачи удалены.")
    else:
        bot.send_message(message.chat.id, "Напишите слово 'yes' после команды /cleartasks, чтобы избежать случайного удаления задач.")
    

# сделать конечный автомат
# сделать конечный автомат
# сделать конечный автомат

@bot.message_handler(commands=['cancel'])
def cancel(message):
    bot.send_message(message.chat.id, "Отмена предыдущего действия (пока бессмысленная вещь :) )")


def remind_thread():
    db = SQLighter("idoit.db")
    time = None
    while True:
        date = datetime.now()
        now = str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2)
        if time != now:
            users = db.get_users_reminders(now)
            for id, tasks in users.items():
                bot.send_message(id, tasks)
            time = now
    db.close()
    

thread_remind = Thread(target=remind_thread)
thread_remind.daemon = True
thread_remind.start()


if __name__ == "__main__":
    bot.polling(True)
