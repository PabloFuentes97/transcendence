from django.db import models


class UserAuth(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    is_2fa_enabled = models.BooleanField(default=False)
    key_2fa= models.CharField(max_length=200, default="")
    is_from_intra = models.BooleanField(default=False)
