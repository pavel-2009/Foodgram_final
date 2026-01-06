from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status

from tags.models import Tag
from users.models import User
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredient, Favorite, ShoppingCart


class RecipeModelTest(TestCase):

    def setUp(self):
        self.tag1 = Tag.objects.create(name='Breakfast',
                                       color='#FF5733', slug='breakfast')
        self.tag2 = Tag.objects.create(name='Lunch',
                                       color='#33FF57', slug='lunch')
        self.user = User.objects.create_user(username='testuser',
                                             password='testpass',
                                             email='testuser@example.com')
        self.author = User.objects.create_user(username='authoruser',
                                               password='authorpass',
                                               email='authoruser@example.com')
        self.ingredient1 = Ingredient.objects.create(name='Sugar',
                                                     measurement_unit='grams')
        self.ingredient2 = Ingredient.objects.create(name='Salt',
                                                     measurement_unit='grams')

        self.recipe = Recipe.objects.create(
            author=self.author,
            name='Test Recipe',
            image='iVBORw0KGgoAAAANSUhEUgAAAAUA'
                  'AAAFCAYAAACNbyblAAAAHElEQVQI12P4'
                  '//8/w38GIAXDIBKE0DHxgljNBAAO'
                  '9TXL0Y4OHwAAAABJRU5ErkJggg==',
            text='This is a test recipe.',
            cooking_time=10
        )
        self.recipe.tags.add(self.tag1, self.tag2)
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient1,
            amount=100
        )

    def test_recipe_creation(self):
        self.assertEqual(self.recipe.name, 'Test Recipe')
        self.assertEqual(self.recipe.author.username, 'authoruser')
        self.assertEqual(self.recipe.cooking_time, 10)
        self.assertIn(self.tag1, self.recipe.tags.all())
        self.assertIn(self.tag2, self.recipe.tags.all())
        recipe_ingredient = RecipeIngredient.objects.get(
            recipe=self.recipe,
            ingredient=self.ingredient1
        )
        self.assertEqual(recipe_ingredient.amount, 100)
        self.assertEqual(recipe_ingredient.ingredient.name, 'Sugar')

    def test_recipe_string_representation(self):
        self.assertEqual(str(self.recipe), 'Test Recipe')

    def test_flags_default(self):
        response = self.client.get(f'/api/recipes/{self.recipe.id}/')
        data = response.data

        self.assertFalse(data['is_favorited'])
        self.assertFalse(data['is_in_shopping_cart'])

    def test_recipeingredient_string_representation(self):
        recipe_ingredient = RecipeIngredient.objects.get(
            recipe=self.recipe,
            ingredient=self.ingredient1
        )
        expected_str = f"{self.recipe.name} - {self.ingredient1.name} (100.0)"
        self.assertEqual(str(recipe_ingredient), expected_str)

    def test_invalid_image_format(self):
        invalid_image_recipe = Recipe(
            author=self.author,
            name='Invalid Image Recipe',
            image='NotAValidBase64String',
            text='This recipe has invalid image format.',
            cooking_time=10
        )
        with self.assertRaises(Exception):
            invalid_image_recipe.clean()

    def test_cooking_time_validation(self):
        invalid_time_recipe = Recipe(
            author=self.author,
            name='Invalid Time Recipe',
            image='iVBORw0KGgoAAAANSUhEUgAAAAUA'
                  'AAAFCAYAAACNbyblAAAAHElEQVQI12P4'
                  '//8/w38GIAXDIBKE0DHxgljNBAAO'
                  '9TXL0Y4OHwAAAABJRU5ErkJggg==',
            text='This recipe has invalid cooking time.',
            cooking_time=-1
        )
        with self.assertRaises(Exception):
            invalid_time_recipe.clean()

    def test_unique_ingredient_per_recipe(self):
        with self.assertRaises(Exception):
            RecipeIngredient.objects.create(
                recipe=self.recipe,
                ingredient=self.ingredient1,
                amount=50
            )


class RecipeAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.ingredient1 = Ingredient.objects.create(name='Flour',
                                                     measurement_unit='grams')
        self.ingredient2 = Ingredient.objects.create(name='Eggs',
                                                     measurement_unit='pieces')

        self.tag1 = Tag.objects.create(name='Dinner',
                                       color='#3357FF', slug='dinner')
        self.tag2 = Tag.objects.create(name='Snack',
                                       color='#FF33A1', slug='snack')

        self.user = User.objects.create_user(username='apiuser',
                                             password='apipass',
                                             email='apiuser@example.com')
        self.author = User.objects.create_user(username='apiauthor',
                                               password='apiauthpass',
                                               email='apiauthor@example.com')

        self.user_token = Token.objects.create(user=self.user)
        self.author_token = Token.objects.create(user=self.author)

        self.recipe = Recipe.objects.create(
            author=self.author,
            name='API Test Recipe',
            image='iVBORw0KGgoAAAANSUhEUgAAAAUA'
                  'AAAFCAYAAACNbyblAAAAHElEQVQI12P4'
                  '//8/w38GIAXDIBKE0DHxgljNBAAO'
                  '9TXL0Y4OHwAAAABJRU5ErkJggg==',
            text='This is a test recipe for API.',
            cooking_time=15
        )

    def test_recipes_list_api(self):
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('API Test Recipe', str(response.content))

    def test_recipe_detail_api(self):
        response = self.client.get(f'/api/recipes/{self.recipe.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('This is a test recipe for API.', str(response.content))

    def test_create_recipe_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa
        tag = Tag.objects.create(name='Test', color='#FF5733', slug='test')

        data = {
            'name': 'New API Recipe',
            'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA'
                     'AAAFCAYAAACNbyblAAAAHElEQVQI12P4'
                     '//8/w38GIAXDIBKE0DHxgljNBAAO'
                     '9TXL0Y4OHwAAAABJRU5ErkJggg==',
            'text': 'This is a new recipe created via API.',
            'cooking_time': 20,
            'tags': [tag.id],
            'ingredients': []
        }
        response = self.client.post('/api/recipes/', data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('New API Recipe', str(response.content))

    def test_update_recipe_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.author_token.key}')  # noqa
        data = {
            'name': 'Updated API Recipe',
            'cooking_time': 25
        }
        response = self.client.patch(f'/api/recipes/{self.recipe.id}/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Updated API Recipe', str(response.content))

    def test_delete_recipe_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.author_token.key}')  # noqa
        response = self.client.delete(f'/api/recipes/{self.recipe.id}/')
        self.assertEqual(response.status_code, 204)
        get_response = self.client.get(f'/api/recipes/{self.recipe.id}/')
        self.assertEqual(get_response.status_code, 404)

    def test_create_unauthorized_recipe_api(self):
        data = {
            'author': self.author.id,
            'name': 'Unauthorized Recipe',
            'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA'
                     'AAAFCAYAAACNbyblAAAAHElEQVQI12P4'
                     '//8/w38GIAXDIBKE0DHxgljNBAAO'
                     '9TXL0Y4OHwAAAABJRU5ErkJggg==',
            'text': 'This recipe should not be created.',
            'cooking_time': 30
        }
        response = self.client.post('/api/recipes/', data)
        self.assertEqual(response.status_code, 401)

    def test_update_notautorised_recipe_api(self):
        data = {
            'name': 'Illegal Update Recipe',
            'cooking_time': 35
        }
        response = self.client.patch(f'/api/recipes/{self.recipe.id}/', data)
        self.assertEqual(response.status_code, 401)

    def test_delete_notautorised_recipe_api(self):
        response = self.client.delete(f'/api/recipes/{self.recipe.id}/')
        self.assertEqual(response.status_code, 401)

    def test_recipe_not_found_api(self):
        response = self.client.get('/api/recipes/9999/')
        self.assertEqual(response.status_code, 404)

    def test_create_recipe_invalid_data_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa
        from tags.models import Tag
        tag = Tag.objects.create(name='Test', color='#FF5733', slug='test')

        data = {
            'name': '',
            'image': 'InvalidBase64String',
            'text': 'This recipe has invalid data.',
            'cooking_time': -5,
            'tags': [tag.id],
            'ingredients': []
        }
        response = self.client.post('/api/recipes/', data)
        self.assertEqual(response.status_code, 400)

    def test_update_recipe_invalid_data_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.author_token.key}')  # noqa
        data = {
            'name': '',
            'cooking_time': -10
        }
        response = self.client.patch(f'/api/recipes/{self.recipe.id}/', data)
        self.assertEqual(response.status_code, 400)

    def test_delete_nonexistent_recipe_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.author_token.key}')  # noqa
        response = self.client.delete('/api/recipes/9999/')
        self.assertEqual(response.status_code, 404)

    def test_not_author_cannot_update_recipe_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa
        data = {
            'name': 'Attempted Unauthorized Update',
            'cooking_time': 40
        }
        response = self.client.patch(f'/api/recipes/{self.recipe.id}/', data)
        self.assertEqual(response.status_code, 403)

    def test_not_author_cannot_delete_recipe_api(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa
        response = self.client.delete(f'/api/recipes/{self.recipe.id}/')
        self.assertEqual(response.status_code, 403)

    def test_filters_on_recipes_list(self):
        tag1 = Tag.objects.create(name='Tag1', color='#FF0000', slug='tag1')
        tag2 = Tag.objects.create(name='Tag2', color='#00FF00', slug='tag2')

        ingredient1 = Ingredient.objects.create(name='Ingredient1', measurement_unit='g')  # noqa
        ingredient2 = Ingredient.objects.create(name='Ingredient2', measurement_unit='ml')  # noqa

        recipe1 = Recipe.objects.create(
            author=self.user,
            name='Recipe1',
            image='',
            text='Test recipe 1',
            cooking_time=10
        )
        recipe1.tags.add(tag1)
        recipe1.ingredients.add(ingredient1)

        recipe2 = Recipe.objects.create(
            author=self.user,
            name='Recipe2',
            image='',
            text='Test recipe 2',
            cooking_time=20
        )
        recipe2.tags.add(tag2)
        recipe2.ingredients.add(ingredient2)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa

        response = self.client.get(f'/api/recipes/?author={self.user.id}')  # noqa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        response = self.client.get('/api/recipes/?tags=tag1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Recipe1')

    def test_filters_on_recipes_list_no_results(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa
        response = self.client.get('/api/recipes/?tags=nonexistenttag')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_filters_is_favorited(self):
        Favorite.objects.create(user=self.user, recipe=self.recipe)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa
        response = self.client.get('/api/recipes/?is_favorited=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.recipe.id)

    def test_filters_is_in_shopping_cart(self):
        ShoppingCart.objects.create(user=self.user, recipe=self.recipe)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa
        response = self.client.get('/api/recipes/?is_in_shopping_cart=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.recipe.id)

    def test_create_with_tags(self):
        from tags.models import Tag
        tag1 = Tag.objects.create(name='Tag1', color='#FF0000', slug='tag1')
        tag2 = Tag.objects.create(name='Tag2', color='#00FF00', slug='tag2')

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa
        response = self.client.post('/api/recipes/', {
            'name': 'New Recipe',
            'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA'
                     'AAAFCAYAAACNbyblAAAAHElEQVQI12P4'
                     '//8/w38GIAXDIBKE0DHxgljNBAAO'
                     '9TXL0Y4OHwAAAABJRU5ErkJggg==',
            'text': 'This is a new recipe',
            'cooking_time': 15,
            'tags': [tag1.id, tag2.id],
            'ingredients': []
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['tags']), 2)
        tag_ids = [tag['id'] for tag in response.data['tags']]
        self.assertIn(tag1.id, tag_ids)
        self.assertIn(tag2.id, tag_ids)

    def test_create_with_ingredients(self):
        from ingredients.models import Ingredient
        ingredient1 = Ingredient.objects.create(name='Ingredient1', measurement_unit='g')  # noqa
        ingredient2 = Ingredient.objects.create(name='Ingredient2', measurement_unit='ml')  # noqa

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa
        response = self.client.post('/api/recipes/', {
            'name': 'New Recipe with Ingredients',
            'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA'
                     'AAAFCAYAAACNbyblAAAAHElEQVQI12P4'
                     '//8/w38GIAXDIBKE0DHxgljNBAAO'
                     '9TXL0Y4OHwAAAABJRU5ErkJggg==',
            'text': 'This is a new recipe with ingredients',
            'cooking_time': 20,
            'tags': [],
            'ingredients': [
                {'id': ingredient1.id, 'amount': 100},
                {'id': ingredient2.id, 'amount': 200}
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['ingredients']), 2)
        ingredient_ids = [ing['id'] for ing in response.data['ingredients']]
        self.assertIn(ingredient1.id, ingredient_ids)
        self.assertIn(ingredient2.id, ingredient_ids)

    def test_create_with_duplicate_ingredients(self):
        ingredient = Ingredient.objects.create(name='Ingredient', measurement_unit='g')  # noqa

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')  # noqa
        response = self.client.post('/api/recipes/', {
            'name': 'Recipe with Duplicate Ingredients',
            'image': 'iVBORw0KGgoAAAANSUhEUgAAAAUA'
                     'AAAFCAYAAACNbyblAAAAHElEQVQI12P4'
                     '//8/w38GIAXDIBKE0DHxgljNBAAO'
                     '9TXL0Y4OHwAAAABJRU5ErkJggg==',
            'text': 'This recipe has duplicate ingredients',
            'cooking_time': 25,
            'tags': [],
            'ingredients': [
                {'id': ingredient.id, 'amount': 100},
                {'id': ingredient.id, 'amount': 150}
            ]
        }, format='json')
        self.assertEqual(response.data['ingredients'][0]['id'], ingredient.id)
        self.assertEqual(response.data['ingredients'][0]['amount'], 250)
