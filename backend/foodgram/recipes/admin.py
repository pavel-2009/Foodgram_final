from django.contrib import admin

from .models import Recipe, RecipeIngredient, Favorite, ShoppingCart


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time')
    search_fields = ('name', 'author__username')
    list_filter = ('tags', 'author')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_recipes')
    search_fields = ('user__username', 'recipes__name')

    def get_recipes(self, obj):
        # возвращаем через запятую имена всех рецептов
        return ", ".join([recipe.name for recipe in obj.recipes.all()])

    # чтобы колонка имела нормальное название
    get_recipes.short_description = 'Recipes'
