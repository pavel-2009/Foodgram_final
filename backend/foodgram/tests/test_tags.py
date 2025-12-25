from django.test import TestCase

from tags.models import Tag


class TagModelTest(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(
            id=1,
            name='Vegan',
            color='#00FF00',
            slug='vegan'
        )
        self.invalid_tag = Tag(
            id=2,
            name='InvalidColor',
            color='00FF00',
            slug='sss'
        )

    def test_tag_creation(self):
        self.assertEqual(self.tag.name, 'Vegan')
        self.assertEqual(self.tag.color, '#00FF00')
        self.assertEqual(self.tag.slug, 'vegan')

    def test_tag_str_method(self):
        self.assertEqual(str(self.tag), 'Vegan')

    def test_validate_color_valid(self):
        try:
            self.tag.validate_color()
        except ValueError:
            self.fail("validate_color() raised ValueError unexpectedly!")

    def test_validate_color_invalid(self):
        with self.assertRaises(ValueError):
            self.invalid_tag.validate_color()

    def test_invalid_color_not_hex(self):
        self.invalid_tag.color = '#GGHHII'
        with self.assertRaises(ValueError):
            self.invalid_tag.validate_color()

    def test_id(self):
        self.assertEqual(self.tag.id, 1)
        self.assertEqual(self.invalid_tag.id, 2)

    def test_post(self):
        response = self.client.post('/api/tags/', {
            'name': 'Dessert',
            'color': '#FF00FF',
            'slug': 'dessert'
        })
        self.assertEqual(response.status_code, 405)

    def test_get_tag_list(self):
        response = self.client.get('/api/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Vegan', str(response.content))

    def test_get_tag_detail(self):
        response = self.client.get(f'/api/tags/{self.tag.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Vegan', str(response.content))

    def test_put_tag(self):
        response = self.client.put(f'/api/tags/{self.tag.id}/', {
            'name': 'UpdatedVegan',
            'color': '#00FF00',
            'slug': 'updated-vegan'
        })
        self.assertEqual(response.status_code, 405)

    def test_delete_tag(self):
        response = self.client.delete(f'/api/tags/{self.tag.id}/')
        self.assertEqual(response.status_code, 405)

    def tearDown(self):
        self.tag.delete()
        self.invalid_tag.delete()
