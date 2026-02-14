"""
Serializers pour l'API Géographique du Tchad
"""

from rest_framework import serializers
from .models import Province, Departement, Commune


class CommuneListSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour lister les communes
    """
    class Meta:
        model = Commune
        fields = ['id', 'nom', 'type_commune', 'population']


class CommuneDetailSerializer(serializers.ModelSerializer):
    """
    Serializer détaillé pour une commune
    """
    departement_nom = serializers.CharField(source='departement.nom', read_only=True)
    province_nom = serializers.CharField(source='departement.province.nom', read_only=True)
    
    class Meta:
        model = Commune
        fields = [
            'id',
            'nom',
            'departement',
            'departement_nom',
            'province_nom',
            'type_commune',
            'latitude',
            'longitude',
            'superficie',
            'population',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DepartementListSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour lister les départements
    """
    nombre_communes = serializers.IntegerField(read_only=True)
    province_nom = serializers.CharField(source='province.nom', read_only=True)
    
    class Meta:
        model = Departement
        fields = [
            'id',
            'code',
            'nom',
            'chef_lieu',
            'province',
            'province_nom',
            'nombre_communes'
        ]


class DepartementDetailSerializer(serializers.ModelSerializer):
    """
    Serializer détaillé pour un département avec ses communes
    """
    communes = CommuneListSerializer(many=True, read_only=True)
    nombre_communes = serializers.IntegerField(read_only=True)
    province_nom = serializers.CharField(source='province.nom', read_only=True)
    code_complet = serializers.CharField(read_only=True)
    
    class Meta:
        model = Departement
        fields = [
            'id',
            'code',
            'code_complet',
            'nom',
            'chef_lieu',
            'province',
            'province_nom',
            'latitude',
            'longitude',
            'superficie',
            'population',
            'nombre_communes',
            'communes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProvinceListSerializer(serializers.ModelSerializer):
    """
    Serializer simple pour lister les provinces
    """
    nombre_departements = serializers.IntegerField(read_only=True)
    nombre_communes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Province
        fields = [
            'id',
            'code',
            'nom',
            'chef_lieu',
            'nombre_departements',
            'nombre_communes',
            'population'
        ]


class ProvinceDetailSerializer(serializers.ModelSerializer):
    """
    Serializer détaillé pour une province avec ses départements
    """
    departements = DepartementListSerializer(many=True, read_only=True)
    nombre_departements = serializers.IntegerField(read_only=True)
    nombre_communes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Province
        fields = [
            'id',
            'code',
            'nom',
            'chef_lieu',
            'latitude',
            'longitude',
            'superficie',
            'population',
            'nombre_departements',
            'nombre_communes',
            'departements',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProvinceCompleteSerializer(serializers.ModelSerializer):
    """
    Serializer complet avec départements et communes (structure hiérarchique complète)
    """
    departements = DepartementDetailSerializer(many=True, read_only=True)
    nombre_departements = serializers.IntegerField(read_only=True)
    nombre_communes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Province
        fields = [
            'id',
            'code',
            'nom',
            'chef_lieu',
            'latitude',
            'longitude',
            'superficie',
            'population',
            'nombre_departements',
            'nombre_communes',
            'departements',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# Serializers pour les statistiques
class StatistiquesSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques globales
    """
    nombre_provinces = serializers.IntegerField()
    nombre_departements = serializers.IntegerField()
    nombre_communes = serializers.IntegerField()
    population_totale = serializers.IntegerField()
    superficie_totale = serializers.DecimalField(max_digits=12, decimal_places=2)