from django.db import models

class Caitem(models.Model):
    """Model for items based on legacy CAITEM table"""
    # Primary Key and Timestamps
    zid = models.OneToOneField('authentication.Business', models.CASCADE, db_column='zid', primary_key=True)
    ztime = models.DateTimeField(blank=True, null=True)
    zutime = models.DateTimeField(blank=True, null=True)

    # Basic Information
    xitem = models.CharField(max_length=100, verbose_name = 'Item Code')  # Item Code
    xalias = models.CharField(max_length=100, blank=True, null=True, verbose_name = 'Alias')  # Alias Name
    xitemnew = models.CharField(max_length=100, blank=True, null=True)  # New Item Code
    xitemold = models.CharField(max_length=100, blank=True, null=True)  # Old Item Code
    xdrawing = models.CharField(max_length=100, blank=True, null=True)  # Drawing Number
    xscode = models.CharField(max_length=100, blank=True, null=True)  # Short Code
    xdesc = models.CharField(max_length=250, blank=True, null=True , verbose_name = 'Description')  # Description
    xlong = models.CharField(max_length=1000, blank=True, null=True, verbose_name = 'Long Description')  # Long Description
    xlinks = models.CharField(max_length=500, blank=True, null=True)  # Related Links

    # Classifications
    xgitem = models.CharField(max_length=100, blank=True, null=True)  # Item Group
    xcitem = models.CharField(max_length=100, blank=True, null=True)  # Item Category
    xcat = models.CharField(max_length=100, blank=True, null=True)  # Category
    xpricecat = models.CharField(max_length=100, blank=True, null=True)  # Price Category
    xtaxcat = models.CharField(max_length=100, blank=True, null=True)  # Tax Category
    xduty = models.CharField(max_length=100, blank=True, null=True)  # Duty

    # Location and Organization
    xorigin = models.CharField(max_length=100, blank=True, null=True)  # Origin
    xdiv = models.CharField(max_length=100, blank=True, null=True)  # Division
    xwh = models.CharField(max_length=100, blank=True, null=True, verbose_name = 'Warehouse')  # Warehouse
    xsup = models.CharField(max_length=100, blank=True, null=True)  # Supplier

    # Item Control
    xtypeserial = models.CharField(max_length=100, blank=True, null=True)  # Serial Type
    xbatchman = models.CharField(max_length=1, blank=True, null=True)  # Batch Management
    xabc = models.CharField(max_length=100, blank=True, null=True)  # ABC Classification
    xlife = models.IntegerField(blank=True, null=True)  # Shelf Life

    # Physical Attributes
    xwtunit = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)  # Weight per Unit
    xunitwt = models.CharField(max_length=100, blank=True, null=True)  # Weight Unit
    xl = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)  # Length
    xw = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)  # Width
    xh = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)  # Height
    xunitlen = models.CharField(max_length=100, blank=True, null=True)  # Length Unit

    # Ordering Parameters
    xminordqty = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)  # Minimum Order Qty
    xminordval = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)  # Minimum Order Value
    xordmult = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)  # Order Multiple
    xyield = models.DecimalField(max_digits=18, decimal_places=10, blank=True, null=True)  # Yield Percentage

    # Lead Times
    xdtf = models.IntegerField(blank=True, null=True)  # Delivery Time Fixed
    xptf = models.IntegerField(blank=True, null=True)  # Production Time Fixed
    xleadf = models.IntegerField(blank=True, null=True)  # Lead Time Fixed
    xleadv = models.IntegerField(blank=True, null=True)  # Lead Time Variable
    xleadt = models.IntegerField(blank=True, null=True)  # Total Lead Time

    # Units and Conversions
    xunitstk = models.CharField(max_length=100, blank=True, null=True)  # Stock Unit
    xunitalt = models.CharField(max_length=100, blank=True, null=True)  # Alternate Unit
    xunitiss = models.CharField(max_length=100, blank=True, null=True)  # Issue Unit
    xunitpck = models.CharField(max_length=100, blank=True, null=True)  # Pack Unit
    xunitsta = models.CharField(max_length=100, blank=True, null=True)  # Standard Unit
    xunitpur = models.CharField(max_length=100, blank=True, null=True)  # Purchase Unit
    xunitsel = models.CharField(max_length=100, blank=True, null=True)  # Sales Unit

    # Conversion Factors
    xcfiss = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)  # Issue CF
    xcfpck = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)  # Pack CF
    xcfsta = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)  # Standard CF
    xcfpur = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)  # Purchase CF
    xcfsel = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)  # Sales CF

    # Pricing and Costs
    xstdcost = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True, verbose_name = 'Standard Cost')  # Standard Cost
    xstdprice = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True, verbose_name = 'Standard Price')  # Standard Price
    xsplprice = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)  # Special Price
    xminprice = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)  # Minimum Price
    xmargincost = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Margin Cost
    xdisc = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Discount')  # Discount
    xcomm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # Commission
    xcurcost = models.CharField(max_length=100, blank=True, null=True)  # Currency Cost
    xcurprice = models.CharField(max_length=100, blank=True, null=True)  # Currency Price

    # Additional Information
    xnote = models.CharField(max_length=1000, blank=True, null=True)  # Notes
    xexcisecat = models.CharField(max_length=100, blank=True, null=True)  # Excise Category
    xbrand = models.CharField(max_length=100, blank=True, null=True)  # Brand
    xbarcode = models.CharField(max_length=100, blank=True, null=True)  # Barcode
    xmanufacturer = models.CharField(max_length=100, blank=True, null=True)  # Manufacturer
    xwarranty = models.IntegerField(blank=True, null=True)  # Warranty Period

    # Status and Control
    xhide = models.CharField(max_length=1, blank=True, null=True)  # Hide Flag
    xstoporder = models.CharField(max_length=100, blank=True, null=True)  # Stop Order
    xdateeff = models.DateField(blank=True, null=True)  # Effective Date
    xdateexp = models.DateField(blank=True, null=True)  # Expiry Date

    # Stock Control
    xtypestk = models.CharField(max_length=100, blank=True, null=True)  # Stock Type
    xstype = models.CharField(max_length=100, blank=True, null=True)  # Storage Type
    xbinman = models.CharField(max_length=1, blank=True, null=True)  # Bin Management
    xbin = models.CharField(max_length=100, blank=True, null=True)  # Bin Location
    xloc = models.CharField(max_length=100, blank=True, null=True)  # Location

    # Email
    zemail = models.CharField(max_length=50, blank=True, null=True)  # Email From
    xemail = models.CharField(max_length=100, blank=True, null=True)  # Email To

    class Meta:
        managed = False  # Since this is a legacy table
        db_table = 'caitem'
        unique_together = (('zid', 'xitem'),)
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return f"{self.xitem} - {self.xdesc}"
