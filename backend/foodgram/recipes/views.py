from rest_framework import viewsets
from rest_framework import permissions

from .serializers import RecipeSerializer
from .models import Recipe
from . import permissions as user_permissions


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ['patch', 'delete', 'update']:
            self.permission_classes = [user_permissions.IsAuthorOrReadOnly]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')  # noqa
        author = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')

        queryset = Recipe.objects.all()

        if is_favorited:
            queryset = queryset.filter(is_favorited=(True if is_favorited == '1' else False))  # noqa
        if is_in_shopping_cart:
            queryset = queryset.filter(is_in_shopping_cart=(True if is_in_shopping_cart == '1' else False))  # noqa
        if author:
            queryset = queryset.filter(author__id=author)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)

        return queryset.distinct()
