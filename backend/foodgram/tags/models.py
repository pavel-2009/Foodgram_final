from django.db import models


class Tag(models.Model):
    name: models.CharField = models.CharField(max_length=200)
    color: models.CharField = models.CharField(max_length=7)
    slug: models.SlugField = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def validate_color(self):
        if not self.color.startswith('#') or len(self.color) != 7:
            raise ValueError("Color must be in HEX format, e.g., #RRGGBB")
        try:
            int(self.color[1:], 16)
        except ValueError:
            raise ValueError("Color must be in HEX format, e.g., #RRGGBB")
