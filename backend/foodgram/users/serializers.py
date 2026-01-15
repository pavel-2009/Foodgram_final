from rest_framework import serializers
from django.contrib.auth import get_user_model
import base64

User = get_user_model()


def image_to_base64(image_field):
    """Convert image field to base64 string."""
    if not image_field:
        return None
    try:
        with image_field.open('rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception:
        return None


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscribed_users.filter(user=request.user).exists()
        return False


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed',  # noqa
                  'recipes_count', 'recipes')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscribed_users.filter(user=request.user).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit is not None and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return [{
            'id': recipe.id,
            'name': recipe.name,
            'image': image_to_base64(recipe.image),
            'cooking_time': recipe.cooking_time
        } for recipe in recipes]
