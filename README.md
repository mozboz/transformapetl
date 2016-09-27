# Transformap ETL

## Setup dev:

    make installpostgres
    make virtualenv
    make setupdb
    source .env/bin/activate
    make runserver

Refer to Makefile for further details; it should serve as a guide to how to
manage the local Python development environment.

## Postgresql JSONB field support in Django

The JSON field support appears to be quite good, django's queryset API supports
several operations for querying data inside JSONB fields.

See: https://docs.djangoproject.com/en/1.10/ref/contrib/postgres/fields/#containment-and-key-operations

## Usage

python manage.py transformap -i jobs/jobfile.json

Admin interface: /admin
API URL: /places-api/

New jobs should be created as .YAML files in jobs/

## Misc

ETL business logic: places/management/commands
REST API configuration: places/api.py



