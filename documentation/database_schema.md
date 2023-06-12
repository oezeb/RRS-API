# Database Schema

## Entity Relationship Diagram

![Entity Relationship Diagram](schema.svg)

## Tables

- `users`

The `users` table stores user information in the system, including their username, name, password, role, and email.

- `rooms`

The `rooms` table contains information about the rooms in the system, such as their type, status, name, capacity, and image.

- `sessions`

The `sessions` table represents sessions in which users can make reservations, like school semesters. The `is_current` column indicates if the session is the current session.

- `reservations`

The `reservations` table stores information about room reservations. It includes the basic details of a reservation. Multiple time slots can be reserved at once, and the details of each time slot are stored in the `time_slots` table.

The `privacy` column controls the visibility of reservation details based on user privileges.

- `time_slots`

The `time_slots` table stores the time slots of reservations. Each time slot has a `status`, indicating whether it is pending, approved, rejected, etc. Storing the `status` in the `time_slots` table allows individual time slots to be managed separately from the entire reservation.

- `settings`

The `settings` table contains system configuration settings, such as the maximum reservation time and time window.

- `periods`

The `periods` table holds predefined time periods. Administrators define periods like 8:00-9:00, which users can select and combine to create reservation time slots.

- `notices`

The `notices` table stores the notices that are displayed to users.
