# -*- coding: utf-8 -*-
 
import telebot # https://github.com/eternnoir/pyTelegramBotAPI
import sys
sys.path.insert(0,'..')
import config
from queue import Queue
from threading import Thread
from datetime import datetime, timedelta
from krypt_bot.SQLighter import SQLighter


bot = telebot.TeleBot(config.token_kryptbot)
db = None
save_queue = Queue()
db_queue = Queue()


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handler(message):
    if len(message.text) <= 3000:
        text_handler(message)
        save_queue.put(message)
    else:
        bot.send_message(message.chat.id, "Your message is too big! 🖕🏻")
    db_queue.put(message.from_user)


def text_handler(message):
    words = message.text.split()
    length = len(words)
    letter = words[length - 1][:1]
    text = ""
    
    if length == 1:
        end = words[0][-1:]
        if letter.isupper() and end.isupper():
            pass
        elif letter.isupper():
            end = end.upper()
            letter = letter.lower()
        elif end.isupper():
            end = end.lower()
            letter = letter.upper()
        text = end + words[0][1:-1] + letter
    else:
        for i in range(0, length):
            temp = words[i][:1]
            if temp.isupper():
                letter = letter.upper()
            words[i] = letter + words[i][1:]
            letter = temp.lower()
            text = " ".join(words)
            
    bot.send_message(message.chat.id, text)


def logging_messages():
    while True:
        if not save_queue.empty():
            message = save_queue.get()
            date = str( datetime.fromtimestamp(message.date) + timedelta(hours=3) )
            user = "id: %s, username: %s, %s %s" % (message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
            text = message.text + "\n"
            with open("krypto_log.txt", "a") as log:
                log.write(str.join(" -> ", (date, user, text)))
    
    
def db_worker():
    while True:
        if db is None:
            global db
            db = SQLighter('krypto.db')
        else:
            if db_queue.empty():
                row = db_queue.get()
                db.add_user(row)
    
    
thread_logging = Thread(target=logging_messages)
thread_logging.daemon = True
thread_logging.start()

thread_db = Thread(target=db_worker)
thread_db.daemon = True
thread_db.start()


if __name__ == "__main__":
    bot.polling(True)