#coding:UTF-8

"""
   Micro Mutual Platform (MMP)
   ~~~~~~~~~~~~~~~

   A micro mutual platform written with Flask and sqlite3.

   :copyright:
   :license:
"""
import os
import sys

from flask import Flask, request, session, redirect, g, url_for
from flask import render_template, flash

from models import *
from config import *
from utils import *

SECRET_KEY = 'development key'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

@app.before_request
def before_request():
    g.user = None
    if 'username' in session:
        try:
            try:
                g.user = session['username']
            except TypeError:
                pass
        except KeyError:
            pass

@app.route('/')
def welcome_page():
    '''
    homepage of MMP.
    if one has logged, it will present models of site.
    otherwise, it will show simple welcome page.
    '''
    if g.user:
        ms= welcome(session['username'])
        return render_template('welcome.html', username=session['username'],
                               usertype=ms['usertype'], notice=ms['notice'], event=ms['event'])
    else:
        return render_template('index.html')

@app.route('/people/<username>')
def people_page(username):
    if not g.user:
        return redirect(url_for('welcome_page'))
    messages = account(username)
    if session['username'] == username:
        return render_template("mypage.html", messages=messages)
    else:
        return render_template("yourpage.html", messages=messages)

@app.route('/people/<username>/tasks')
def people_tasks_page(username):
    if not g.user:
        return redirect(url_for('welcome_page'))
    messages = user_tasks(username)
    if session['username'] == username:
        return render_template("mytasks.html", messages=messages)
    else:
        return render_template("yourtasks.html", messages=messages)    

@app.route('/accounts/<username>', methods=['GET', 'POST'])
def update_account_page(username):
    #  TODO -> update accout information
    if not g.user:
        return redirect(url_for('welcome_page'))
    error = None
    if request.mehod == 'POST':
        pass

@app.route('/peoples')
def all_users_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    return render_template("peoples.html", messages=peoples())

@app.route('/task/<task_id>', methods=['GET', 'POST'])
def task_page(task_id):
    if not g.user:
        return redirect(url_for('welcome_page'))
    error = None
    if request.method == 'POST':
        pass
    ms = task_info(task_id)
    poster = ms.get('poster')
    helper = ms.get('helper', None)
    title = ms.get('title')
    content = ms.get('content')
    create_date = format_datetime(ms.get('create_date'))
    public_date = format_datetime(ms.get('public_date'))
    end_date = format_datetime(ms.get('end_date'))
    statu = ms.get('statu_str')
    score = ms.get('score')
    return render_template('task.html', poster=poster, helper=helper, title=title, 
                           content=content, create_date=create_date, public_date=public_date,
                           end_date=end_date, statu=statu, username=session['username'])

@app.route('/task/<task_id>/tags', methods=['GET', 'POST'])
def task_tags_page(task_id):
    if not g.user:
        return redirect(url_for('welcome_page'))
    error = None
    if request.methos == 'POST':
        # TODO
        return redirect('/task/%s' % task_id)
    return render_template('task_tags.html')

@app.route('/tasks')
def all_tasks_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    task_ids, posters, create_dates, status, titles = [], [], [], [], []
    for t in tasks()['tasks']:
        task_ids.append(t['task_id'])
        posters.append(t['poster'])
        create_dates.append(format_datetime(t['create_date']))
        titles.append(t['title'])
        status.append(t['statu_str'])
    print(status)
    return render_template('tasks.html', ids=task_ids, titles=titles, posters=posters,
                           create_dates=create_dates, status=status, num=len(titles))

@app.route('/notices')
def notices_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    return render_template('notice.html', messages=notice())

@app.route('/events')
def events_page():
    pass

@app.route('/help')
def help_page():
    return render_template("help.html", messages=[])

@app.route('/recent')
def recent_page():
    pass

@app.route('/urgent')
def urgent_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    return render_template('urgent.html', messages=urgents())    

@app.route('/popular')
def popular_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    return render_template('popular.html', messages=popular_tasks())    

@app.route('/tag/<tagname>')
def tag_info_page(tagname):
    if not g.user:
        return redirect(url_for('welcome_page'))
    ms = tag_info(tagname)
    return render_template('tag.html', name=ms['tagname'], creater=ms['creator']['username'],
                           init=format_datetime(ms['init_time']), tasks=ms['tasks'])

@app.route('/tags')
def all_tags_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    tag_ids, tagnames = [], []
    for tag in tags()['tags']:
        tag_ids.append(tag['tag_id'])
        tagnames.append(tag['tagname'])
    return render_template('tags.html', ids=tag_ids, names=tagnames, num=len(tag_ids))

@app.route('/new/task', methods=["GET", "POST"])
def new_task_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    error = None
    tagnames = [t['tagname'] for t in tags()["tags"]]
    if request.method == "POST":
        if not request.form['title']:
            error = "You have to enter the title of task"
        elif not request.form['content']:
            error = "You have to enter the content of task"
        else:
            # error = date(request.form, "public")
            # if type(error) == str:
            #     return render_template('new_task.html', error=error, tags=tagnames)
            # public_date = error
            public_date = datetime.now().timestamp()
            error = date(request.form, "end")
            if type(error) == str:
                return render_template('new_task.html', error=error, tags=tagnames)
            end_date = error
            now = int(datetime.now().timestamp())
            print(public_date, end_date, now)
            # if public_date < now:
            #     error = "You need enter a public date after NOW"
            if end_date < public_date:
                error = "You need enter a end date after public date"
            else:
                tagnames = [tag for tag in tagnames if request.form.get(tag, None)]
                ms = new_task(session['username'], request.form["title"], request.form['content'],
                              public_date, end_date, tagnames)
                return redirect(url_for("task_page", task_id=ms["task_id"]))
    return render_template('new_task.html', error=error, tags=tags()["tags"])

@app.route('/new/tag', methods=["GET", "POST"])
def new_tag_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    error = None
    if request.method == 'POST':
        if not request.form['tagname']:
            error = "You have to enter the name of tag"
        else:
            tagname = request.form['tagname']
            if have_tagname(tagname):
                error = "The name is already created, see:"
                ms = tag_info(tagname)
                return render_template('new_tag.html', error=error, name=ms['tagname'])
            else:
                new_tag(session['username'], tagname)
                return redirect(url_for('tag_info_page', tagname=tagname))
    return render_template('new_tag.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    ''' Logs the user in. '''
    if g.user:
        return redirect(url_for('welcome_page'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = "You have to enter your username"
        elif not request.form['password']:
            error = "You have to enter your password"
        else:
            statu = log_in(request.form['username'], request.form['password'])
            if statu < 0:
                error = 'Invalid username'
            elif statu == 0:
                error = 'Invalid password'
            else:
                flash('You were logged in')
                session['username'] = request.form['username']
                return redirect(url_for('welcome_page'))
    return render_template('login.html', error=error)

@app.route('/register/phone', methods=['GET', 'POST'])
def register_phone():
    ''' registers the user, 1st step, confrom phone number '''
    if g.user:
        return redirect(url_for('welcome_page'))
    error = None
    if request.method == 'POST':
        if not request.form['telephone']:
            error = 'You have to enter a telephone number'
        phone = int(request.form['telephone'])
        if have_phone(phone):
            error = 'The telephone number is already regisitered'
        else:
            session['telephone'] = request.form['telephone']
            return redirect(url_for('register_valid'))
    return render_template('register_phone.html', error=error)

@app.route('/register/valid', methods=['GET', 'POST'])
def register_valid():
    ''' registers the user, 2nd step, validate phone number '''
    if g.user:
        return redirect(url_for('welcome_page'))
    if 'telephone' not in session:
        return redirect(url_for('register_phone'))
    if request.method == 'POST':
        session['sure'] = True
        return redirect(url_for('register_info'))
    return render_template('register_valid.html', phone=session['telephone'])

@app.route('/register/info', methods=['GET', 'POST'])
def register_info():
    if g.user:
        return redirect(url_for('welcome_page'))
    if 'telephone' not in session:
        return redirect(url_for('register_phone'))
    if not session['sure']:
        return redirect(url_for('register_valid'))
    
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['user_id']:
            error = 'You have to enter your student number'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif not request.form['address']:
            error = 'You have to enter your address'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        else:
            try:
                user_id = int(request.form['user_id'])
            except ValueError:
                error = "Invalid Student No or Staff No."
        type_int = str(request.form.get("type")) == "student" and STUDENT or STAFF
        if error is None:
            username = request.form['username']
            if have_user_id(user_id):
                error = 'The student number is already taken'
            elif have_username(username):
                error = 'The username is already taken'
            else:
                user_messages = register_user(user_id, username, type_int, 
                                              session['telephone'], request.form['address'],
                                              request.form['password'])
                session.pop('telephone', None)
                session.pop('sure', None)
                flash('You were successfully registered and can login now')
                return redirect(url_for('login'))
    return render_template('register_info.html', phone=session['telephone'], error=error)

@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('welcome_page'))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'renew':
        os.system("rm *.db")
        init_db()
    else:
        app.debug = True
        app.run()
