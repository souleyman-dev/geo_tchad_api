# API Géo Tchad

API REST pour consulter et gérer l'organisation administrative et les
données géographiques du Tchad. Le projet est construit avec Django et
Django REST Framework.

## Fonctionnalités

- Gestion des provinces, départements et communes ;
- représentation hiérarchique des données :
  `Province -> Département -> Commune` ;
- recherche par nom, code ou chef-lieu ;
- filtres par province, département et type de commune ;
- pagination et tri des résultats ;
- statistiques globales ;
- recherche avancée dans les communes, départements et provinces ;
- interface d'administration Django ;
- commande d'import des données depuis un fichier CSV ;
- configuration CORS prévue pour une application React ou toute autre
  application frontend.

Les données incluses dans le dépôt représentent actuellement **23 provinces,
95 départements et 361 communes**. Le nombre de communes peut évoluer selon
les données importées.

## Technologies

- Python 3.10 ou supérieur ;
- Django 4.2 ;
- Django REST Framework ;
- django-filter ;
- SQLite pour le développement ;
- PostgreSQL ou MySQL possibles en production.

## Installation

Clonez le dépôt puis placez-vous dans son dossier :

```bash
git clone https://github.com/dickerChad/geo_tchad_api.git
cd geo_tchad_api
```

Créez et activez un environnement virtuel :

```bash
python -m venv .venv
source .venv/bin/activate
```

Sous Windows PowerShell :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Installez les dépendances :

```bash
pip install -r requirements.txt
```

Appliquez les migrations :

```bash
python manage.py migrate
```

## Importer les données géographiques

Le fichier `tchad_organisation_administrative.csv` contient les données
administratives utilisées par le projet. Importez-le avec la commande
suivante :

```bash
python manage.py import_geo_data tchad_organisation_administrative.csv
```

Pour remplacer toutes les données existantes avant l'import :

```bash
python manage.py import_geo_data tchad_organisation_administrative.csv --clear
```

Le fichier CSV doit contenir les colonnes suivantes :

```text
province_code
province_nom
province_chef_lieu
departement_code
departement_nom
departement_chef_lieu
communes
```

## Lancer le serveur

```bash
python manage.py runserver
```

L'API est alors accessible à l'adresse suivante :

```text
http://127.0.0.1:8000/api/
```

L'interface d'administration est disponible ici :

```text
http://127.0.0.1:8000/admin/
```

Pour créer un compte administrateur :

```bash
python manage.py createsuperuser
```

## Endpoints principaux

Toutes les routes API sont préfixées par `/api/`.

### Provinces

| Méthode | Route | Description |
| --- | --- | --- |
| GET | `/provinces/` | Liste paginée des provinces |
| POST | `/provinces/` | Créer une province |
| GET | `/provinces/{id}/` | Détails d'une province |
| PUT/PATCH | `/provinces/{id}/` | Modifier une province |
| DELETE | `/provinces/{id}/` | Supprimer une province |
| GET | `/provinces/{id}/complete/` | Province avec départements et communes |
| GET | `/provinces/statistiques/` | Statistiques globales |

### Départements

| Méthode | Route | Description |
| --- | --- | --- |
| GET | `/departements/` | Liste paginée des départements |
| POST | `/departements/` | Créer un département |
| GET | `/departements/{id}/` | Détails avec ses communes |
| PUT/PATCH | `/departements/{id}/` | Modifier un département |
| DELETE | `/departements/{id}/` | Supprimer un département |
| GET | `/departements/par_province/` | Départements regroupés par province |

### Communes

| Méthode | Route | Description |
| --- | --- | --- |
| GET | `/communes/` | Liste paginée des communes |
| POST | `/communes/` | Créer une commune |
| GET | `/communes/{id}/` | Détails d'une commune |
| PUT/PATCH | `/communes/{id}/` | Modifier une commune |
| DELETE | `/communes/{id}/` | Supprimer une commune |
| GET | `/communes/par_departement/` | Communes regroupées par département |
| GET | `/communes/recherche_avancee/` | Recherche dans toute la hiérarchie |

## Recherche, filtres et pagination

Les paramètres suivants peuvent être combinés selon la ressource :

- `search` : recherche textuelle ;
- `province` : identifiant d'une province, notamment pour les communes ;
- `province_code` : code d'une province ;
- `departement` : identifiant d'un département ;
- `departement_code` : code d'un département ;
- `type_commune` : `urbaine`, `rurale` ou `mixte` ;
- `ordering` : champ de tri, par exemple `nom`, `code` ou `-population` ;
- `page` : numéro de page.

Exemples :

```bash
# Rechercher une province
curl "http://127.0.0.1:8000/api/provinces/?search=BATHA"

# Lister les départements d'une province
curl "http://127.0.0.1:8000/api/departements/?province_code=02"

# Lister les communes urbaines d'une province
curl "http://127.0.0.1:8000/api/communes/?province=1&type_commune=urbaine"

# Recherche avancée
curl "http://127.0.0.1:8000/api/communes/recherche_avancee/?q=Mongo"

# Récupérer une province avec toute sa structure
curl "http://127.0.0.1:8000/api/provinces/1/complete/"
```

La recherche avancée utilise le paramètre `q`. Les listes sont paginées avec
une taille de page par défaut de 20 éléments.

## Exemple de réponse

Une requête `GET /api/provinces/` renvoie une réponse paginée de ce type :

```json
{
  "count": 23,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "code": "01",
      "nom": "Batha",
      "chef_lieu": "Ati",
      "nombre_departements": 3,
      "nombre_communes": 15,
      "population": null
    }
  ]
}
```

## Tests et vérifications

Vérifier la configuration Django :

```bash
python manage.py check
```

Exécuter les tests :

```bash
python manage.py test
```


