# -*- coding: utf-8 -*-

import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import re
import config
import telebot  # https://github.com/eternnoir/pyTelegramBotAPI
import db_handler as db
from telebot import types
from datetime import datetime, timedelta
from telebot.apihelper import ApiException


bot = telebot.TeleBot(config.token_idoitbot)

MAIN_MENU = types.ReplyKeyboardMarkup(resize_keyboard=True)
MAIN_MENU.row('Показать все задачи')
MAIN_MENU.row('Задачи')
MAIN_MENU.row('Напоминания')
MAIN_MENU.row('Часовой пояс', 'Помощь')


@bot.message_handler(commands=['start'])
def start(message):
    if db.new_user(message.chat):
        send_message(message.chat.id,
                     "Бот *I Do It* помогает Вам помнить о всех важных задачах и делах, а также "
                     "напоминает о них, когда это необходимо.\n", parse_mode='Markdown')
        set_tz(message)
    else:
        main_menu(message)


@bot.message_handler(func=lambda message: message.text == 'Главное меню' and message.content_type == 'text')
def main_menu(message):
    state = db.get_state(message.chat)
    if state != 'timezone':
        db.set_state(message.chat, 'init')
        send_message(message.chat.id, "*Главное меню*",
                     reply_markup=MAIN_MENU, parse_mode='Markdown')
    else:
        set_tz(message)


@bot.message_handler(func=lambda message: message.text == 'Помощь' and message.content_type == 'text')
def help(message):
    state = db.get_state(message.chat)
    if state == 'init':
        send_message(message.chat.id,
                     "*Как работать с I Do It Bot*\n\n"
                     "Откройте клавиатуру бота и выберите _одну из команд_:\n"
                     "1. *Показать все задачи* - отправляет Ваши существующие на данный момент задачи.\n"
                     "2. *Задачи* - открывает меню задач, где их можно добавлять, изменять, удалять и т.д.\n"
                     "3. *Напоминания* - открывает меню напоминаний, где их можно добавлять, удалять и т.д.\n"
                     "4. *Часовой пояс* - настройка часового пояса (для корректной работы напоминаний).\n"
                     "5. *Помощь* - меню, в котором Вы находитесь прямо сейчас.\n",
                     reply_markup=MAIN_MENU, parse_mode='Markdown')
    else:
        send_message(message.chat.id, "Для вызова инструкции вернитесь в главное меню.")


@bot.message_handler(func=lambda message: message.text == 'Завершить' and message.content_type == 'text')
def done(message):
    state = db.get_state(message.chat)
    if state == 'timezone':
        db.set_state(message.chat, 'init')
        main_menu(message)
    elif state == 'add_task' or state == 'del_task' or state == 'clear_tasks':
        db.set_state(message.chat, 'tasks')
        tasks(message)
    elif state == 'add_rem' or state == 'del_rem' or state == 'clear_rems':
        db.set_state(message.chat, 'reminders')
        reminders(message)


@bot.message_handler(func=lambda message: message.text == 'Часовой пояс' and message.content_type == 'text')
def set_tz(message):
    state = db.get_state(message.chat)
    if state == 'init' or state == 'timezone':
        db.set_state(message.chat, 'timezone') if state == 'init' else None
        markup = types.ReplyKeyboardHide()
        send_message(message.chat.id,
                     "Для правильной работы напоминаний, укажите Ваш часовой пояс в формате UTC: "
                     "*[-12; +14]*\n\nПример: +3\n_(Московское время)_",
                     reply_markup=markup, parse_mode='Markdown')
    else:
        send_message(message.chat.id, "Для настройки часового пояса вернитесь в главное меню.")


@bot.message_handler(regexp=r'^[+-]?[0-1]?[0-9]\s?$')
def timezone(message):
    state = db.get_state(message.chat)
    if state == 'timezone':
        tz = int(re.search(r'^[+-]?[0-1]?[0-9]\s?$', message.text).group())
        if -12 <= tz <= 14:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Завершить')
            date = datetime.utcnow() + timedelta(hours=tz)
            send_message(message.chat.id,
                         "Часовой пояс установлен.\nВаше время сейчас: *%02d%s%02d*\n\n"
                         "Если время указано верно, нажмите '*Завершить*'.\n"
                         "Если нет - введите ещё раз." % (date.hour, ':', date.minute),
                         reply_markup=markup, parse_mode='Markdown')
            db.set_timezone(message.chat, tz)
        else:
            send_message(message.chat.id,
                         "Часовой пояс указан в неверном формате, попробуйте ещё раз.\n"
                         "UTC: *[-12; +14]*", parse_mode='Markdown')
    elif state == 'add_task':
        add_task(message)


@bot.message_handler(func=lambda message: message.text == 'Задачи' and message.content_type == 'text')
def tasks(message):
    state = db.get_state(message.chat)
    if state == 'init' or state == 'tasks':
        db.set_state(message.chat, 'tasks') if state == 'init' else None
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Показать все задачи')
        markup.row('Добавить')
        markup.row('Удалить', 'Удалить все')
        markup.row('Главное меню')
        send_message(message.chat.id, "*Меню задач*", reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == 'Напоминания' and message.content_type == 'text')
def reminders(message):
    state = db.get_state(message.chat)
    if state == 'init' or state == 'reminders':
        db.set_state(message.chat, 'reminders') if state == 'init' else None
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Показать все напоминания')
        markup.row('Добавить')
        markup.row('Удалить', 'Удалить все')
        markup.row('Главное меню')
        send_message(message.chat.id, "*Меню напоминаний*", reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == 'Показать все задачи' and message.content_type == 'text')
def show_tasks(message):
    state = db.get_state(message.chat)
    if state == 'init' or state == 'tasks':
        text = db.show_tasks(message.from_user)
        send_message(message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == 'Показать все напоминания' and message.content_type == 'text')
def show_rems(message):
    state = db.get_state(message.chat)
    if state == 'reminders':
        text = db.show_rems(message.from_user)
        send_message(message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == 'Добавить' and message.content_type == 'text')
def add(message):
    state = db.get_state(message.chat)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Завершить')
    if state == 'tasks' or state == 'add_task':
        db.set_state(message.chat, 'add_task') if state == 'tasks' else None
        send_message(message.chat.id,
                     "Напишите свои задачи.\n"
                     "Формат: _одна задача = одна строка_\n\n"
                     "Задачи можно добавлять отдельными сообщениями, либо в одном сообщении "
                     "несколько задач, каждую начиная с новой строки.",
                     reply_markup=markup, parse_mode='Markdown')
    elif state == 'reminders' or state == 'add_rem':
        db.set_state(message.chat, 'add_rem') if state == 'reminders' else None
        send_message(message.chat.id,
                     "Установите напоминания.\n"
                     "Формат: _13:45_ или _13-45_\n\n"
                     "Напоминания можно добавлять отдельными сообщениями, либо в одном сообщении "
                     "несколько задач, каждая при этом начинается с новой строки.",
                     reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == 'Удалить' and message.content_type == 'text')
def delete(message):
    state = db.get_state(message.chat)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if state == 'tasks' or state == 'del_task':
        tasks = db.all_tasks(message.chat)
        if tasks:
            db.set_state(message.chat, 'del_task') if state == 'tasks' else None
            for task in tasks:
                markup.row(task[:30])
            markup.row('Завершить')
            send_message(message.chat.id,
                         "Выберите задачу для удаления, нажав на неё на клавиатуре.\n\n"
                         "Чтобы окончить процесс удаления, нажмите кнопку '*Завершить*'.",
                         reply_markup=markup, parse_mode='Markdown')
        else:
            done(message)
    elif state == 'reminders' or state == 'del_rem':
        rems = db.all_rems(message.chat)
        if rems:
            db.set_state(message.chat, 'del_rem') if state == 'reminders' else None
            for rem in rems:
                markup.row('• ' + rem)
            markup.row('Завершить')
            send_message(message.chat.id,
                         "Выберите напоминание для удаления, нажав на него на клавиатуре.\n\n"
                         "Чтобы окончить процесс удаления, нажмите кнопку '*Завершить*'.",
                         reply_markup=markup, parse_mode='Markdown')
        else:
            done(message)


@bot.message_handler(func=lambda message: message.text == 'Удалить все' and message.content_type == 'text')
def clear(message):
    state = db.get_state(message.chat)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Да, точно', 'Нет, не надо')
    if state == 'tasks' or state == 'clear_tasks':
        db.set_state(message.chat, 'clear_tasks') if state == 'tasks' else None
        send_message(message.chat.id,
                     "*Вы точно хотите удалить все задачи?*",
                     reply_markup=markup, parse_mode='Markdown')
    elif state == 'reminders' or state == 'clear_rems':
        db.set_state(message.chat, 'clear_rems') if state == 'reminders' else None
        send_message(message.chat.id,
                     "*Вы точно хотите удалить все напоминания?*",
                     reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(regexp=r'^(\d?\d)\. .*')
def del_task(message):
    state = db.get_state(message.chat)
    if state == 'del_task':
        num = int(re.search(r'^(\d?\d)', message.text).group())
        try:
            db.del_task(message.chat, num)
            send_message(message.chat.id, "Задача удалена.")
        except ValueError:
            send_message(message.chat.id, "Порядковый номер задачи указан неверно.")
        delete(message)


@bot.message_handler(regexp=r'^• ([0-2]?[0-9][.:-][0-5][0-9])')
def del_rem(message):
    state = db.get_state(message.chat)
    if state == 'del_rem':
        clock = re.findall(r'^• ([0-2]?[0-9][.:-][0-5][0-9])', message.text)[0]
        hour, minute = map(int, re.split(r'[.:-]', clock))
        if hour in range(0, 24) and minute in range(0, 60):
            db.del_rem(message.chat, hour, minute)
            send_message(message.chat.id, "Напоминание удалено.")
        delete(message)


@bot.message_handler(func=lambda message: message.text == 'Да, точно' and message.content_type == 'text')
def yes(message):
    state = db.get_state(message.chat)
    if state == 'clear_tasks':
        db.clear_tasks(message.from_user)
        send_message(message.chat.id, "Ваши задачи удалены.")
        done(message)
    elif state == 'clear_rems':
        db.clear_rems(message.from_user)
        send_message(message.chat.id, "Ваши напоминания удалены.")
        done(message)


@bot.message_handler(func=lambda message: message.text == 'Нет, не надо' and message.content_type == 'text')
def no(message):
    state = db.get_state(message.chat)
    if state == 'clear_tasks' or state == 'clear_rems':
        done(message)


@bot.message_handler(regexp=r'([0-2]?[0-9][.:-][0-5][0-9])')
def add_rem(message):
    state = db.get_state(message.chat)
    if state == 'add_rem':
        try:
            rems = re.findall(r'([0-2]?[0-9][.:-][0-5][0-9])', message.text)
            for rem in rems:
                db.add_rem(message.chat, rem)
            send_message(message.chat.id,
                         "Напоминания добавлены.\n"
                         "Вы можете добавить ещё напоминания, либо окончить процесс добавления, "
                         "нажав кнопку '*Завершить*'.", parse_mode='Markdown')
        except OverflowError:
            db.set_state(message.chat, 'reminders')
            send_message(message.chat.id, "Количество напоминалок единовременно не может превышать 30.\n")
            reminders(message)
    elif state == 'add_task':
        add_task(message)


@bot.message_handler(func=lambda message: message.content_type == 'text')
def add_task(message):
    state = db.get_state(message.chat)
    if state == 'add_task':
        added = 0
        try:
            for task in message.text.split("\n"):
                db.add_task(message.chat, task)
                added += 1
            send_message(message.chat.id,
                         "Все задачи добавлены.\n"
                         "Вы можете добавить ещё задач, либо окончить процесс добавления, "
                         "нажав кнопку '*Завершить*'.",
                         parse_mode='Markdown')
        except OverflowError:
            db.set_state(message.chat, 'tasks')
            send_message(message.chat.id,
                         "Задач добавлено %d.\n"
                         "Количество задач единовременно *не может превышать 20*.\n"
                         "Для добавления новых задач, удалите старые." % added)
            tasks(message)
        except ValueError:
            send_message(message.chat.id, "Задач добавлено %d.\n"
                                          "Длина текста задачи должна быть в пределах *от 2х до 150ти символов*.\n"
                                          "Попробуйте ещё раз." % added)
    elif state == 'timezone':
        set_tz(message)


def send_message(chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None, 
                 parse_mode=None, disable_notification=None):
    try:
        bot.send_message(chat_id, text, disable_web_page_preview, reply_to_message_id, reply_markup, parse_mode,
                         disable_notification)
        # with open('log.txt', 'a') as log:
        #     log.write("[ id: %d, text: %s ]\n" % (chat_id, text.replace("\n", " | ")))
    except ApiException as e:
        print(e)


if __name__ == "__main__":
    db.check_db_exist()
    bot.polling(True)
