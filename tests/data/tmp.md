A meeting room reservation system database contains the following tables:

- users:
  - username (primary key)
  - password
  - name 
  - email (optional)

- rooms:
  - room_id (primary key)
  - room_name
  - capacity

- reservations:
  - resv_id (primary key)
  - username (foreign key)
  - room_id (foreign key)
  - title
  - note (optional)
  - status (1: pending, 2: confirmed, 3: cancelled, 4: rejected)
  - created_time
  - update_time (optional)
  - cancel_time (optional)

- time_slots
  - slot_id
  - resv_id
  - username
  - start_time
  - end_time

Introducing `time_slots` table help make multiple reservations using only
one `resv_id`.

We already have the following data in the database:

- users:

  username   password    name     email
  ---------- ----------- -------- ------------------------------------------------------------------
  j_li       password1   李俊     [j_li@example.com](mailto:j_li@example.com)
  x_wang     password2   王小明   [x_wang@example.com](mailto:x_wang@example.com)
  y_zhang    password3   张燕     
  q_zhao     password4   赵琪     [q_zhao@example.com](mailto:q_zhao@example.com)
  f_chen     password5   陈峰     

rooms:

  room_id   room_name   capacity
  --------- ----------- ----------
        1   406               108
        2   519                40
        3   516                40
        4   408                32
        5   412                24
        6   419                 0
        7   523                 0
        8   522                 0

