from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class UserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.other_user = User.objects.create_user(
            email='test2@example.com',
            username='testuser2',
            password='testpassword2',
            first_name='Test2',
            last_name='User2'
        )
        self.token = Token.objects.create(user=self.user)

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpassword'))

    def test_unique_email(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='test@example.com',
                username='anotheruser',
                password='anotherpass',
                first_name='Another',
                last_name='User'
            )

    def test_is_subscribed_default(self):
        self.assertFalse(self.user.is_subscribed)

    def test_user_str(self):
        self.assertEqual(str(self.user), 'test@example.com')

    def test_user_full_name(self):
        full_name = f"{self.user.first_name} {self.user.last_name}"
        self.assertEqual(full_name, 'Test User')

    def test_user_email_field_exists(self):
        self.assertTrue(hasattr(self.user, 'email'))

    def test_user_is_subscribed_field_exists(self):
        self.assertTrue(hasattr(self.user, 'is_subscribed'))

    def test_user_required_fields(self):
        required_fields = User.REQUIRED_FIELDS
        self.assertIn('username', required_fields)
        self.assertIn('first_name', required_fields)
        self.assertIn('last_name', required_fields)

    def test_username_field_is_email(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_user_password_change(self):
        self.user.set_password('newpassword')
        self.user.save()
        self.assertTrue(self.user.check_password('newpassword'))

    def test_unauthenticated_user_can_access_user_list(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_can_access_user_detail(self):
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_can_create_user(self):
        response = self.client.post('/api/users/', {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_user_cannot_access_me_endpoint(self):
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_change_password(self):
        response = self.client.post('/api/users/set_password/', {
            'current_password': 'testpassword',
            'new_password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_access_me_endpoint(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_authenticated_user_can_change_password(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/api/users/set_password/', {
            'current_password': 'testpassword',
            'new_password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_authenticated_user_change_password_with_wrong_password(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/api/users/set_password/', {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_user_can_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/api/auth/token/logout/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())

    def test_unauthenticated_user_can_login(self):
        response = self.client.post('/api/auth/token/login/', {
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_token', response.data)

    def test_unauthenticated_user_cannot_login_with_wrong_credentials(self):
        response = self.client.post('/api/auth/token/login/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unexisting_user(self):
        response = self.client.post('/api/auth/token/login/', {
            'email': 'nonexistent@example.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_user_cannot_logout_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        response = self.client.post('/api/auth/token/logout/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination_on_user_list(self):
        # Create additional users to test pagination
        for i in range(15):
            User.objects.create_user(
                email=f'user{i}@example.com',
                username=f'user{i}',
                password='password123',
                first_name=f'User{i}',
                last_name=f'Lastname{i}'
            )
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_user_list_pagination_page_size(self):
        for i in range(15):
            User.objects.create_user(
                email=f'user{i}@example.com',
                username=f'user{i}',
                password='password123',
                first_name=f'User{i}',
                last_name=f'Lastname{i}'
            )
        response = self.client.get('/api/users/?page_size=5')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_filters_on_recipes_list(self):
        from tags.models import Tag
        from ingredients.models import Ingredient
        from recipes.models import Recipe

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

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        response = self.client.get('/api/recipes/?author={}'.format(self.user.id))  # noqa
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = self.client.get('/api/recipes/?tags=tag1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Recipe1')

    def test_filters_on_recipes_list_no_results(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/recipes/?tags=nonexistenttag')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_with_tags(self):
        from tags.models import Tag
        tag1 = Tag.objects.create(name='Tag1', color='#FF0000', slug='tag1')
        tag2 = Tag.objects.create(name='Tag2', color='#00FF00', slug='tag2')

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/api/recipes/', {
            'name': 'New Recipe',
            'image': '',
            'text': 'This is a new recipe',
            'cooking_time': 15,
            'tags': [tag1.id, tag2.id],
            'ingredients': []
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['tags']), 2)
