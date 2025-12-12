# Project P5

## Requirements
The following applications are required to run the application and all of it's dependencies
```
git
python 3
docker
docker-compose
react
```

## Copy project
```sh
git clone https://github.com/BTS-ESNA-2024-2026/P5-stock.git
cd P5-stock
```
The source code of the application is now downloaded and ready to be launched

## Initialize python and project
Create a venv and download required python libs
```sh
python -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
#check for any miss installs in the stack
```

## Generate application's private keys
/!\ DO NOT SHARE **__private.pem__** EVER ONCE CREATED /!\
```sh
openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048
openssl pkey -in private.pem -pubout -out public.pem
```

## Initialize database in docker
The docker-compose will create the docker image and run init.sql to create and expose the database on 3306
```sh
cd /database/mysql-docker
docker compose up -d
docker ps # confirm creation of docker
cd ../..
```

## Run the application
The application is now ready to be launched
```sh
flask --app src run
#or
flask --app src run --debug # includes hot reload, /!\ do not use in production
```