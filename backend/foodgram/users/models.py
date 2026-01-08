from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email: models.EmailField = models.EmailField(unique=True)
    is_subscribed: models.BooleanField = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class UserSubscription(models.Model):
    user: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscriptions: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_users'
    )

    class Meta:
        unique_together = ('user', 'subscriptions')
