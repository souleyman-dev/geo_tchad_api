from django.shortcuts import render

# Create your views here.
"""
Views et ViewSets pour l'API Géographique du Tchad
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q

from .models import Province, Departement, Commune
from .serializers import (
    ProvinceListSerializer,
    ProvinceDetailSerializer,
    ProvinceCompleteSerializer,
    DepartementListSerializer,
    DepartementDetailSerializer,
    CommuneListSerializer,
    CommuneDetailSerializer,
    StatistiquesSerializer,
)


class ProvinceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les provinces
    
    list: Retourne la liste de toutes les provinces
    retrieve: Retourne les détails d'une province
    create: Crée une nouvelle province (admin)
    update: Met à jour une province (admin)
    delete: Supprime une province (admin)
    
    Actions supplémentaires:
    - complete: Retourne la structure complète (province + départements + communes)
    - search: Recherche de provinces par nom
    """
    queryset = Province.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'code', 'chef_lieu']
    ordering_fields = ['code', 'nom', 'population']
    ordering = ['code']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProvinceDetailSerializer
        elif self.action == 'complete':
            return ProvinceCompleteSerializer
        return ProvinceListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Précharger les relations pour optimiser les performances
        if self.action in ['retrieve', 'list']:
            queryset = queryset.prefetch_related('departements')
        elif self.action == 'complete':
            queryset = queryset.prefetch_related(
                'departements__communes'
            )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def complete(self, request, pk=None):
        """
        Retourne la structure complète d'une province avec tous ses départements et communes
        GET /api/provinces/{id}/complete/
        """
        province = self.get_object()
        serializer = ProvinceCompleteSerializer(province)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        Retourne les statistiques globales des provinces
        GET /api/provinces/statistiques/
        """
        stats = Province.objects.aggregate(
            nombre_provinces=Count('id'),
            population_totale=Sum('population'),
            superficie_totale=Sum('superficie')
        )
        stats['nombre_departements'] = Departement.objects.count()
        stats['nombre_communes'] = Commune.objects.count()
        
        serializer = StatistiquesSerializer(stats)
        return Response(serializer.data)


class DepartementViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les départements
    
    list: Retourne la liste de tous les départements
    retrieve: Retourne les détails d'un département avec ses communes
    create: Crée un nouveau département (admin)
    update: Met à jour un département (admin)
    delete: Supprime un département (admin)
    
    Filtres disponibles:
    - province: Filtrer par province (ID ou code)
    - search: Rechercher par nom, chef-lieu
    """
    queryset = Departement.objects.select_related('province')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['province', 'code']
    search_fields = ['nom', 'chef_lieu', 'province__nom']
    ordering_fields = ['code', 'nom', 'population']
    ordering = ['province__code', 'code']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DepartementDetailSerializer
        return DepartementListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer par code de province si fourni dans les query params
        province_code = self.request.query_params.get('province_code', None)
        if province_code:
            queryset = queryset.filter(province__code=province_code)
        
        # Précharger les communes pour les détails
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('communes')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def par_province(self, request):
        """
        Retourne les départements regroupés par province
        GET /api/departements/par_province/
        """
        provinces = Province.objects.prefetch_related('departements').all()
        data = []
        
        for province in provinces:
            data.append({
                'province': ProvinceListSerializer(province).data,
                'departements': DepartementListSerializer(
                    province.departements.all(), 
                    many=True
                ).data
            })
        
        return Response(data)


class CommuneViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les communes
    
    list: Retourne la liste de toutes les communes
    retrieve: Retourne les détails d'une commune
    create: Crée une nouvelle commune (admin)
    update: Met à jour une commune (admin)
    delete: Supprime une commune (admin)
    
    Filtres disponibles:
    - departement: Filtrer par département (ID)
    - province: Filtrer par province (ID)
    - type_commune: Filtrer par type (urbaine, rurale, mixte)
    - search: Rechercher par nom
    """
    queryset = Commune.objects.select_related('departement__province')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['departement', 'type_commune']
    search_fields = ['nom', 'departement__nom', 'departement__province__nom']
    ordering_fields = ['nom', 'population']
    ordering = ['nom']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CommuneDetailSerializer
        return CommuneListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer par province si fourni
        province_id = self.request.query_params.get('province', None)
        if province_id:
            queryset = queryset.filter(departement__province_id=province_id)
        
        # Filtrer par code de province si fourni
        province_code = self.request.query_params.get('province_code', None)
        if province_code:
            queryset = queryset.filter(departement__province__code=province_code)
        
        # Filtrer par code de département si fourni
        dept_code = self.request.query_params.get('departement_code', None)
        if dept_code:
            queryset = queryset.filter(departement__code=dept_code)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def par_departement(self, request):
        """
        Retourne les communes regroupées par département
        GET /api/communes/par_departement/
        """
        departements = Departement.objects.prefetch_related('communes').select_related('province').all()
        data = []
        
        for dept in departements:
            data.append({
                'departement': DepartementListSerializer(dept).data,
                'communes': CommuneListSerializer(
                    dept.communes.all(), 
                    many=True
                ).data
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def recherche_avancee(self, request):
        """
        Recherche avancée de communes
        GET /api/communes/recherche_avancee/?q=<terme>
        
        Recherche dans: nom de la commune, département, province
        """
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'error': 'Paramètre "q" requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        communes = self.get_queryset().filter(
            Q(nom__icontains=query) |
            Q(departement__nom__icontains=query) |
            Q(departement__province__nom__icontains=query)
        )
        
        serializer = self.get_serializer(communes, many=True)
        return Response({
            'query': query,
            'count': communes.count(),
            'results': serializer.data
        })