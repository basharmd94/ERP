from django.db import models

class Xcodes(models.Model):
    """Model for common codes based on legacy XCODES table"""
    # Primary Key and Timestamps
    zid = models.IntegerField(db_column='zid', primary_key=True)
    ztime = models.DateTimeField(blank=True, null=True)  # Creation Time
    zutime = models.DateTimeField(blank=True, null=True)  # Update Time

    # Code Information
    xtype = models.CharField(max_length=100, verbose_name='Code Type')
    xcode = models.CharField(max_length=100, verbose_name='Code Value')
    xdescdet = models.CharField(max_length=250, blank=True, null=True, verbose_name='Description')
    xprops = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Properties/Parameters')
    xcodealt = models.CharField(max_length=100, blank=True, null=True, verbose_name='Alternative Code')

    # Additional Information
    xteam = models.CharField(max_length=100, blank=True, null=True, verbose_name='Team')
    zactive = models.CharField(max_length=1, blank=True, null=True, verbose_name='Active Status')

    class Meta:
        managed = False  # Since this is a legacy table
        db_table = 'xcodes'
        unique_together = (('zid', 'xtype', 'xcode'),)  # Composite unique key
        verbose_name = 'Common Code'
        verbose_name_plural = 'Common Codes'

    def __str__(self):
        return f"[{self.xtype}] {self.xcode} - {self.xdescdet or 'N/A'}"
