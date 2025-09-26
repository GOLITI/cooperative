# 📊 API Financière - Documentation Complète

## Vue d'ensemble

L'API Financière fournit un système complet de gestion comptable et financière pour les coopératives, incluant :

- 💰 **Comptes comptables** (actifs, passifs, revenus, charges)
- 📊 **Transactions** avec double-écriture automatique
- 💳 **Prêts aux membres** avec gestion des remboursements
- 🏦 **Épargne des membres** avec calcul d'intérêts
- 📈 **Rapports financiers** (bilan, compte de résultat)

## 🔗 Base URL
```
http://localhost:8000/api/finance/
```

## 🔐 Authentification

Toutes les requêtes nécessitent un token d'authentification :
```http
Authorization: Token votre_token_ici
```

## 📁 Endpoints Principaux

### 1. Catégories de Comptes

#### Liste des catégories
```http
GET /api/finance/categories/
```

#### Créer une catégorie
```http
POST /api/finance/categories/
Content-Type: application/json

{
  "name": "Immobilisations",
  "code": "2",
  "description": "Biens durables de l'entreprise",
  "parent": null
}
```

#### Détail d'une catégorie
```http
GET /api/finance/categories/{id}/
```

### 2. Comptes Comptables

#### Liste des comptes
```http
GET /api/finance/accounts/
```

**Paramètres de filtrage :**
- `account_type`: asset, liability, equity, revenue, expense
- `category`: ID de la catégorie
- `search`: recherche par nom/code

#### Créer un compte
```http
POST /api/finance/accounts/
Content-Type: application/json

{
  "name": "Caisse principale",
  "code": "512001",
  "account_type": "asset",
  "category": 1,
  "description": "Liquidités en caisse",
  "is_system": false
}
```

#### Historique des transactions d'un compte
```http
GET /api/finance/accounts/{id}/transactions/
```

#### Bilan comptable
```http
GET /api/finance/accounts/balance_sheet/
```

**Réponse :**
```json
{
  "assets": 150000.00,
  "liabilities": 80000.00,
  "equity": 70000.00,
  "balance_check": 0.00,
  "as_of_date": "2024-01-15"
}
```

#### Compte de résultat
```http
GET /api/finance/accounts/income_statement/?year=2024
```

**Réponse :**
```json
{
  "revenues": 120000.00,
  "expenses": 95000.00,
  "net_income": 25000.00,
  "period": "2024",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

### 3. Transactions Financières

#### Liste des transactions
```http
GET /api/finance/transactions/
```

**Paramètres de filtrage :**
- `transaction_type`: sale, purchase, payment, receipt, manual, loan, savings
- `source`: cash, bank, mobile_money
- `debit_account`, `credit_account`: IDs des comptes
- `member`: ID du membre
- `is_reconciled`: true/false

#### Créer une transaction
```http
POST /api/finance/transactions/
Content-Type: application/json

{
  "transaction_type": "manual",
  "amount": 5000.00,
  "debit_account": 1,
  "credit_account": 2,
  "description": "Achat matériel bureau",
  "reference": "FAC001",
  "source": "bank"
}
```

#### Valider une transaction
```http
POST /api/finance/transactions/{id}/validate_transaction/
```

#### Marquer comme rapprochée
```http
POST /api/finance/transactions/{id}/reconcile/
```

#### Statistiques des transactions
```http
GET /api/finance/transactions/stats/?period=30
```

**Réponse :**
```json
{
  "total_transactions": 245,
  "total_amount": 85430.00,
  "transactions_by_type": {
    "sale": {"count": 120, "amount": 45000.00},
    "purchase": {"count": 80, "amount": 32000.00},
    "manual": {"count": 45, "amount": 8430.00}
  },
  "monthly_transactions": [...],
  "period_start": "2024-01-01",
  "period_end": "2024-01-31"
}
```

### 4. Prêts aux Membres

#### Liste des prêts
```http
GET /api/finance/loans/
```

**Paramètres de filtrage :**
- `status`: pending, approved, disbursed, completed, cancelled
- `member`: ID du membre

#### Demander un prêt
```http
POST /api/finance/loans/
Content-Type: application/json

{
  "member": 1,
  "requested_amount": 10000.00,
  "purpose": "Achat d'équipement agricole",
  "duration_months": 24,
  "interest_rate": 6.5
}
```

#### Approuver un prêt
```http
POST /api/finance/loans/{id}/approve/
Content-Type: application/json

{
  "approved_amount": 9500.00
}
```

#### Débourser un prêt
```http
POST /api/finance/loans/{id}/disburse/
```

#### Enregistrer un remboursement
```http
POST /api/finance/loans/{id}/record_payment/
Content-Type: application/json

{
  "amount": 500.00
}
```

### 5. Épargne des Membres

#### Liste des comptes d'épargne
```http
GET /api/finance/savings/
```

**Paramètres de filtrage :**
- `savings_type`: regular, term_deposit, special
- `member`: ID du membre

#### Ouvrir un compte d'épargne
```http
POST /api/finance/savings/
Content-Type: application/json

{
  "member": 1,
  "savings_type": "regular",
  "interest_rate": 4.0,
  "minimum_balance": 500.00
}
```

#### Effectuer un dépôt
```http
POST /api/finance/savings/{id}/deposit/
Content-Type: application/json

{
  "amount": 1000.00
}
```

#### Effectuer un retrait
```http
POST /api/finance/savings/{id}/withdraw/
Content-Type: application/json

{
  "amount": 200.00
}
```

#### Capitaliser les intérêts
```http
POST /api/finance/savings/{id}/capitalize_interest/
```

## 🏗️ Structure des Modèles

### AccountCategory
```json
{
  "id": 1,
  "name": "Immobilisations",
  "code": "2",
  "description": "Biens durables",
  "parent": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Account
```json
{
  "id": 1,
  "name": "Caisse principale",
  "code": "512001",
  "account_type": "asset",
  "category": 1,
  "current_balance": 15420.50,
  "is_system": false,
  "description": "Liquidités en caisse",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### FinancialTransaction
```json
{
  "id": 1,
  "transaction_number": "TXN-2024-00001",
  "transaction_type": "sale",
  "amount": 2500.00,
  "debit_account": 1,
  "credit_account": 2,
  "description": "Vente produits agricoles",
  "reference": "VTE001",
  "source": "cash",
  "transaction_date": "2024-01-15T14:30:00Z",
  "member": 1,
  "sale": 1,
  "is_reconciled": false,
  "validated_at": null,
  "created_by": 1,
  "validated_by": null
}
```

### MemberLoan
```json
{
  "id": 1,
  "loan_number": "PRT-2024-00001",
  "member": 1,
  "requested_amount": 10000.00,
  "approved_amount": 9500.00,
  "outstanding_balance": 8500.00,
  "interest_rate": 6.5,
  "duration_months": 24,
  "monthly_payment": 418.25,
  "purpose": "Achat équipement",
  "status": "disbursed",
  "application_date": "2024-01-10",
  "approval_date": "2024-01-12",
  "disbursement_date": "2024-01-15",
  "approved_by": 1
}
```

### MemberSavings
```json
{
  "id": 1,
  "member": 1,
  "savings_type": "regular",
  "current_balance": 5430.00,
  "interest_rate": 4.0,
  "minimum_balance": 500.00,
  "opening_date": "2024-01-15",
  "last_interest_date": "2024-01-01",
  "accrued_interest": 18.10
}
```

## 🔒 Permissions

- **CanViewFinances** : Lecture des données financières
- **CanManageFinances** : Création/modification des données
- **CanValidateTransactions** : Validation des transactions et opérations spéciales

## 📊 Rapports Disponibles

1. **Bilan comptable** : `/accounts/balance_sheet/`
2. **Compte de résultat** : `/accounts/income_statement/`
3. **Statistiques des transactions** : `/transactions/stats/`
4. **Historique par compte** : `/accounts/{id}/transactions/`

## 🧪 Tests

### Test rapide
```bash
python test_finance_quick.py
```

### Test complet
```bash
python test_finance_api.py
```

## 🚀 Démarrage

1. **Activer l'environnement virtuel :**
```bash
cd backend
source venv/bin/activate
```

2. **Démarrer le serveur :**
```bash
python manage.py runserver
```

3. **Tester l'API :**
```bash
cd ..
python test_finance_quick.py
```

## 📋 Codes d'Erreur

- `400` : Données invalides ou logique métier violée
- `401` : Non authentifié
- `403` : Permissions insuffisantes
- `404` : Ressource non trouvée
- `500` : Erreur serveur

## 💡 Bonnes Pratiques

1. **Double-écriture** : Chaque transaction affecte deux comptes (débit/crédit)
2. **Validation** : Les transactions importantes doivent être validées
3. **Rapprochement** : Marquer les transactions rapprochées avec les relevés
4. **Catégorisation** : Utiliser les catégories pour organiser les comptes
5. **Référencement** : Toujours inclure des références pour la traçabilité

---

*Cette API fournit un système comptable complet pour la gestion financière des coopératives avec respect des principes de la comptabilité en partie double.*