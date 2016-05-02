#coding:UTF-8

import time

from werkzeug.security import check_password_hash

from database import get_db, query_db
from config import *

__all__ = [
    get_user,
    get_user_id_from_phone,
    get_user_id_from_name,
    get_task,

    register_user,
    
    welcome,
    account,
    user_tasks,
    task_info,
    get_peoples,
    tasks,
    ]

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

    def tags(self):
        ''' tags of this task. '''
        rv = query_db('''select tag_id from ttl where task_id = ?''', [self.task_id])
        for tag_id in rv:
            yield Tag(tag_id)

    def participate_users(self, statu):
        ''' get users who participate that task. '''
        rv = query_db('''select user_id from tub where task_id = ? and statu = ?''',
                      [self.task_id, statu])
        for user_id in rv:
            user = User(user_id)
            tub = TUb(user, self)
            yield user, tub
    
class Tag(object):
    def __init__(self, tag_id=None, tagname=None):
        ''' should check tag_id '''
        if tag_id is None:
            self.tag_id = self.create_db(tagname)
        else:
            self.tag_id = tag_id
        if tag_id is not None:
            self.load_db()

    def create_db(self, tagname):
        '''
        create a new tag and return tag_id,
        return None if tagname has in db.
        '''
        if get_tag_id(tagname) is not None:
            return None
        db = get_db()
        db.execute('''insert into tags (tagname) values (?)''',
                   [tagname])
        db.commit()
        return get_tag_id(tagname)
        

    def load_db(self):
        ''' load tagname from tags. '''
        rv = query_db('''select * from tags where tag_id = ?''',
                      [self.tag_id], one=True)
        [_, self.tagname, self.creater, self.creater_time] = rv

    def update_db(self):
        ''' update tagname of tag. '''
        db = get_db()
        db.execute('''update tags set tagname = ?, creater = ?, create_time = ?
                      where tag_id = ?''',
                   [self.tagname, self.creater, self.create_time, self.tag_id])
        db.commit()

    def delete_db(self):
        ''' delete tag in tags '''
        db = get_db()
        db.execute(''' delete from tags where tag_id = ?''',
                   [tag_id])
        db.commit()

class TTl(object):
    def __init__(self, tag, task, create=False):
        self.tag = tag
        self.task = task
        if create:
            self.create_db()

    def create_db(self):
        '''
        create a new connection betweem tag and task.
        '''
        db = get_db()
        db.execute('''insert into ttl (task_id, tag_id) values (?, ?)''',
                   [self.task.task_id, self.tag.tag_id])
        db.commit()

    def delete_db(self):
        ''' delete t-t in ttl '''
        db = get_db()
        db.execute('''delete from ttl where task_id = ? and tag_id = ?''',
                   [self.task.task_id, self.tag.tag_id])
        db.commit()
    
class TUb(object):
    def __init__(self, user, task, create=False):
        self.user = user
        self.task = task
        if create:
            self.create_db()
        self.load_db()

    def create_db(self):
        '''
        create a new connection betweem user and task.
        '''
        db = get_db()
        db.execute('''insert into tub (user_id, task_id) values (?, ?)''',
                   [self.user.user_id, self.task.task_id])
        db.commit()

    def load_db(self):
        ''' load t-u from tub '''
        rv = query_db('''select * from tub where user_id = ? and task_id = ?''',
                      [self.user.user_id, self.task.task_id], one=True)
        [_, _, self.statu, self.score] = rv

    def update_db(self):
        ''' update t-u to tub '''
        db = get_db()
        db.execute('''update tub set statu = ?, score = ? where user_id = ? and task_id = ?''',
                   [self.statu, self.score, self.user.user_id, self.task.task_id])
        db.commit()

    def delete_db(self):
        ''' delete t-u in tub '''
        db = get_db()
        db.execute('''delete from tub where user_id = ? and task_id = ?''',
                   [self.user.user_id, self.task.task_id])
        db.commit()
        
class User(object):
    def __init__(self, user_id, username=None, create=False):
        self.user_id = user_id
        if create:
            self.user_id = create_db(user_id, username)
        self.load_db()

    def create_db(self, username, user_type):
        '''
        create a new user.
        '''
        db = get_db()
        db.execute('''insert into users (user_id, user_name) values (?, ?)''',
                   [self.user_id, username])
        db.commit()

    def load_db(self):
        ''' load user from users '''
        rv = query_db('''select * from users where user_id = ?''',
                      [self.user_id], one=True)
        [_, self.user_type, self.username, self.phone_no, self.pw_hash,
             self.address, self.score] = rv

    def update_db(self):
        ''' update user in users '''
        db = get_db()
        db.execute('''update users set user_type = ?, username = ?, phone_no = ?,
                   pw_hash = ?, address = ?, score = ? where user_id = ?''',
                   [self.user_type, self.user_id, self.user_name, self.phone_no, self.pw_hash,
                    self.address, self. score])
        db.commit()

    def delete_db(self):
        ''' delete user in users '''
        db = get_db()
        db.execute('''delete from users where user_id = ?''', [self.user_id])
        db.commit()

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def get_events(self):
        ''' get all events '''
        rv = query_db('''select task_id from events where user_id = ? order by event_id desc''',
                      [self.user_id])
        for task_id in rv:
            yield Event(task_id)

    def unchecked_events(self):
        ''' get unchecked events '''
        for task in self.get_events:
            if task.statu == RAISD:
                yield task

    def created_tasks(self):
        ''' get tasks created by user '''
        rv = query_db('''select task_id from tasks where user_id = ? order by task_id desc''',
                      [self.user_id])
        for task_id in rv:
            yield Task(task_id)

    def participate_tasks(self, statu):
        ''' get tasks user participate '''
        rv = query_db('''select task_id from tub where user_id = ? and statu = ?
                         order by task_id desc''', [self.user_id, statu])
        for task_id in rv:
            task = Task(task_id)
            creator = User(task.user_id)
            yield task, creator

    def post_task(self, title, content, maxp, public_date, begin_date, end_date, tags):
        task = Task(user=self)
        task.title = title
        task.content = content
        task.max_parti = maxp
        task.public_date = public_date
        task.begin_date = begin_date
        task.end_date = end_date
        task.update_db()
        
        ttls = [TTl(tag, task, True) for tag in tags]

        return task, ttls

    def receive_task(self, task):
        tub = TUb(self, task, True)
        tub.statu = RECEIVED
        tub.update_db()
        return tub

    def commit_posted(self, task, helper, score):
        tub = Tub(helper, task)
        tub.score = score
        tub.statu = COMPLETE
        tub.update_db()
        return tub

    def abort_recieved(self, task):
        tub = Tub(self, task)
        tub.statu = ABORT
        tub.update_db()
        return tub

    def statu_info(self):
        pass

class Event(object):
    def __init__(self, event_id=None, user_id=None, task_id=None, another_id=None, act=None):
        if event_id is None:
            self.event_id = self.create_db(user_id, task_id, another_id, act)
        else:
            self.event_id = event_id
        self.load_db()

    def create_db(self, user_id, task_id, another_id, act):
        db = get_db()
        created_time = int(time.time())
        db.excute('''insert into events (user_id, task_id, another_id, act, init_date, statu)
                  values (?, ?, ?, ?, ?, ?)''', [user_id, another_id, act, init_date, RAISED])
        db.commit()
        rv = query_db('''select event_id from events where user_id = ? and task_id = ?
                      and another_id = ? and act = ? and init_data = ?''',
                      [user_id, another_id, act, init_date], one=True)
        return rv[0]

    def load_db(self):
        rv = query_db('''select * from events where event_id = ?''',
                      [self.event_id], one=True)
        [_, self.user_id, self.task_id, self.another_id, self.act, self.init_date,
             self.statu] = rv

    def update_db(self):
        db = get_db()
        db.execute('''update events set statu = ? where event_id = ?''',
                   [self.statu, self.event_id])
        db.commit()

    def delete_db(self):
        db = get_db()
        db.execute('''delete from events where event_id = ?''', [self.event_id])

class Notice(object):
    def __init__(self, notice_id=None, user_id=None, info=None):
        if notice_id is None:
            self.notice_id = self.create_id(user_id, info)
        else:
            self.notice_id = notice_id
        self.load_db()

    def create_db(self, user_id, info):
        db = get_db()
        created_time = int(time.time())
        db.execute('''insert into notices (user_id, release_date, info) values (?, ?, ?)''',
                   [user_id, created_time, release_date])
        db.commit()
        rv = query_db('''select notice_id from notices where user_id = ? and release_date = ?''',
                      [user_id, created_time], one=True)
        return rv[0]

    def load_db(self):
        rv = query_db('''select * from notices where notice_id = ? ''', [notice_id], one=True)
        [_, self.user_id, self.release_date, self.info] = rv

    def update_db(self):
        db = get_db()
        db.execute('''update notices set user_id = ?, release_dat = ? info = ?
                   where notice_id = ?''', [self.user_id, self.release_date,
                                            self.info, self.notice_id])
        db.commit()

    def delete_db(self):
        db = get_db()
        db.execute('''delete from notices where notice_id = ?''', [self.notice_id])
    
def get_type_id(typename):
    ''' look up the type_id for a typename. '''
    rv = query_db('''select type_id from types where typename = ?''',
                  [typename], one=True)
    return rv[0] if rv else None

def get_user(user_id, from_term='user_id'):
    ''' look up the user_id '''
    rv = query_db('select user_id from users where % = ? ' % (from_term), [user_id], one=True)
    return User(rv) if rv else None

def get_user_id_from_phone(phone_no):
    ''' look up the user_id for a phone number '''
    rv = query_db('''select user_id from users where phone_no = ?''', [phone], one=True)
    return rv[0] if rv else None

def get_user_id_from_name(username):
    ''' look up the user_id for a username '''
    rv = query_db('''select user_id from users where username = ?''', [usename], one=True)
    return rv[0] if rv else None

def get_task(task_id):
    ''' get the task for a task_id '''
    return Task(task_id)

def register_user(phone_no, username, user_type, user_id, address, pw_hash):
    user = User(user_id, username, True)
    user.phone_no = phone_no
    user.pw_hash = pw_hash
    user.address = address
    user.user_type = user_type
    user.update_db()
    return user

def ordered_notices(begin, to):
    rv = query_db('''select notice_id, user_id from notices order by notice_id desc limit ?''', [to])
    for [notice_id, user_id] in rv[begin:]:
        yield Notice(notice_id), User(user_id)

def all_users():
    rv = query_db('''select user_id from users where user_type = ? order by score desc''',
                  [STAFF])
    for user_id in rv:
        yield User(user_id)

def unsolved_tasks():
    rv = query_db('''select task_id from tasks where end_date = -1''', [])
    for task_id from rv:
        task = Task(task_id)
        user = User(task.user_id)
        yield task, user

def solved_tasks():
    rv = query_db('''select task_id from tasks where end_date > 0''', [])
    for task_id from rv:
        task = Task(task_id)
        user = User(task.user_id)
        yield task, user

def get_notices():
    rv = query_db('''select notice_id from notices where ''')

def welcome(user_id, show_num=5):
    user = get_user(user_id)
    messages = {}
    messages['notice'] = len(user.unchecked_notices(0, show_num))
    messages['event'] = len(user.unchecked_events())
    return messages

def account(username):
    user = get_user(username, 'username')
    messages = {}
    messages['user'] = user
    return messages

def user_tasks(username):
    user = get_user(username, 'username')
    messages = {}
    messages['create'] = list(user.created_tasks())
    messages['recived'] = list(user.participate_tasks(RECIVED))
    messages['complete'] = list(user.participate_tasks(COMPLETE))
    messages['abort'] = list(user.participate_tasks(ABORT))
    return messages

def get_peoples():
    messages = {}
    messages['users'] = list(all_users())
    return messages

def task_info(task_id):
    task = Task(task_id)
    creator = User(task.user_id)
    
    messages = {}
    messages['task'] = task
    messages['tags'] = list(task.tags())
    messages['creator'] = creator
    messages['recived'] = list(task.participate_users(RECIVED))
    messages['complete'] = list(task.participate_users(COMPLETE))
    messages['abort'] = list(task.participate_users(ABORT))

def tasks():
    messages = {}
    messages['new'] = list(unsolved_tasks())
    messages['solved'] = list(solved_tasks())
    return messages

def notices(user_id):
    messages = {}
    messages['notices'] = list(get_notices())
    return messages

def urgents():
    pass

def popular_tasks():
    pass

def tag():
    pass

def tags():
    pass

def new_task(user_id):
    pass

def new_tag(user_id):
    pass

