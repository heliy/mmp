#coding:UTF-8

"""
   Micro Mutual Platform (MMP)
   ~~~~~~~~~~~~~~~

   A micro mutual platform written with Flask and sqlite3.

   :copyright:
   :license:
"""

from flask import Flask, request, session, redirect, g
from flask import render_template, flash
from werkzeug.security import generate_password_hash

from models import *

app = Flask(__name__)

@app.route('/')
def welcome():
    '''
    homepage of MMP.
    if one has logged, it will present models of site.
    otherwise, it will show simple welcome page.
    '''
    if g.user:
        messages = welcome(session['user_id'])
        return render_template('welcome.html', messages=messages)
    else:
        return render_template('index.html')

@app.route('/people/<username>')
def user_info(username):
    if not g.user:
        return redirect(url_for('welcome'))
    messages = user(username)
    if session['username'] == username:
        return render_template("mypage.html", messages=messages)
    else:
        return render_template("yourpage.html", messages=messages)

@app.route('/peoples')
def all_users():
    if not g.user:
        return redirect(url_for('welcome'))
    return render_template("peoples.html", messages=peoples())

@app.route('/task/<task_id>')
def task_info(task_id):
    if not g.user:
        return redirect(url_for('welcome'))
    return render_template("task.html", messages=task(task_id))

@app.route('/tasks')
def all_tasks():
    if not g.user:
        return redirect(url_for('welcome'))
    return render_template('tasks.html', messages=tasks())

@app.route('/notice')
def notice():
    if not g.user:
        return redirect(url_for('welcome'))
    return render_template('notice.html', messages=notice(session['user_id']))

@app.route('/help')
def help():
    return render_template("help.html", messages=[])

@app.route('/urgent')
def urgent():
    if not g.user:
        return redirect(url_for('welcome'))
    return render_template('urgent.html', messages=urgents())    

@app.route('/popular')
def popular():
    if not g.user:
        return redirect(url_for('welcome'))
    return render_template('popular.html', messages=popular_tasks())    

@app.route('/tag/<tag_id>')
def tag_info(tag_id):
    if not g.user:
        return redirect(url_for('welcome'))
    return render_template('tag.html', messages=tag(tag_id))

@app.route('/tags')
def all_tags():
    if not g.user:
        return redirect(url_for('welcome'))
    return render_template('tags.html', messages=tags())

@app.route('/new/task')
def new_task():
    if not g.user:
        return redirect(url_for('welcome'))
    return render_template('new_task.html', messages=new_task(session['user_id']))

@app.route('/new/tag')
def new_tag():
    if not g.user:
        return redirect(url_for('welcome'))
    return render_template('new_tag.html', messages=new_tag(session['user_id']))

@app.route('/login', methods=['GET', 'POST'])
def login():
    ''' Logs the user in. '''
    if g.user:
        return redirect(url_for('welcome'))
    error = None
    if request.method == 'POST':
        user = get_user(request.form['username'], 'username')
        if user is None:
            error = 'Invalid username'
        elif not user.check_password(request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user.user_id
            session['username'] = user.username
            return redirect(url_for('welcome'))
    return render_template('login.html', error=error)

@app.route('/register/phone', methods=['GET', 'POST'])
def register_phone():
    ''' registers the user, 1st step, confrom phone number '''
    if g.user:
        return redirect(url_for('welcome'))
    error = None
    if request.method == 'POST':
        if not request.form['telephone']:
            error = 'You have to enter a telephone number'
        elif get_user_id_from_phone(request.form['telephone']) is not None:
            error = 'The telephone number is already regisitered'
        else:
            session['telephone'] = request.form['telephone']
            return redirect(url_for('register_valid'))
    return render_template('register_phone.html', error=error)

@app.route('/register/valid', method=['GET', 'POST']):
def register_valid():
    ''' registers the user, 2nd step, validate phone number '''
    if g.user:
        return redirect(url_for('welcome'))
    if request.method == 'POST':
        # TODO
        return redirect(url_for('register_info'))
    return render_template('register_valid.html', messages=[session['telephone']])

@app.route('/register/info', method=['GET', 'POST'])
def register_info():
    if g.user:
        return redirect(url_for('welcome'))
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
        elif get_user(request.form['user_id']) is not None:
            error = 'The student number is already taken'
        elif get_user_id_from_name(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            register_user(session['telephone'], request.form['username'],
                          request.form['user_id'], request.form['address'],
                          generate_password_hash(request.form['password']))
            session.pop('telephone', None)
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register_info.html', messages=[session['telephone']],
                           error=error)

@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('welcome'))

if __name__ == "__main__":
    app.debug = True
    app.run()
