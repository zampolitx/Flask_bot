create table if not exists birthday (
    id              integer primary key AUTOINCREMENT, 
    date_bd         text not NULL, 
    full_name       text not NULL, 
    description     text not NULL,
    user_id         text not null);
