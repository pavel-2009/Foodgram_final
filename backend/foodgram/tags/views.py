from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import permissions

from . import models
from . import serializers


class TagList(ListAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (permissions.AllowAny,)


class TagDetail(RetrieveAPIView):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (permissions.AllowAny,)
