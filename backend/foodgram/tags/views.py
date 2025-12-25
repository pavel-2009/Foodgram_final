from rest_framework.generics import ListAPIView, RetrieveAPIView

from . import models
from . import serializers


class TagList(ListAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class TagDetail(RetrieveAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
