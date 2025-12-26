from django.db import models


class Tag(models.Model):
    name: str = models.CharField()
    color: str = models.CharField()
    slug: str = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def validate_color(self):
        if not self.color.startswith('#') or len(self.color) != 7:
            raise ValueError("Color must be in HEX format, e.g., #RRGGBB")
        try:
            int(self.color[1:], 16)
        except ValueError:
            raise ValueError("Color must be in HEX format, e.g., #RRGGBB")
