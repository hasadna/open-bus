# Getting Started with PostGRES 

In this tutorial you will set up your postgres server with a dump of open bus db.

There are two ways to set up a postgres server:
1) Installing PostGRES & pgadmin
2) Running Docker Image

## Installing PostGRES & pgadmin

### Windows:
1. Install postgreSQL using this [tutorial](http://www.postgresqltutorial.com/install-postgresql/).
2. Install pgadmin from [here](https://www.postgresql.org/ftp/pgadmin/pgadmin4/v1.5/windows/).
   Tutorial can be found here[tutorial](http://www.postgresqltutorial.com/connect-to-postgresql-database/).
3. Download DB dump from [here](https://drive.google.com/open?id=0B9FEqRIWfmxLdUI1Zk5SZFB0bzg).
4. Uploading the Dump using pgadmin:
5. Create a new database using `CREATE DATABASE obus;` in command line or via pgadmin gui.
6. Right click on database name in pgadmin and press Restore.
7. Select dump file and in format choose `Costum or tar`.

## Running Docker Image
based on this [tutorial](https://github.com/hasadna/open-bus/blob/dfeaea67d8c4ed51bd0a4b0c30cffbac095ff81b/gtfs/local_db/README.md)
### Linux:
1. Install Docker. Preferably follow this [tutorial](https://docs.docker.com/engine/installation/linux/ubuntu/)
2. Create a new folder with the files: [`init_dump_load.sh`](https://github.com/hasadna/open-bus/blob/master/gtfs/local_db/init_dump_load.sh) and download latest db dump found [here](https://drive.google.com/open?id=0B9FEqRIWfmxLdUI1Zk5SZFB0bzg) as `dump.dmp`
3. Run in the folder the follwing command: `docker run -d --name db -v $(pwd):/docker-entrypoint-initdb.d -p 5432:5432 postgres`
4. Now you have a docker container which runs a postgreSQL db with open bus data! confirm the container is actually running with command `docker ps`
5. Connect to db using: `psql -h localhost -p 5432 -U obus obus`

### Windows:
1. Install Docker for windows using this [tutorial](https://docs.docker.com/docker-for-windows/install/#download-docker-for-windows)
* Note: you may need to install Docker Toolbox
2. Create a new folder with these files: [`init_dump_load.sh`](https://github.com/hasadna/open-bus/blob/master/gtfs/local_db/init_dump_load.sh) and download latest db dump found [here](https://drive.google.com/open?id=0B9FEqRIWfmxLdUI1Zk5SZFB0bzg) as `dump.dmp`
3. Run Docker Quickstart Terminal
4. In the terminal change to the directory you created and run the follwing command: `docker run -d --name db -v $(pwd):/docker-entrypoint-initdb.d -p 5432:5432 postgres`
5. Now you have a docker container which runs a postgreSQL db with open bus data! confirm the container is actually running with command `docker ps`
6. Connect in the terminal to the db using: `psql -h $(docker-machine ip) -p 5432 -U obus obus` 
