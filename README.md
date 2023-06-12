# Room Reservation System API

## Description

This is a REST API for a room reservation system. It is built using the Flask framework and uses a MySQL database. For more information on the database schema, see the [database schema](./documentation/database_schema.md) documentation.

## Installation

### Prerequisites

- MySQL Server

The project uses a MySQL database. You can install MySQL server on your machine by following the instructions [here](https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/).

- Environment Variables

In order to connect to the database, the project requires the following environment variables to be set:

variable      | optional | description
------------- | -------- | -------------------------------------------------
`DB_HOST`     | yes      | The host of the database. Defaults to `localhost`
`DB_PORT`     | yes      | The port of the database. Defaults to `3306`
`DATABASE`    | no       | The name of the database
`DB_USER`     | no       | The user used to connect to the database
`DB_PASSWORD` | no       | The password used to connect to the database

- python
- docker (optional)

### Setup

The project is built as a python package which makes its installation easy. 

```bash
$ pipenv install . # install the project
$ pipenv install waitress
$ pipenv shell # activate the virtual environment
$ waitress-serve --port=5000 --call 'app:create_app' 
```

- Using Docker

Alternatively, you can build and run the project using docker.

```bash
$ docker build -t rrs-api . # build the docker image
$ docker run -p 5000:5000 rrs-api # run the docker image
```

### Database Initialization

The project implement a command line interface (CLI) that can be used to initialize the database. The CLI can be accessed by running the following command:

```bash
$ flask init-db --help
Usage: flask init-db [OPTIONS]

Options:
  --user TEXT      user used to init the database. Defaults to the value of
                   $DB_USER environment variable
  --password TEXT  user's password. Defaults to the value of $DB_PASSWORD
                   environment variable
```

The CLI will create the database and populate it with the required tables and required initial data.

## Usage

The API is documented using Open API specification. You can access the documentation by running the project and navigating to `http://localhost:5000/api/docs.json`. 

## Documentation

Additional documentation can be found in the [documentation](./documentation) directory.