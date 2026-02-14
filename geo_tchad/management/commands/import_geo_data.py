"""
Script de management Django pour importer les données du CSV
Usage: python manage.py import_geo_data <chemin_vers_csv>
"""

from django.core.management.base import BaseCommand
import csv
from collections import defaultdict
from geo_tchad.models import Province, Departement, Commune


class Command(BaseCommand):
    help = 'Importe les données géographiques du Tchad depuis un fichier CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Chemin vers le fichier CSV contenant les données'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime toutes les données existantes avant l\'import'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        clear_data = options.get('clear', False)

        if clear_data:
            self.stdout.write(self.style.WARNING('Suppression des données existantes...'))
            Commune.objects.all().delete()
            Departement.objects.all().delete()
            Province.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Données supprimées'))

        # Structures pour stocker les données
        provinces_data = {}
        departements_data = {}
        communes_data = []

        self.stdout.write(self.style.NOTICE(f'Lecture du fichier: {csv_file}'))

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    province_code = row['province_code']
                    province_nom = row['province_nom']
                    province_chef_lieu = row['province_chef_lieu']
                    
                    dept_code = row['departement_code']
                    dept_nom = row['departement_nom']
                    dept_chef_lieu = row['departement_chef_lieu']
                    
                    communes = row['communes']
                    
                    # Stocker les provinces
                    if province_code not in provinces_data:
                        provinces_data[province_code] = {
                            'nom': province_nom,
                            'chef_lieu': province_chef_lieu
                        }
                    
                    # Stocker les départements
                    if dept_code:  # Vérifier que le département n'est pas vide
                        dept_key = f"{province_code}-{dept_code}"
                        if dept_key not in departements_data:
                            departements_data[dept_key] = {
                                'province_code': province_code,
                                'code': dept_code,
                                'nom': dept_nom,
                                'chef_lieu': dept_chef_lieu
                            }
                        
                        # Stocker les communes
                        if communes:
                            communes_list = [c.strip() for c in communes.split(',')]
                            for commune in communes_list:
                                if commune:  # Vérifier que le nom n'est pas vide
                                    communes_data.append({
                                        'dept_key': dept_key,
                                        'nom': commune
                                    })

            # Créer les provinces
            self.stdout.write(self.style.NOTICE('Création des provinces...'))
            province_objects = {}
            for code, data in provinces_data.items():
                province, created = Province.objects.get_or_create(
                    code=code,
                    defaults={
                        'nom': data['nom'],
                        'chef_lieu': data['chef_lieu']
                    }
                )
                province_objects[code] = province
                if created:
                    self.stdout.write(f'  ✓ Province créée: {province}')

            # Créer les départements
            self.stdout.write(self.style.NOTICE('Création des départements...'))
            departement_objects = {}
            for dept_key, data in departements_data.items():
                province = province_objects[data['province_code']]
                departement, created = Departement.objects.get_or_create(
                    province=province,
                    code=data['code'],
                    defaults={
                        'nom': data['nom'],
                        'chef_lieu': data['chef_lieu']
                    }
                )
                departement_objects[dept_key] = departement
                if created:
                    self.stdout.write(f'  ✓ Département créé: {departement}')

            # Créer les communes
            self.stdout.write(self.style.NOTICE('Création des communes...'))
            communes_created = 0
            for commune_data in communes_data:
                departement = departement_objects[commune_data['dept_key']]
                commune, created = Commune.objects.get_or_create(
                    departement=departement,
                    nom=commune_data['nom']
                )
                if created:
                    communes_created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Import terminé avec succès!\n'
                    f'  Provinces: {len(province_objects)}\n'
                    f'  Départements: {len(departement_objects)}\n'
                    f'  Communes: {communes_created}'
                )
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Erreur: Fichier non trouvé: {csv_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de l\'import: {str(e)}')
            )
            raise