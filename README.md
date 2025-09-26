# Coopérative – Plateforme de gestion

Ce dépôt contient le code source complet du projet **Coopérative**, une solution modulaire pour la gestion des membres, des stocks, des ventes, de la finance et du reporting des coopératives agricoles ou artisanales.

## Architecture

- **Backend** : Django 5 + Django REST Framework, PostgreSQL, Celery/Redis, Django Allauth & Guardian, configuration via `django-environ`.
- **Frontend** : React 19 (Vite), React Router, React Query, Tailwind CSS 4, Chart.js, DataTables.
- **Asynchrone** : Celery, Redis, planification via Celery Beat.

## Démarrage rapide

### Prérequis

- Python 3.12+
- Node.js 18+
- PostgreSQL & Redis

### Backend

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env  # puis ajustez les variables
python backend/manage.py migrate
python backend/manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Structure

```
backend/
  cooperative/      # Configuration principale Django + Celery
  accounts/         # Utilisateurs, rôles, authentification
  members/          # Placeholder module membres
  inventory/        # Placeholder module stocks
  sales/
  finance/
  reports/
frontend/
  src/
    pages/          # Dashboard, Membres, Stocks (démonstration)
```

## Tests & Qualité

- `python backend/manage.py check` pour vérifier la configuration Django.
- `npm run lint` et `npm run build` côté frontend.

---

Pour toute amélioration ou ajout de fonctionnalité, merci de créer une branche dédiée avant de soumettre une Pull Request.
