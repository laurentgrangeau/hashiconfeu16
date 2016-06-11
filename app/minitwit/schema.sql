create table flag (
  flag_id SERIAL PRIMARY KEY
);

drop table if exists twituser;
create table twituser (
  username text not null,
  email text not null,
  pw_hash text not null,
  user_id SERIAL primary key
);

drop table if exists follower;
create table follower (
  who_id integer,
  whom_id integer
);

drop table if exists message;
create table message (
  author_id integer not null,
  text text not null,
  pub_date integer,
  message_id serial primary key
);
