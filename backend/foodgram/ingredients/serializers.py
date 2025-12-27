from rest_framework import serializers

from . import models


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['*']
