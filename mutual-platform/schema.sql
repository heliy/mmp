drop table if exists users;
create table users(
    user_id integer primary key,
    username text not null,
    phone_no integer default -1,
    pw_hash text default "empty",
    email text default "empty",
    address text default "empty",
);

drop table if exists tasks;
create table tasks(
    task_id integer primary key autoincrement,
    post_user integer not null,
    create_date integer not null,
    max_participants integer default 1,
    title text default "empty",
    content text default "empty",
    public_date integer default -1,
    begin_date integer default -1,
    end_date integer default -1,
)

drop table if exists types;
create table types(
    type_id integer primary key autoincrement,
    typename text not null,
)

drop table if exists ttl;
create table ttl(
    task_id integer not null,
    type_id integer not null,
    primary key (type_id, task_id),
)

drop table if exists tub;
create table tub(
    user_id integer not null,
    task_id integer not null,
    statu integer default -1,
    score integer default -1,
    primary key (user_id, task_id),
)
