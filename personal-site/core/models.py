from django.db import models

# Create your models here.

class PortfolioMixin(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True