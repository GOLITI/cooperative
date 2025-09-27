#!/bin/bash

# Script pour démarrer le serveur Django et tester les API

echo "🚀 Démarrage du serveur Django..."

cd /home/marc-goliti/PROJETS/DJANGO/cooperative/backend

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier que Django fonctionne
echo "📋 Vérification de Django..."
python manage.py check

if [ $? -ne 0 ]; then
    echo "❌ Erreur dans la configuration Django"
    exit 1
fi

# Lancer le serveur en arrière-plan
echo "🎯 Lancement du serveur Django..."
python manage.py runserver 127.0.0.1:8000 &
SERVER_PID=$!

# Attendre que le serveur démarre
sleep 3

# Tester les endpoints
echo "🧪 Test des endpoints API..."

echo "📝 Test de l'endpoint membres..."
curl -s "http://127.0.0.1:8000/api/v1/members/members/" -w "\nStatus: %{http_code}\n"

echo -e "\n📦 Test de l'endpoint inventaire..."
curl -s "http://127.0.0.1:8000/api/v1/inventory/products/" -w "\nStatus: %{http_code}\n"

echo -e "\n💰 Test de l'endpoint ventes..."
curl -s "http://127.0.0.1:8000/api/v1/sales/sales/" -w "\nStatus: %{http_code}\n"

echo -e "\n✅ Tests terminés. Serveur PID: $SERVER_PID"
echo "Pour arrêter le serveur: kill $SERVER_PID"