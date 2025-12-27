from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import filters

from . import serializers, models


class IngredientList(ListAPIView):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


class IngredientDetail(RetrieveAPIView):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
