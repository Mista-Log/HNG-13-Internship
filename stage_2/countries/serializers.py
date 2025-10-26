from rest_framework import serializers
from .models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
        'id','name','capital','region','population',
        'currency_code','exchange_rate','estimated_gdp','flag_url','last_refreshed_at'
        ]


    def validate(self, data):
        # name, population, currency_code required per task
        # but allow currency_code to be null when countries API doesn't provide it.
        if self.instance is None:
            # on create through API (not refresh), ensure required fields
            if 'name' not in data or not data.get('name'):
                raise serializers.ValidationError({'name': 'is required'})
            if 'population' not in data or data.get('population') is None:
                raise serializers.ValidationError({'population': 'is required'})
            if 'currency_code' not in data or data.get('currency_code') is None:
                raise serializers.ValidationError({'currency_code': 'is required'})
        return data