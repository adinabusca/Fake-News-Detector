from django.db import models

# Create your models here.
class SourceStats(models.Model):
    source = models.CharField(max_length=255, unique=True)
    positive = models.IntegerField(default = 0)
    neutral = models.IntegerField(default = 0)
    negative = models.IntegerField(default = 0)
    fake = models.IntegerField(default=0)
    real = models.IntegerField(default=0)

    def __str__(self):
        return self.source