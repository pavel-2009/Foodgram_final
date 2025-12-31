from rest_framework import serializers

from users.serializers import UserSerializer
from tags.serializers import TagSerializer
from .models import Recipe, RecipeIngredient
from tags.models import Tag


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'is_favorited', 'is_in_shopping_cart',
            'ingredients', 'name',
            'image', 'text', 'cooking_time',
        ]
        required_fields = ['ingredients', 'tags', 'image', 'name', 'text', 'cooking_time']  # noqa

    def create(self, validated_data):
        ingredients_data = self.initial_data.get('ingredients', [])
        tags_data = validated_data.pop('tags')
        author = self.context['request'].user
        validated_data['author'] = author
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        from ingredients.models import Ingredient

        ingredients_dict = {}
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount', 0)

            if ingredient_id in ingredients_dict:
                ingredients_dict[ingredient_id] += amount
            else:
                ingredients_dict[ingredient_id] = amount

        for ingredient_id, total_amount in ingredients_dict.items():
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=total_amount
            )

        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        return representation
