# starts cluster
minikube start

# setup environment variables docker
eval $(minikube docker-env)

# set up rabbitMQ operator
kubectl apply -f kubernetes/cluster-operator.yml
kubectl apply -f kubernetes/rabbitmqcluster.yaml

export PROJECT_ID=august-tesla-333012
export CLUSTER_NAME=video-converter-cluster-1
export REGION=europe-north1

# create docker file  
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/video-api/flask-api:v25 ./api
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/video-api/converter:v25 ./encoder

# push the container in the cluster
kubectl create -f kubernetes/api-deployment.yaml
kubectl create -f kubernetes/converter-deployment.yaml

# setup rabbitMQ service monitor
kubectl apply -f kubernetes/rabbitmq-servicemonitor.yaml
kubectl apply -f kubernetes/rabbitmq-cluster-operator-podmonitor.yaml

# setup HPA
kubectl apply -f kubernetes/hpa.yaml
