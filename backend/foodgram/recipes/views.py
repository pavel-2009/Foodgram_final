from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404

from .serializers import RecipeSerializer
from .models import Recipe, Favorite
from . import permissions as user_permissions


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ['partial_update', 'destroy', 'update']:
            self.permission_classes = [user_permissions.IsAuthorOrReadOnly]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')  # noqa
        author = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')

        queryset = Recipe.objects.all().order_by('id')

        if is_favorited is not None and user.is_authenticated:
            if is_favorited == '1':
                queryset = queryset.filter(favorited_by__user=user)
            else:
                queryset = queryset.exclude(favorited_by__user=user)

        if is_in_shopping_cart is not None and user.is_authenticated:
            if is_in_shopping_cart == '1':
                queryset = queryset.filter(in_carts__user=user)
            else:
                queryset = queryset.exclude(in_carts__user=user)

        if author:
            queryset = queryset.filter(author__id=author)

        if tags:
            queryset = queryset.filter(tags__slug__in=tags)

        return queryset.distinct()


class FavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response(RecipeSerializer(recipe).data, status=201)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=204)

class FavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response(RecipeSerializer(recipe).data, status=201)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=204)