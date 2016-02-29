# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'..')
import config
import telebot # https://github.com/eternnoir/pyTelegramBotAPI


bot = telebot.TeleBot(config.token_kryptexbot)


@bot.message_handler(commands=['help'])
def helper(message):
    bot.send_message(message.chat.id, "Как работать с Kryptex Bot:\nПока никак, он просто реверсит твои сообщения.\n\nСписок всех остальных команд можно посмотреть снизу справа, нажав на значок [/]")
    

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handler(message):
    if len(message.text) <= 3000:
        text_handler(message)
    else:
        bot.send_message(message.chat.id, "Your message is too big! 🖕🏻")
    

def text_handler(message):
    bot.send_message(message.chat.id, message.text[::-1])


if __name__ == "__main__":
    bot.polling(True)
