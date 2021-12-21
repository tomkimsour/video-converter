# Description
Implementation of the different component of a kubernetes cluster making video conversion

# API
This api allows to upload one video and tell which format you want to send back.
Then provides a link to download the converted file.

# Encoder
Video encoder worker. It receives a message from a pod, fetches the video file in a local storage change format and write it in another local storage.

# Before running setup script
- Install Helm (https://helm.sh/docs/intro/install/)
- Install Prometheus with helm:
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack --create-namespace -n monitoring
```
- Install Prometheus adapter (needs to be redone if custom-metrics-config-map.yaml is changed)
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install -f kubernetes/custom-metrics-config-map.yaml prometheus-adapter prometheus-community/prometheus-adapter -n monitoring
```
