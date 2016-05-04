drop table if exists users;
create table users (
    user_id integer primary key,
    username text not null,
    user_type integer not null default 0,
    phone_no integer default -1,
    pw_hash text default "empty",
    -- email text default "empty",
    address text default "empty",
    score float default 0.,
    latest_sign_time integer default 0,
    raised_events integer default 0,
    raised_notices integer default 0
);

drop table if exists tasks;
create table tasks (
    task_id integer primary key autoincrement,
    poster integer not null,
    helper integer default -1,
    create_date integer not null,
    title text default "empty",
    content text default "empty",
    public_date integer default -1,
    end_date integer default -1,
    statu integer default 0,
    score float default 0.
);

drop table if exists tags;
create table tags(
    tag_id integer primary key autoincrement,
    tagname text not null,
    creater integer default -1,
    create_time integer default -1
);

drop table if exists ttl;
create table ttl(
    task_id integer not null,
    tag_id integer not null,
    primary key (tag_id, task_id)
);

-- drop table if exists tub;
-- create table tub(
--     user_id integer not null,
--     task_id integer not null,
--     statu integer default -1,
--     score integer default -1,
--     primary key (user_id, task_id)
-- );

drop table if exists events;
create table events(
    event_id integer primary key autoincrement,
    user_id integer not null,
    task_id integer not null,
    act integer not null,
    init_date integer not null,
    statu integer not null default 0
);

drop table if exists notices;
create table notices(
    notice_id integer primary key autoincrement,
    user_id integer not null,
    created_date integer not null,
    title text default "empty",
    info text default "empty"
);
