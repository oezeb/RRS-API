drop table if exists reservations;
drop table if exists reservation_tickets;
drop table if exists users;
drop table if exists sessions;
drop table if exists rooms;
drop table if exists periods;

/*==============================================================*/
/* Table: periods                                               */
/*==============================================================*/
create table periods 
(
   period_id            integer                        not null,
   name                 varchar(50)                    not null,
   start_time           time                           not null,
   end_time             time                           not null,
   constraint PK_PERIODS primary key clustered (period_id)
);

/*==============================================================*/
/* Table: rooms                                                 */
/*==============================================================*/
create table rooms 
(
   room_id              integer                        not null,
   name                 varchar(50)                    not null,
   seating_capacity     integer                        not null,
   open_time            time                           not null,
   close_time           time                           not null,
   type                 integer                        not null,
   status               integer                        not null,
   constraint PK_ROOMS primary key clustered (room_id)
);

/*==============================================================*/
/* Table: sessions                                              */
/*==============================================================*/
create table sessions 
(
   session_id           integer                        not null,
   name                 varchar(50)                    not null,
   is_current           bit                            null,
   start_time           timestamp                      not null,
   end_time             timestamp                      not null,
   constraint PK_SESSIONS primary key clustered (session_id)
);

/*==============================================================*/
/* Table: users                                                 */
/*==============================================================*/
create table users 
(
   username             varchar(50)                    not null,
   password             varchar(1024)                    not null,
   name                 varchar(50)                    null,
   level                integer                        null,
   email                varchar(100)                   null,
   constraint PK_USERS primary key clustered (username)
);

/*==============================================================*/
/* Table: reservation_tickets                                   */
/*==============================================================*/
create table reservation_tickets 
(
   reservation_id       integer                        not null,
   username             varchar(50)                    not null,
   constraint PK_RESERVATION_TICKETS primary key clustered (reservation_id),
   constraint FK_RESERVAT_USER_RESE_USERS foreign key (username)
      references users (username)
      on update restrict
      on delete restrict
);

/*==============================================================*/
/* Table: reservations                                          */
/*==============================================================*/
create table reservations 
(
   reservation_id       integer                        not null,
   reservation_no       integer                        not null,
   room_id              integer                        not null,
   session_id           integer                        not null,
   start_time           timestamp                      not null,
   end_time             timestamp                      not null,
   status               integer                        not null,
   note                 varchar(100)                   null,
   create_time          timestamp                      null,
   update_time          timestamp                      null,
   cancel_time          timestamp                      null,
   constraint PK_RESERVATIONS primary key clustered (reservation_id, reservation_no),
   constraint FK_RESERVAT_RESERVATI_RESERVAT foreign key (reservation_id)
      references reservation_tickets (reservation_id)
      on update restrict
      on delete restrict,
   constraint FK_RESERVAT_ROOM_RESE_ROOMS foreign key (room_id)
      references rooms (room_id)
      on update restrict
      on delete restrict,
   constraint FK_RESERVAT_SESSION_R_SESSIONS foreign key (session_id)
      references sessions (session_id)
      on update restrict
      on delete restrict
);
