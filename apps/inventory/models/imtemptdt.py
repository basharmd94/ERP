# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Imtemptdt(models.Model):
    """
    Model representing temporary transaction detail records.
    This is the detail table for imtemptrn (header table).
    """
    ztime = models.DateTimeField(blank=True, null=True)
    zutime = models.DateTimeField(blank=True, null=True)
    zid = models.CharField(max_length=100, primary_key=True)  # Modified to handle composite key
    ximtmptrn = models.CharField(max_length=100)
    xtorlno = models.IntegerField()
    xitem = models.CharField(max_length=100, blank=True, null=True)
    xqtyord = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    xunit = models.CharField(max_length=100, blank=True, null=True)
    ximtrnnum = models.CharField(max_length=100, blank=True, null=True)
    xdocnum = models.CharField(max_length=100, blank=True, null=True)
    xrate = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)
    xval = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    zemail = models.CharField(max_length=50, blank=True, null=True)
    xemail = models.CharField(max_length=100, blank=True, null=True)
    xbatch = models.CharField(max_length=200, blank=True, null=True)
    xbin = models.CharField(max_length=100, blank=True, null=True)
    xqtyreq = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    xdatesch = models.DateField(blank=True, null=True)
    xfrslnum = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    xtoslnum = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    xstdprice = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    xlineamt = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'imtemptdt'
        unique_together = (('zid', 'ximtmptrn', 'xtorlno'),)

    def __str__(self):
        return f"Detail {self.ximtmptrn}-{self.xtorlno}: {self.xitem}"