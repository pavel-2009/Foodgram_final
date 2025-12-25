from rest_framework import serializers

from . import models


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['*']
