# 📦 API d'Inventaire - Documentation Complète

## 🎯 Vue d'ensemble

L'API d'inventaire de la coopérative permet la gestion complète des produits, catégories, unités de mesure et mouvements de stock. Elle offre des fonctionnalités avancées de calculs automatiques, d'alertes de stock et de statistiques.

## 🔗 Endpoints Disponibles

### Base URL
```
http://127.0.0.1:8000/api/inventory/
```

## 📦 Catégories de Produits

### 📋 Liste des catégories
```http
GET /api/inventory/categories/
```

### ➕ Créer une catégorie
```http
POST /api/inventory/categories/
Content-Type: application/json

{
    "name": "Fruits et Légumes",
    "description": "Produits frais de saison"
}
```

### 📄 Détail d'une catégorie
```http
GET /api/inventory/categories/{id}/
```

### ✏️ Modifier une catégorie
```http
PUT /api/inventory/categories/{id}/
Content-Type: application/json

{
    "name": "Fruits et Légumes Bio",
    "description": "Produits frais biologiques de saison"
}
```

### 🗑️ Supprimer une catégorie
```http
DELETE /api/inventory/categories/{id}/
```

## 📏 Unités de Mesure

### 📋 Liste des unités
```http
GET /api/inventory/units/
```

### ➕ Créer une unité
```http
POST /api/inventory/units/
Content-Type: application/json

{
    "name": "Kilogramme",
    "symbol": "kg",
    "unit_type": "weight"
}
```

**Types d'unités disponibles:**
- `weight` - Poids
- `volume` - Volume
- `count` - Nombre/Quantité
- `length` - Longueur
- `area` - Surface

### 📄 Détail d'une unité
```http
GET /api/inventory/units/{id}/
```

## 🛍️ Produits

### 📋 Liste des produits
```http
GET /api/inventory/products/
```

**Paramètres de filtrage:**
- `?category={id}` - Filtrer par catégorie
- `?is_active=true/false` - Produits actifs/inactifs
- `?search={terme}` - Recherche textuelle
- `?ordering=name,-created_at` - Tri des résultats

### ➕ Créer un produit
```http
POST /api/inventory/products/
Content-Type: application/json

{
    "name": "Tomates cerises",
    "description": "Tomates cerises biologiques",
    "category": 1,
    "unit": 1,
    "cost_price": "3.50",
    "selling_price": "5.00",
    "minimum_stock": 5,
    "maximum_stock": 50,
    "current_stock": 20,
    "is_active": true
}
```

### 📄 Détail d'un produit
```http
GET /api/inventory/products/{id}/
```

### 📊 Statistiques globales des produits
```http
GET /api/inventory/products/stats/
```

**Réponse:**
```json
{
    "total_products": 15,
    "total_value": "1250.00",
    "low_stock_count": 3,
    "out_of_stock_count": 1,
    "categories_count": 5
}
```

### 🚨 Alertes de stock globales
```http
GET /api/inventory/products/alerts/
```

### 📉 Produits en stock faible
```http
GET /api/inventory/products/low_stock/
```

### 📊 Statistiques d'un produit spécifique
```http
GET /api/inventory/products/{id}/stats/
```

**Réponse:**
```json
{
    "total_movements": 25,
    "total_in": "150.00",
    "total_out": "75.00",
    "current_stock": "20.00",
    "stock_value": "100.00",
    "last_movement": "2024-01-15T10:30:00Z"
}
```

### 🚨 Alertes d'un produit spécifique
```http
GET /api/inventory/products/{id}/alerts/
```

### ⚡ Ajustement de stock
```http
POST /api/inventory/products/{id}/adjust-stock/
Content-Type: application/json

{
    "new_stock": 25,
    "reason": "Inventaire physique"
}
```

## 📊 Mouvements de Stock

### 📋 Liste des mouvements
```http
GET /api/inventory/stock-movements/
```

**Paramètres de filtrage:**
- `?product={id}` - Mouvements d'un produit spécifique
- `?movement_type=IN/OUT` - Type de mouvement
- `?date_from=2024-01-01` - À partir de cette date
- `?date_to=2024-01-31` - Jusqu'à cette date

### ➕ Créer un mouvement de stock
```http
POST /api/inventory/stock-movements/
Content-Type: application/json

{
    "product": 1,
    "movement_type": "IN",
    "quantity": 10,
    "reason": "Réapprovisionnement",
    "reference": "REF001"
}
```

**Types de mouvements:**
- `IN` - Entrée de stock
- `OUT` - Sortie de stock
- `ADJUSTMENT` - Ajustement d'inventaire
- `TRANSFER` - Transfert
- `LOSS` - Perte
- `RETURN` - Retour

### 📄 Détail d'un mouvement
```http
GET /api/inventory/stock-movements/{id}/
```

## 🔐 Authentification

Tous les endpoints nécessitent une authentification JWT. Incluez le token dans l'en-tête:

```http
Authorization: Bearer {votre_token_jwt}
```

## 🔒 Permissions

### Permissions requises par endpoint:

- **Lecture** (`CanViewInventory`):
  - GET sur tous les endpoints
  
- **Gestion complète** (`CanManageInventory`):
  - POST, PUT, PATCH, DELETE sur tous les endpoints
  - Actions spéciales (ajustement de stock, etc.)

## 📱 Codes de Réponse HTTP

- `200 OK` - Succès
- `201 Created` - Ressource créée
- `204 No Content` - Suppression réussie
- `400 Bad Request` - Données invalides
- `401 Unauthorized` - Non authentifié
- `403 Forbidden` - Permissions insuffisantes
- `404 Not Found` - Ressource non trouvée
- `500 Internal Server Error` - Erreur serveur

## 🎨 Format des Réponses

### Liste paginée
```json
{
    "count": 50,
    "next": "http://127.0.0.1:8000/api/inventory/products/?page=2",
    "previous": null,
    "results": [...]
}
```

### Erreur de validation
```json
{
    "field_name": ["Ce champ est obligatoire."],
    "another_field": ["Cette valeur doit être positive."]
}
```

## 🧪 Tests et Validation

L'API a été entièrement testée avec le script `test_inventory_api.py` qui valide:

- ✅ CRUD complet pour toutes les entités
- ✅ Authentification et permissions
- ✅ Calculs automatiques de stock
- ✅ Filtres et recherches
- ✅ Actions avancées (statistiques, alertes)
- ✅ Ajustements de stock
- ✅ Validation des données

## 🚀 Utilisation Frontend

Cette API est prête pour l'intégration avec le frontend Vue.js. Elle respecte les standards REST et fournit toutes les données nécessaires pour une interface utilisateur complète de gestion d'inventaire.

## 📚 Documentation Interactive

La documentation interactive Swagger est disponible à:
```
http://127.0.0.1:8000/api/schema/swagger-ui/
```