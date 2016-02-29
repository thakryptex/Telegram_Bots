# -*- coding: utf-8 -*-

import re
import sqlite3
from datetime import datetime, timedelta


class SQLighter:
    
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
            
    
    def add_user(self, user):
        with self.connection:
            row = self.cursor.execute('select id from users where id=?', (str(user.id),)).fetchone()
            if row == None:
                self.connection.execute('insert into users values (?, ?, ?, ?)', (str(user.id), user.username, str.join(" ", (user.first_name, user.last_name)), "0" ) )
                self.connection.commit()
            
            
    def set_timezone(self, user, utc):
        with self.connection:
            self.connection.execute('update users set timezone = ? where id = ?', ( str(utc), str(user.id)))
            self.connection.commit()
            
            
    def show_reminders(self, user):
        with self.connection:
            delta = self.cursor.execute('select timezone from users where id = ?', (str(user.id),)).fetchone()[0]
            rows = self.cursor.execute('select time from reminders where id = ? order by time', (str(user.id),)).fetchall()
            times = []
            text = None
            num = 0
            for row in rows:
                temp = re.split('[:]', row[0])
                time = datetime(year=2016, month=1, day=1, hour=int(temp[0]), minute=int(temp[1]) ) + timedelta(hours=int(delta))
                times.append(str(time.hour).zfill(2) + ":" + str(time.minute).zfill(2))
            for t in times:
                if num == 0:
                    text = "Your reminders:\n" + t
                    num = 1
                else:
                    num += 1
                    text += "\n" + t
            return text
            
            
    def set_reminder(self, user, time):
        with self.connection:
            delta = self.cursor.execute('select timezone from users where id=?', (str(user.id),)).fetchone()[0]
            if time is not None:
                time = datetime(year=2016, month=1, day=1, hour=time.hour, minute=time.minute) - timedelta(hours=delta)
                self.connection.execute('insert into reminders values (?, ?)', (str(user.id), str(time.hour).zfill(2).strip() + ":" + str(time.minute).zfill(2).strip() ))
            self.connection.commit()
    
    
    def del_reminder(self, user, time):
        with self.connection:
            delta = self.cursor.execute('select timezone from users where id=?', (str(user.id),)).fetchone()[0]
            if time is not None:
                time = datetime(year=2016, month=1, day=1, hour=time.hour, minute=time.minute) - timedelta(hours=delta)
                self.connection.execute('delete from reminders where time = ?', (str(time.hour).zfill(2) + ":" + str(time.minute).zfill(2), ))
            self.connection.commit()
            
            
    def clear_rems(self, user):
        with self.connection:
            row = self.cursor.execute('delete from reminders where id=?', (str(user.id),)).fetchone()
            self.connection.commit()
            
    
    def show_tasks(self, user):
        with self.connection:
            rows = self.cursor.execute('select task from tasks where id = ? order by rowid', (str(user.id),)).fetchall()
            text = None
            num = 0
            for row in rows:
                if num == 0:
                    text = "Your tasks:\n1 - " + row[0]
                    num = 1
                else:
                    num += 1
                    text += "\n" + str(num) + " - " + row[0]
            return text
            
            
    def add_task(self, user, task):
        with self.connection:
            if len(task) > 1:
                self.connection.execute('insert into tasks values (?, ?)', ( str(user.id), task.strip()))
                self.connection.commit()
            
            
    def remove_task(self, user, num):
        with self.connection:
            rows = self.cursor.execute('select task from tasks where id = ? order by rowid', (str(user.id),)).fetchall()
            if len(rows) < num:
                raise ValueError
            task = rows[num-1][0]
            self.connection.execute('delete from tasks where task = ?', (task, ))
            self.connection.commit()
            
            
    def clear_tasks(self, user):
        with self.connection:
            row = self.cursor.execute('delete from tasks where id=?', (str(user.id),)).fetchone()
            self.connection.commit()
            
            
    def get_users_reminders(self, time):
        with self.connection:
            rows = self.cursor.execute('select id, task from tasks where id in (select id from reminders where time = ?) order by id, rowid', (time,)).fetchall()
            user_tasks ={}
            num = 0
            for row in rows:
                if row[0] not in user_tasks:
                    user_tasks[row[0]] = "Your tasks:\n1 - " + row[1]
                    num = 1
                else:
                    num += 1
                    user_tasks[row[0]] += "\n" + str(num) + " - " + row[1]
            return user_tasks
    
    
    def close(self):
        self.connection.close()
        
        
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  
        
def add_user(user):
    db = SQLighter("idoit.db")
    db.add_user(user)
    db.close()
    

def update_utc(user, utc):
    db = SQLighter("idoit.db")
    db.set_timezone(user, utc)
    db.close()
    
    
def show_reminders(user):
    db = SQLighter("idoit.db")
    text = db.show_reminders(user)
    db.close()
    return text


def set_reminder(user, time):
    db = SQLighter("idoit.db")
    db.set_reminder(user, time)
    db.close()
    
    
def del_reminder(user, time):
    db = SQLighter("idoit.db")
    db.del_reminder(user, time)
    db.close()
    

def clear_rems(user):
    db = SQLighter("idoit.db")
    db.clear_rems(user)
    db.close()
    
    
def show_tasks(user):
    db = SQLighter("idoit.db")
    text = db.show_tasks(user)
    db.close()
    return text
    
    
def add_task(user, task):
    db = SQLighter("idoit.db")
    db.add_task(user, task)
    db.close()
    

def remove_task(user, num):
    db = SQLighter("idoit.db")
    db.remove_task(user, num)
    db.close()
    
    
def clear_tasks(user):
    db = SQLighter("idoit.db")
    db.clear_tasks(user)
    db.close()
    
