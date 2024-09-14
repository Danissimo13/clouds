#!/bin/bash

export SHELL=/bin/bash

eval $(minikube -p minikube docker-env --shell=bash)
eval $(SHELL=/bin/bash minikube -p minikube docker-env)

cd ../
docker build -t clouds:v2 -f ./Clouds/Dockerfile .

kubectl label nodes minikube nodeGroupPurpose=minikube

cd ./.helm-charts/clouds
helm dependency build
helm upgrade --install --set image=clouds:v2 \
             --set imagePullPolicy=Never \
             --set environment=Production \
             --set commit_hash=local \
             --set nodeGroupPurpose=minikube \
             --set reqCpuCores=0 \
             --set reqMemory=0 \
             --set limCpuCores=0 \
             --set limMemory=0 \
            clouds ./ --namespace durakru --create-namespace;
             
cd ../../.minikube