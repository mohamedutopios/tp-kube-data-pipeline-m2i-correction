```markdown
# 📊 Monitoring avec Prometheus et Grafana

## Table of Contents

<details>

   <summary>Contents</summary>

1. [🌐 Accès aux interfaces](#-accs-aux-interfaces)
   1. [Prometheus (Collecte des métriques)](#prometheus-collecte-des-mtriques)
   1. [Grafana (Visualisation)](#grafana-visualisation)
1. [⚙️ Configuration Grafana](#-configuration-grafana)
   1. [1. Vérifier la datasource Prometheus](#1-vrifier-la-datasource-prometheus)
1. [📈 Import des Dashboards](#-import-des-dashboards)
   1. [Procédure d'import](#procdure-dimport)
1. [🎯 Dashboards recommandés](#-dashboards-recommands)
   1. [🏆 Dashboards essentiels pour le projet](#-dashboards-essentiels-pour-le-projet)
   1. [📦 Dashboards par composant](#-dashboards-par-composant)
      1. [Pods et Deployments](#pods-et-deployments)
      1. [Nœuds](#nuds)
      1. [Réseau](#rseau)
      1. [Vue globale](#vue-globale)
1. [🔍 Requêtes PromQL utiles](#-requtes-promql-utiles)
   1. [Dans Prometheus (http://localhost:9090/graph)](#dans-prometheus-httplocalhost9090graph)
      1. [CPU](#cpu)
      1. [Memory](#memory)
      1. [Network](#network)
      1. [Status des Pods](#status-des-pods)
      1. [Disk I/O](#disk-io)
1. [✅ Vérifications](#-vrifications)
   1. [1. Vérifier les Targets Prometheus](#1-vrifier-les-targets-prometheus)
   1. [2. Tester une requête simple](#2-tester-une-requte-simple)
   1. [3. Vérifier la connexion Grafana → Prometheus](#3-vrifier-la-connexion-grafana--prometheus)
1. [🚨 Troubleshooting](#-troubleshooting)
   1. [Problème : Targets DOWN dans Prometheus](#problme--targets-down-dans-prometheus)
   1. [Problème : Pas de données dans Grafana](#problme--pas-de-donnes-dans-grafana)
   1. [Problème : Dashboard vide (namespace filter)](#problme--dashboard-vide-namespace-filter)
   1. [Problème : Grafana ne se connecte pas à Prometheus](#problme--grafana-ne-se-connecte-pas--prometheus)
1. [📊 Métriques disponibles](#-mtriques-disponibles)
1. [🎯 Dashboards prioritaires pour ce projet](#-dashboards-prioritaires-pour-ce-projet)
1. [🔗 Commandes rapides](#-commandes-rapides)
1. [📝 Résumé](#-rsum)

</details>

## 📋 Prérequis

- Cluster Kubernetes (Kind) en cours d'exécution
- Namespace `bank-pipeline` déployé avec vos applications

---

## 🚀 Déploiement

### 1. Appliquer les manifests de monitoring

```bash
# Déployer Prometheus, Grafana, kube-state-metrics et node-exporter
kubectl apply -f monitoring/monitoring.yaml

# Vérifier que tous les pods sont Running
kubectl get pods -n monitoring

# Attendre que tout soit prêt (1-2 minutes)
kubectl wait --for=condition=ready pod --all -n monitoring --timeout=300s
```

**Pods attendus :**
```
NAME                                   READY   STATUS    RESTARTS   AGE
prometheus-xxxxx                       1/1     Running   0          1m
grafana-xxxxx                          1/1     Running   0          1m
kube-state-metrics-xxxxx               1/1     Running   0          1m
node-exporter-xxxxx                    1/1     Running   0          1m
```

---

## 🌐 Accès aux interfaces

### Prometheus (Collecte des métriques)

```bash
# Port-forward vers Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

**URL** : http://localhost:9090

**Points d'intérêt :**
- **Targets** : http://localhost:9090/targets → Vérifier que tous les endpoints sont **UP**
- **Graph** : http://localhost:9090/graph → Exécuter des requêtes PromQL

### Grafana (Visualisation)

```bash
# Port-forward vers Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

**URL** : http://localhost:3000

**Identifiants par défaut :**
- **Username** : `admin`
- **Password** : `admin`

> 💡 Grafana demandera de changer le mot de passe au premier login

---

## ⚙️ Configuration Grafana

### 1. Vérifier la datasource Prometheus

1. **Menu** (☰) → **Connections** → **Data sources**
2. Cliquer sur **Prometheus**
3. Vérifier l'URL : `http://prometheus.monitoring.svc.cluster.local:9090`
4. Cliquer sur **Save & Test**
5. Vous devez voir : ✅ **"Successfully queried the Prometheus API"**

---

## 📈 Import des Dashboards

### Procédure d'import

1. Dans Grafana : **Menu** (☰) → **Dashboards** → **New** → **Import**
2. Entrer l'**ID du dashboard**
3. Cliquer sur **Load**
4. Sélectionner **Prometheus** comme datasource
5. Cliquer sur **Import**
6. **Filtrer par namespace** : `bank-pipeline`

---

## 🎯 Dashboards recommandés

### 🏆 Dashboards essentiels pour le projet

| ID | Nom | Description | Utilité |
|----|-----|-------------|---------|
| **6417** | Kubernetes Cluster Monitoring | Vue complète du cluster | CPU, Memory, Network par pod ⭐ |
| **15760** | Kubernetes Views Pods | Détails avancés des pods | Monitoring détaillé par pod ⭐ |
| **15661** | Kubernetes Cluster Monitoring (Prometheus) | Monitoring complet | Vue d'ensemble du cluster |

### 📦 Dashboards par composant

#### Pods et Deployments
| ID | Nom | Description |
|----|-----|-------------|
| **6781** | Kubernetes Pods | Métriques par pod |
| **747** | Kubernetes Deployment/StatefulSet/DaemonSet | Métriques des déploiements |
| **8588** | Kubernetes Deployment Metrics | Monitoring des deployments |
| **737** | Kubernetes Pod Resources | Ressources des pods |

#### Nœuds
| ID | Nom | Description |
|----|-----|-------------|
| **1860** | Node Exporter Full | Métriques complètes des nœuds ⭐ |
| **13824** | Kubernetes Nodes | Monitoring des nœuds |

#### Réseau
| ID | Nom | Description |
|----|-----|-------------|
| **11074** | Kubernetes Network | Traffic réseau par pod |

#### Vue globale
| ID | Nom | Description |
|----|-----|-------------|
| **315** | Kubernetes Cluster Monitoring | Vue d'ensemble du cluster |
| **12740** | Kubernetes Monitoring | Monitoring général |

---

## 🔍 Requêtes PromQL utiles

### Dans Prometheus (http://localhost:9090/graph)

#### CPU
```promql
# CPU par pod dans bank-pipeline
sum(rate(container_cpu_usage_seconds_total{namespace="bank-pipeline", container!="", container!="POD"}[5m])) by (pod)

# CPU total du namespace
sum(rate(container_cpu_usage_seconds_total{namespace="bank-pipeline"}[5m]))
```

#### Memory
```promql
# Memory par pod
sum(container_memory_working_set_bytes{namespace="bank-pipeline", container!="", container!="POD"}) by (pod)

# Memory totale utilisée
sum(container_memory_working_set_bytes{namespace="bank-pipeline"})
```

#### Network
```promql
# Trafic réseau reçu par pod
sum(rate(container_network_receive_bytes_total{namespace="bank-pipeline"}[5m])) by (pod)

# Trafic réseau émis par pod
sum(rate(container_network_transmit_bytes_total{namespace="bank-pipeline"}[5m])) by (pod)
```

#### Status des Pods
```promql
# Nombre de pods Running
count(kube_pod_status_phase{namespace="bank-pipeline", phase="Running"})

# Nombre de restarts
sum(kube_pod_container_status_restarts_total{namespace="bank-pipeline"})

# Pods par phase
count(kube_pod_status_phase{namespace="bank-pipeline"}) by (phase)
```

#### Disk I/O
```promql
# Lectures disque par pod
sum(rate(container_fs_reads_bytes_total{namespace="bank-pipeline"}[5m])) by (pod)

# Écritures disque par pod
sum(rate(container_fs_writes_bytes_total{namespace="bank-pipeline"}[5m])) by (pod)
```

---

## ✅ Vérifications

### 1. Vérifier les Targets Prometheus

**URL** : http://localhost:9090/targets

**Targets attendus (tous doivent être UP) :**
- ✅ **prometheus** (1/1 up) : Prometheus lui-même
- ✅ **kube-state-metrics** (1/1 up) : Métriques des objets K8s
- ✅ **node-exporter** (1/1+ up) : Métriques des nœuds
- ✅ **cadvisor** (1/1+ up) : Métriques des containers

### 2. Tester une requête simple

Dans Prometheus : http://localhost:9090/graph

```promql
up
```

Doit retourner plusieurs résultats avec `value=1`

### 3. Vérifier la connexion Grafana → Prometheus

Dans Grafana :
1. **Menu** → **Connections** → **Data sources** → **Prometheus**
2. Cliquer sur **Save & Test**
3. ✅ Message de succès attendu

---

## 🚨 Troubleshooting

### Problème : Targets DOWN dans Prometheus

```bash
# Vérifier les logs de Prometheus
kubectl logs -n monitoring -l app=prometheus

# Vérifier les permissions RBAC
kubectl auth can-i get nodes/proxy --as=system:serviceaccount:monitoring:prometheus

# Redémarrer Prometheus
kubectl rollout restart deployment/prometheus -n monitoring
```

### Problème : Pas de données dans Grafana

```bash
# Vérifier que Prometheus scrape bien les métriques
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Ouvrir http://localhost:9090/targets

# Tester une requête dans Prometheus
# Aller sur http://localhost:9090/graph et exécuter : up

# Vérifier la datasource dans Grafana
# Menu → Connections → Data sources → Prometheus → Test
```

### Problème : Dashboard vide (namespace filter)

Dans Grafana, en haut du dashboard :
1. Cliquer sur le filtre **"namespace"**
2. Sélectionner **`bank-pipeline`**
3. Les données doivent apparaître

### Problème : Grafana ne se connecte pas à Prometheus

```bash
# Depuis le pod Grafana, tester la connexion
kubectl exec -it -n monitoring deployment/grafana -- sh
wget -qO- http://prometheus.monitoring.svc.cluster.local:9090/api/v1/query?query=up
# Doit retourner du JSON

# Si erreur, vérifier le service Prometheus
kubectl get svc -n monitoring prometheus
```

---

## 📊 Métriques disponibles

Le monitoring expose automatiquement :

| Type | Métriques | Source |
|------|-----------|--------|
| **CPU** | `container_cpu_usage_seconds_total` | cAdvisor |
| **Memory** | `container_memory_working_set_bytes` | cAdvisor |
| **Network** | `container_network_*` | cAdvisor |
| **Disk I/O** | `container_fs_*` | cAdvisor |
| **Pods** | `kube_pod_*` | kube-state-metrics |
| **Deployments** | `kube_deployment_*` | kube-state-metrics |
| **Nodes** | `node_*` | node-exporter |

---

## 🎯 Dashboards prioritaires pour ce projet

Pour monitorer efficacement le pipeline bank-pipeline, importer dans cet ordre :

1. **Dashboard 6417** : Vue d'ensemble (CPU, Memory, Network)
2. **Dashboard 15760** : Détails par pod (Spark, Producer, Web)
3. **Dashboard 1860** : Surveillance des nœuds
4. **Dashboard 11074** : Analyse du trafic réseau (Kafka, MinIO)

---

## 🔗 Commandes rapides

```bash
# Accéder à Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Accéder à Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Vérifier les pods
kubectl get pods -n monitoring

# Logs Prometheus
kubectl logs -n monitoring -l app=prometheus

# Logs Grafana
kubectl logs -n monitoring -l app=grafana

# Redémarrer la stack
kubectl rollout restart deployment/prometheus deployment/grafana -n monitoring
```

---

## 📝 Résumé

✅ **Prometheus** collecte les métriques de tous les pods K8s
✅ **Grafana** visualise ces métriques via des dashboards
✅ **kube-state-metrics** expose les métriques des objets K8s
✅ **node-exporter** expose les métriques des nœuds
✅ **Aucune modification du code applicatif** n'est nécessaire
✅ **Dashboards prêts à l'emploi** disponibles sur grafana.com

---

💡 **Note importante** : Les métriques sont collectées automatiquement par Kubernetes (cAdvisor). Vous n'avez pas besoin de modifier vos applications (Spark, Producer, Web) pour avoir des métriques de base (CPU, Memory, Network).
```