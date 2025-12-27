from django.test import TestCase

from ingredients.models import Ingredient


class IngredientModelTest(TestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(
            name="Sugar",
            measurement_unit="grams"
        )

    def test_ingredient_creation(self):
        self.assertEqual(self.ingredient.name, "Sugar")
        self.assertEqual(self.ingredient.measurement_unit, "grams")

    def test_ingredient_str_method(self):
        self.assertEqual(str(self.ingredient), "Sugar (grams)")

    def test_id(self):
        self.assertIsNotNone(self.ingredient.id)

    def test_get_list(self):
        response = self.client.get('/api/ingredients/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sugar', str(response.content))

    def test_get_detail(self):
        response = self.client.get(f'/api/ingredients/{self.ingredient.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sugar', str(response.content))

    def test_search_ingredient(self):
        response = self.client.get('/api/ingredients/?search=Sug')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sugar', str(response.content))

    def test_unallowed_methods(self):
        response = self.client.post('/api/ingredients/', {
            'name': 'Salt',
            'measurement_unit': 'grams'
        })
        self.assertEqual(response.status_code, 405)
        response = self.client.put(f'/api/ingredients/{self.ingredient.id}/', {
            'name': 'Salt',
            'measurement_unit': 'grams'
        })
        self.assertEqual(response.status_code, 405)
        response = self.client\
            .delete(f'/api/ingredients/{self.ingredient.id}/')
        self.assertEqual(response.status_code, 405)

    def tearDown(self):
        self.ingredient.delete()
