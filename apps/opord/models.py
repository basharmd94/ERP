from django.db import models

class Opord(models.Model):
    xordernum = models.CharField(max_length=20, primary_key=True)
    xdate = models.DateField(null=True, blank=True)
    xcus = models.CharField(max_length=50, null=True, blank=True)
    xstatusord = models.CharField(max_length=20, null=True, blank=True)
    xdisc = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    xdtwotax = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    xsltype = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'opord'  # Keep the table name to match your existing table
        managed = False  # Still don't want Django to manage this table

    def __str__(self):
        return self.xordernum
