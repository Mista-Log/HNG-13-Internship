from rest_framework import serializers
from .models import AnalyzedString

class AnalyzeStringSerializer(serializers.ModelSerializer):
    value = serializers.CharField()

    class Meta:
        model = AnalyzedString
        fields = ['id', 'value', 'length', 'is_palindrome', 'unique_characters',
                  'word_count', 'sha256_hash', 'character_frequency_map', 'created_at']
        read_only_fields = ['id', 'length', 'is_palindrome', 'unique_characters',
                            'word_count', 'sha256_hash', 'character_frequency_map', 'created_at']

    def validate_value(self, v):
        if not isinstance(v, str):
            raise serializers.ValidationError("value must be a string")
        if v == "":
            raise serializers.ValidationError("value must not be empty")
        return v
