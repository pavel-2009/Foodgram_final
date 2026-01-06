from django.db import models
from django.core.exceptions import ValidationError

import base64

from users.models import User
from tags.models import Tag
from ingredients.models import Ingredient


class Recipe(models.Model):
    tags: models.ManyToManyField = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredients: models.ManyToManyField = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
    )
    name: models.CharField = models.CharField(max_length=200)
    image: models.CharField = models.CharField()
    text: models.TextField = models.TextField()
    cooking_time: models.PositiveIntegerField = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def clean(self):
        if self.cooking_time < 1:
            raise ValidationError('Cooking time must be a positive integer.')
        try:
            base64.b64decode(self.image, validate=True)
        except Exception:
            raise ValidationError('Image must be in valid base64 format.')
        return super().clean()


class RecipeIngredient(models.Model):
    recipe: models.ForeignKey = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient: models.ForeignKey = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount: models.FloatField = models.FloatField(default=1.0)

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name} ({self.amount})"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )

    class Meta:
        unique_together = ('user', 'recipe')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts'
    )

    class Meta:
        unique_together = ('user', 'recipe')
