#coding:UTF-8

import time

from database import get_db, query_db

class Task(object):
    def __init__(self, task_id=None, user=None):
        if task_id is None:
            self.task_id = self.create_db(user)
        else:
            self.task_id = task_id
        self.load_db()

    def create_db(self, post_user):
        ''' create a new task and return task_id '''
        db = get_db()
        user_id = post_user.user_id
        created_time = int(time.time())
        
        db.execute('''insert into tasks (post_user, create_data) values (?, ?)''',
                   [user_id, created_time])
        db.commit()
        rv = query_db('''select task_id from tasks where post_usr = ? and create_data= ?''',
                      [user_id, created_time], one=True)
        return rv[0] if rv else None
        

    def load_db(self):
        ''' load items from tasks '''
        rv = query_db('''select * from tasks where task_id = ?''',
                      [self.task_id], one=True)
        [_, self.post_user, self.create_date, self.max_parti] = rv[:4]
        [self.title, self.content, self.public_date, self.begin_date, self.end_date] = rv[4:]

    def update_db(self):
        ''' update items in tasks '''
        db = get_db()
        db.execute('''update tasks set post_user = ?, create_date = ?,
                   max_participants = ?, title = ?, content = ?, public_date = ?,
                   begin_date = ?, end_date = ? where task_id = ? ''',
                   [self.post_user, self.create_date, self.max_parti, self.title,
                    self.content, self.public_date, self.begin_date, self.end_date])
        db.commit()

    def delete_db(self):
        ''' detele this task from db. '''
        db = get_db()
        db.execute('''delete from tasks where task_id = ?''',
                   [self.task_id])
    
class Type(object):
    def __init__(self, type_id=None, typename=None):
        ''' should check type_id '''
        if type_id is None:
            self.type_id = self.create_db(typename)
        else:
            self.type_id = type_id
        if type_id is not None:
            self.load_db()

    def create_db(self, typename):
        '''
        create a new type and return type_id,
        return None if typename has in db.
        '''
        if get_type_id(typename) is not None:
            return None
        db = get_db()
        db.execute('''insert into types (typename) values (?)''',
                   [typename])
        db.commit()
        return get_type_id(typename)
        

    def load_db(self):
        ''' load typename from types. '''
        rv = query_db('''select type_id from types where type_id = ?''',
                      [self.type_id], one=True)
        self.typename = rv[0]

    def update_db(self):
        ''' update typename of type. '''
        db = get_db()
        db.execute('''update types set typename = ? where type_id = ?''',
                   [self.typename, self.type_id])
        db.commit()

    def delete_db(self):
        ''' delete type in types '''
        db = get_db()
        db.execute(''' delete from types where type_id = ?''',
                   [type_id])
        db.commit()

class TTl(object):
    def __init__(self, type_obj, task, create=False):
        self.type_obj = type_obj
        self.task = task
        if create:
            self.create_db()

    def create_db(self):
        db = get_db()
        db.execute('''insert into ttl (task_id, type_id) values (?, ?)''',
                   [self.task.task_id, self.type_obj.type_id])
        db.commit()

    def delete_db(self):
        db = get_db()
        db.execute('''delete from ttl where task_id = ? and type_id = ?''',
                   [self.task.task_id, self.type_obj.type_id])
        db.commit()
    
class TUb(object):
    def __init__(self, user, task, create=False):
        self.user = user
        self.task = task
        if create:
            self.create_db()
        self.load_db()

    def create_db(self):
        db = get_db()
        db.execute('''insert into tub (user_id, task_id) values (?, ?)''',
                   [self.user.user_id, self.task.task_id])
        db.commit()

    def load_db(self):
        rv = query_db('''select * from tub where user_id = ? and task_id = ?''',
                      [self.user.user_id, self.task.task_id], one=True)
        [_, _, self.statu, self.score] = rv

    def update_db(self):
        db = get_db()
        db.execute('''update tub set statu = ?, score = ? where user_id = ? and task_id = ?''',
                   [self.statu, self.score, self.user.user_id, self.task.task_id])
        db.commit()

    def delete_db(self):
        db = get_db()
        db.execute('''delete from tub where user_id = ? and task_id = ?''',
                   [self.user.user_id, self.task.task_id])
        db.commit()
        
class User(object):
    def __init__(self, user_id, username=None, create=False):
        self.user_id = user_id
        if create:
            self.user_id = user_id(username)
        self.load_db()

    def create_db(self, username):
        db = get_db()
        db.execute('''insert into users (user_id, user_name) values (?, ?)''',
                   [self.user_id, username])
        db.commit()

    def load_db(self):
        rv = query_db('''select * from users where user_id = ?''',
                      [self.user_id], one=True)
        [_, self.username, self.phone_no, self.pw_hash, self.email, self.address] = rv

    def update_db(self):
        db = get_db()
        db.execute('''update users set username = ?, phone_no = ?, pw_hash = ?,
                   email = ?, address = ? where user_id = ?''',
                   [self.user_id, self.user_name, self.phone_no, self.pw_hash,
                    self.email, self.address])
        db.commit()

    def delete_db(self):
        db = get_db()
        db.execute('''delete from users where user_id = ?''', [self.user_id])
        db.commit()

    def post_task(self, title, context, types):
        pass

    def view_tasks(self):
        pass

    def reveive_task(self):
        pass

    def commit_posted(self):
        pass

    def statu_info(self):
        pass

