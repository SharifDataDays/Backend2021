# How to use
Just follow these steps.

## Env vars
First of all, set env files, one in deploy directory and another one in thebackend/settings.  
Copy the .env.examples to .env and set variables.

```bash
cp thebackend/settings/.env.example thebackend/settings/.env
cp deploy/.env.example deploy/.env

```

## ConfigMap
Set setting file in deploy/kubernetes/backend-configmap.yml. Default is production.

## Minikube setup
If you're using minikube which is not good, you have to set minikube docker vars.
`eval $(minikube docker-env)`

## Build Dockerfile
`docker -t datadays21-backend:v1 . -f deploy/Dockerfile`

## Fire up
Apply configmap, service and deployment.  
TODO: add a makefile for the Sake of laziness.
  
easy-peasy ...
