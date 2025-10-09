# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Imtrn(models.Model):
    ztime = models.DateTimeField(blank=True, null=True)
    zutime = models.DateTimeField(blank=True, null=True)
    zid = models.IntegerField('ZID', db_column='zid', primary_key=True)  # The composite primary key (zid, ximtrnnum) found, that is not supported. The first column is selected.
    ximtrnnum = models.CharField(max_length=100)
    xitem = models.CharField(max_length=100, blank=True, null=True)
    xitemrow = models.CharField(max_length=100, blank=True, null=True)
    xitemcol = models.CharField(max_length=100, blank=True, null=True)
    xwh = models.CharField(max_length=100, blank=True, null=True)
    xdate = models.DateField(blank=True, null=True)
    xyear = models.IntegerField(blank=True, null=True)
    xper = models.IntegerField(blank=True, null=True)
    xqty = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    xval = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    xvalpost = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    xdoctype = models.CharField(max_length=100, blank=True, null=True)
    xdocnum = models.CharField(max_length=100, blank=True, null=True)
    xdocrow = models.IntegerField(blank=True, null=True)
    xnote = models.CharField(max_length=1000, blank=True, null=True)
    xaltqty = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    xdiv = models.CharField(max_length=100, blank=True, null=True)
    xsec = models.CharField(max_length=100, blank=True, null=True)
    xproj = models.CharField(max_length=100, blank=True, null=True)
    xbatch = models.CharField(max_length=200, blank=True, null=True)
    xdateexp = models.DateField(blank=True, null=True)
    xdaterec = models.DateField(blank=True, null=True)
    xlicense = models.CharField(max_length=100, blank=True, null=True)
    xcus = models.CharField(max_length=100, blank=True, null=True)
    xsup = models.CharField(max_length=100, blank=True, null=True)
    xaction = models.CharField(max_length=100, blank=True, null=True)
    xsign = models.IntegerField(blank=True, null=True)
    xtime = models.DateTimeField(blank=True, null=True)
    zemail = models.CharField(max_length=50, blank=True, null=True)
    xemail = models.CharField(max_length=100, blank=True, null=True)
    xtrnim = models.CharField(max_length=4, blank=True, null=True)
    xfrslnum = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    xtoslnum = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    xrectrn = models.CharField(max_length=100, blank=True, null=True)
    xbin = models.CharField(max_length=100, blank=True, null=True)
    xteam = models.CharField(max_length=100, blank=True, null=True)
    xmember = models.CharField(max_length=100, blank=True, null=True)
    xmanager = models.CharField(max_length=100, blank=True, null=True)
    xdept = models.CharField(max_length=100, blank=True, null=True)
    xstdprice = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'imtrn'
        unique_together = (('zid', 'ximtrnnum'),)
