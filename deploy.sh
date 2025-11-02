#!/usr/bin/env bash
set -euo pipefail

NS=bank-pipeline
echo "[+] Creating namespace and applying base manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl -n $NS apply -f k8s/secrets.yaml
kubectl -n $NS apply -f k8s/configmaps.yaml

echo "[+] Deploying infra (Kafka/ZK, Postgres, MySQL, MongoDB, MinIO)..."
kubectl -n $NS apply -f k8s/kafka-zk.yaml
kubectl -n $NS apply -f k8s/postgres.yaml
kubectl -n $NS apply -f k8s/mysql.yaml
kubectl -n $NS apply -f k8s/mongodb.yaml
kubectl -n $NS apply -f k8s/minio.yaml
kubectl -n $NS apply -f k8s/mongodb-init-job.yaml

echo "[+] Waiting 20s for infra to settle..."
sleep 20

echo "[+] Deploying apps (producer, spark, web)..."
kubectl -n $NS apply -f k8s/apps-producer.yaml
kubectl -n $NS apply -f k8s/apps-spark.yaml
kubectl -n $NS apply -f k8s/apps-web.yaml

echo "[✓] Done. Use port-forward to access services."
