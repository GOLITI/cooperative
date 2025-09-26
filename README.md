# Coopérative - Système de Gestion Coopérative

## 🎯 Description

Système de gestion complet pour une coopérative, développé avec Django REST Framework et React. Cette application permet la gestion des membres, de l'inventaire, des ventes et des finances d'une coopérative.

## 🚀 Fonctionnalités Implémentées

### ✅ Authentification et Sécurité
- 🔐 Système d'authentification JWT complet
- 👥 Gestion des rôles et permissions granulaires
- 🔑 Endpoints : login, logout, registration, refresh tokens
- 🛡️ Permissions basées sur les rôles (Admin, Manager, Member, Viewer)

### ✅ Gestion des Membres
- 👤 CRUD complet des membres
- 📋 Types d'adhésion configurables
- 💳 Gestion des cotisations et paiements
- 📊 Statistiques et rapports des membres
- 🔍 Recherche et filtrage avancés

### ✅ Gestion de l'Inventaire
- 📦 Gestion des produits et catégories
- 📏 Unités de mesure configurables
- 📊 Suivi des mouvements de stock
- 💹 Calculs automatiques des quantités
- ⚠️ Système d'alertes de stock
- 📈 Statistiques temps réel

## 🛠️ Technologies Utilisées

### Backend
- **Django 5.2.6** - Framework web principal
- **Django REST Framework** - API REST
- **JWT Authentication** - Authentification sécurisée
- **PostgreSQL** - Base de données (compatible SQLite pour dev)
- **Python 3.11+** - Langage de programmation

### Frontend (À venir)
- **React 18** - Interface utilisateur
- **TypeScript** - Typage statique
- **Tailwind CSS** - Framework CSS
- **React Query** - Gestion d'état serveur

## 📁 Structure du Projet

```
cooperative/
├── backend/                 # Application Django
│   ├── accounts/           # Authentification et utilisateurs
│   ├── members/            # Gestion des membres
│   ├── inventory/          # Gestion de l'inventaire
│   ├── cooperative_management/ # Configuration principale
│   └── manage.py
├── frontend/               # Application React (à venir)
└── docs/                   # Documentation
```

## 🔧 Installation et Configuration

### Prérequis
- Python 3.11+
- PostgreSQL (optionnel, SQLite par défaut)
- Git

### Installation

1. **Cloner le repository**
```bash
git clone https://github.com/GOLITI/cooperative.git
cd cooperative
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configuration de la base de données**
```bash
python manage.py migrate
python manage.py collectstatic
```

5. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

6. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

## 📚 API Endpoints

### 🔐 Authentification
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/logout/` - Déconnexion
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/token/refresh/` - Actualiser le token

### 👥 Membres
- `GET/POST /api/members/members/` - Liste/Création des membres
- `GET/PUT/DELETE /api/members/members/{id}/` - Détail/Modification/Suppression
- `GET /api/members/membership-types/` - Types d'adhésion
- `GET /api/members/payments/` - Paiements des membres

### 📦 Inventaire
- `GET/POST /api/inventory/products/` - Produits
- `GET/POST /api/inventory/categories/` - Catégories
- `GET/POST /api/inventory/units/` - Unités de mesure
- `GET/POST /api/inventory/stock-movements/` - Mouvements de stock
- `GET /api/inventory/products/stats/` - Statistiques
- `GET /api/inventory/products/alerts/` - Alertes de stock

## 🧪 Tests

### Exécuter les tests
```bash
# Tests unitaires Django
python manage.py test

# Tests des endpoints API
python test_final.py
```

## 📋 Roadmap

### 🔄 En cours de développement
- [ ] API des ventes et clients
- [ ] API financière (comptabilité)
- [ ] Interface React frontend
- [ ] Tableau de bord analytics

### 🎯 Fonctionnalités futures
- [ ] Rapports PDF automatisés
- [ ] Notifications en temps réel
- [ ] Module de communication interne
- [ ] Application mobile

## 🤝 Contribution

Les contributions sont les bienvenues ! Merci de :

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Contact

- **Développeur** : Marc GOLITI
- **Email** : [votre-email@exemple.com]
- **Projet** : [https://github.com/GOLITI/cooperative](https://github.com/GOLITI/cooperative)

---

⭐ Si ce projet vous plaît, n'hésitez pas à lui donner une étoile !