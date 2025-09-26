# Documentation Technique - Backend Django

## Architecture du Système

### Structure des Applications Django

```
backend/
├── cooperative/          # Configuration principale
│   ├── settings.py      # Configuration Django
│   ├── urls.py         # URLs principales
│   ├── wsgi.py         # Interface WSGI
│   ├── asgi.py         # Interface ASGI
│   └── celery.py       # Configuration Celery
├── core/               # Modèles et utilitaires de base
│   ├── models.py       # TimestampedModel, SoftDeleteModel, Address, Contact, ActivityLog
│   └── admin.py        # Interface d'administration
├── members/            # Gestion des membres
│   ├── models.py       # Member, MembershipType, MembershipFee, FamilyMember
│   └── admin.py        # Interface d'administration
├── inventory/          # Gestion des stocks
│   ├── models.py       # Product, Category, StockMovement, Inventory, InventoryLine
│   └── admin.py        # Interface d'administration
├── sales/             # Gestion des ventes
│   ├── models.py       # Sale, SaleItem, Customer, Payment, Promotion, Order
│   └── admin.py        # Interface d'administration
├── finance/           # Gestion financière
│   ├── models.py       # Account, FinancialTransaction, MemberSavings, Loan, Budget
│   └── admin.py        # Interface d'administration
├── reports/           # Rapports et statistiques
│   ├── models.py       # Report, Dashboard, ReportTemplate
│   └── admin.py        # Interface d'administration
└── api/               # API REST endpoints (à développer)
```

## Modèles de Données

### Core Models

#### TimestampedModel (Abstrait)
```python
- created_at: DateTimeField (auto)
- updated_at: DateTimeField (auto)
```

#### SoftDeleteModel (Abstrait, hérite de TimestampedModel)
```python
- is_active: BooleanField (default=True)
- deleted_at: DateTimeField (nullable)
+ soft_delete()
+ restore()
```

#### Address
```python
- street: CharField(255)
- city: CharField(100)
- region: CharField(100)
- country: CharField(100, default="Sénégal")
- postal_code: CharField(20, optional)
```

#### Contact
```python
- phone_primary: CharField(20)
- phone_secondary: CharField(20, optional)
- email: EmailField(optional)
- whatsapp: CharField(20, optional)
```

#### ActivityLog
```python
- user: ForeignKey(User, nullable)
- action: CharField(50)
- model_name: CharField(50)
- object_id: PositiveIntegerField
- details: JSONField
- ip_address: GenericIPAddressField(nullable)
```

### Members Models

#### MembershipType
```python
- name: CharField(100, unique)
- description: TextField
- monthly_fee: DecimalField(10,2)
- benefits: JSONField
- is_active: BooleanField(default=True)
```

#### Member (hérite de SoftDeleteModel)
```python
- user: OneToOneField(User)
- membership_number: CharField(20, unique)
- membership_type: ForeignKey(MembershipType)
- birth_date: DateField
- gender: CharField(1) ['M', 'F']
- nationality: CharField(50, default="Sénégalaise")
- id_number: CharField(30)
- profession: CharField(100)
- address: ForeignKey(Address)
- contact: ForeignKey(Contact)
- emergency_contact_*: CharField
- join_date: DateField
- status: CharField(20) ['active', 'suspended', 'inactive', 'honorary']
- skills: JSONField
- specialties: JSONField
- photo: ImageField
- id_document: FileField
+ is_up_to_date_with_fees()
```

#### MembershipFee
```python
- member: ForeignKey(Member)
- amount: DecimalField(10,2)
- period_month: PositiveIntegerField(1-12)
- period_year: PositiveIntegerField
- payment_date: DateField
- payment_method: CharField(20) ['cash', 'mobile', 'bank', 'check']
- receipt_number: CharField(50, unique)
- notes: TextField(optional)
```

### Inventory Models

#### Category (hérite de SoftDeleteModel)
```python
- name: CharField(100, unique)
- description: TextField(optional)
- parent: ForeignKey(self, nullable)
- code: CharField(20, unique)
```

#### Unit
```python
- name: CharField(50, unique)
- abbreviation: CharField(10)
- unit_type: CharField(20) ['weight', 'volume', 'length', 'unit', 'other']
```

#### Product (hérite de SoftDeleteModel)
```python
- name: CharField(200)
- description: TextField(optional)
- category: ForeignKey(Category)
- sku: CharField(50, unique)
- barcode: CharField(50, optional)
- unit: ForeignKey(Unit)
- cost_price: DecimalField(12,2)
- selling_price_member: DecimalField(12,2)
- selling_price_non_member: DecimalField(12,2)
- current_stock: DecimalField(15,3)
- minimum_stock: DecimalField(15,3)
- maximum_stock: DecimalField(15,3)
- status: CharField(20) ['active', 'inactive', 'discontinued']
- expiry_date: DateField(nullable)
- image: ImageField(optional)
+ is_low_stock (property)
+ stock_value (property)
```

### Sales Models

#### Customer (hérite de SoftDeleteModel)
```python
- name: CharField(200)
- customer_type: CharField(20) ['member', 'non_member', 'corporate']
- member: ForeignKey(Member, nullable)
- phone: CharField(20)
- email: EmailField(optional)
- address: ForeignKey(Address, nullable)
- credit_limit: DecimalField(12,2)
- current_credit: DecimalField(12,2)
- loyalty_points: PositiveIntegerField
+ available_credit (property)
```

#### Sale
```python
- sale_number: CharField(20, unique)
- customer: ForeignKey(Customer)
- sale_date: DateTimeField
- subtotal: DecimalField(12,2)
- discount_amount: DecimalField(12,2)
- tax_amount: DecimalField(12,2)
- total_amount: DecimalField(12,2)
- payment_status: CharField(20) ['pending', 'partial', 'paid', 'overdue']
- status: CharField(20) ['draft', 'confirmed', 'delivered', 'cancelled', 'returned']
- notes: TextField(optional)
- salesperson: ForeignKey(User, nullable)
- delivery_date: DateTimeField(nullable)
- delivery_address: ForeignKey(Address, nullable)
+ calculate_totals()
```

### Finance Models

#### Account (hérite de SoftDeleteModel)
```python
- code: CharField(20, unique)
- name: CharField(200)
- account_type: CharField(20) ['asset', 'liability', 'equity', 'revenue', 'expense']
- parent: ForeignKey(self, nullable)
- balance: DecimalField(15,2)
- is_reconcilable: BooleanField
```

#### FinancialTransaction
```python
- transaction_number: CharField(20, unique)
- date: DateField
- description: CharField(255)
- transaction_type: CharField(20)
- amount: DecimalField(15,2)
- debit_account: ForeignKey(Account)
- credit_account: ForeignKey(Account)
- reference_type: CharField(20, optional)
- reference_id: PositiveIntegerField(nullable)
- created_by: ForeignKey(User, nullable)
- notes: TextField(optional)
- is_reconciled: BooleanField
```

## Configuration

### Variables d'Environnement Importantes

```env
# Base de données PostgreSQL
DB_NAME=cooperative
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis pour cache et Celery
REDIS_URL=redis://localhost:6379/0

# Configuration Django
SECRET_KEY=your_secret_key
DEBUG=True/False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Email (pour allauth)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=your_smtp_host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Applications Django Installées

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Local apps
    'accounts',
    'core',
    'members',
    'inventory',
    'sales',
    'finance',
    'reports',
    'api',
]
```

## Commandes Utiles

### Développement
```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic

# Lancer le serveur de développement
python manage.py runserver

# Lancer Celery worker
celery -A cooperative worker -l info

# Shell Django
python manage.py shell
```

### Production
```bash
# Variables d'environnement de production
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Serveur WSGI avec Gunicorn
gunicorn cooperative.wsgi:application

# Serveur web avec Nginx (configuration séparée)
```

## Prochaines Étapes

1. **API REST** : Développement des endpoints avec Django REST Framework
2. **Authentification JWT** : Système d'authentification pour le frontend
3. **Serializers** : Sérialisation des données pour l'API
4. **ViewSets** : Vues basées sur les classes pour CRUD
5. **Permissions** : Système de permissions granulaires
6. **Filtres** : Filtres avancés pour les listes
7. **Pagination** : Pagination des résultats
8. **Tests** : Tests unitaires et d'intégration
9. **Documentation API** : Documentation automatique avec Swagger

## Sécurité

- ✅ Authentification robuste avec Django Allauth
- ✅ Hachage des mots de passe
- ✅ Protection CSRF
- ✅ Validation des entrées utilisateur
- ✅ Journal d'audit complet
- ✅ Suppression logique des données sensibles
- 🔄 Permissions granulaires (à développer)
- 🔄 Rate limiting (à développer)
- 🔄 Chiffrement des données sensibles (à développer)