from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse

from .serializers import RecipeSerializer
from .models import Recipe, Favorite, ShoppingCart
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
                queryset = queryset.filter(in_shopping_carts__user=user)
            else:
                queryset = queryset.exclude(in_shopping_carts__user=user)

        if author:
            queryset = queryset.filter(author__id=author)

        if tags:
            queryset = queryset.filter(tags__slug__in=tags)

        return queryset.distinct()

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])  # noqa
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            Favorite.objects.get_or_create(user=user, recipe=recipe)
            return Response({
                'id': recipe.id,
                'name': recipe.name,
                'image': recipe.image,
                'cooking_time': recipe.cooking_time
            }, status=201)

        elif request.method == 'DELETE':
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=204)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])  # noqa
    def download_shopping_cart(self, request):
        shopping_cart_items = request.user.shopping_cart.recipes.all()
        ingredient_totals = {}

        for recipe in shopping_cart_items:
            for ri in recipe.recipe_ingredients.all():
                ingredient = ri.ingredient
                if ingredient.name in ingredient_totals:
                    ingredient_totals[ingredient.name]['amount'] += ri.amount
                else:
                    ingredient_totals[ingredient.name] = {
                        'measurement_unit': ingredient.measurement_unit,
                        'amount': ri.amount
                    }

        lines = ["Shopping List:\n"]
        for name, details in ingredient_totals.items():
            lines.append(f"- {name} ({details['measurement_unit']}): {details['amount']}\n")  # noqa

        content = ''.join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'  # noqa
        return response

    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])  # noqa
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        cart, created = ShoppingCart.objects.get_or_create(user=user)

        user_recipes = cart.recipes.all()

        if request.method == 'POST':
            if recipe in user_recipes:
                return Response({
                    'errors': 'Recipe is already in the shopping cart.'
                }, status=400)

            user.shopping_cart.recipes.add(recipe)
            return Response({
                'id': recipe.id,
                'name': recipe.name,
                'image': recipe.image,
                'cooking_time': recipe.cooking_time
            }, status=201)

        elif request.method == 'DELETE':
            if recipe not in user_recipes:
                return Response({
                    'errors': 'Recipe is not in the shopping cart.'
                }, status=400)

            user.shopping_cart.recipes.remove(recipe)
            return Response(status=204)
