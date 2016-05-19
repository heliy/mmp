#coding:UTF-8

import time

from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db, query_db
from database import test_init as init_db

from config import *

__all__ = [
    # VALID
    'have_phone',
    'have_user_id',
    'have_username',
    'have_tagname',

    # POST
    'init_db',
    'register_user',
    'log_in',
    'new_tag',
    'new_task',
    'new_notice',
    'commit_task',
    'receive_task',
    'complete_task',
    'abort_task',
    'check_events',
    'now_time_events',
    'check_notices',
    'hit_task',
    
    # GET
    'phone2name',
    'welcome',
    'account',
    'task_info',
    'tag_info',
    'notice_info',
    'user_tasks',
    'tasks',
    'notices',
    'urgents',
    'recents',
    'populars',
    'tags',
    'events',
    'past_helpers',
    ]

user_pool = {}
task_pool = {}
tag_pool = {}
notice_pool = {}

def add_user_pool(user):
    user_pool[user.user_id] = user
    user_pool[user.username] = user

def add_task_pool(task):
    task_pool[task.task_id] = task

def add_tag_pool(tag):
    tag_pool[tag.tag_id] = tag
    tag_pool[tag.tagname] = tag

def add_notice_pool(notice):
    notice_pool[notice.notice_id] = notice

def get_user(value, is_id=True):
    if value in user_pool:
        return user_pool[value]
    if is_id:
        user = User(value)
    else:
        user = User(username=value)
    add_user_pool(user)
    return user

def get_task(task_id):
    if task_id in task_pool:
        task = task_pool[task_id]
    else:
        task = Task(task_id)
        add_task_pool(task)
    return task

def get_tag(value, is_id=True):
    if value in tag_pool:
        return tag_pool[value]
    if is_id:
        tag = Tag(value)
    else:
        tag = Tag(tagname=value)
    add_tag_pool(tag)
    return tag

def get_notice(notice_id):
    if notice_id in notice_pool:
        return notice_pool[notice_id]
    notice = Notice(notice_id)
    add_notice_pool(notice)
    return notice
        
class User(object):
    def __init__(self, user_id=None, username=None, create=False):
        self.user_id = user_id
        self.username = username
        if create:
            self.create_db(username)
        if self.username is not None:
            self.load_db(username, 'username')
        else:
            self.load_db(user_id)

    def create_db(self, username):
        '''
        create a new user.
        '''
        db = get_db()
        t = int(time.time())
        db.execute('''insert into users (user_id, username, latest_sign_time)
                   values (?, ?, ?)''', [self.user_id, username, t])
        db.commit()

    def load_db(self, value, item='user_id'):
        ''' load user from users '''
        rv = query_db('select * from users where %s = ?' % (item), [value], one=True)
        [self.user_id, self.username, self.user_type, self.phone_no, self.pw_hash, self.address,
         self.latest, self.raised_events, self.raised_notices] = rv

    def update_db(self):
        ''' update user in users '''
        db = get_db()
        db.execute('''update users set user_type = ?, username = ?, phone_no = ?,
                      pw_hash = ?, address = ?, latest_sign_time = ?,
                      raised_events = ?, raised_notices = ? where user_id = ?''',
                   [self.user_type, self.username, self.phone_no, self.pw_hash, self.address,
                    self.latest, self.raised_events, self.raised_notices, self.user_id])
        db.commit()

    def delete_db(self):
        ''' delete user in users '''
        db = get_db()
        db.execute('''delete from users where user_id = ?''', [self.user_id])
        db.commit()

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def update_login(self):
        self.latest = int(time.time())
        self.update_db()
        
    def new_tag(self, tagname):
        tag = Tag(tagname=tagname, creator=self, create=True)
        add_tag_pool(tag)
        return tag

    def post_task(self, title='title', content='content', public_date=None, end_date=None, tags=[], calls=[]):
        if public_date is None:
            public_date = int(time.time())
        if end_date is None:
            end_date = public_date+1*60*60
        task = Task(user=self)
        task.title = title
        task.content = content
        task.public_date = public_date
        task.end_date = end_date
        task.update_db()
        ttls = [TTl(tag, task, True) for tag in tags]
        add_task_pool(task)
        for user in calls:
            event = Event(user_id=user.user_id, task_id=task.task_id, act=CALL)
        return task
    
    def receive_task(self, task):
        if task.poster_id == self.user_id:
            return None

        if task.helper() is not None:
            return None

        task.be_received(self)        
        event = Event(user_id=task.poster_id, task_id=task.task_id, act=RAISED)

    def created_tasks(self):
        rv = query_db('''select task_id from tasks where poster = ? order by task_id desc''',
                      [self.user_id])
        for task_id in rv:
            yield get_task(task_id[0])

    def add_events(self):
        self.raised_events += 1
        self.update_db()

    def check_events(self, task):
        print(task)
        rv = query_db('''select event_id from events where user_id = ? and task_id = ?
                         and statu == ?''', [self.user_id, task.task_id, RAISED])
        for eid in rv:
            event = Event(eid[0])
            event.check()
            self.raised_events -= 1
        self.update_db()
                
    def participate_tasks(self, statu):
        ''' get tasks user participate '''
        rv = query_db('''select task_id from tasks where helper = ? and closed_statu = ?
                         and is_closed = ? order by task_id desc''', [self.user_id, statu, OPEN])
        for task_id in rv:
            yield get_task(task_id[0])

    def participate_closed_tasks(self):
        rv = query_db('''select task_id from tasks where helper = ? and is_closed = ?
                         order by task_id desc''', [self.user_id, CLOSED])
        for task_id in rv:
            print(task_id[0])
            yield get_task(task_id[0])        

    def all_events(self):
        rv = query_db('''select event_id from events where user_id = ?
                         order by event_id desc''', [self.user_id])
        for event_id in rv:
            yield Event(event_id[0])

    def unchecked_events(self):
        ''' get unchecked events '''
        for event in self.all_events():
            if event.statu == RAISED:
                yield event

    def complete_task(self, task):
        task.closed_statu = COMPLETE
        task.update_db()
        event = Event(user_id=task.poster().user_id, task_id=task.task_id, act=COMPLETE)

    def commit_task(self, task, score):
        if self.user_id == task.poster().user_id:
            task.helper_score = score
            event = Event(user_id=task.helper().user_id, task_id=task.task_id, act=COMMIT)
        else:
            task.poster_score = score
            event = Event(user_id=task.poster().user_id, task_id=task.task_id, act=COMMIT)
        if task.poster_score > 0 and task.helper_score > 0:
            task.close()
        print(task.poster_score, task.helper_score, task.is_closed)
        task.update_db()

    def abort_task(self, task):
        task.closed_statu = ABORT
        task.update_db()
        event = Event(user_id=task.poster().user_id, task_id=task.task_id, act=ABORT)

    def mark(self):
        helper_scores = [task.helper_score for task in self.participate_closed_tasks()]
        poster_scores = [task.poster_score for task in self.created_tasks() if task.poster_score > 0]
        score = 0.7*(len(helper_scores) == 0 and 4.0 or sum(helper_scores)/len(helper_scores))
        score += 0.3*(len(poster_scores) == 0 and 4.0 or sum(poster_scores)/len(poster_scores))
        return score

    def post_notice(self, title='title', info='info'):
        notice = Notice(user_id=self.user_id, title=title, info=info)
        for user in all_users():
            user.add_notice()
        return notice

    def add_notice(self):
        self.raised_notices += 1
        self.update_db()

    def check_notices(self):
        self.raised_notices = 0
        self.update_db()

    def have_notices(self):
        return self.raised_notices > 0

    def have_events(self):
        return self.raised_events > 0
    
    
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
        
        db.execute('''insert into tasks (poster, create_date) values (?, ?)''',
                   [user_id, created_time])
        db.commit()
        rv = query_db('''select task_id from tasks where poster = ? and create_date= ?''',
                      [user_id, created_time], one=True)
        return rv[0] if rv else None

    def load_db(self):
        ''' load items from tasks '''
        rv = query_db('''select * from tasks where task_id = ?''', [self.task_id], one=True)
        [_, self.poster_id, self.helper_id, self.create_date, self.title, self.content,
         self.public_date, self.end_date, self.closed_statu, self.is_closed,
         self.poster_score, self.helper_score, self.hits] = rv

    def update_db(self):
        ''' update items in tasks '''
        db = get_db()
        db.execute('''update tasks set poster = ?, helper = ?, create_date = ?,
                   title = ?, content = ?, public_date = ?, end_date = ?, closed_statu = ?,
                   is_closed = ?, poster_score = ?, helper_score = ?, hits = ? where task_id = ? ''',
                   [self.poster_id, self.helper_id, self.create_date, self.title, self.content,
                    self.public_date, self.end_date, self.closed_statu, self.is_closed,
                    self.poster_score, self.helper_score, self.hits, self.task_id])
        db.commit()

    def delete_db(self):
        ''' detele this task from db. '''
        db = get_db()
        db.execute('''delete from tasks where task_id = ?''',
                   [self.task_id])

    def add_hit(self):
        self.hits += 1
        self.update_db()

    def hit_score(self, now=None):
        if now is None:
            now = int(time.time())
        return self.hits
        # return 60*float(self.hits)/(now-self.public_date)

    def poster(self):
        return get_user(self.poster_id)
    
    def helper(self):
        return get_user(self.helper_id) if self.helper_id >= 0 else None

    def now_time(self):
        if ALREADY == self.closed_statu or RECEIVED == self.closed_statu:
            now = int(time.time())
            if now > self.end_date:
                self.closed_statu = FAILED
                event = Event(user_id=self.poster_id, task_id=self.task_id, act=FAILED)
                if self.helper() is not None:
                    event = Event(user_id=self.helper_id, task_id=self.task_id, act=FAILED)
                self.close()
                self.update_db()

    def be_received(self, helper):
        self.helper_id = helper.user_id
        self.closed_statu = RECEIVED
        self.update_db()

    def tags(self):
        rv = query_db('''select tag_id from ttl where task_id = ?''', [self.task_id])
        for tag_id in rv:
            yield get_tag(tag_id[0])

    def delete_tag(self, tag):
        ttl = TTl(tag, self)
        ttl.delete_db()

    def add_tag(self, tag):
        ttl = TTl(tag, self, True)

    def statu_str(self):
        if self.is_closed == CLOSED:
            return CLOSED_STR
        else:
             return TASK_STATU_LABELS[self.closed_statu]
         
    def close(self):
        self.is_closed = CLOSED
        self.update_db()

class Tag(object):
    def __init__(self, tag_id=None, tagname=None, creator=None, create=False):
        if create:
            self.create_db(tagname, creator)
        elif tag_id is None:
            self.load_db(tagname, 'tagname')
        else:
            self.load_db(tag_id)
        self.load_db()

    def create_db(self, tagname, creator):
        '''
        create a new tag and return tag_id.
        '''
        db = get_db()
        db.execute('''insert into tags (tagname, creater) values (?, ?)''',
                   [tagname, creator.user_id])
        db.commit()
        self.load_db(tagname, 'tagname')
        self.init_time = int(time.time())
        self.update_db()
        return self.tag_id

    def load_db(self, value=None, item='tag_id'):
        if value is None:
            value = self.tag_id

        
        rv = query_db('select * from tags where %s = ?' % (item),
                      [value], one=True)
        [self.tag_id, self.tagname, self.creater, self.init_time] = rv

    def update_db(self):
        ''' update tagname of tag. '''
        db = get_db()
        db.execute('''update tags set tagname = ?, creater = ?, create_time = ?
                      where tag_id = ?''',
                   [self.tagname, self.creater, self.init_time, self.tag_id])
        db.commit()

    def delete_db(self):
        ''' delete tag in tags '''
        db = get_db()
        db.execute(''' delete from tags where tag_id = ?''', [self.tag_id])
        db.commit()

    def creator(self):
        return get_user(self.creater)

    def tasks(self):
        rv = query_db('''select task_id from ttl where tag_id = ? order by task_id
                         desc''', [self.tag_id])
        tasks = [get_task(tid[0]) for tid in rv]
        tasks_dic = {}
        for task in tasks:
            date = task.create_date%(24*60*60)
            if date in tasks_dic:
                tasks_dic[date].append(task)
            else:
                tasks_dic[date] = [task]

        def rank_task(task):
            return task.poster().mark()
        
        for date in sorted(tasks_dic.keys(), reverse=True):
            for task in sorted(tasks_dic[date], key=rank_task):
                yield task            

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
        
class Event(object):
    def __init__(self, event_id=None, user_id=None, task_id=None, act=None):
        if event_id is None:
            self.event_id = self.create_db(user_id, task_id, act)
        else:
            self.event_id = event_id
        self.load_db()
        if event_id is None:
            self.user().add_events()

    def create_db(self, user_id, task_id, act):
        db = get_db()
        init_date = int(time.time())
        db.execute('''insert into events (user_id, task_id, act, init_date, statu)
                  values (?, ?, ?, ?, ?)''', [user_id, task_id, act, init_date, RAISED])
        db.commit()
        rv = query_db('''select event_id from events where user_id = ? and task_id = ?
                      and init_date = ?''', [user_id, task_id, init_date], one=True)
        return rv[0]

    def load_db(self):
        rv = query_db('''select * from events where event_id = ?''',
                      [self.event_id], one=True)
        [self.event_id, self.user_id, self.task_id, self.act, self.init_date, self.statu] = rv

    def update_db(self):
        db = get_db()
        db.execute('''update events set statu = ? where event_id = ?''',
                   [self.statu, self.event_id])
        db.commit()

    def delete_db(self):
        db = get_db()
        db.execute('''delete from events where event_id = ?''', [self.event_id])

    def check(self):
        self.statu = CHECKED
        self.update_db()

    def user(self):
        return get_user(self.user_id)

    def task(self):
        return get_task(self.task_id)

class Notice(object):
    def __init__(self, notice_id=None, user_id=None, title='title', info='info'):
        if notice_id is None:
            self.notice_id = self.create_db(user_id, title, info)
        else:
            self.notice_id = notice_id
        self.load_db()

    def create_db(self, user_id, title, info):
        db = get_db()
        created_time = int(time.time())
        db.execute('''insert into notices (user_id, created_date, title, info) values
                   (?, ?, ?, ?)''', [user_id, created_time, title, info])
        db.commit()
        rv = query_db('''select notice_id from notices where user_id = ? and created_date = ?''',
                      [user_id, created_time], one=True)
        return rv[0]

    def load_db(self):
        rv = query_db('''select * from notices where notice_id = ? ''', [self.notice_id], one=True)
        [self.notice_id, self.user_id, self.created_date, self.title, self.info] = rv

    def update_db(self):
        db = get_db()
        db.execute('''update notices set user_id = ?, created_date = ?, title = ?, info = ?
                   where notice_id = ?''', [self.user_id, self.created_date, self.title,
                                            self.info, self.notice_id])
        db.commit()

    def delete_db(self):
        db = get_db()
        db.execute('''delete from notices where notice_id = ?''', [self.notice_id])

    def poster(self):
        return get_user(self.user_id)

def all_tags():
    rv = query_db('''select tag_id from tags order by tag_id desc''')
    for tag_id in rv:
        yield get_tag(tag_id[0])

def all_users(user_type=STUDENT):
    rv = query_db('''select user_id from users where user_type = ? order by user_id desc''',
                  [user_type])
    for user_id in rv:
        yield get_user(user_id[0])

def all_tasks(statu=None):
    if statu is None:
        rv = query_db('''select task_id from tasks order by task_id desc''')
    elif statu == CLOSED_STR:
        rv = query_db('''select task_id from tasks where is_closed = ? order by task_id desc''',
                      [CLOSED])
    else:
        rv = query_db('''select task_id from tasks where closed_statu == ? order by task_id
                      desc''', [statu])
    for task_id in rv:
        yield get_task(task_id[0])

def all_notices():
    rv = query_db('''select notice_id from notices order by notice_id desc''')
    for notice_id in rv:
        yield get_notice(notice_id[0])

def all_events(user_id):
    rv = query_db('''select event_id from events where user_id = ? order by event_id desc''',
                  [user_id])
    for event_id in rv:
        yield Event(event_id[0])

def phone2user(phone_no):
    rv = query_db('''select user_id from users where phone_no = ?''', [phone_no], one=True)
    return get_user(rv[0])

# ------------ VALID ----------------------------------

def have_phone(phone_no):
    rv = query_db('''select phone_no from users''')
    for p in rv:
        if p[0] == phone_no:
            return True
    return False

def have_username(username):
    rv = query_db('''select username from users''')
    for un in rv:
        if username == un[0]:
            return True
    return False

def have_user_id(user_id):
    rv = query_db('''select user_id from users''')
    for ui in rv:
        # print("in db:", ui[0])
        if user_id == ui[0]:
            return True
    return False

def have_tagname(tagname):
    rv = query_db('''select tagname from tags''')
    for ui in rv:
        if tagname == ui[0]:
            return True
    return False    

# ------------- POST ------------------------------------

def register_user(user_id, username, user_type, phone_no, address, password):
    user = User(user_id, username, True)
    user.phone_no = phone_no
    user.pw_hash = generate_password_hash(password)
    user.address = address
    user.user_type = user_type
    user.update_db()
    add_user_pool(user)
    return account(user.user_id)

def log_in(phone_no, pw):
    if have_phone(phone_no):
        user = phone2user(phone_no)
        if user.check_password(pw):
            return account(user.user_id)  # success
        else:
            return 0                      # incorrect password
    return -1                             # have not registered

def new_tag(username, tagname):
    user = get_user(username, False)
    user.new_tag(tagname)

def new_task(username, title, content, public_date, end_date, tagnames, callnames):
    user = get_user(username, False)
    tags = [get_tag(tagname, False) for tagname in tagnames]
    calls = [get_user(username, False) for username in callnames]
    task = user.post_task(title, content, public_date, end_date, tags, calls)
    return task_info(task.task_id)

def commit_task(username, task_id, mark):
    user = get_user(username, False)
    task = get_task(task_id)
    user.commit_task(task, mark)
    
def receive_task(username, task_id):
    user = get_user(username, False)
    task = get_task(task_id)
    user.receive_task(task)

def complete_task(username, task_id):
    user = get_user(username, False)
    task = get_task(task_id)
    user.complete_task(task)

def abort_task(username, task_id):
    user = get_user(username, False)
    task = get_task(task_id)
    user.abort_task(task)

def new_notice(username, title, info):
    user = get_user(username, False)
    notice = user.post_notice(title, info)
    return notice_info(notice.notice_id)

def check_events(username, tid, is_task=True):
    user = get_user(username, False)
    if is_task:
        task = get_task(tid)
        user.check_events(task)
    else:
        event = Event(tid)
        task = event.task()
        user.check_events(task)

def check_notices(username):
    user = get_user(username, False)
    user.check_notices()

def now_time_events():
    for user in all_users():
        for event in all_events(user.user_id):
            event.now_time()

def hit_task(task_id):
    task = get_task(task_id)
    if task.is_closed == OPEN:
        task.add_hit()

# ------------- GET --------------------------------------

def welcome(username):
    user = get_user(username, False)
    messages = {}
    messages['notice'] = user.raised_notices
    messages['event'] = user.raised_events
    messages['usertype'] = user.user_type
    return messages

def phone2name(phone):
    user = phone2user(phone_no)
    return user.username

def account(username):
    user = get_user(username, False)
    messages = {}
    messages['usertype'] = user.user_type
    messages['username'] = user.username
    messages['phone_no'] = user.phone_no
    messages['user_id'] = user.user_id
    messages['address'] = user.address
    messages['score'] = user.mark()
    return messages

def task_info(task_id):
    messages = {}
    task = get_task(task_id)
    messages['task_id'] = task.task_id
    messages['poster'] = task.poster().username
    if task.helper():
        messages['helper'] = task.helper().username
    messages['create_date'] = task.create_date
    messages['title'] = task.title
    messages['content'] = task.content
    messages['public_date'] = task.public_date
    messages['end_date'] = task.end_date
    messages['statu'] = task.statu_str()
    messages['poster_score'] = task.poster_score
    messages['helper_score'] = task.helper_score    
    messages['tags'] = [tag.tagname for tag in task.tags()]
    messages['hits'] = task.hit_score()
    return messages

def tag_info(tagname):
    tag = get_tag(tagname, False)
    messages = {}
    messages['tag_id'] = tag.tag_id
    messages['tagname'] = tag.tagname
    messages['creator'] = account(tag.creator().username)
    messages['init_time'] = tag.init_time
    messages['tasks'] = [task.task_id for task in tag.tasks()]
    return messages

def notice_info(notice_id):
    messages = {}
    notice = get_notice(notice_id)
    messages['notice_id'] = notice.notice_id
    messages['poster'] = account(notice.poster().username)
    messages['post_date'] = notice.created_date
    messages['title'] = notice.title
    messages['info'] = notice.info
    return messages

def event_info(event_id):
    event = Event(event_id)
    messages = {}
    messages['event_id'] = event.event_id
    messages['task'] = task_info(event.task().task_id)
    messages['user'] = account(event.user().username)
    messages['act'] = event.act
    messages['raised_date'] = event.init_date
    messages['statu'] = event.statu == RAISED
    return messages

def user_tasks(username):
    user = get_user(username, False)
    messages = {}
    messages[CREATE] = [task_info(task.task_id) for task in user.created_tasks()]
    messages[CLOSED_STR] = [task_info(task.task_id) for task in user.participate_closed_tasks()]
    messages[RECEIVED_STR] = [task_info(task.task_id) for task in user.participate_tasks(RECEIVED)]
    messages[COMPLETE_STR] = [task_info(task.task_id) for task in user.participate_tasks(COMPLETE)]
    messages[FAILED_STR] = [task_info(task.task_id) for task in user.participate_tasks(FAILED)]
    messages[ABORT_STR] = [task_info(task.task_id) for task in user.participate_tasks(ABORT)]
    print(messages)
    return messages

def peoples():
    messages = {}
    messages['users'] = [account(user.username) for user in all_users()]
    return {"users": messages}

def tasks():
    messages = []
    for task in all_tasks():
        messages.append(task_info(task.task_id))
    return {'tasks': messages}

def notices():
    messages = []
    for notice in all_notices():
        messages.append(notice_info(notice.notice_id))
    return {"notices": messages}

def urgents(time_scale):
    messages = []
    t = int(time.time())+time_scale
    rv = query_db('''select task_id from tasks where closed_statu = ? and end_date < ?
                     order by end_date''', [ALREADY, t])
    for task_id in rv:
        messages.append(task_info(task_id[0]))
    return {"urgents": messages}

def recents(time_scale):
    messages = []
    t = int(time.time())-time_scale
    rv = query_db('''select task_id from events where init_date > ?''', [t])
    for task_id in list(set([id[0] for id in rv])):
        if get_task(task_id).is_closed == OPEN:
            messages.append(task_info(task_id))
    return {"recents": messages}    

def populars():
    messages = []
    t = int(time.time())
    rv = query_db('''select task_id from tasks where is_closed = ? ''', [OPEN])
    tasks = [get_task(r[0]) for r in rv]
    def rank_key(x):
        return x.hit_score(t)
    tasks.sort(key=rank_key, reverse=True)
    for task in tasks:
        messages.append(task_info(task.task_id))
    return {'populars':messages}

def tags():
    messages = []
    for tag in all_tags():
        messages.append(tag_info(tag.tagname))
    return {"tags": messages}

def events(username):
    user = get_user(username, False)
    messages = {}
    messages['num_unchecked'] = user.raised_events
    messages['events'] = []
    for event in user.all_events():
        messages['events'].append(event_info(event.event_id))
    return messages

def past_helpers(username):
    messages = []
    user = get_user(username, False)
    helpers = set()
    for task in user.created_tasks():
        task.helper() is not None and helpers.add(task.helper())
        
    def rank_help(helper):
        return helper.mark()
    messages = [account(helper.username) for helper in sorted(list(helpers),
                                                              key=rank_help, reverse=True)]
    return {"helpers": messages}
