# starts cluster
minikube start

# setup environment variables docker
eval $(minikube docker-env)

# set up rabbitMQ operator
kubectl apply -f kubernetes/cluster-operator.yml
kubectl apply -f kubernetes/rabbitmqcluster.yaml

# enable ingress
minikube addons enable ingress

# create docker file  
docker build --tag flask-api ./api
docker build --tag converter ./encoder

# push the container in the cluster
kubectl create -f kubernetes/api-deployment.yaml
kubectl create -f kubernetes/converter-deployment.yaml

# setup rabbitMQ service monitor
kubectl apply -f kubernetes/rabbitmq-servicemonitor.yaml
kubectl apply -f kubernetes/rabbitmq-cluster-operator-podmonitor.yaml

# setup HPA
kubectl apply -f kubernetes/hpa.yaml
