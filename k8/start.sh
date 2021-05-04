#!/bin/bash

# Start minikube
# minikube start --driver=virtualbox

# Enable ingress controller
minikube addons enable ingress
kubectl get pods -n kube-system

# Create namespace
kubectl apply -f app-ns.yaml 

# Start web services
kubectl apply -f web-deployment.yaml
kubectl apply -f risk-deployment.yaml

# Start ingress resource 
kubectl apply -f app-ingress.yaml

# Add ingress IP to /etc/hosts
blocks=$( echo $(kubectl get ingress -A | grep app-ingress | grep -o -E '[0-9]+') )
IFS=' ' read -r -a array <<< "$blocks"
for i in {0..3}
do
	if [[ $i -eq 0 ]]
 	then
 		ip="${array[i]}"
 	else
 		ip="$ip.${array[i]}"
 	fi
done

echo "$ip charts.xyz" | sudo tee -a /etc/hosts > /dev/null
