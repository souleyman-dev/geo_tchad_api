"""
Configuration des URLs pour l'API Géographique du Tchad
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProvinceViewSet, DepartementViewSet, CommuneViewSet

# Créer le router et enregistrer les viewsets
router = DefaultRouter()
router.register(r'provinces', ProvinceViewSet, basename='province')
router.register(r'departements', DepartementViewSet, basename='departement')
router.register(r'communes', CommuneViewSet, basename='commune')

app_name = 'geo_tchad'

urlpatterns = [
    path('', include(router.urls)),
]

"""
Routes disponibles:

PROVINCES:
----------
GET    /api/provinces/                    - Liste toutes les provinces
POST   /api/provinces/                    - Créer une province (admin)
GET    /api/provinces/{id}/               - Détails d'une province
PUT    /api/provinces/{id}/               - Modifier une province (admin)
DELETE /api/provinces/{id}/               - Supprimer une province (admin)
GET    /api/provinces/{id}/complete/      - Structure complète (avec depts et communes)
GET    /api/provinces/statistiques/       - Statistiques globales

DÉPARTEMENTS:
-------------
GET    /api/departements/                 - Liste tous les départements
POST   /api/departements/                 - Créer un département (admin)
GET    /api/departements/{id}/            - Détails d'un département
PUT    /api/departements/{id}/            - Modifier un département (admin)
DELETE /api/departements/{id}/            - Supprimer un département (admin)
GET    /api/departements/par_province/    - Départements regroupés par province

COMMUNES:
---------
GET    /api/communes/                     - Liste toutes les communes
POST   /api/communes/                     - Créer une commune (admin)
GET    /api/communes/{id}/                - Détails d'une commune
PUT    /api/communes/{id}/                - Modifier une commune (admin)
DELETE /api/communes/{id}/                - Supprimer une commune (admin)
GET    /api/communes/par_departement/     - Communes regroupées par département
GET    /api/communes/recherche_avancee/   - Recherche avancée

PARAMÈTRES DE RECHERCHE:
------------------------
?search=<terme>           - Recherche par nom
?province=<id>            - Filtrer par province
?province_code=<code>     - Filtrer par code province
?departement=<id>         - Filtrer par département
?departement_code=<code>  - Filtrer par code département
?type_commune=<type>      - Filtrer par type (urbaine/rurale/mixte)
?ordering=<champ>         - Trier par champ
?page=<num>               - Pagination

EXEMPLES D'UTILISATION:
-----------------------
GET /api/provinces/?search=BATHA
GET /api/departements/?province_code=02
GET /api/communes/?province=1&type_commune=urbaine
GET /api/communes/recherche_avancee/?q=Mongo
GET /api/provinces/1/complete/
"""