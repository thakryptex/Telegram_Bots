# -*- coding: utf-8 -*-

import sqlite3


class SQLighter:
    
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        
    
    def select_all(self):
        with self.connection:
            return self.cursor.execute('select * from users').fetchall()
            
    
    def get_user(self, user_id):
        with self.connection:
            return self.cursor.execute('select * from users where id=?', (user_id,)).fetchall()[0]
            
    
    def add_user(self, user):
        with self.connection:
            row = self.cursor.execute('select id, messages from users where id=?', (str(user.id),)).fetchone()
            if row == None:
                self.connection.execute('insert into users values (?, ?, ?, ?)', (str(user.id), user.username, str.join(" ", (user.first_name, user.last_name)), str(1) ) )
            else:
                self.connection.execute('update users set messages = ? where id = ?', ( str(row[1] + 1), str(row[0])))
            self.connection.commit()
            
    
    def close(self):
        self.connection.close()