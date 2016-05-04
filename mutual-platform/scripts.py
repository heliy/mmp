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
