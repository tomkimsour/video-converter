# setup environment viriables docker
eval $(minikube docker-env)

# starts cluster
minikube start

# create docker file  
docker build --tag flask-api ./api

# push the container in the cluster
kubectl create -f api/api-deployment.yaml