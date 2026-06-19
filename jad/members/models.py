from django.db import models
from django.contrib.auth.models import User

class Warehouse_Info(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="warehouse"
    )
    length = models.FloatField(default=0)
    width  = models.FloatField(default=0)
    height = models.FloatField(default=0)

    class Meta:
        db_table = "Warehouse_Info"

class Box_Info(models.Model):
    warehouse = models.ForeignKey(
        Warehouse_Info,
        on_delete=models.CASCADE,
        related_name="boxes"
    )
    length = models.FloatField()
    width  = models.FloatField()
    height = models.FloatField()
    weight = models.FloatField()
    color  = models.CharField(max_length=100)

    class Meta:
        db_table = "Box_Info"
