from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APIClient

# from users.models import UserSubscription

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


class UserSubscriptionTestCase(TestCase):
    pass
