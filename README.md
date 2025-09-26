# 🏦 Système de Gestion Coopérative

Un système complet de gestion pour coopératives agricoles développé avec Django REST Framework et React + TypeScript.

## ✨ Fonctionnalités Implémentées

### 🔧 API Backend Django REST Framework
- **🔐 Authentification et Autorisation** : Système complet avec tokens, rôles et permissions granulaires
- **👥 Gestion des Membres** : CRUD complet, profils utilisateurs, historique d'adhésion, rôles
- **📦 Inventaire** : Gestion des produits, catégories, stock en temps réel, alertes de stock bas
- **🛒 Ventes** : Commandes, factures, gestion des clients, suivi des livraisons
- **💰 Finance** : Transactions, comptes bancaires, prêts, épargne, calculs automatiques
- **📊 Rapports** : Système avancé de génération de rapports personnalisables
- **📚 Documentation API** : Swagger/OpenAPI intégré avec exemples et schémas

### 🌐 Interface Web React + TypeScript
- **⚡ Architecture moderne** : Vite, Material-UI, React Router, Tanstack Query
- **🔒 Authentification sécurisée** : Gestion des sessions, routes protégées, tokens persistants
- **📱 Interface responsive** : Design adaptatif mobile/desktop avec thème coopératif
- **📈 Tableaux de bord** : Statistiques en temps réel, métriques financières, alertes
- **🧩 Navigation modulaire** : Accès à tous les modules depuis une interface unifiée

### 🔧 Infrastructure et Outils
- **🌍 API REST complète** : Plus de 50 endpoints documentés
- **🔄 CORS configuré** : Communication frontend-backend sécurisée
- **🧪 Comptes de test** : `admin/admin` et `demo/demo123` pour démonstration
- **📖 Documentation interactive** : Interface Swagger accessible

## 🚀 URLs d'accès

- **Frontend React** : http://localhost:5173/
- **Backend Django** : http://127.0.0.1:8000/
- **Documentation API** : http://127.0.0.1:8000/swagger/
- **Admin Django** : http://127.0.0.1:8000/admin/

## 📋 Prérequis

- Python 3.8+
- Node.js 16+
- SQLite (par défaut) ou PostgreSQL

## ⚡ Installation Rapide

### 1. Clone du repository
```bash
git clone https://github.com/GOLITI/cooperative.git
cd cooperative
```

### 2. Configuration Backend Django
```bash
# Création de l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installation des dépendances
pip install -r requirements.txt

# Configuration de la base de données
cd backend
python manage.py migrate
python manage.py loaddata fixtures/*.json

# Création des utilisateurs de test
cd ..
python create_test_users.py

# Démarrage du serveur Django
cd backend
python manage.py runserver
```

### 3. Configuration Frontend React
```bash
# Dans un nouveau terminal
cd frontend-react

# Installation des dépendances Node.js
npm install

# Démarrage du serveur de développement
npm run dev
```

## 👤 Comptes de Test

| Utilisateur | Mot de passe | Rôle | Permissions |
|-------------|--------------|------|-------------|
| `admin` | `admin` | Administrateur | Accès complet à tous les modules |
| `demo` | `demo123` | Utilisateur | Accès limité pour démonstration |

## 🏗️ Architecture

```
cooperative/
├── backend/                 # API Django REST Framework
│   ├── cooperative/         # Configuration principale
│   ├── accounts/            # Authentification et utilisateurs
│   ├── members/             # Gestion des membres
│   ├── inventory/           # Gestion de l'inventaire
│   ├── sales/               # Gestion des ventes
│   ├── finance/             # Gestion financière
│   └── reporting/           # Système de rapports
├── frontend-react/          # Application React + TypeScript
│   ├── src/
│   │   ├── components/      # Composants réutilisables
│   │   ├── pages/           # Pages de l'application
│   │   ├── contexts/        # Contextes React (Auth, etc.)
│   │   └── services/        # Services API
└── docs/                    # Documentation
```

## 📊 Modules Disponibles

### 1. 👥 Gestion des Membres
- Inscription et profils des membres
- Gestion des adhésions et cotisations
- Historique des activités
- Rôles et permissions personnalisés

### 2. 📦 Inventaire
- Catalogue de produits agricoles
- Gestion des catégories et unités
- Suivi des stocks en temps réel
- Alertes de réapprovisionnement

### 3. 🛒 Ventes
- Création de commandes
- Gestion des clients
- Facturation automatique
- Suivi des livraisons

### 4. 💰 Finance
- Comptes bancaires multiples
- Transactions automatisées
- Système de prêts aux membres
- Comptes d'épargne collectifs

### 5. 📊 Rapports
- Rapports financiers personnalisables
- Statistiques des ventes
- Analyses des membres
- Exportation en PDF/Excel

## 🔧 API Endpoints Principaux

| Module | Endpoints | Description |
|--------|-----------|-------------|
| Auth | `/api/auth/login/`, `/api/auth/me/` | Authentification |
| Members | `/api/members/` | CRUD des membres |
| Inventory | `/api/inventory/products/` | Gestion produits |
| Sales | `/api/sales/orders/` | Commandes |
| Finance | `/api/finance/accounts/` | Comptes financiers |
| Reports | `/api/reports/templates/` | Rapports |

## 🧪 Tests et Développement

```bash
# Tests backend
cd backend
python manage.py test

# Linting frontend
cd frontend-react
npm run lint

# Build de production
npm run build
```

## 📈 Prochaines Fonctionnalités

- [ ] **API des Notifications** : Système d'alertes en temps réel
- [ ] **Tests Automatisés** : Suite complète de tests unitaires et d'intégration
- [ ] **Déploiement Docker** : Containerisation pour production
- [ ] **Progressive Web App** : Application mobile native
- [ ] **Intégrations** : APIs externes (banques, comptabilité)

## 🤝 Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Pushez vers la branche
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👨‍💻 Auteur

**GOLITI** - [GitHub](https://github.com/GOLITI)

---

**🚀 Système opérationnel et prêt à l'utilisation !**