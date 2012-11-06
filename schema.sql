drop table if exists tasks;
create table tasks (
  id integer primary key autoincrement,
  title string not null,
  detail string not null
);