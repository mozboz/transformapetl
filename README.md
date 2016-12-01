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

## Misc

ETL business logic: places/management/commands
REST API configuration: places/api.py

## Deployment

For development, testing or demo purposes, use the Django development server:

python manage.py runserver 0.0.0.0:9000

Navigate to http://localhost:9000 ...

- /admin for the Admin area
- /places-api for the REST API interface
- /map-instance/MAP-INSTANCE-ID for the GEOJSON API

For production use, deploy Django using WSGI. See:
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/

## Usage

To run a job, create a YAML job file in /jobs, then:

    python manage.py transformap -i jobs/jobfile.yaml

This fetch and save the partner's data to the database.