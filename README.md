# Système de Gestion des Coopératives

Un système complet de gestion pour les coopératives agricoles et artisanales en Afrique, développé avec Django (backend) et React (frontend).

## 🎯 Objectifs du Projet

- **Digitaliser** la gestion des membres et des adhésions
- **Automatiser** le suivi des stocks et inventaires  
- **Rationaliser** la gestion financière et comptable
- **Fournir** des outils d'analyse pour la prise de décision
- **Faciliter** la communication entre membres et gestionnaires

## 🏗️ Architecture Technique

### Backend - Django
- **Framework**: Django 5.2.6
- **API REST**: Django REST Framework
- **Base de données**: PostgreSQL
- **Cache**: Redis
- **Tâches asynchrones**: Celery
- **Authentification**: Django Allauth

### Frontend - React (À venir)
- **Framework**: React avec Vite
- **Styling**: Tailwind CSS + daisyUI
- **State Management**: Context API / Zustand
- **HTTP Client**: Axios

## 📋 Fonctionnalités Implémentées

### ✅ Phase 1 - Core System (Terminé)

#### 🔧 Infrastructure de Base
- [x] Configuration projet Django avec structure modulaire
- [x] Configuration PostgreSQL avec variables d'environnement
- [x] Configuration Redis et Celery pour tâches asynchrones
- [x] Système d'authentification avec Django Allauth
- [x] Configuration CORS pour intégration frontend
- [x] Logging et monitoring des erreurs

#### 👥 Gestion des Membres
- [x] **Types d'adhésion** : Différents niveaux avec cotisations personnalisées
- [x] **Profils complets** : Informations personnelles, contact, documents
- [x] **Système de cotisations** : Suivi automatique des paiements mensuels
- [x] **Contacts d'urgence** : Gestion des personnes à contacter
- [x] **Membres de famille** : Liens familiaux et dépendants
- [x] **Compétences et spécialités** : Classification des expertises

#### 📦 Gestion des Stocks
- [x] **Catalogue produits** : Classification hiérarchique par catégories
- [x] **Unités de mesure** : Support des différentes unités (kg, litre, unité, etc.)
- [x] **Codes produits** : SKU et codes-barres pour identification
- [x] **Mouvements de stock** : Entrées, sorties, ajustements, transferts
- [x] **Inventaires physiques** : Système de comptage et ajustement
- [x] **Valorisation FIFO** : Calcul automatique de la valeur du stock
- [x] **Alertes de stock** : Notifications pour stock faible ou périmé

#### 💰 Gestion des Ventes
- [x] **Clients membres/non-membres** : Différenciation des prix
- [x] **Système de vente** : Factures, paiements, remises
- [x] **Modes de paiement** : Espèces, Mobile Money, virements, crédit
- [x] **Promotions** : Système de remises et offres spéciales
- [x] **Commandes** : Gestion des livraisons différées
- [x] **Points de fidélité** : Programme de récompenses clients

#### 🏦 Gestion Financière
- [x] **Plan comptable** : Comptes adaptés aux coopératives
- [x] **Transactions** : Journal des recettes et dépenses
- [x] **Épargne membres** : Comptes d'épargne avec intérêts
- [x] **Microcrédit** : Système de prêts aux membres avec garanties
- [x] **Budgets** : Planification et suivi budgétaire
- [x] **Rapprochement bancaire** : Gestion des relevés

#### 📊 Système de Rapports
- [x] **Modèles de rapports** : Templates personnalisables
- [x] **Génération PDF/Excel** : Export dans différents formats
- [x] **Tableaux de bord** : Dashboards personnalisés
- [x] **Paramètres flexibles** : Filtres par période, membre, produit

#### 🔒 Sécurité et Audit
- [x] **Authentification** : Système robuste avec allauth
- [x] **Journal d'activité** : Traçabilité complète des actions
- [x] **Soft delete** : Suppression logique des données importantes
- [x] **Contrôle d'accès** : Permissions granulaires par module

## 📁 Structure du Projet

```
cooperative/
├── backend/                    # Application Django
│   ├── cooperative/           # Configuration principale
│   ├── accounts/             # Authentification utilisateurs
│   ├── core/                 # Modèles et utilitaires de base
│   ├── members/              # Gestion des membres
│   ├── inventory/            # Gestion des stocks
│   ├── sales/               # Gestion des ventes
│   ├── finance/             # Gestion financière
│   ├── reports/             # Rapports et statistiques
│   ├── api/                 # API REST endpoints
│   ├── static/              # Fichiers statiques
│   ├── media/               # Fichiers uploadés
│   └── templates/           # Templates HTML
└── frontend/                # Application React (À venir)
```

## 🔧 Installation et Configuration

### Prérequis
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Node.js 18+ (pour le frontend)

### Backend Setup

```bash
# Cloner le projet
git clone https://github.com/GOLITI/cooperative.git
cd cooperative/backend

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configuration de la base de données
cp .env.example .env
# Éditer .env avec vos paramètres PostgreSQL

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

### Variables d'Environnement

```env
# Base de données
DB_NAME=cooperative
DB_USER=postgres  
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your_secret_key
DEBUG=True
```

## 🚀 Roadmap

### ⏳ Phase 2 - API et Frontend (En cours)
- [ ] API REST complète avec Django REST Framework
- [ ] Interface React avec Tailwind CSS + daisyUI
- [ ] Authentification JWT côté frontend
- [ ] Tableaux de bord interactifs

### ⏳ Phase 3 - Fonctionnalités Avancées
- [ ] Application mobile React Native
- [ ] Intégrations Mobile Money (Orange, MTN)
- [ ] Notifications SMS et email
- [ ] Système de QR codes pour produits
- [ ] Mode hors-ligne avec synchronisation

### ⏳ Phase 4 - Optimisation et Déploiement
- [ ] Optimisation performances
- [ ] Tests automatisés complets  
- [ ] Documentation API complète
- [ ] Scripts de déploiement Docker
- [ ] Formation utilisateurs

## 🏆 Public Cible

- **Coopératives agricoles** : Gestion des récoltes et ventes groupées
- **Coopératives artisanales** : Suivi production et commercialisation
- **Associations de producteurs** : Mutualisation des ressources
- **GIE** : Gestion collective et transparente

## 💡 Valeur Ajoutée

- ✅ **Simplicité d'usage** : Interface intuitive adaptée au contexte africain
- ✅ **Fonctionnalités métier** : Conçu spécifiquement pour les coopératives
- ✅ **Mode hors-ligne** : Fonctionne même sans connexion internet
- ✅ **Multi-langues** : Support français et langues locales  
- ✅ **Coût abordable** : Solution accessible aux petites structures
- ✅ **Support local** : Assistance et formation dans la région
