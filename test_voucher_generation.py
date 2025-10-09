#!/usr/bin/env python
"""
Test script for voucher number generation
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.inventory.utils import get_voucher_number_by_prefix, VoucherNumberGenerator

def test_grn_generation():
    """Test GRN number generation with zid = 100001"""
    
    print("=" * 60)
    print("🧪 Testing GRN Number Generation")
    print("=" * 60)
    
    prefix = "GRN-"
    zid = 100001
    
    print(f"📋 Prefix: {prefix}")
    print(f"🏢 ZID: {zid}")
    print("-" * 40)
    
    try:
        # Generate next GRN number
        next_number = get_voucher_number_by_prefix(prefix, zid)
        print(f"✅ Generated Number: {next_number}")
        
        # Show configuration details
        generator = VoucherNumberGenerator()
        config = generator.config.get_config(prefix)
        if config:
            print(f"\n📊 Configuration Details:")
            print(f"   Table: {config['table']}")
            print(f"   Column: {config['column']}")
            
        print(f"\n💡 Note: The same number is returned because we're only")
        print(f"   generating numbers, not saving them to the database.")
        print(f"   In real usage, each generated number would be saved")
        print(f"   when creating actual transactions.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")

def test_all_available_prefixes():
    """Test all available prefixes"""
    
    print("\n" + "=" * 60)
    print("🔍 Testing All Available Prefixes")
    print("=" * 60)
    
    generator = VoucherNumberGenerator()
    all_prefixes = generator.config.get_all_prefixes()
    zid = 100001
    
    print(f"🏢 Testing with ZID: {zid}")
    print(f"📝 Found {len(all_prefixes)} configured prefixes:\n")
    
    for i, prefix in enumerate(all_prefixes, 1):
        try:
            config = generator.config.get_config(prefix)
            number = get_voucher_number_by_prefix(prefix, zid)
            print(f"{i:2d}. {prefix:<6} → {number:<12} (Table: {config['table']}, Column: {config['column']})")
        except Exception as e:
            print(f"{i:2d}. {prefix:<6} → ❌ Error: {str(e)[:50]}...")

def test_different_zids():
    """Test with different ZIDs"""
    
    print("\n" + "=" * 60)
    print("🏢 Testing Different ZIDs")
    print("=" * 60)
    
    prefix = "GRN-"
    test_zids = [100001, 100002, 100003]
    
    print(f"📋 Testing prefix: {prefix}")
    print(f"🔢 Testing ZIDs: {test_zids}\n")
    
    for zid in test_zids:
        try:
            number = get_voucher_number_by_prefix(prefix, zid)
            print(f"ZID {zid}: {number}")
        except Exception as e:
            print(f"ZID {zid}: ❌ Error: {e}")

def show_usage_example():
    """Show usage example"""
    
    print("\n" + "=" * 60)
    print("📚 Usage Example in Django Views")
    print("=" * 60)
    
    example_code = '''
# In your Django view or form:
from apps.inventory.utils import get_voucher_number_by_prefix

def create_grn_view(request):
    if request.method == 'POST':
        # Get the next GRN number
        zid = request.user.zid  # or however you get the company ID
        grn_number = get_voucher_number_by_prefix("GRN-", zid)
        
        # Create your GRN record
        grn = GRN.objects.create(
            xgrnnum=grn_number,
            zid=zid,
            # ... other fields
        )
        
        return JsonResponse({'grn_number': grn_number})
'''
    
    print(example_code)

if __name__ == "__main__":
    test_grn_generation()
    test_all_available_prefixes()
    test_different_zids()
    show_usage_example()