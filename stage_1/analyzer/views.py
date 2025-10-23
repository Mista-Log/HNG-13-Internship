from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from django.shortcuts import get_object_or_404
from .models import AnalyzedString
from .serializers import AnalyzeStringSerializer
from .utils import parse_nl_query, NLParseError
from django.db import IntegrityError

class CreateListStringsView(ListCreateAPIView):
    """
    POST /strings
    """
    serializer_class = AnalyzeStringSerializer
    queryset = AnalyzedString.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.data
        if 'value' not in data:
            return Response({"detail": 'Missing "value" field'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(data['value'], str):
            return Response({"detail": '"value" must be a string'}, status=422)
        value = data['value']
        import hashlib
        sha = hashlib.sha256(value.encode('utf-8')).hexdigest()
        if AnalyzedString.objects.filter(id=sha).exists():
            return Response({"detail": "String already exists"}, status=status.HTTP_409_CONFLICT)
        # post
        instance = AnalyzedString(value=value)
        try:
            instance.save()
        except IntegrityError:
            # possible race or unique constraint violation
            return Response({"detail": "String already exists"}, status=status.HTTP_409_CONFLICT)

        return Response(instance.to_representation(), status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        # apply query params
        is_pal = request.query_params.get('is_palindrome')
        min_length = request.query_params.get('min_length')
        max_length = request.query_params.get('max_length')
        word_count = request.query_params.get('word_count')
        contains_character = request.query_params.get('contains_character')

        filters_applied = {}

        if is_pal is not None:
            if is_pal.lower() not in ('true', 'false'):
                return Response({"detail": "is_palindrome must be true or false"}, status=400)
            filters_applied['is_palindrome'] = is_pal.lower() == 'true'
            qs = qs.filter(is_palindrome=filters_applied['is_palindrome'])

        if min_length is not None:
            try:
                ml = int(min_length)
            except ValueError:
                return Response({"detail": "min_length must be integer"}, status=400)
            filters_applied['min_length'] = ml
            qs = qs.filter(length__gte=ml)

        if max_length is not None:
            try:
                mx = int(max_length)
            except ValueError:
                return Response({"detail": "max_length must be integer"}, status=400)
            filters_applied['max_length'] = mx
            qs = qs.filter(length__lte=mx)

        if word_count is not None:
            try:
                wc = int(word_count)
            except ValueError:
                return Response({"detail": "word_count must be integer"}, status=400)
            filters_applied['word_count'] = wc
            qs = qs.filter(word_count=wc)

        if contains_character is not None:
            if len(contains_character) != 1:
                return Response({"detail": "contains_character must be a single character"}, status=400)
            filters_applied['contains_character'] = contains_character
            qs = qs.filter(character_frequency_map__has_key=contains_character)  # Postgres JSONField helper
            # If not Postgres, fallback:
            # qs = qs.filter(character_frequency_map__contains={contains_character: 1})  # approximate

        data = [o.to_representation() for o in qs]
        return Response({
            "data": data,
            "count": len(data),
            "filters_applied": filters_applied
        }, status=200)

class RetrieveDeleteStringView(RetrieveDestroyAPIView):
    """
    GET /strings/{string_value}
    """
    serializer_class = AnalyzeStringSerializer
    queryset = AnalyzedString.objects.all()
    lookup_field = 'value'
    lookup_url_kwarg = 'string_value'

    def retrieve(self, request, *args, **kwargs):
        # lookup by raw value (URL-encoded in client)
        value = kwargs.get(self.lookup_url_kwarg)
        if value is None:
            return Response({"detail": "string_value missing in URL"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = get_object_or_404(AnalyzedString, value=value)
        except Exception:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(obj.to_representation(), status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        value = kwargs.get(self.lookup_url_kwarg)
        obj = AnalyzedString.objects.filter(value=value).first()
        if not obj:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class DeleteStringView(generics.DestroyAPIView):
#     """
#     DELETE /strings/{string_value}
#     """
#     queryset = AnalyzedString.objects.all()
#     lookup_field = 'value'
#     lookup_url_kwarg = 'string_value'
    

#     def delete(self, request, *args, **kwargs):
#         print("hello")
#         value = kwargs.get(self.lookup_url_kwarg)
#         obj = AnalyzedString.objects.filter(value=value).first()
#         if not obj:
#             return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
#         obj.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class ListStringsView(generics.ListAPIView):
#     """
#     GET /strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a
#     """
#     serializer_class = AnalyzeStringSerializer
#     queryset = AnalyzedString.objects.all()

#     def get(self, request, *args, **kwargs):
#         qs = self.filter_queryset(self.get_queryset())

#         # apply query params
#         is_pal = request.query_params.get('is_palindrome')
#         min_length = request.query_params.get('min_length')
#         max_length = request.query_params.get('max_length')
#         word_count = request.query_params.get('word_count')
#         contains_character = request.query_params.get('contains_character')

#         filters_applied = {}

#         if is_pal is not None:
#             if is_pal.lower() not in ('true', 'false'):
#                 return Response({"detail": "is_palindrome must be true or false"}, status=400)
#             filters_applied['is_palindrome'] = is_pal.lower() == 'true'
#             qs = qs.filter(is_palindrome=filters_applied['is_palindrome'])

#         if min_length is not None:
#             try:
#                 ml = int(min_length)
#             except ValueError:
#                 return Response({"detail": "min_length must be integer"}, status=400)
#             filters_applied['min_length'] = ml
#             qs = qs.filter(length__gte=ml)

#         if max_length is not None:
#             try:
#                 mx = int(max_length)
#             except ValueError:
#                 return Response({"detail": "max_length must be integer"}, status=400)
#             filters_applied['max_length'] = mx
#             qs = qs.filter(length__lte=mx)

#         if word_count is not None:
#             try:
#                 wc = int(word_count)
#             except ValueError:
#                 return Response({"detail": "word_count must be integer"}, status=400)
#             filters_applied['word_count'] = wc
#             qs = qs.filter(word_count=wc)

#         if contains_character is not None:
#             if len(contains_character) != 1:
#                 return Response({"detail": "contains_character must be a single character"}, status=400)
#             filters_applied['contains_character'] = contains_character
#             qs = qs.filter(character_frequency_map__has_key=contains_character)  # Postgres JSONField helper
#             # If not Postgres, fallback:
#             # qs = qs.filter(character_frequency_map__contains={contains_character: 1})  # approximate

#         data = [o.to_representation() for o in qs]
#         return Response({
#             "data": data,
#             "count": len(data),
#             "filters_applied": filters_applied
#         }, status=200)

class NaturalLanguageFilterView(APIView):
    """
    GET /strings/filter-by-natural-language?query=...
    """
    def get(self, request, *args, **kwargs):
        q = request.query_params.get('query')
        if not q:
            return Response({"detail": "query parameter is required"}, status=400)
        try:
            parsed = parse_nl_query(q)
        except NLParseError as e:
            return Response({"detail": str(e)}, status=400)
        parsed_filters = parsed['parsed_filters']

        # convert parsed_filters to DB filters
        qs = AnalyzedString.objects.all()
        # simple conflict detection: e.g., parsed has min_length > max_length if both present
        if 'min_length' in parsed_filters and 'max_length' in parsed_filters:
            if parsed_filters['min_length'] > parsed_filters['max_length']:
                return Response({"detail": "Conflicting filters in parsed query"}, status=422)

        if parsed_filters.get('is_palindrome') is True:
            qs = qs.filter(is_palindrome=True)
        if parsed_filters.get('word_count') is not None:
            qs = qs.filter(word_count=parsed_filters['word_count'])
        if parsed_filters.get('min_length') is not None:
            qs = qs.filter(length__gte=parsed_filters['min_length'])
        if parsed_filters.get('max_length') is not None:
            qs = qs.filter(length__lte=parsed_filters['max_length'])
        if parsed_filters.get('contains_character') is not None:
            ch = parsed_filters['contains_character']
            if len(ch) != 1:
                return Response({"detail": "parsed contains_character not single char"}, status=422)
            qs = qs.filter(character_frequency_map__has_key=ch)

        data = [o.to_representation() for o in qs]
        return Response({
            "data": data,
            "count": len(data),
            "interpreted_query": parsed
        }, status=200)
