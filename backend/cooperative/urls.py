"""
Configuration des URLs pour le système de gestion des coopératives.
Structure modulaire avec routes par fonctionnalité.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Configuration de l'admin Django
admin.site.site_header = "Administration des Coopératives"
admin.site.site_title = "Gestion Coopératives"
admin.site.index_title = "Panneau d'administration"

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),
    
    # Authentification (allauth)
    path('auth/', include('allauth.urls')),
    
    # API d'authentification
    path('api/auth/', include('accounts.urls')),
    
    # API des membres
    path('api/members/', include('members.api_urls')),
    
    # API de l'inventaire
    path('api/inventory/', include('inventory.api_urls')),
    
    # API des ventes
    path('api/sales/', include('sales.api_urls')),
    
    # Documentation API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Application principale (temporairement désactivée)
    # path('', include('core.urls')),
]

# URLs à activer progressivement après création des vues
# urlpatterns += [
#     path('api/members/', include('members.urls')),
#     path('api/inventory/', include('inventory.urls')),
#     path('api/sales/', include('sales.urls')),
#     path('api/finance/', include('finance.urls')),
#     path('api/reports/', include('reports.urls')),
#     path('api/v1/', include('api.urls')),
# ]

# Servir les fichiers media et static en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
