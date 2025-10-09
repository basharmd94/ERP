# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Casup(models.Model):
    ztime = models.DateTimeField(blank=True, null=True)
    zutime = models.DateTimeField(blank=True, null=True)
    zid = models.OneToOneField('Zbusiness', models.DO_NOTHING, db_column='zid', primary_key=True)  # The composite primary key (zid, xsup) found, that is not supported. The first column is selected.
    xsup = models.CharField(max_length=100)
    xshort = models.CharField(max_length=100, blank=True, null=True)
    xorg = models.CharField(max_length=100)
    xadd1 = models.CharField(max_length=100, blank=True, null=True)
    xadd2 = models.CharField(max_length=100, blank=True, null=True)
    xcity = models.CharField(max_length=100, blank=True, null=True)
    xstate = models.CharField(max_length=100, blank=True, null=True)
    xzip = models.CharField(max_length=100, blank=True, null=True)
    xcountry = models.CharField(max_length=100, blank=True, null=True)
    xsalute = models.CharField(max_length=100, blank=True, null=True)
    xfirst = models.CharField(max_length=100, blank=True, null=True)
    xmiddle = models.CharField(max_length=100, blank=True, null=True)
    xlast = models.CharField(max_length=100, blank=True, null=True)
    xtitle = models.CharField(max_length=100, blank=True, null=True)
    xemail = models.CharField(max_length=100, blank=True, null=True)
    xphone = models.CharField(max_length=40, blank=True, null=True)
    xfax = models.CharField(max_length=100, blank=True, null=True)
    xurl = models.CharField(max_length=100, blank=True, null=True)
    xid = models.CharField(max_length=100, blank=True, null=True)
    xtaxnum = models.CharField(max_length=100, blank=True, null=True)
    xaccap = models.CharField(max_length=100, blank=True, null=True)
    xaccgit = models.CharField(max_length=100, blank=True, null=True)
    xgsup = models.CharField(max_length=100, blank=True, null=True)
    xgprice = models.CharField(max_length=100, blank=True, null=True)
    xsic = models.CharField(max_length=100, blank=True, null=True)
    xtaxscope = models.CharField(max_length=100, blank=True, null=True)
    xstatussup = models.CharField(max_length=100, blank=True, null=True)
    xcrlimit = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    xcrterms = models.IntegerField(blank=True, null=True)
    xdisc = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    xagent = models.CharField(max_length=100, blank=True, null=True)
    xcomm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    xcur = models.CharField(max_length=100, blank=True, null=True)
    xpayins = models.CharField(max_length=1000, blank=True, null=True)
    xlocation = models.CharField(max_length=100, blank=True, null=True)
    xlicense = models.CharField(max_length=100, blank=True, null=True)
    xdateexp = models.DateField(blank=True, null=True)
    xpermitapp = models.CharField(max_length=100, blank=True, null=True)
    xby = models.CharField(max_length=100, blank=True, null=True)
    xzonedel = models.CharField(max_length=100, blank=True, null=True)
    xtimeslot = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'casup'
        unique_together = (('zid', 'xsup'), ('zid', 'xorg'),)
