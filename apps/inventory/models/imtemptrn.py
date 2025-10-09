# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Imtemptrn(models.Model):
    ztime = models.DateTimeField(blank=True, null=True)
    zutime = models.DateTimeField(blank=True, null=True)
    zid = models.CharField(max_length=100)  # Business ID - part of composite key
    ximtmptrn = models.CharField(max_length=100)  # Voucher number - part of composite key
    xref = models.CharField(max_length=100, blank=True, null=True)
    xdate = models.DateField(blank=True, null=True)
    xyear = models.IntegerField(blank=True, null=True)
    xper = models.IntegerField(blank=True, null=True)
    xdatecom = models.DateField(blank=True, null=True)
    xrem = models.CharField(max_length=500, blank=True, null=True)
    xstatustor = models.CharField(max_length=100, blank=True, null=True)
    xdiv = models.CharField(max_length=100, blank=True, null=True)
    xsec = models.CharField(max_length=100, blank=True, null=True)
    xproj = models.CharField(max_length=100, blank=True, null=True)
    xwh = models.CharField(max_length=100, blank=True, null=True)
    xsign = models.IntegerField(blank=True, null=True)
    xaction = models.CharField(max_length=100, blank=True, null=True)
    zemail = models.CharField(max_length=50, blank=True, null=True)
    xemail = models.CharField(max_length=100, blank=True, null=True)
    xdept = models.CharField(max_length=100, blank=True, null=True)
    xtrnimf = models.CharField(max_length=4, blank=True, null=True)
    xtrnimt = models.CharField(max_length=4, blank=True, null=True)
    xglref = models.CharField(max_length=100, blank=True, null=True)
    xsup = models.CharField(max_length=100, blank=True, null=True)
    xcus = models.CharField(max_length=100, blank=True, null=True)
    xteam = models.CharField(max_length=100, blank=True, null=True)
    xmember = models.CharField(max_length=100, blank=True, null=True)
    xmanager = models.CharField(max_length=100, blank=True, null=True)
    xtyperec = models.CharField(max_length=100, blank=True, null=True)
    xdateinv = models.DateField(blank=True, null=True)
    xstatustrn = models.CharField(max_length=100, blank=True, null=True)
    xapprover = models.CharField(max_length=100, blank=True, null=True)
    xemail1 = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'imtemptrn'
        unique_together = (('zid', 'ximtmptrn'),)  # Composite primary key: business_id + voucher_number


    def __str__(self):
        return f"{self.ximtmptrn} - {self.xref}"
