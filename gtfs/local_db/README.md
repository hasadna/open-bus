# Local GTFS DB

## General

This directory allows you to create a local GTFS DB for development
and testing using Postgres in a Docker container.

## Requirements

Docker. Install using `yum install docker` or any equivalent. There
are also Docker versions for Mac and Windows.

## Usage

### Running the DB

With the Docker service started, run the following:

    docker run -d --name db -v $(pwd):/docker-entrypoint-initdb.d -p 5432:5432 postgres

Verify the DB is running using `docker ps`. You should get something
like the following:

    $ docker ps
    CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
    fbc6eb5e8e94        postgres            "/docker-entrypoint.s"   4 seconds ago       Up 3 seconds        0.0.0.0:5432->5432/tcp   db

Now you can connect to the DB at `localhost:5432` using `psql` or any
library.

### Stopping the DB

Run `docker stop db` to stop the container, then `docker rm db` to
delete it.

## Updating the schema

To update the schema, simply edit `schema.txt` and re-run the DB. Do
**not** change the file extension to `.sql` as it will make it run
before the init script, which will fail.
