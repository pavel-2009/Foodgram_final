from django.db import models


class Ingredient(models.Model):
    name: models.CharField = models.CharField(max_length=200)
    measurement_unit: models.CharField = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"
