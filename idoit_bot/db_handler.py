# -*- coding: utf-8 -*-

import re
from threading import Thread
from db_model import Database
from datetime import datetime, timedelta
from idoit_bot import send_message


NAME = "idoit.db"


def check_db_exist():
    db = Database(NAME)
    with db.connection:
        if db.check_tables() != 4:
            db.create_tables()


def new_user(user):
    db = Database(NAME)
    with db.connection:
        if not db.has_id(user.id):
            if user.type == 'private':
                db.add_user(user)
            else:
                db.add_group(user)
            db.add_state(user.id)
            return True
        return False


def set_state(user, state):
    db = Database(NAME)
    with db.connection:
        db.set_state(user.id, state)


def get_state(user):
    db = Database(NAME)
    with db.connection:
        return db.get_state(user.id)


def set_timezone(user, utc):
    db = Database(NAME)
    with db.connection:
        db.set_timezone(user, utc)


def show_tasks(user):
    db = Database(NAME)
    with db.connection:
        text = "*Задачи:*\n"
        tasks = all_tasks(user)
        if tasks:
            text += "\n".join(tasks)
        else:
            text = "У вас нет задач."
        return text


def show_rems(user):
    db = Database(NAME)
    with db.connection:
        text = "*Напоминания:*\n"
        rems = all_rems(user)
        if rems:
            text += "\n".join(rems)
        else:
            text = "У вас нет напоминаний."
        return text


def add_task(user, task):
    db = Database(NAME)
    with db.connection:
        if db.num_of_tasks(user) >= 20:
            raise OverflowError
        if 150 < len(task) < 2:
            raise ValueError
        db.add_task(user, task.strip())


def add_rem(user, time):
    db = Database(NAME)
    with db.connection:
        if db.num_of_rems(user) >= 30:
            raise OverflowError
        delta = db.get_timezone(user)
        hour, minute = map(int, re.split(r'[.:-]', time))
        if hour in range(0, 24) and minute in range(0, 60):
            time = datetime(2016, 1, 1, hour, minute) - timedelta(hours=delta)
            db.set_reminder(user, str(time.hour).zfill(2) + ":" + str(time.minute).zfill(2))


def all_tasks(user):
    db = Database(NAME)
    with db.connection:
        tasks = db.show_tasks(user)
        return ["%d. %s" % (i, task[0]) for i, task in enumerate(tasks, 1)]


def all_rems(user):
    db = Database(NAME)
    with db.connection:
        times = []
        delta = db.get_timezone(user)
        rems = db.show_reminders(user)
        for row in rems:
            hour, minute = map(int, re.split(r'[.:-]', row[0]))
            time = datetime(2016, 1, 1, hour, minute) + timedelta(hours=delta)
            times.append(str(time.hour).zfill(2) + ":" + str(time.minute).zfill(2))
        return times


def del_task(user, num):
    db = Database(NAME)
    with db.connection:
        tasks = db.show_tasks(user)
        if len(tasks) < num:
            raise ValueError
        task = tasks[num - 1][0]
        db.del_task(task)


def del_rem(user, hour, minute):
    db = Database(NAME)
    with db.connection:
        delta = db.get_timezone(user)
        time = datetime(2016, 1, 1, hour, minute) - timedelta(hours=delta)
        db.del_reminder(user, str(time.hour).zfill(2) + ":" + str(time.minute).zfill(2))


def clear_rems(user):
    db = Database(NAME)
    with db.connection:
        db.clear_rems(user)


def clear_tasks(user):
    db = Database(NAME)
    with db.connection:
        db.clear_tasks(user)


def get_tasks_on_time(time):
    db = Database(NAME)
    with db.connection:
        users_tasks = db.get_tasks_on_time(time)
        usertask_dict = {user[0]: [t[1] for t in users_tasks if t[0] == user[0]] for user in users_tasks}
        send_dict = {}
        for d in usertask_dict:
            send_dict[d] = "*Задачи:*\n" + "\n".join(["%d. %s" % (i, task) for i, task in enumerate(usertask_dict[d], 1)])
        return send_dict


def remind_thread():
    db = Database(NAME)
    time = None
    while True:
        date = datetime.utcnow()
        now = str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2)
        if time != now:
            users = get_tasks_on_time(now)
            for id, tasks in users.items():
                send_message(id, tasks, parse_mode='Markdown')
            time = now
    db.close()


thread_remind = Thread(target=remind_thread)
thread_remind.daemon = True
thread_remind.start()
