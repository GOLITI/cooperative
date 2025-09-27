# 🧪 GUIDE DE TEST COMPLET - CoopManager

## 🚀 Démarrage des Serveurs

### 1. Backend Django
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```
**URL** : http://127.0.0.1:8000

### 2. Frontend React
```bash
cd frontend  
npm start
```
**URL** : http://localhost:3000

---

## 🔐 Tests d'Authentification

### Test 1 : Connexion Admin Existant
1. **Aller sur** : http://localhost:3000
2. **Redirection automatique** vers `/login`
3. **Saisir** :
   - Username: `admin`
   - Password: `admin123`
4. **Cliquer** "Se connecter"
5. **Résultat attendu** : Redirection vers `/dashboard` avec interface complète

### Test 2 : Inscription Nouvel Admin
1. **Sur la page login**, cliquer "S'inscrire comme admin de coopérative"
2. **Remplir le formulaire** :
   - Prénom: `Marie`
   - Nom: `Martin`
   - Username: `marie_admin`
   - Email: `marie@coop-test.com`
   - Mot de passe: `motdepasse123`
   - Confirmer: `motdepasse123`
3. **Cliquer** "S'inscrire"
4. **Résultat attendu** : 
   - Message de succès
   - Redirection automatique vers `/dashboard`
   - Authentification automatique

### Test 3 : Boutons Voir Mot de Passe
1. **Sur les pages login/register**
2. **Cliquer l'icône œil** dans les champs mot de passe
3. **Résultat attendu** : Basculement texte visible/masqué

### Test 4 : Gestion des Erreurs
1. **Tenter connexion avec mauvais credentials**
2. **Laisser des champs vides**
3. **Utiliser un email invalide à l'inscription**
4. **Résultat attendu** : Messages d'erreur clairs et pertinents

---

## 🏠 Tests Interface Dashboard

### Test 5 : Navigation
1. **Une fois connecté**, tester la sidebar :
   - 📊 Dashboard
   - 👥 Membres
   - 📦 Inventaire  
   - 💰 Ventes
   - 🏦 Finance
   - 📈 Rapports
2. **Résultat attendu** : Navigation fluide avec pages "À venir"

### Test 6 : Responsive Design
1. **Redimensionner la fenêtre** (mobile/tablet/desktop)
2. **Résultat attendu** : 
   - Sidebar devient drawer mobile
   - Interface s'adapte
   - Bouton hamburger apparaît

### Test 7 : Menu Utilisateur
1. **Cliquer l'avatar** en haut à droite
2. **Tester** :
   - Mon Profil → Page "À venir"
   - Déconnexion → Retour `/login`

---

## 🔗 Tests API Integration

### Test 8 : Vérification Token JWT
1. **Ouvrir Developer Tools** (F12)
2. **Aller dans Network/Réseau**
3. **Naviguer dans l'interface**
4. **Vérifier** : Header `Authorization: Bearer [token]` sur les requêtes API

### Test 9 : Refresh Automatique
1. **Attendre 1 heure** (ou modifier l'expiration pour test rapide)
2. **Faire une action** nécessitant API
3. **Résultat attendu** : Refresh automatique transparent

### Test 10 : Persistance Session
1. **Se connecter**
2. **Fermer/rouvrir l'onglet**
3. **Résultat attendu** : Toujours connecté (localStorage)
4. **Vider localStorage** → Retour `/login`

---

## ⚡ Tests de Performance

### Test 11 : Temps de Chargement
- **Login page** : < 2s
- **Dashboard** : < 3s  
- **Navigation** : < 1s

### Test 12 : Gestion Hors Ligne
1. **Couper la connexion réseau**
2. **Tenter navigation**
3. **Résultat attendu** : Messages d'erreur appropriés

---

## 🐛 Tests de Robustesse

### Test 13 : Backend Déconnecté
1. **Arrêter le serveur Django**
2. **Tenter actions dans React**
3. **Résultat attendu** : Messages d'erreur réseau clairs

### Test 14 : Données Corrompues
1. **Modifier localStorage manuellement**
2. **Recharger la page**
3. **Résultat attendu** : Nettoyage auto et redirection login

---

## 📊 Validation Fonctionnalités

### ✅ Fonctionnalités à Valider

#### Authentification
- [ ] Connexion admin/admin123 fonctionne
- [ ] Inscription nouveau compte fonctionne  
- [ ] Boutons voir/masquer mot de passe
- [ ] Validation formulaires (erreurs claires)
- [ ] Redirection après connexion
- [ ] Déconnexion propre

#### Interface
- [ ] Dashboard s'affiche correctement
- [ ] Navigation sidebar fonctionnelle
- [ ] Menu utilisateur accessible
- [ ] Responsive design mobile/desktop
- [ ] Loading states visibles
- [ ] Messages d'erreur/succès

#### API Integration
- [ ] Tokens JWT dans les requêtes
- [ ] Refresh automatique des tokens
- [ ] Gestion erreurs réseau
- [ ] Persistance session localStorage

#### Sécurité
- [ ] Routes protégées (redirection login)
- [ ] Nettoyage session à la déconnexion
- [ ] Validation côté client ET serveur
- [ ] Pas de données sensibles en localStorage

---

## 🎯 Résultats Attendus

### Expérience Utilisateur
1. **Connexion fluide** en 2-3 clics
2. **Interface moderne** et intuitive
3. **Navigation rapide** entre modules
4. **Messages clairs** en cas de problème
5. **Responsive** sur tous devices

### Technique
1. **0 erreur console** JavaScript
2. **API calls** avec authentification automatique
3. **Session persistante** entre visites
4. **Refresh transparent** des tokens
5. **Déconnexion sécurisée**

---

## 🚨 Problèmes Connus et Solutions

### "CORS Error"
**Solution** : Vérifier que Django tourne sur `:8000` et React sur `:3000`

### "Token Invalid" 
**Solution** : Vider localStorage et se reconnecter

### "Network Error"
**Solution** : Vérifier que les deux serveurs fonctionnent

### Page Blanche React
**Solution** : Vérifier console pour erreurs JS, redémarrer npm start

---

## 📋 Checklist Final

Avant de valider la phase d'authentification :

- [ ] **Backend** : Serveur Django actif (port 8000)
- [ ] **Frontend** : Serveur React actif (port 3000)  
- [ ] **Database** : Users admin et test_admin existent
- [ ] **API** : Endpoints auth fonctionnels (/api/v1/auth/)
- [ ] **Login** : Connexion admin/admin123 réussie
- [ ] **Register** : Inscription nouveau compte réussie
- [ ] **Dashboard** : Interface complète accessible
- [ ] **Navigation** : Tous modules accessibles
- [ ] **UX** : Boutons mot de passe fonctionnels
- [ ] **Sécurité** : Routes protégées + JWT valide

**🎉 Une fois tous les tests validés, l'authentification est prête pour production !**