from rest_framework import serializers
import base64
from django.core.files.base import ContentFile

from tags.serializers import TagSerializer
from .models import Recipe, RecipeIngredient, Favorite, ShoppingCart
from tags.models import Tag


def validate_image(value):
    try:
        base64.b64decode(value, validate=True)
    except Exception:
        raise serializers.ValidationError('Image must be in valid base64 format.')  # noqa


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            # Handle data:image/png;base64,... format
            if data.startswith('data:image'):
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                data = base64.b64decode(imgstr)
                data = ContentFile(data, name='temp.' + ext)
            else:
                # Handle plain base64 format
                try:
                    decoded_data = base64.b64decode(data)
                    data = ContentFile(decoded_data, name='recipe_image.png')
                except Exception:
                    pass
        return super().to_internal_value(data)

    def to_representation(self, value):
        if not value:
            return None
        try:
            with value.open('rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')  # noqa
                return encoded_string
        except Exception:
            return None


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
    author = serializers.ReadOnlyField(source='author.id')
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'is_favorited', 'is_in_shopping_cart',
            'ingredients', 'name',
            'image', 'text', 'cooking_time',
        ]
        extra_kwargs = {
            'ingredients': {'required': True},
            'tags': {'required': True},
            'image': {'required': True},
            'name': {'required': True},
            'text': {'required': True},
            'cooking_time': {'required': True},
        }

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(user=user, recipes=obj).exists()

    def create(self, validated_data):
        ingredients_data = self.initial_data.get('ingredients', [])
        tags_data = validated_data.pop('tags')
        validated_data.pop('recipe_ingredients', None)
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

        recipe.full_clean()

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = self.initial_data.get('ingredients')
        validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        normal_fields = [
            f.name for f in instance._meta.get_fields()
            if not (f.many_to_many or f.one_to_many)
        ]
        for attr, value in validated_data.items():
            if attr in normal_fields:
                setattr(instance, attr, value)

        instance.full_clean()
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()

            from ingredients.models import Ingredient
            from recipes.models import RecipeIngredient

            ingredients_dict = {}
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.get('id')
                amount = ingredient_data.get('amount', 0)
                ingredients_dict[ingredient_id] = (
                    ingredients_dict.get(ingredient_id, 0) + amount
                )

            for ingredient_id, total_amount in ingredients_dict.items():
                ingredient = Ingredient.objects.get(id=ingredient_id)
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=total_amount
                )

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        return representation
