#coding:UTF-8


import models as m

nana = m.register_user(1, 'nana', m.STUDENT, 71, 'pku', 'rtus')
yuri = m.register_user(2, 'yuri', m.STUDENT, 72, 'pku', '43yu')
mochi = m.register_user(4, 'mochi', m.STUDENT, 332, 'pku', 'scaa')
leader = m.register_user(3, 'leader', m.STAFF, 999, 'pku', 'miho')

yuri.new_tag('ameda')
nana.new_tag('mochi')
leader.new_tag('ablum')
tags = [x for x in m.get_tags()]

yuri.post_task('no.4', tags=[m.Tag(tagname='ablum')])
nana.post_task('hale', tags=[m.Tag(tagname='mochi')])
leader.post_task('hand', tags=tags)

students = list(m.all_users())
staffs = list(m.all_users(m.STAFF))
tasks = list(m.unsolved_tasks())

nana.receive_task(tasks[0])
nana.participate_tasks(m.RECEIVED)

for event in yuri.unchecked_events():
    yuri.check_event(event)

nana.complete_task(tasks[0])
yuri.commit_task(tasks[0], 5)

mochi.receive_task(tasks[2])
mochi.abort_task(tasks[2])

leader.post_notice()

