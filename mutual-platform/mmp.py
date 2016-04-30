#coding:UTF-8

"""
   Micro Mutual Platform (MMP)
   ~~~~~~~~~~~~~~~

   A micro mutual platform written with Flask and sqlite3.

   :copyright:
   :license:
"""

from flask import Flask, request, session, redirect, g
from flask import render_template

app = Flask(__name__)

@app.route('/')
def welcome():
    '''
    homepage of MMP.
    if one has logged, it will present models of site.
    otherwise, it will show simple welcome page.
    '''
    if g.user:
        return render_template('welcome.html', messages=welcome(session['user_id']))
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
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    pass

@app.route('/logout')
def logout():
    pass

if __name__ == "__main__":
    app.debug = True
    app.run()
