#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def test_zid_values():
    try:
        with connection.cursor() as cursor:
            # Check what zid values exist for SRE records
            cursor.execute("""
                SELECT DISTINCT zid, COUNT(*) as count
                FROM imtemptrn 
                WHERE ximtmptrn LIKE %s
                GROUP BY zid
                ORDER BY zid
            """, ['%SRE-%'])
            
            zid_results = cursor.fetchall()
            print("ZID values for SRE records:")
            for zid, count in zid_results:
                print(f"  ZID {zid}: {count} records")
            
            # Check a few sample SRE records with their zid
            cursor.execute("""
                SELECT zid, ximtmptrn, xdate, xwh, xglref, xstatustrn
                FROM imtemptrn 
                WHERE ximtmptrn LIKE %s
                LIMIT 5
            """, ['%SRE-%'])
            
            sample_results = cursor.fetchall()
            print("\nSample SRE records:")
            for row in sample_results:
                print(f"  ZID: {row[0]}, SRE: {row[1]}, Date: {row[2]}, WH: {row[3]}, GL: {row[4]}, Status: {row[5]}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_zid_values()