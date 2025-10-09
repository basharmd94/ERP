from django.db import models

class Casup(models.Model):
    """Model for suppliers based on legacy CASUP table"""
    # Primary Key and Timestamps
    zid = models.OneToOneField('authentication.Business', models.CASCADE, db_column='zid', primary_key=True)
    ztime = models.DateTimeField(blank=True, null=True)  # Creation Time
    zutime = models.DateTimeField(blank=True, null=True)  # Update Time

    # Basic Information
    xsup = models.CharField(max_length=100)  # Supplier Code
    xshort = models.CharField(max_length=100, blank=True, null=True)  # Short Name
    xorg = models.CharField(max_length=100)  # Organization Name

    # Address Information
    xadd1 = models.CharField(max_length=100, blank=True, null=True)  # Address Line 1
    xadd2 = models.CharField(max_length=100, blank=True, null=True)  # Address Line 2
    xcity = models.CharField(max_length=100, blank=True, null=True)  # City
    xstate = models.CharField(max_length=100, blank=True, null=True)  # State
    xzip = models.CharField(max_length=100, blank=True, null=True)  # ZIP Code
    xcountry = models.CharField(max_length=100, blank=True, null=True)  # Country

    # Contact Person Details
    xsalute = models.CharField(max_length=100, blank=True, null=True)  # Salutation
    xfirst = models.CharField(max_length=100, blank=True, null=True)  # First Name
    xmiddle = models.CharField(max_length=100, blank=True, null=True)  # Middle Name
    xlast = models.CharField(max_length=100, blank=True, null=True)  # Last Name
    xtitle = models.CharField(max_length=100, blank=True, null=True)  # Title

    # Contact Information
    xemail = models.CharField(max_length=100, blank=True, null=True)  # Email
    xphone = models.CharField(max_length=40, blank=True, null=True)  # Phone
    xfax = models.CharField(max_length=100, blank=True, null=True)  # Fax
    xurl = models.CharField(max_length=100, blank=True, null=True)  # Website

    # Business Information
    xid = models.CharField(max_length=100, blank=True, null=True)  # Business ID
    xtaxnum = models.CharField(max_length=100, blank=True, null=True)  # Tax Number
    xaccap = models.CharField(max_length=100, blank=True, null=True)  # AP Account
    xaccgit = models.CharField(max_length=100, blank=True, null=True)  # GIT Account
    xgsup = models.CharField(max_length=100, blank=True, null=True)  # Supplier Group
    xgprice = models.CharField(max_length=100, blank=True, null=True)  # Price Group
    xsic = models.CharField(max_length=100, blank=True, null=True)  # SIC Code
    xtaxscope = models.CharField(max_length=100, blank=True, null=True)  # Tax Scope

    # Status and Credit
    xstatussup = models.CharField(max_length=100, blank=True, null=True)  # Supplier Status
    xcrlimit = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)  # Credit Limit
    xcrterms = models.IntegerField(blank=True, null=True)  # Credit Terms
    xdisc = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Discount

    # Commission Information
    xagent = models.CharField(max_length=100, blank=True, null=True)  # Agent
    xcomm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Commission

    # Payment and Currency
    xcur = models.CharField(max_length=100, blank=True, null=True)  # Currency
    xpayins = models.CharField(max_length=1000, blank=True, null=True)  # Payment Instructions

    # Location and Delivery
    xlocation = models.CharField(max_length=100, blank=True, null=True)  # Location
    xzonedel = models.CharField(max_length=100, blank=True, null=True)  # Delivery Zone
    xtimeslot = models.CharField(max_length=100, blank=True, null=True)  # Delivery Time Slot

    # License and Permits
    xlicense = models.CharField(max_length=100, blank=True, null=True)  # License Number
    xdateexp = models.DateField(blank=True, null=True)  # License Expiry Date
    xpermitapp = models.CharField(max_length=100, blank=True, null=True)  # Permit Application

    # Other Information
    xby = models.CharField(max_length=100, blank=True, null=True)  # Created By

    class Meta:
        managed = False  # Since this is a legacy table
        db_table = 'casup'
        unique_together = (('zid', 'xsup'), ('zid', 'xorg'))  # Composite unique keys
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return f"{self.xsup} - {self.xorg}"
