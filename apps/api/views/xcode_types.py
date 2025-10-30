"""
XCode Types Configuration
Defines all valid xcode types and their mappings for the generic xcode API
"""

# Define valid xtype mappings for security and validation
# Key: URL parameter (lowercase, hyphenated)
# Value: Database xtype value (exact match from xcodes table)
VALID_XTYPES = {
    'abc-code': 'ABC Code',
    'area': 'Area',
    'bank': 'Bank',
    'bank-branch-name': 'Bank Branch Name',
    'bank1': 'Bank1',
    'benefit-payable': 'Benefit Payable',
    'blood-group1': 'Blood Group1',
    'brand': 'Brand',
    'brands': 'Brand',  # Alias for backward compatibility
    'color': 'Color',
    'cost-center': 'Cost Center',
    'cost-center1': 'Cost Center1',
    'country': 'Country',
    'course1': 'Course1',
    'customer-group': 'Customer Group',
    'customer-order-title': 'Customer Order Title',
    'delivery-order-title': 'Delivery Order Title',
    'department1': 'Department1',
    'design': 'Design',
    'designation1': 'Designation1',
    'discipline1': 'Discipline1',
    'division': 'Division',
    'division1': 'Division1',
    'employee-category1': 'Employee Category1',
    'employee-grade1': 'Employee Grade1',
    'employee-group': 'Employee Group',
    'fa-location': 'FA Location',
    'fa-type': 'FA Type',
    'grade': 'Grade',
    'grade1': 'Grade1',
    'grading-key': 'Grading Key',
    'grn-cost': 'GRN Cost',
    'hs-code': 'HS Code',
    'import-costing': 'Import Costing',
    'insurance-company': 'Insurance Company',
    'item-category': 'Item Category',
    'item-class': 'Item Class',
    'item-group': 'Item Group',
    'job-factor': 'Job Factor',
    'job-weight1': 'Job Weight1',
    'jobstatus': 'JobStatus',
    'leave-type': 'Leave Type',
    'location-type': 'Location Type',
    'location1': 'Location1',
    'manufacturer': 'Manufacturer',
    'manufacturing-shifting': 'Manufacturing Shifting',
    'material': 'Material',
    'measurement-1': 'Measurement-1',
    'measurement-2': 'Measurement-2',
    'measurement-3': 'Measurement-3',
    'measurement-unit': 'Measurement Unit',
    'measurement-unit-1': 'Measurement Unit-1',
    'measurement-unit-2': 'Measurement Unit-2',
    'measurement-unit-1-alt': 'Measurement Unit 1',
    'measurement-unit-2-alt': 'Measurement Unit 2',
    'measurement-unit-3-alt': 'Measurement Unit 3',
    'medical-condition': 'Medical Condition',
    'membership-type1': 'Membership Type1',
    'payment-code': 'Payment Code',
    'price-category': 'Price Category',
    'price-group': 'Price Group',
    'project': 'Project',
    'region': 'Region',
    'relationship1': 'Relationship1',
    'religion1': 'Religion1',
    'sales-returns-title': 'Sales Returns Title',
    'sales-type': 'Sales Type',
    'salesperson': 'Salesperson',
    'section': 'Section',
    'section1': 'Section1',
    'shift': 'Shift',
    'supplier-group': 'Supplier Group',
    'supplier-status': 'Supplier Status',
    'tax-category': 'Tax Category',
    'tax-code': 'Tax Code',
    'tax-scope': 'Tax Scope',
    'territory': 'Territory',
    'training-type1': 'Training Type1',
    'unit-number': 'Unit Number',
    'unit-of-measure': 'Unit of Measure',
    'units': 'Unit of Measure',  # Alias for backward compatibility
    'warehouse': 'Warehouse',
    'weight-unit': 'Weight Unit',
    'welfare1': 'Welfare1',
    'xrandom': 'xrandom'
}

def get_valid_xtypes():
    """
    Get list of all valid xtype keys
    """
    return list(VALID_XTYPES.keys())

def get_db_xtype(xtype):
    """
    Get database xtype value for a given URL parameter

    Args:
        xtype (str): URL parameter xtype

    Returns:
        str: Database xtype value or None if invalid
    """
    return VALID_XTYPES.get(xtype)

def is_valid_xtype(xtype):
    """
    Check if xtype is valid

    Args:
        xtype (str): URL parameter xtype

    Returns:
        bool: True if valid, False otherwise
    """
    return xtype in VALID_XTYPES
