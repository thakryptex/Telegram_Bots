# -*- coding: utf-8 -*-

import sqlite3


class Database:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def check_tables(self):
        num = self.cursor.execute("SELECT count(name) FROM sqlite_master where name = 'users' or name = 'reminders' or "
                                  "name = 'states' or name = 'tasks';").fetchone()[0]
        return num

    def create_tables(self):
        self.connection.execute("CREATE TABLE users"
                                "(id int PRIMARY KEY, username text, full_name text,title text,timezone int DEFAULT 0)")
        self.connection.execute("CREATE TABLE tasks"
                                "(id integer not null, task text, UNIQUE(id, task) ON CONFLICT IGNORE)")
        self.connection.execute("CREATE TABLE reminders"
                                "(id integer not null, time numeric, UNIQUE(id, time) ON CONFLICT IGNORE)")
        self.connection.execute("CREATE TABLE states"
                                "(id int PRIMARY KEY, state text not NULL DEFAULT 'init')")
        self.connection.commit()

    def has_id(self, id):
        result = self.cursor.execute('SELECT id FROM users WHERE id=? LIMIT 1', (str(id),)).fetchone()
        return False if result is None else True

    def add_state(self, id):
        self.connection.execute('INSERT INTO states (id) VALUES (?)', (str(id),))
        self.connection.commit()

    def set_state(self, id, state):
        self.connection.execute('UPDATE states SET state = ? WHERE id = ?', (state, str(id)))
        self.connection.commit()

    def get_state(self, id):
        state = self.cursor.execute('SELECT state FROM states WHERE id=?', (str(id),)).fetchone()[0]
        return state

    def add_user(self, user):
        self.connection.execute('INSERT INTO users (id, username, full_name) VALUES (?, ?, ?)',
                                (str(user.id), user.username,
                                 " ".join(filter(None, [user.first_name, user.last_name]))))
        self.connection.commit()

    def add_group(self, group):
        self.connection.execute('INSERT INTO users (id, title) VALUES (?, ?)', (str(group.id), group.title))
        self.connection.commit()

    def set_timezone(self, user, utc):
        self.connection.execute('UPDATE users SET timezone = ? WHERE id = ?', (str(utc), str(user.id)))
        self.connection.commit()

    def get_timezone(self, user):
        timezone = self.cursor.execute('SELECT timezone FROM users WHERE id = ? LIMIT 1', (str(user.id),)).fetchone()[0]
        return timezone

    def show_tasks(self, user):
        tasks = self.cursor.execute('SELECT task FROM tasks WHERE id = ? ORDER BY rowid', (str(user.id),)).fetchall()
        return tasks

    def add_task(self, user, task):
        self.connection.execute('INSERT INTO tasks VALUES (?, ?)', (str(user.id), task))
        self.connection.commit()

    def del_task(self, task):
        self.connection.execute('DELETE FROM tasks WHERE task = ?', (task,))
        self.connection.commit()

    def clear_tasks(self, user):
        self.cursor.execute('DELETE FROM tasks WHERE id=?', (str(user.id),))
        self.connection.commit()

    def show_reminders(self, user):
        reminders = self.cursor.execute('SELECT time FROM reminders WHERE id = ? ORDER BY time',
                                        (str(user.id),)).fetchall()
        return reminders

    def set_reminder(self, user, time):
        self.connection.execute('INSERT INTO reminders VALUES (?, ?)', (str(user.id), time))
        self.connection.commit()

    def del_reminder(self, user, time):
        self.connection.execute('DELETE FROM reminders WHERE id = ? AND time = ?', (str(user.id), time,))
        self.connection.commit()

    def clear_rems(self, user):
        self.connection.execute('DELETE FROM reminders WHERE id=?', (str(user.id),))
        self.connection.commit()

    def num_of_tasks(self, user):
        number = self.cursor.execute('SELECT count(task) FROM tasks WHERE id = ?', (str(user.id),)).fetchone()[0]
        return number

    def num_of_rems(self, user):
        number = self.cursor.execute('SELECT count(time) FROM reminders WHERE id = ?', (str(user.id),)).fetchone()[0]
        return number

    def get_tasks_on_time(self, time):
        users_tasks = self.cursor.execute('SELECT id, task FROM tasks WHERE id IN (SELECT id FROM reminders '
                                          'WHERE time = ?) ORDER BY id, rowid', (time,)).fetchall()
        return users_tasks

    def close(self):
        self.connection.close()
