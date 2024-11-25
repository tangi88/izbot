create table locations(
    id integer primary key,
    latitude float,
    longitude float,
    date_create datetime,
    date_create_repr varchar(255)
);

create table shots(
    id integer primary key,
    date_create datetime,
    date_create_repr varchar(255)
    side varchar(255)
);
