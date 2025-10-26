from django.db import models
from django.utils import timezone


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=16, blank=True, null=True)
    exchange_rate = models.FloatField(blank=True, null=True)
    estimated_gdp = models.FloatField(blank=True, null=True)
    flag_url = models.URLField(blank=True, null=True)
    last_refreshed_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.name


class RefreshStatus(models.Model):
    last_refreshed_at = models.DateTimeField(null=True, blank=True)
    total_countries = models.IntegerField(default=0)


class Meta:
    # Ensure a single row
    verbose_name = "Refresh Status"
    verbose_name_plural = "Refresh Status"


    def __str__(self):
        return f"Refreshed: {self.last_refreshed_at} (total={self.total_countries})"