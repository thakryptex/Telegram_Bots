# -*- coding: utf-8 -*-

import sys
sys.path.insert(0,'..')
import config
import telebot # https://github.com/eternnoir/pyTelegramBotAPI


bot = telebot.TeleBot(config.token_relsbot)


@bot.message_handler(commands=['help'])
def helper(message):
    bot.send_message(message.chat.id, "Никто тебе не поможет, bitch.")
    

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
