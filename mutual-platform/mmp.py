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

@app.route('/task/<task_id>')
def task_info_page(task_id):
    if not g.user:
        return redirect(url_for('welcome_page'))
    return render_template("task.html", messages=task_info(task_id))

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
    return render_template('tasks.html', messages=tasks())

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

@app.route('/tag/<tag_id>')
def tag_info_page(tag_id):
    if not g.user:
        return redirect(url_for('welcome_page'))
    return render_template('tag.html', messages=tag(tag_id))

@app.route('/tags')
def all_tags_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    return render_template('tags.html', messages=tags())

@app.route('/new/task', methods=["GET", "POST"])
def new_task_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    return render_template('new_task.html', messages=new_task(session['user_id']))

@app.route('/new/tag')
def new_tag_page():
    if not g.user:
        return redirect(url_for('welcome_page'))
    return render_template('new_tag.html', messages=new_tag(session['user_id']))

@app.route('/login', methods=['GET', 'POST'])
def login():
    ''' Logs the user in. '''
    if g.user:
        return redirect(url_for('welcome_page'))
    error = None
    if request.method == 'POST':
        user = get_user(request.form['username'], False)
        if user is None:
            error = 'Invalid username'
        elif not user.check_password(request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user.user_id
            session['username'] = user.username
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
