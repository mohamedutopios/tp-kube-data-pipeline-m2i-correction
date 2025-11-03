# Définir le namespace
$NS = "bank-pipeline"

Write-Host "[+] Création du namespace et application des manifests de base..."

kubectl apply -f k8s/namespace.yaml
kubectl -n $NS apply -f k8s/secrets.yaml
kubectl -n $NS apply -f k8s/configmaps.yaml

Write-Host "[+] Déploiement de l'infrastructure (Kafka/ZK, Postgres, MySQL, MongoDB, MinIO)..."

kubectl -n $NS apply -f k8s/kafka-zk.yaml
kubectl -n $NS apply -f k8s/postgres.yaml
kubectl -n $NS apply -f k8s/mysql.yaml
kubectl -n $NS apply -f k8s/mongodb.yaml
kubectl -n $NS apply -f k8s/minio.yaml
kubectl -n $NS apply -f k8s/mongodb-init-job.yaml

Write-Host "[+] Attente de 20s pour que l'infrastructure se stabilise..."
Start-Sleep -Seconds 20

Write-Host "[+] Déploiement des applications (producer, spark, web)..."

kubectl -n $NS apply -f k8s/apps-producer.yaml
kubectl -n $NS apply -f k8s/apps-spark.yaml
kubectl -n $NS apply -f k8s/apps-web.yaml

Write-Host "[V] Terminé. Utilisez port-forward pour accéder aux services."
