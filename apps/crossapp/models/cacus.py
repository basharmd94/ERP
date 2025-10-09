from django.db import models

class Cacus(models.Model):
    """Model for customers based on legacy CACUS table"""
    # Primary Key and Timestamps
    zid = models.OneToOneField('authentication.Business', models.CASCADE, db_column='zid', primary_key=True)
    ztime = models.DateTimeField(blank=True, null=True)
    zutime = models.DateTimeField(blank=True, null=True)

    # Basic Information
    xcus = models.CharField(max_length=100)  # Customer Code
    xshort = models.CharField(max_length=100, blank=True, null=True)  # Short Name
    xorg = models.CharField(max_length=100, blank=True, null=True)  # Organization Name

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
    xmobile = models.CharField(max_length=100, blank=True, null=True)  # Mobile
    xfax = models.CharField(max_length=100, blank=True, null=True)  # Fax
    xurl = models.CharField(max_length=100, blank=True, null=True)  # Website

    # Business Information
    xid = models.CharField(max_length=100, blank=True, null=True)  # Business ID
    xtaxnum = models.CharField(max_length=100, blank=True, null=True)  # Tax Number
    xaccar = models.CharField(max_length=100, blank=True, null=True)  # AR Account
    xacctd = models.CharField(max_length=100, blank=True, null=True)  # TD Account
    xgcus = models.CharField(max_length=100, blank=True, null=True)  # Customer Group
    xgprice = models.CharField(max_length=100, blank=True, null=True)  # Price Group
    xsic = models.CharField(max_length=100, blank=True, null=True)  # SIC Code
    xtaxscope = models.CharField(max_length=100, blank=True, null=True)  # Tax Scope

    # Status and Credit
    xstatuscus = models.CharField(max_length=100, blank=True, null=True)  # Customer Status
    xcrlimit = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)  # Credit Limit
    xcreditr = models.CharField(max_length=100, blank=True, null=True)  # Credit Rating
    xcrterms = models.IntegerField(blank=True, null=True)  # Credit Terms
    xdisc = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Discount

    # Sales Information
    xagent = models.CharField(max_length=100, blank=True, null=True)  # Sales Agent
    xcomm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Commission

    # Additional Information
    xpayins = models.CharField(max_length=1000, blank=True, null=True)  # Payment Instructions
    xindustry = models.CharField(max_length=100, blank=True, null=True)  # Industry

    # Important Dates
    xdatecra = models.DateField(blank=True, null=True)  # Credit Approval Date
    xdateapp = models.DateField(blank=True, null=True)  # Approval Date
    xdateexp = models.DateField(blank=True, null=True)  # Expiry Date
    xdatecorp = models.DateField(blank=True, null=True)  # Corporation Date
    xdatecre = models.DateField(blank=True, null=True)  # Creation Date
    xdatefst = models.DateField(blank=True, null=True)  # First Transaction Date

    # Additional Addresses
    xbilladd = models.CharField(max_length=100, blank=True, null=True)  # Billing Address

    # Registration and Compliance
    xlicense = models.CharField(max_length=100, blank=True, null=True)  # License Number
    xtypebo = models.CharField(max_length=100, blank=True, null=True)  # Business Type
    xeccnum = models.CharField(max_length=100, blank=True, null=True)  # ECC Number
    xeccrange = models.CharField(max_length=100, blank=True, null=True)  # ECC Range
    xeccdiv = models.CharField(max_length=100, blank=True, null=True)  # ECC Division
    xecccom = models.CharField(max_length=100, blank=True, null=True)  # ECC Commissionerate
    xvatnum = models.CharField(max_length=100, blank=True, null=True)  # VAT Number
    xcstnum = models.CharField(max_length=100, blank=True, null=True)  # CST Number
    xpannum = models.CharField(max_length=100, blank=True, null=True)  # PAN Number
    xregoff = models.CharField(max_length=100, blank=True, null=True)  # Registered Office

    # Delivery Information
    xmethodpay = models.CharField(max_length=100, blank=True, null=True)  # Payment Method
    xmethodship = models.CharField(max_length=100, blank=True, null=True)  # Shipping Method

    # Miscellaneous
    xrem = models.CharField(max_length=500, blank=True, null=True)  # Remarks
    xpoints = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)  # Points
    xsp = models.CharField(max_length=100, blank=True, null=True)  # Sales Person
    xdate = models.DateField(blank=True, null=True)  # Date

    class Meta:
        managed = False
        db_table = 'cacus'
        unique_together = (('zid', 'xcus'),)
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.xcus} - {self.xorg or self.xshort or 'N/A'}"
