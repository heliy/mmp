#coding:UTF-8

class Task(object):
    def __init__(self, catogories, title, content):
        self.catogories = catogories
        self.title = title
        self.content = content

    def update_state(self):
        pass

class User(object):
    def __init__(self, username, pass_key, student_no, location):
        self.username = username
        self.pass_key = pass_key
        self.location = location
        self.student_no = student_no

    def post_task(self):
        pass

    def view_tasks(self):
        pass

    def reveive_task(self):
        pass

    def commit_posted(self):
        pass

    def statu_info(self):
        pass

class Tub(object):
    def __init__(self):
        pass
