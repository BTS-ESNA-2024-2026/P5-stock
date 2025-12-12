## Create and host docker for database

the docker-compose will create the docker image and run init.sql to create and expose the database on 3306
```bash
cd /database/mysql-docker
docker compose up -d
docker ps # confirm creation of docker
```