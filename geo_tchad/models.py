"""
Modèles pour l'API Géographique du Tchad
Organisation administrative selon l'Ordonnance N°0037/PR/2018
"""

from django.db import models
from django.core.validators import MinLengthValidator


class Province(models.Model):
    """
    Représente une province du Tchad (23 provinces)
    """
    code = models.CharField(
        max_length=2,
        unique=True,
        validators=[MinLengthValidator(2)],
        help_text="Code à 2 chiffres de la province (ex: '01', '02')"
    )
    nom = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Nom de la province"
    )
    chef_lieu = models.CharField(
        max_length=100,
        help_text="Chef-lieu de la province"
    )
    
    # Métadonnées géographiques optionnelles
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Latitude du chef-lieu"
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Longitude du chef-lieu"
    )
    superficie = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Superficie en km²"
    )
    population = models.IntegerField(
        null=True,
        blank=True,
        help_text="Population estimée"
    )
    
    # Métadonnées de gestion
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'provinces'
        ordering = ['code']
        verbose_name = 'Province'
        verbose_name_plural = 'Provinces'
    
    def __str__(self):
        return f"{self.code} - {self.nom}"
    
    @property
    def nombre_departements(self):
        """Retourne le nombre de départements dans cette province"""
        return self.departements.count()
    
    @property
    def nombre_communes(self):
        """Retourne le nombre total de communes dans cette province"""
        return sum(dept.communes.count() for dept in self.departements.all())


class Departement(models.Model):
    """
    Représente un département du Tchad (95 départements)
    """
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name='departements',
        help_text="Province parente"
    )
    code = models.CharField(
        max_length=2,
        validators=[MinLengthValidator(2)],
        help_text="Code à 2 chiffres du département (ex: '01', '02')"
    )
    nom = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Nom du département"
    )
    chef_lieu = models.CharField(
        max_length=100,
        help_text="Chef-lieu du département"
    )
    
    # Métadonnées géographiques optionnelles
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Latitude du chef-lieu"
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Longitude du chef-lieu"
    )
    superficie = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Superficie en km²"
    )
    population = models.IntegerField(
        null=True,
        blank=True,
        help_text="Population estimée"
    )
    
    # Métadonnées de gestion
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departements'
        ordering = ['province__code', 'code']
        verbose_name = 'Département'
        verbose_name_plural = 'Départements'
        unique_together = [['province', 'code']]
        indexes = [
            models.Index(fields=['province', 'code']),
            models.Index(fields=['nom']),
        ]
    
    def __str__(self):
        return f"{self.province.code}-{self.code} - {self.nom}"
    
    @property
    def code_complet(self):
        """Retourne le code complet province-département"""
        return f"{self.province.code}-{self.code}"
    
    @property
    def nombre_communes(self):
        """Retourne le nombre de communes dans ce département"""
        return self.communes.count()


class Commune(models.Model):
    """
    Représente une commune du Tchad (365 communes)
    """
    departement = models.ForeignKey(
        Departement,
        on_delete=models.CASCADE,
        related_name='communes',
        help_text="Département parent"
    )
    nom = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Nom de la commune"
    )
    
    # Métadonnées géographiques optionnelles
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Latitude"
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Longitude"
    )
    superficie = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Superficie en km²"
    )
    population = models.IntegerField(
        null=True,
        blank=True,
        help_text="Population estimée"
    )
    
    # Type de commune (urbaine, rurale, etc.)
    TYPE_CHOICES = [
        ('urbaine', 'Urbaine'),
        ('rurale', 'Rurale'),
        ('mixte', 'Mixte'),
    ]
    type_commune = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='rurale',
        help_text="Type de commune"
    )
    
    # Métadonnées de gestion
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'communes'
        ordering = ['departement__province__code', 'departement__code', 'nom']
        verbose_name = 'Commune'
        verbose_name_plural = 'Communes'
        indexes = [
            models.Index(fields=['departement', 'nom']),
            models.Index(fields=['nom']),
        ]
    
    def __str__(self):
        return self.nom
    
    @property
    def province(self):
        """Retourne la province de la commune"""
        return self.departement.province
    
    @property
    def code_complet(self):
        """Retourne le code complet province-département-commune"""
        return f"{self.departement.province.code}-{self.departement.code}-{self.nom}"