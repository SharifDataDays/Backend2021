# Deploy, using docker

## Clone the repository
`git clone https://github.com/SharifDataDays/Backend2021.git`

## Step into project dir
`cd Backend2021`

## Env vars
First of all, set env files, one in deploy directory and another one in thebackend/settings.  
Copy the .env.examples to .env and set variables.

```bash
cp thebackend/settings/.env.example thebackend/settings/.env
cp deploy/.env.example deploy/.env

```

## Build and Deploy
Run this command to build and up services.
```bash
docker-compose -f deploy/docker-compose.yml up -d --build
# check everything is fine
docker-compose -f deploy/docker-compose.yml ps
```

+ if you already build images, remove --build option
+ run these command from project root directory
