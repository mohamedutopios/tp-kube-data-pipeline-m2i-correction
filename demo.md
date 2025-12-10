Voici **les 3 commandes exactes** (🔹Resource Group → 🔹ACR → 🔹AKS avec ACR attaché), prêtes à copier-coller.

---

# ✅ 1️⃣ Créer un Resource Group

```bash
az group create \
  --name myRG \
  --location francecentral
```

---

# ✅ 2️⃣ Créer un registre ACR

👉 Nom **unique globalement**, uniquement lettres/nombres.

```bash
az acr create \
  --resource-group myRG \
  --name myacr12345 \
  --sku Standard \
  --location francecentral
```

> `--sku Basic | Standard | Premium`
> `Standard` = bon compromis pour CI/CD + AKS.

---

# ✅ 3️⃣ Créer AKS et l’attacher automatiquement à l’ACR

> ⚠ IMPORTANT : lorsque tu attaches l’ACR, tu dois passer **le nom du registre sans `.azurecr.io`**.

```bash
az aks create \
  --resource-group myRG \
  --name myAKS \
  --node-count 2 \
  --node-vm-size Standard_B4ms \
  --generate-ssh-keys \
  --attach-acr myacr12345mohamed
```

💡 Cette commande :

* crée un cluster AKS
* crée le nodepool par défaut
* ajoute l’ACR RBAC Pull (AcrPull)
* autorise AKS à tirer tes images Docker depuis ton ACR

---

# 🔄 4️⃣ (Optionnel) Récupérer les credentials kubectl

```bash
az aks get-credentials \
  --resource-group myRG \
  --name myAKS \
  --overwrite-existing
```

---

# ⭐ Résumé clair

| Élément             | Commande                     |
| ------------------- | ---------------------------- |
| Resource Group      | `az group create`            |
| ACR                 | `az acr create`              |
| AKS attaché à ACR   | `az aks create --attach-acr` |
| Kubectl credentials | `az aks get-credentials`     |

---

# 🔥 Tu veux que je t’écrive un script Bash complet ?

💬 **Par exemple : `create_infra.sh` qui crée tout, vérifie, et affiche les infos utiles ?**
