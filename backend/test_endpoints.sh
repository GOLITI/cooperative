#!/bin/bash

echo "🧪 Test des endpoints API Django"
echo "=================================="

# Base URL
BASE_URL="http://127.0.0.1:8000/api/v1"

# Fonction pour tester un endpoint
test_endpoint() {
    local module=$1
    local endpoint=$2
    local url="$BASE_URL/$module/$endpoint/"
    
    echo -n "  $endpoint"
    
    # Ajouter des espaces pour alignement
    printf "%*s" $((25 - ${#endpoint})) ""
    
    # Test avec curl
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    case $response in
        200) echo "✅ OK (200)" ;;
        401) echo "🔒 Auth requise (401)" ;;
        404) echo "❌ Non trouvé (404)" ;;
        500) echo "⚠️  Erreur serveur (500)" ;;
        000) echo "❌ Connexion échouée" ;;
        *) echo "⚠️  Status $response" ;;
    esac
}

# Test de chaque module
echo ""
echo "📁 Module: core"
echo "------------------------------"
test_endpoint "core" "addresses"
test_endpoint "core" "contacts"
test_endpoint "core" "activity-logs"

echo ""
echo "📁 Module: members"
echo "------------------------------"
test_endpoint "members" "members"
test_endpoint "members" "membership-fees"

echo ""
echo "📁 Module: inventory"
echo "------------------------------"
test_endpoint "inventory" "categories"
test_endpoint "inventory" "products"
test_endpoint "inventory" "stock-movements"
test_endpoint "inventory" "units"
test_endpoint "inventory" "inventories"

echo ""
echo "📁 Module: sales"
echo "------------------------------"
test_endpoint "sales" "customers"
test_endpoint "sales" "sales"

echo ""
echo "📁 Module: finance"
echo "------------------------------"
test_endpoint "finance" "accounts"
test_endpoint "finance" "transactions"
test_endpoint "finance" "member-savings"
test_endpoint "finance" "loans"
test_endpoint "finance" "loan-payments"
test_endpoint "finance" "budgets"
test_endpoint "finance" "budget-lines"

echo ""
echo "📁 Module: reports"
echo "------------------------------"
test_endpoint "reports" "reports"
test_endpoint "reports" "dashboards"
test_endpoint "reports" "report-templates"

echo ""
echo "=================================="
echo "📊 RÉSUMÉ"
echo "=================================="
echo "✅ OK (200)           - Endpoint fonctionnel avec données"
echo "🔒 Auth requise (401) - Endpoint protégé, normal"
echo "❌ Non trouvé (404)   - Endpoint ou URL incorrecte"
echo "⚠️  Autre status      - Problème à investiguer"
echo ""
echo "Note: Les endpoints avec authentification requise (401) sont normaux"
echo "et indiquent que l'API fonctionne correctement."