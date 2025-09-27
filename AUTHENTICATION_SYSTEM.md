# 🔐 SYSTÈME D'AUTHENTIFICATION - CoopManager

## Vue d'ensemble

Le système d'authentification de CoopManager est conçu pour gérer différents types d'utilisateurs dans le contexte des coopératives agricoles africaines.

## 👥 Types d'Utilisateurs

### 1. **Super Administrateur (Django Admin)**
- **Qui** : Administrateur technique du système
- **Accès** : Django Admin (`/admin/`)
- **Permissions** : Gestion complète du système
- **Utilisation** : Maintenance, configuration globale, support technique

### 2. **Administrateur de Coopérative**
- **Qui** : Gestionnaire d'une coopérative spécifique
- **Accès** : Interface React (`/dashboard`)  
- **Permissions** : Gestion complète de SA coopérative
- **Utilisation** : Gestion quotidienne, rapports, membres

### 3. **Membres de la Coopérative** *(Future implémentation)*
- **Qui** : Agriculteurs membres d'une coopérative
- **Accès** : Interface mobile/web simplifiée
- **Permissions** : Consultation de leurs données, ventes
- **Utilisation** : Voir leurs transactions, stock, cotisations

## 🚀 Processus d'Inscription

### Pour les Administrateurs de Coopérative

1. **Inscription libre** via `/register`
   - Nom, prénom, email, nom d'utilisateur
   - Mot de passe sécurisé
   - **Aucune validation préalable nécessaire**

2. **Création automatique du compte**
   - Génération des tokens JWT
   - Connexion automatique après inscription
   - Accès immédiat au dashboard

3. **Configuration de la coopérative**
   - Première connexion → Assistant de configuration
   - Informations sur la coopérative
   - Paramètres initiaux

## 🔑 Processus de Connexion

### Interface React (Administrateurs)
- **URL** : `/login`
- **Endpoint API** : `POST /api/v1/auth/login/`
- **Credentials** : username + password
- **Réponse** : JWT tokens + données utilisateur
- **Stockage** : localStorage (access_token, refresh_token)

### Django Admin (Super Admin)
- **URL** : `/admin/`
- **Credentials** : admin/admin123
- **Session** : Django sessions classiques
- **Utilisation** : Gestion technique uniquement

## 🏛️ Architecture JWT

### Tokens
- **Access Token** : Durée courte (1 heure)
- **Refresh Token** : Durée longue (7 jours)
- **Rotation automatique** : Refresh transparent côté React

### Sécurité
- **Intercepteurs Axios** : Ajout automatique du Bearer token
- **Refresh automatique** : Renouvellement des tokens expirés
- **Déconnexion sécurisée** : Nettoyage localStorage + blacklist token

## 📱 Flux Utilisateur Complet

### 1. Nouvel Administrateur de Coopérative
```
1. Visite http://localhost:3000
2. Redirected → /login
3. Clic "S'inscrire comme admin de coopérative"
4. Remplit formulaire /register
5. Soumission → JWT tokens générés
6. Redirection automatique → /dashboard
7. Assistant de configuration coopérative
```

### 2. Administrateur Existant
```
1. Visite http://localhost:3000
2. Redirected → /login (si non connecté)
3. Saisit username/password
4. Authentification JWT
5. Redirection → /dashboard
6. Navigation dans l'interface
```

### 3. Session Expirée
```
1. Token expire pendant navigation
2. Intercepteur détecte 401
3. Refresh automatique du token
4. Retry de la requête originale
5. Continuation transparente
```

## 🔧 Configuration Technique

### Backend Django
```python
# Endpoints d'authentification
POST /api/v1/auth/login/      # Connexion
POST /api/v1/auth/register/   # Inscription
POST /api/v1/auth/refresh/    # Refresh token
POST /api/v1/auth/logout/     # Déconnexion
```

### Frontend React
```javascript
// Services disponibles
authService.login({username, password})
authService.register(userData)
authService.logout()
authService.refreshToken()

// Context d'authentification
const { user, isAuthenticated, login, logout } = useAuth()
```

## 🌟 Fonctionnalités Implémentées

### ✅ Authentification
- [x] Connexion JWT fonctionnelle
- [x] Inscription administrateurs
- [x] Refresh automatique des tokens
- [x] Routes protégées React
- [x] Gestion d'erreurs complète
- [x] Interface utilisateur intuitive

### ✅ Sécurité
- [x] Validation côté client et serveur
- [x] Hachage sécurisé des mots de passe
- [x] Protection CSRF désactivée pour API
- [x] Tokens JWT sécurisés
- [x] Nettoyage automatique des sessions

### ✅ UX/UI
- [x] Boutons voir/masquer mot de passe
- [x] Messages d'erreur clairs
- [x] Loading states
- [x] Redirections intelligentes
- [x] Design Material-UI cohérent

## 🚧 Améliorations Futures

### Phase 2 : Gestion Multi-Coopératives
- **Association utilisateur ↔ coopérative**
- **Permissions granulaires**
- **Interface de sélection de coopérative**

### Phase 3 : Membres de Coopératives
- **Système d'invitation**
- **Interface simplifiée pour agriculteurs**
- **Authentification mobile (SMS/QR codes)**

### Phase 4 : Fonctionnalités Avancées
- **2FA (authentification à double facteur)**
- **Single Sign-On (SSO)**
- **Gestion des rôles avancée**
- **Audit trail des connexions**

---

## 🧪 Tests Actuels

### Comptes de Test Disponibles

1. **Super Admin Django**
   - Username: `admin`
   - Password: `admin123`
   - Accès: http://127.0.0.1:8000/admin/

2. **Test Admin React**
   - Username: `test_admin` 
   - Password: `testpass123`
   - Accès: http://localhost:3000/login

### URLs Fonctionnelles
- **Frontend React** : http://localhost:3000
- **Backend Django** : http://127.0.0.1:8000
- **API Documentation** : http://127.0.0.1:8000/api/docs/
- **Django Admin** : http://127.0.0.1:8000/admin/

**🎉 Le système d'authentification est maintenant complet et sécurisé !**