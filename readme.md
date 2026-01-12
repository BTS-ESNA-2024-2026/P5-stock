# Project P5

## Requirements
The following applications are required to run the application and all of it's dependencies
```
git
python 3
docker
docker-compose
pnpm (for frontend)
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

## Initialize frontend with Vite + React
Navigate to the frontend directory and install dependencies
```sh
cd frontend
pnpm install
cd ..
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

### Development Mode (with Vite hot reload)
Terminal 1 - Start the frontend dev server:
```sh
cd frontend
pnpm dev
```
This runs on http://localhost:5173/

Terminal 2 - Start Flask backend:
```sh
flask --app src run --debug # includes hot reload
```
This runs on http://localhost:5000/

The frontend will proxy API requests to the Flask backend. To make API calls in React components, use:
```javascript
fetch('/api/endpoint')
```

### Production Mode
Build the frontend first, then run Flask:
```sh
cd frontend
pnpm build
cd ..
flask --app src run
```

This builds the React app to `src/frontend/dist/` and Flask serves it at the root URL.