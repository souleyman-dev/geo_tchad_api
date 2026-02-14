"""
Configuration de l'interface d'administration Django
"""

from django.contrib import admin
from django.db.models import Count
from .models import Province, Departement, Commune


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des Provinces
    """
    list_display = [
        'code',
        'nom',
        'chef_lieu',
        'population',
        'superficie',
        'get_nb_departements',
        'get_nb_communes'
    ]
    list_filter = ['nom']
    search_fields = ['code', 'nom', 'chef_lieu']
    ordering = ['code']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('code', 'nom', 'chef_lieu')
        }),
        ('Données géographiques', {
            'fields': ('latitude', 'longitude', 'superficie'),
            'classes': ('collapse',)
        }),
        ('Données démographiques', {
            'fields': ('population',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _nb_departements=Count('departements', distinct=True),
        )
        return queryset
    
    @admin.display(ordering='_nb_departements', description='Départements')
    def get_nb_departements(self, obj):
        return obj._nb_departements
    
    @admin.display(description='Communes')
    def get_nb_communes(self, obj):
        return obj.nombre_communes


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des Départements
    """
    list_display = [
        'code',
        'nom',
        'chef_lieu',
        'province',
        'population',
        'get_nb_communes'
    ]
    list_filter = ['province', 'nom']
    search_fields = ['code', 'nom', 'chef_lieu', 'province__nom']
    ordering = ['province__code', 'code']
    autocomplete_fields = ['province']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('province', 'code', 'nom', 'chef_lieu')
        }),
        ('Données géographiques', {
            'fields': ('latitude', 'longitude', 'superficie'),
            'classes': ('collapse',)
        }),
        ('Données démographiques', {
            'fields': ('population',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('province').annotate(
            _nb_communes=Count('communes', distinct=True)
        )
        return queryset
    
    @admin.display(ordering='_nb_communes', description='Communes')
    def get_nb_communes(self, obj):
        return obj._nb_communes


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    """
    Configuration de l'administration des Communes
    """
    list_display = [
        'nom',
        'departement',
        'get_province',
        'type_commune',
        'population'
    ]
    list_filter = [
        'type_commune',
        'departement__province',
        'departement'
    ]
    search_fields = [
        'nom',
        'departement__nom',
        'departement__province__nom'
    ]
    ordering = ['nom']
    autocomplete_fields = ['departement']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('departement', 'nom', 'type_commune')
        }),
        ('Données géographiques', {
            'fields': ('latitude', 'longitude', 'superficie'),
            'classes': ('collapse',)
        }),
        ('Données démographiques', {
            'fields': ('population',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'departement__province'
        )
        return queryset
    
    @admin.display(ordering='departement__province__nom', description='Province')
    def get_province(self, obj):
        return obj.departement.province.nom


# Configuration du site admin
admin.site.site_header = "Administration API Géo Tchad"
admin.site.site_title = "API Géo Tchad"
admin.site.index_title = "Gestion des données géographiques du Tchad"