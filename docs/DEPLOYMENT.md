# Deployment Guide

## Docker Compose
Build and run the entire ecosystem locally using Docker containers:
```bash
docker-compose up --build
```

## Kubernetes
Apply manifests to your cluster:
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```
