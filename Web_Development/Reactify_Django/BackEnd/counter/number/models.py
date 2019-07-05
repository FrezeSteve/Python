from django.db import models


class Counter(models.Model):
    number = models.PositiveIntegerField(default=0)

    def __str__(self): str(self.number)

