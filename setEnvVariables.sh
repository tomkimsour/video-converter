export PROJECT_ID=august-tesla-333012
export CLUSTER_NAME=video-converter-cluster-1
export REGION=europe-north1

//create cluster
gcloud container clusters create $CLUSTER_NAME --image-type cos

// change kubectl config
gcloud container clusters get-credentials $CLUSTER_NAME

// build a container
docker build --platform linux/amd64 --tag europe-north1-docker.pkg.dev/video-converter-umea/video-api/flask-api:v1 .
