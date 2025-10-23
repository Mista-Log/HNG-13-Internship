from django.db import models
from django.utils import timezone
import hashlib
import json

class AnalyzedString(models.Model):
    # Use sha256 hash as primary key (64 hex chars)
    id = models.CharField(max_length=64, primary_key=True, editable=False)
    # raw string value (unique to avoid duplicates)
    value = models.TextField(unique=True)
    # Stored computed properties (mirrors the other fields for convenience)
    length = models.PositiveIntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.PositiveIntegerField()
    word_count = models.PositiveIntegerField()
    sha256_hash = models.CharField(max_length=64)  # duplicate of id for clarity
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Compute SHA256
        sha = hashlib.sha256(self.value.encode('utf-8')).hexdigest()
        self.id = sha
        self.sha256_hash = sha

        # Compute length
        self.length = len(self.value)

        # Word count (split on whitespace)
        self.word_count = len(self.value.split())

        # Unique characters (case-sensitive)
        self.unique_characters = len(set(self.value))

        # Character frequency map (case-sensitive, counts each exact char)
        freq = {}
        for ch in self.value:
            freq[ch] = freq.get(ch, 0) + 1
        self.character_frequency_map = freq

        # Palindrome: case-insensitive, ignore non-alphanumeric
        import re
        cleaned = re.sub(r'[^0-9a-zA-Z]', '', self.value).lower()
        self.is_palindrome = cleaned == cleaned[::-1]

        super().save(*args, **kwargs)

    def to_representation(self):
        # convenience method for responses
        return {
            "id": self.sha256_hash,
            "value": self.value,
            "properties": {
                "length": self.length,
                "is_palindrome": self.is_palindrome,
                "unique_characters": self.unique_characters,
                "word_count": self.word_count,
                "sha256_hash": self.sha256_hash,
                "character_frequency_map": self.character_frequency_map,
            },
            "created_at": self.created_at.isoformat().replace('+00:00', 'Z') if self.created_at.tzinfo else self.created_at.isoformat() + "Z"
        }
